const CarbonCertificate = artifacts.require("CarbonCertificate");
const CarbonMarket = artifacts.require("CarbonMarket");

module.exports = async function(deployer, network, accounts) {
  
  await deployer.deploy(CarbonCertificate, "Carbon Certificate", "CCERT", "https://example.com/meta/");
  const cert = await CarbonCertificate.deployed();

  
  await deployer.deploy(CarbonMarket, cert.address);
  const market = await CarbonMarket.deployed();

 
  await web3.eth.sendTransaction({ from: accounts[0], to: market.address, value: web3.utils.toWei("10", "ether") });

  
  if (accounts.length > 1) {
    await market.addValidator(accounts[1], { from: accounts[0] });
  }
  if (accounts.length > 2) {
    await market.addValidator(accounts[2], { from: accounts[0] });
  }

  console.log("CarbonMarket deployed at", market.address);
  console.log("CarbonCertificate deployed at", cert.address);
};
