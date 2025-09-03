from stellar_sdk import Keypair, Server, TransactionBuilder, Network, Asset

# --------------------------
# 1. Setup Stellar network
# --------------------------
# Use TESTNET for experiments
server = Server("https://horizon-testnet.stellar.org")
network_passphrase = Network.TESTNET_NETWORK_PASSPHRASE

# --------------------------
# 2. Create keypairs
# --------------------------
# Issuer account (creates the token)
issuer_kp = Keypair.random()
print("Issuer Public Key:", issuer_kp.public_key)
print("Issuer Secret:", issuer_kp.secret)

# Distributor account (holds and distributes the token)
distributor_kp = Keypair.random()
print("Distributor Public Key:", distributor_kp.public_key)
print("Distributor Secret:", distributor_kp.secret)

# --------------------------
# 3. Fund accounts on Testnet
# --------------------------
print("Fund accounts using Friendbot testnet...")
import requests
requests.get(f"https://friendbot.stellar.org?addr={issuer_kp.public_key}")
requests.get(f"https://friendbot.stellar.org?addr={distributor_kp.public_key}")

# --------------------------
# 4. Define your asset
# --------------------------
token_code = "MYTOKEN"  # Token symbol (1-12 chars)
my_token = Asset(code=token_code, issuer=issuer_kp.public_key)

# --------------------------
# 5. Trustline: Distributor trusts the token
# --------------------------
distributor_account = server.load_account(distributor_kp.public_key)

trust_transaction = (
    TransactionBuilder(
        source_account=distributor_account,
        network_passphrase=network_passphrase,
        base_fee=100
    )
    .append_change_trust_op(
        asset=my_token,
        limit="1000000"  # max amount the distributor can hold
    )
    .set_timeout(30)
    .build()
)

trust_transaction.sign(distributor_kp)
trust_response = server.submit_transaction(trust_transaction)
print("Trustline created:", trust_response)

# --------------------------
# 6. Issuer sends tokens to distributor
# --------------------------
issuer_account = server.load_account(issuer_kp.public_key)

payment_transaction = (
    TransactionBuilder(
        source_account=issuer_account,
        network_passphrase=network_passphrase,
        base_fee=100
    )
    .append_payment_op(
        destination=distributor_kp.public_key,
        asset=my_token,
        amount="1000"  # Amount of token to issue
    )
    .set_timeout(30)
    .build()
)

payment_transaction.sign(issuer_kp)
payment_response = server.submit_transaction(payment_transaction)
print(f"Sent 1000 {token_code} to distributor:", payment_response)
