# BITCOIN-SCRIPTING

## Goal:
To create and validate Bitcoin transactions using Legacy (P2PKH) and SegWit (P2SH-P2WPKH) address formats.To interact with bitcoind, create transactions, and analyze the scripts involved.Also compare the transaction sizes and understand the differences.

Members:
<br>
- [Param Saxena(230001060)](https://github.com/SAXENA-PARAM)
- [Saumya Vaidya(230008035)](https://github.com/samthedoctor)
- [Jagrit(230051005)](https://github.com/idJagrit)


### Language Choice:
1. Bitcoin Core (bitcoind): A full node implementation of Bitcoin.
2. Python : For scripting and interacting with bitcoind.
3. Bitcoin CLI (bitcoin-cli): Command-line tool to interact with bitcoind.
4. Bitcoin Debugger: For validating and decoding scripts.
5. Library Dependencies:
 For Python: python-bitcoinlib or bitcoinrpc.

## 🔹 Step 1: Install Bitcoin Core
1. Download Bitcoin Core: [Bitcoin Core Download](https://bitcoincore.org/en/download/)  
2. Install it by dragging it to the Applications folder.  
3. Verify the installation:  
   ```bash
   bitcoin-cli --version
   ```

---

## 🔹 Step 2: Configure Bitcoin Core for Regtest Mode
1. Create a Bitcoin data directory:  
   ```bash
   mkdir -p ~/Library/Application\ Support/Bitcoin
   ```
2. Create and edit the configuration file:  
   ```bash
   nano ~/Library/Application\ Support/Bitcoin/bitcoin.conf
   ```
3. Paste the following configuration and save:  
   ```
   regtest=1
   server=1
   txindex=1
   rpcuser=RPC_USER
   rpcpassword=RPC_PASSWORD
   rpcallowip=127.0.0.1
   rpcport=RPC_PORT
   fallbackfee=0.0002
   mintxfee=0.00001
   txconfirmtarget=1
   ```

---

## 🔹 Step 3: Start Bitcoin Core in Regtest Mode
Run the following command to start Bitcoin Core:  
```bash
bitcoind -regtest -daemon
```
Verify if it's running:  
```bash
bitcoin-cli -regtest getblockchaininfo
```

---

## 🔹 Step 4: Generate Initial Blocks
Generate 101 blocks to create BTC for testing:  
```bash
bitcoin-cli -regtest generatetoaddress 101 $(bitcoin-cli -regtest getnewaddress)
```

---

## 🔹 Step 5: Run the Part 1 Python Scripts
These scripts:  
✔ Connect to bitcoind  
✔ Create/load a wallet  
✔ Generate 3 legacy addresses (A, B, C)  
✔ Fund address A  
✔ Send BTC from A → B  

Navigate to the **Question1** folder and run the scripts:  
```bash
cd /Question1
python -u transaction_a_to_b.py
python -u transaction_b_to_c.py
```

If errors occur:  
- Ensure `bitcoind` is running.  
- Check `bitcoin.conf` settings.  
- Create a wallet if necessary:  
  ```bash
  bitcoin-cli -regtest createwallet "test_wallet"
  ```

---

## 🔹 Step 6: Run the Question 2 Python Script
This script:  
✔ Fetches UTXOs from B  
✔ Creates a transaction from B → C  
✔ Decodes & analyzes the transaction  

Navigate to the **Question2** folder and run the script:  
```bash
cd /Question2
python -u q2.py
```

---

## 🔹 Step 7: Debug Bitcoin Scripts
Install `btcdeb` for debugging:  
```bash
brew install bitcoin
```
Or compile from source:  
```bash
git clone https://github.com/bitcoin-core/btcdeb.git
cd btcdeb
make
```

Run the debugger:  
```bash
btcdeb -v -s "<signature><public_key> OP_DUP OP_HASH160<recipient_public_key_hash>OP_EQUALVERIFYOP_CHECKSIG"
```

---
