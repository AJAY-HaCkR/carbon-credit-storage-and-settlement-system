// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "../@openzeppelin/contracts/access/Ownable.sol";
import "../@openzeppelin/contracts/utils/structs/EnumerableSet.sol";
import "./CarbonCertificate.sol";

contract CarbonMarket is Ownable {
    using EnumerableSet for EnumerableSet.AddressSet;

    enum CertType { NONE, ESCERT, REC, OTHER }
    enum ClaimStatus { Pending, Approved, Rejected, Burned }

    struct Claim {
        uint256 id;
        address user;
        CertType ctype;
        uint256 units;
        uint256 ethEquivalentWei;
        ClaimStatus status;
        uint256 createdAt;
    }

    CarbonCertificate public certificate;
    uint256 public nextClaimId;
    mapping(uint256 => Claim) public claims;
    mapping(address => uint256) public carbonBalance;
    EnumerableSet.AddressSet private validators;

    uint256 public redeemRateWei; // wei per unit
    event ClaimSubmitted(uint256 id, address user, CertType ctype, uint256 units, uint256 ethWei);
    event ClaimApproved(uint256 id, address user, uint256 units, uint256 ethWei);
    event ClaimRejected(uint256 id, address user);
    event ClaimBurned(address user, uint256 units, uint256 ethWei);
    event ValidatorAdded(address account);

    constructor(address certAddr) {
        certificate = CarbonCertificate(certAddr);
        nextClaimId = 1;
        redeemRateWei = 0;
    }

    modifier onlyValidator() {
        require(validators.contains(msg.sender), "not validator");
        _;
    }

    function addValidator(address a) external onlyOwner {
        require(validators.add(a), "exists");
        emit ValidatorAdded(a);
    }

    // Submit claim; credit type passed as string index from frontend via integer mapping
    function submitClaim(uint256 units, CertType ctype, uint256 ethEquivalentWei) external {
        require(units > 0, "bad units");
        require(ctype != CertType.NONE, "bad type");
        uint256 id = nextClaimId++;
        claims[id] = Claim(id, msg.sender, ctype, units, ethEquivalentWei, ClaimStatus.Pending, block.timestamp);
        emit ClaimSubmitted(id, msg.sender, ctype, units, ethEquivalentWei);
    }

    // Validator approves, increases on-chain unit balance and optionally pays out ETH
    function approveClaim(uint256 id, uint256 payoutWei) external onlyValidator {
        Claim storage c = claims[id];
        require(c.status == ClaimStatus.Pending, "not pending");
        c.status = ClaimStatus.Approved;
        carbonBalance[c.user] += c.units;

        if (payoutWei > 0) {
            require(address(this).balance >= payoutWei, "insufficient contract ETH");
            (bool ok, ) = payable(c.user).call{value: payoutWei}("");
            require(ok, "transfer failed");
        }

        // mint a certificate when milestone crossed (example: every 100 units)
        uint256 milestone = 100;
        uint256 beforeBalance = carbonBalance[c.user] - c.units;
        uint256 afterBalance = carbonBalance[c.user];
        if (afterBalance / milestone > beforeBalance / milestone) {
            certificate.mintTo(c.user);
        }

        emit ClaimApproved(id, c.user, c.units, payoutWei);
    }

    function rejectClaim(uint256 id) external onlyValidator {
        Claim storage c = claims[id];
        require(c.status == ClaimStatus.Pending, "not pending");
        c.status = ClaimStatus.Rejected;
        emit ClaimRejected(id, c.user);
    }

    function setRedeemRate(uint256 weiPerUnit) external onlyOwner {
        redeemRateWei = weiPerUnit;
    }

    function burn(uint256 units) external {
        require(units > 0, "bad");
        require(carbonBalance[msg.sender] >= units, "insufficient units");
        uint256 ethOut = units * redeemRateWei;
        require(address(this).balance >= ethOut, "insufficient contract ETH");
        carbonBalance[msg.sender] -= units;
        (bool ok, ) = payable(msg.sender).call{value: ethOut}("");
        require(ok, "transfer failed");
        emit ClaimBurned(msg.sender, units, ethOut);
    }

    receive() external payable {}
    fallback() external payable {}
}
