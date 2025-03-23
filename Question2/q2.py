import json
import time
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal

# Connect to Bitcoin Core RPC
RPC_USER = "testuser"
RPC_PASSWORD = "testpass123"
RPC_PORT = 18443
RPC_URL = f"http://{RPC_USER}:{RPC_PASSWORD}@127.0.0.1:{RPC_PORT}/wallet/segwit_wallet"
rpc_connection = AuthServiceProxy(RPC_URL)

def wait_for_confirmation(txid, max_attempts=10):
    """Wait for a transaction to be confirmed."""
    for _ in range(max_attempts):
        tx_details = rpc_connection.gettransaction(txid)
        if tx_details["confirmations"] > 0:
            return True
        time.sleep(2)
    return False

def create_transaction(from_address, to_address, amount, fee):
    """Create, sign, and broadcast a transaction."""
    unspent = rpc_connection.listunspent(1, 9999999, [from_address])

    if not unspent:
        raise Exception(f"No UTXO found for {from_address}")

    utxo = unspent[0]
    txid, vout, utxo_amount = utxo["txid"], utxo["vout"], Decimal(str(utxo["amount"]))

    change = utxo_amount - amount - fee
    if change < 0:
        raise Exception("Insufficient funds after fee deduction.")

    inputs = [{"txid": txid, "vout": vout}]
    outputs = {to_address: float(amount), from_address: float(change)}

    raw_tx = rpc_connection.createrawtransaction(inputs, outputs)
    signed_tx = rpc_connection.signrawtransactionwithwallet(raw_tx)

    if not signed_tx["complete"]:
        raise Exception("Transaction signing failed.")

    txid = rpc_connection.sendrawtransaction(signed_tx["hex"])
    return txid, signed_tx["hex"]

def main():
    try:
        print("🔹 Loading Wallet 'segwit_wallet'...")
        if "segwit_wallet" not in rpc_connection.listwallets():
            raise Exception("Wallet 'segwit_wallet' is not loaded!")

        print("✅ Wallet 'segwit_wallet' is loaded.")

        print("\n🔹 Generating P2SH-SegWit addresses...")
        address_a = rpc_connection.getnewaddress("", "p2sh-segwit")
        address_b = rpc_connection.getnewaddress("", "p2sh-segwit")
        address_c = rpc_connection.getnewaddress("", "p2sh-segwit")

        print(f"🔹 Address A': {address_a}")
        print(f"🔹 Address B': {address_b}")
        print(f"🔹 Address C': {address_c}")

        print("\n🔹 Funding Address A' with 1 BTC...")
        txid_funding = rpc_connection.sendtoaddress(address_a, Decimal("1.0"))
        print(f"✅ Transaction ID (Funding A'): {txid_funding}")

        print("\n🔹 Mining 1 block to confirm the transaction...")
        rpc_connection.generatetoaddress(1, rpc_connection.getnewaddress())

        if not wait_for_confirmation(txid_funding):
            raise Exception("Funding transaction not confirmed!")

        print("\n🔹 Creating Transaction A' → B'...")
        txid_a_to_b, signed_tx_a_to_b = create_transaction(address_a, address_b, Decimal("0.5"), Decimal("0.0001"))
        print(f"✅ Transaction A' → B' broadcasted: {txid_a_to_b}")

        print("\n🔹 Mining 1 block to confirm A' → B'...")
        rpc_connection.generatetoaddress(1, rpc_connection.getnewaddress())

        if not wait_for_confirmation(txid_a_to_b):
            raise Exception("Transaction A' → B' not confirmed!")

        print("\n🔹 Creating Transaction B' → C'...")
        txid_b_to_c, signed_tx_b_to_c = create_transaction(address_b, address_c, Decimal("0.3"), Decimal("0.0001"))
        print(f"✅ Transaction B' → C' broadcasted: {txid_b_to_c}")

        print("\n🔹 Mining 1 block to confirm B' → C'...")
        rpc_connection.generatetoaddress(1, rpc_connection.getnewaddress())

        if not wait_for_confirmation(txid_b_to_c):
            raise Exception("Transaction B' → C' not confirmed!")

        print("\n🔹 Decoding Transactions...")
        decoded_tx_a_to_b = rpc_connection.decoderawtransaction(signed_tx_a_to_b)
        decoded_tx_b_to_c = rpc_connection.decoderawtransaction(signed_tx_b_to_c)

        # Convert Decimal to String before saving
        data = {
            "txid_a_to_b": txid_a_to_b,
            "txid_b_to_c": txid_b_to_c,
            "decoded_a_to_b": json.loads(json.dumps(decoded_tx_a_to_b, default=str)),
            "decoded_b_to_c": json.loads(json.dumps(decoded_tx_b_to_c, default=str))
        }

        with open("transaction_details.json", "w") as f:
            json.dump(data, f, indent=4)

        print("\n✅ Transactions completed successfully!")
        print(f"🔹 TXID A' → B': {txid_a_to_b}")
        print(f"🔹 TXID B' → C': {txid_b_to_c}")

    except JSONRPCException as e:
        print(f"❌ RPC Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
