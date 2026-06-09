const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');

// Configuration
const RPC_URL = 'https://mainnet.base.org';
const NOOK_ADDRESS = '0xb233BDFFD437E60fA451F62c6c09D3804d285Ba3';
const NOOK_ABI = [
  "function balanceOf(address owner) view returns (uint256)",
  "function transfer(address to, uint amount) returns (bool)",
  "function decimals() view returns (uint8)"
];

// Wallet names to process
const wallets = [
  'abel', 'bagong', 'ball', 'din', 'don', 'gord', 'gordon', 
  'heist', 'herdnol', 'jordi', 'kaiju8', 'kikuk', 'kimak', 'liau', 'pratama'
];

async function main() {
  const targetAddress = process.argv[2];
  if (!targetAddress || !targetAddress.startsWith('0x')) {
    console.error('Usage: node transfer-nook.js <target_address>');
    process.exit(1);
  }

  const provider = new ethers.JsonRpcProvider(RPC_URL);
  const nookContract = new ethers.Contract(NOOK_ADDRESS, NOOK_ABI, provider);
  const decimals = await nookContract.decimals();

  console.log(`Target: ${targetAddress}`);
  console.log(`NOOK Decimals: ${decimals}\n`);

  for (const name of wallets) {
    const envPath = path.join(process.env.HOME, `nookplot-${name}`, '.env');
    if (!fs.existsSync(envPath)) {
      console.log(`[${name}] SKIP: .env not found`);
      continue;
    }

    const envContent = fs.readFileSync(envPath, 'utf8');
    
    // Try multiple private key formats
    let privateKey = null;
    const pkMatch1 = envContent.match(/NOOKPLOT_AGENT_PRIVATE_KEY=(0x[a-fA-F0-9]+)/);
    const pkMatch2 = envContent.match(/WALLET_PRIVATE_KEY=([a-fA-F0-9]+)/);
    const pkMatch3 = envContent.match(/NOOKPLOT_PRIVATE_KEY=(0x[a-fA-F0-9]+)/);
    
    if (pkMatch1) privateKey = pkMatch1[1];
    else if (pkMatch2) privateKey = '0x' + pkMatch2[1];
    else if (pkMatch3) privateKey = pkMatch3[1];

    const addressMatch = envContent.match(/NOOKPLOT_AGENT_ADDRESS=(0x[a-fA-F0-9]+)/i) || 
                         envContent.match(/NOOKPLOT_ADDRESS=(0x[a-fA-F0-9]+)/i);

    if (!privateKey || !addressMatch) {
      console.log(`[${name}] SKIP: No private key or address found`);
      continue;
    }

    const address = addressMatch[1];

    try {
      const wallet = new ethers.Wallet(privateKey, provider);
      const balance = await nookContract.balanceOf(address);
      const balanceFormatted = ethers.formatUnits(balance, decimals);

      console.log(`[${name}] Address: ${address}`);
      console.log(`[${name}] NOOK Balance: ${balanceFormatted}`);

      if (BigInt(balance) > 0n) {
        const ethBalance = await provider.getBalance(address);
        console.log(`[${name}] ETH Balance: ${ethers.formatEther(ethBalance)} (for gas)`);

        if (ethBalance < ethers.parseEther('0.00001')) {
          console.log(`[${name}] WARNING: Low ETH, transfer might fail due to gas`);
        }

        console.log(`[${name}] Transferring ${balanceFormatted} NOOK to ${targetAddress}...`);
        
        const tx = await nookContract.connect(wallet).transfer(targetAddress, balance, { gasLimit: 100000 });
        console.log(`[${name}] TX Hash: ${tx.hash}`);
        
        const receipt = await tx.wait();
        console.log(`[${name}] SUCCESS: Confirmed in block ${receipt.blockNumber}\n`);
      } else {
        console.log(`[${name}] SKIP: Zero balance\n`);
      }
    } catch (error) {
      if (error.message.includes('already known')) {
        console.log(`[${name}] TX already known (likely succeeded, verify balance)\n`);
      } else {
        console.error(`[${name}] ERROR: ${error.message}\n`);
      }
    }

    // Delay 2 seconds between wallets to avoid rate limiting
    await new Promise(r => setTimeout(r, 2000));
  }

  console.log('Done.');
}

main().catch(console.error);
