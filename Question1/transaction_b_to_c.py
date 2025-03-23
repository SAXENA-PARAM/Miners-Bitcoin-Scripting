import json
from decimal import Decimal
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# RPC connection settings (from your bitcoin.conf)
rpc_user = "testuser"
rpc_password = "testpass123"
rpc_port = 18443
rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@127.0.0.1:{rpc_port}")

def decimal_to_float(obj):
    """Convert Decimal to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError("Object of type {} is not JSON serializable".format(type(obj).__name__))

def main():
    try:
        # 1. Ensure the wallet is loaded
        print("Ensuring wallet is loaded...")
        wallet_name = "mywallet"
        loaded_wallets = rpc_connection.listwallets()
        if wallet_name not in loaded_wallets:
            print(f"Wallet '{wallet_name}' not loaded, loading it...")
            rpc_connection.loadwallet(wallet_name)
        else:
            print(f"Wallet '{wallet_name}' is already loaded.")

        # 2. Load details from the previous transaction
        with open("transaction_a_to_b.json", "r") as f:
            prev_data = json.load(f)
        txid_a_to_b = prev_data["txid_a_to_b"]
        script_pubkey_b = prev_data["scriptPubKey_b"]
        address_b = prev_data["address_b"]
        address_c = prev_data["address_c"]

        # 3. Mine a block to confirm the previous transaction
        print("Mining a block to confirm the A-to-B transaction...")
        dummy_address = rpc_connection.getnewaddress()
        rpc_connection.generatetoaddress(1, dummy_address)

        # 4. Get the listunspent for Address B
        print("Listing unspent outputs for Address B...")
        unspent = rpc_connection.listunspent(1, 9999999, [address_b])
        utxo = None
        for u in unspent:
            if u["txid"] == txid_a_to_b:
                utxo = u
                break
        if not utxo:
            raise Exception("No UTXO found for Address B from the A-to-B transaction")
        print(f"Found UTXO: {utxo}")

        # 5. Create a transaction from B to C
        print("Creating raw transaction from B to C...")
        txid = utxo["txid"]
        vout = utxo["vout"]
        amount = float(utxo["amount"])  # Ensure it's a float

        # Send 0.5 BTC to Address C, return change to Address B
        amount_to_send = 0.5
        fee = 0.0001  # Based on paytxfee
        change = amount - amount_to_send - fee
        if change < 0:
            raise Exception("Insufficient funds after accounting for fee")

        inputs = [{"txid": txid, "vout": vout}]
        outputs = {address_c: amount_to_send, address_b: change}
        raw_tx = rpc_connection.createrawtransaction(inputs, outputs)
        print(f"Raw transaction: {raw_tx}")

        # 6. Sign the transaction
        print("Signing the transaction...")
        signed_tx = rpc_connection.signrawtransactionwithwallet(raw_tx)
        if not signed_tx["complete"]:
            raise Exception("Failed to sign transaction")
        signed_tx_hex = signed_tx["hex"]
        print(f"Signed transaction: {signed_tx_hex}")

        # 7. Broadcast the transaction
        print("Broadcasting the transaction...")
        txid_b_to_c = rpc_connection.sendrawtransaction(signed_tx_hex)
        print(f"Transaction B to C broadcasted, txid: {txid_b_to_c}")

        # 8. Decode and analyze the transaction
        print("Decoding the transaction...")
        decoded_tx = rpc_connection.decoderawtransaction(signed_tx_hex)
        print("Decoded transaction:")
        print(json.dumps(decoded_tx, indent=2, default=decimal_to_float))

        # Extract the scriptSig (unlocking script) for the input
        script_sig = decoded_tx["vin"][0]["scriptSig"]["hex"]
        print(f"Unlocking script (scriptSig) for Address B: {script_sig}")

        # 9. Compare scriptSig with the scriptPubKey from A-to-B
        print("\nComparing scripts...")
        print(f"Challenge script (scriptPubKey from A-to-B): {script_pubkey_b}")
        print(f"Response script (scriptSig from B-to-C): {script_sig}")

        # Save the transaction details for the report
        with open("transaction_b_to_c.json", "w") as f:
            json.dump({
                "txid_b_to_c": txid_b_to_c,
                "scriptSig": script_sig,
                "scriptPubKey_b": script_pubkey_b
            }, f, indent=2, default=decimal_to_float)

    except JSONRPCException as e:
        print(f"RPC error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
