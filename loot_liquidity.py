from web3 import Web3
import json

class LiquidityLooter:
    def __init__(self, rpc_url):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))
        if self.web3.is_connected():
            print("Connected to Ethereum blockchain.")
        else:
            raise Exception("Unable to connect to Ethereum blockchain.")

    def fetch_current_pool_price_range(self, pool_address, abi):
        # Convert the pool address to checksum format
        checksum_address = Web3.to_checksum_address(pool_address)

        # Create a contract object using the ABI and the pool's address
        pool_contract = self.web3.eth.contract(address=checksum_address, abi=abi)

        try:
            # Fetching slot0 which contains the current price and other data
            slot0 = pool_contract.functions.slot0().call()
            current_price = slot0[0]

            # Convert current price to a more readable format if necessary
            # This depends on how prices are represented in the contract

            # Return the current price (this can be expanded to include more data)
            return {"current_price": current_price}

        except Exception as e:
            print(f"An error occurred: {e}")
            return None

# Example usage
rpc_url = "https://arb1.arbitrum.io/rpc"  # Arbitrum RPC URL
loot_liquidity = LiquidityLooter(rpc_url)

# The contract address and ABI for the Uniswap v3 pool
pool_address = "0xc91b7b39bbb2c733f0e7459348fd0c80259c8471"
# abi = [...]  # Replace with the ABI provided

# Fetching the pool price range for the specific pool
price_range = loot_liquidity.fetch_current_pool_price_range(pool_address, abi)
print(f"Price Range: {price_range}")
