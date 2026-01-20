// SPDX-License-Identifier: MIT
pragma solidity ^0.8.13;

import "../@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "../@openzeppelin/contracts/access/Ownable.sol";

contract CarbonCertificate is ERC721, Ownable {
    uint256 public nextId;
    string private _base;

    constructor(string memory name_, string memory symbol_, string memory base_) ERC721(name_, symbol_) {
        nextId = 1;
        _base = base_;
    }

    function mintTo(address to) external onlyOwner returns (uint256) {
        uint256 id = nextId;
        _safeMint(to, id);
        nextId++;
        return id;
    }

    function _baseURI() internal view override returns (string memory) {
        return _base;
    }
}
