import json
import time
from decimal import Decimal
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# RPC connection settings (from your bitcoin.conf)
rpc_user = "testuser"
rpc_password = "testpass123"
rpc_port = 18443
rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@127.0.0.1:{rpc_port}")

def decimal_to_str(obj):
    """Convert Decimal objects to string for JSON serialization."""
    if isinstance(obj, Decimal):
        return str(obj)
    raise TypeError("Type not serializable")

def main():
    try:
        # 1. Create or load the wallet
        print("Creating/loading wallet...")
        wallet_name = "mywallet"
        
        # Check if the wallet is already loaded
        loaded_wallets = rpc_connection.listwallets()
        if wallet_name in loaded_wallets:
            print(f"Wallet '{wallet_name}' is already loaded.")
        else:
            # Try to create the wallet if it doesn't exist
            try:
                rpc_connection.createwallet(wallet_name)
                print(f"Wallet '{wallet_name}' created.")
            except JSONRPCException as e:
                if "Database already exists" in str(e):
                    print(f"Wallet '{wallet_name}' already exists, loading it...")
                    rpc_connection.loadwallet(wallet_name)
                else:
                    raise e

        # 2. Generate three legacy addresses (A, B, C)
        print("Generating legacy addresses...")
        address_a = rpc_connection.getnewaddress("Address A", "legacy")
        address_b = rpc_connection.getnewaddress("Address B", "legacy")
        address_c = rpc_connection.getnewaddress("Address C", "legacy")
        print(f"Address A: {address_a}")
        print(f"Address B: {address_b}")
        print(f"Address C: {address_c}")

        # 3. Fund Address A
        print("Funding Address A...")
        # Generate 101 blocks to create coins (coinbase rewards need 100 blocks to mature)
        rpc_connection.generatetoaddress(101, address_a)
        print("Generated 101 blocks to fund Address A")
        balance_a = rpc_connection.getbalance()
        print(f"Balance of Address A: {balance_a} BTC")

        # 4. Create a transaction from A to B
        print("Creating raw transaction from A to B...")
        # List unspent outputs for Address A
        unspent = rpc_connection.listunspent(1, 9999999, [address_a])
        if not unspent:
            raise Exception("No unspent outputs found for Address A")
        utxo = unspent[0]  # Take the first UTXO
        txid = utxo["txid"]
        vout = utxo["vout"]
        amount = Decimal(str(utxo["amount"]))  # Ensure amount is a Decimal

        # Send 1 BTC to Address B, return change to Address A
        amount_to_send = Decimal("1.0")  # Convert to Decimal
        fee = Decimal("0.0001")  # Convert to Decimal
        change = amount - amount_to_send - fee  # Now all values are Decimal

        if change < 0:
            raise Exception("Insufficient funds after accounting for fee")

        # Create raw transaction
        inputs = [{"txid": txid, "vout": vout}]
        outputs = {address_b: float(amount_to_send), address_a: float(change)}  # Convert back to float
        raw_tx = rpc_connection.createrawtransaction(inputs, outputs)
        print(f"Raw transaction: {raw_tx}")

        # 5. Sign the transaction
        print("Signing the transaction...")
        signed_tx = rpc_connection.signrawtransactionwithwallet(raw_tx)
        if not signed_tx["complete"]:
            raise Exception("Failed to sign transaction")
        signed_tx_hex = signed_tx["hex"]
        print(f"Signed transaction: {signed_tx_hex}")

        # 6. Broadcast the transaction
        print("Broadcasting the transaction...")
        txid_a_to_b = rpc_connection.sendrawtransaction(signed_tx_hex)
        print(f"Transaction A to B broadcasted, txid: {txid_a_to_b}")

        # 7. Decode and analyze the transaction
        print("Decoding the transaction...")
        decoded_tx = rpc_connection.decoderawtransaction(signed_tx_hex)
        print("Decoded transaction:")
        print(json.dumps(decoded_tx, indent=2, default=decimal_to_str))  # Fix for Decimal serialization

        # Extract the locking script (scriptPubKey) for Address B
        script_pubkey_b = None
        for vout in decoded_tx["vout"]:
            if "addresses" in vout["scriptPubKey"] and vout["scriptPubKey"]["addresses"][0] == address_b:
                script_pubkey_b = vout["scriptPubKey"]["hex"]
                print(f"Locking script (scriptPubKey) for Address B: {script_pubkey_b}")
                break

        # Save the txid and scriptPubKey for the next script
        with open("transaction_a_to_b.json", "w") as f:
            json.dump({
                "txid_a_to_b": txid_a_to_b,
                "scriptPubKey_b": script_pubkey_b,
                "address_a": address_a,
                "address_b": address_b,
                "address_c": address_c
            }, f, indent=2, default=decimal_to_str)  # Fix for Decimal serialization

    except JSONRPCException as e:
        print(f"RPC error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
