import sys
sys.path.insert(0, '..')
sys.path.insert(0, '../..')

from config import params 

from cryptography.fernet import Fernet
from dotenv import load_dotenv
from eth_account import Account
import json
import math
import os
import requests
from web3 import Web3, EthereumTesterProvider

load_dotenv()  # ###PAUL TODO: do i want to move this somewhere into the params hook? 

def get_secret(key):
    if key not in os.environ:
        raise KeyError(f"Key {key} not found!")
    return os.environ[key]


def get_wallet_key(wallet=1):
    # Load the encryption key
    with open(get_secret(f"KEY_FP_WALLET_{wallet}"), "rb") as key_file:
        key = key_file.read()

    # Instantiate Fernet
    cipher_suite = Fernet(key)

    # Load the encrypted private key
    encrypted_wallet_fp = f"{get_secret('REPO_PATH')}/data/cryptic_wallet_{wallet}.txt"
    with open(encrypted_wallet_fp, "rb") as file:
        encrypted_private_key = file.read()

    # Decrypt the private key
    private_key = cipher_suite.decrypt(encrypted_private_key)

    return private_key


def get_public_address(private_key):
    """given a private key calculate the public address for it 

    params: private_key (bytes, str): can handle the private string as bytes or str
    """ 
    # Assuming `private_key` is your decrypted private key in bytes format
    
    # Decode from bytes to a string, if it's not already a string
    if isinstance(private_key, bytes):
        private_key_str = private_key.decode('utf-8')  # Decoding the byte string to a normal string
    else:
        private_key_str = private_key
    
    # Remove '0x' prefix if present
    if private_key_str.startswith('0x'):
        private_key_str = private_key_str[2:]
    
    # Convert hexadecimal string to bytes
    private_key_bytes = bytes.fromhex(private_key_str)
    
    # Ensure the private key is 32 bytes long
    assert len(private_key_bytes) == 32, "The private key must be exactly 32 bytes long."
    
    # Create an account from the private key
    account = Account.from_key(private_key_bytes)
    public_address = account.address
        
    return public_address


def get_contract_abi(etherscan_api_key, contract_address):
    url = f"https://api.arbiscan.io/api?module=contract&action=getabi&address={contract_address}&apikey={etherscan_api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "1":
            return json.loads(data["result"])
        else:
            raise Exception("Error fetching ABI: " + data["message"])
    else:
        raise Exception("Error fetching ABI: HTTP " + str(response.status_code))
    

def convert_asset_wei_to_human_amount(wei_amount, asset_decimals): 
    human_amount = wei_amount / 10**asset_decimals
    return human_amount 


def convert_asset_human_amount_to_wei(human_amount, asset_decimals): 
    wei_amount = human_amount * 10**asset_decimals
    return wei_amount 


def get_actual_bags_gns_weth(public_address, w3): 
    """
    # ###PAUL TODO: 
        * this function should be refactored into a get_bags(base, quote) with token addresses passed
            * along and then utilizing a get_balance(token_address, w3=w3) 
        * combine this so that the function is called once for each token, instead of once overall  
        * make it so that contract objects are passed to this function instead of recreated 
    """
    
    gns_contract_address = params['token_addresses']['arbitrum']['GNS']
    gns_abi = get_contract_abi(get_secret("ARBISCAN_API"), gns_contract_address)
    checksummed_gns_contract_address = Web3.to_checksum_address(gns_contract_address)
    gns_contract_w3 = w3.eth.contract(address=checksummed_gns_contract_address, abi=gns_abi)
    gns_balance_wei = gns_contract_w3.functions.balanceOf(public_address).call()
    gns_decimals = gns_contract_w3.functions.decimals().call()
    gns_human_bal = gns_balance_wei / 10**gns_decimals

    # WETH STUFF 
    weth_contract_address = params['token_addresses']['arbitrum']['WETH']
    weth_abi = get_contract_abi(get_secret("ARBISCAN_API"), weth_contract_address)
    # Standard ERC-20 ABI with only the balanceOf function, not built into WETH for some odd reason. 
    standard_erc20_functions = [
        {
            "constant": True,
            "inputs": [{"name": "_owner", "type": "address"}],
            "name": "balanceOf",
            "outputs": [{"name": "balance", "type": "uint256"}],
            "type": "function",
        },
        {
            "constant": True,
            "inputs": [],
            "name": "decimals",
            "outputs": [{"name": "", "type": "uint8"}],
            "type": "function",
        }
    ]
    
    weth_abi = weth_abi + standard_erc20_functions
    checksummed_weth_contract_address = Web3.to_checksum_address(weth_contract_address)
    weth_contract_w3 = w3.eth.contract(address=checksummed_weth_contract_address, abi=weth_abi)
    
    weth_balance_wei = weth_contract_w3.functions.balanceOf(public_address).call()
    weth_decimals = weth_contract_w3.functions.decimals().call()
    weth_human_bal = weth_balance_wei / 10**weth_decimals

    # a single function should return each of these for a given base and quote token address 
    bags_dict = {'base': 'GNS', 
                 'quote': 'WETH',

                 'address': {'base':  gns_contract_address, 'quote': weth_contract_address}, 
                 'checksum_address': {'base':  checksummed_gns_contract_address, 'quote': checksummed_weth_contract_address}, 
                 'abi': {'base':  gns_abi, 'quote': weth_abi}, 
                 'w3_contract': {'base':  gns_contract_w3, 'quote': weth_contract_w3},
                 'decimal': {'base':  gns_decimals, 'quote': weth_decimals}, 

                 'actual': {'wei_format': {'base':  gns_balance_wei, 'quote': weth_balance_wei},
                            'human_format': {'base':  gns_human_bal, 'quote': weth_human_bal}, }
                 }
    
    return bags_dict


def initialize_bags_dict(public_address, base, quote, w3): 
    """
    TODO: consideration for how to properly balance `desired` given current_tick within desired spread.  
    """

    bags_dict = get_actual_bags_gns_weth(public_address=public_address, w3=w3)  # TODO: rebuild this, see the fn's docstring for instructions 

    eth_balance_wei = w3.eth.get_balance(public_address)
    eth_balance_human = Web3.from_wei(eth_balance_wei, 'ether')

    bags_dict['actual']['human_format']['eth'] =  eth_balance_human
    bags_dict['actual']['wei_format']['eth'] = eth_balance_wei

    # ###PAUL TODO: belongs in class __init__ definition?  
    bags_dict['desired'] = {# ###PAUL TODO. this gests filled in later because of ordering in the notebook. Not an issue for now but maybe move around later?
                            'wei_format': {'base':  'TODO', 'quote': 'TODO'},
                                           'human_format': {'base':  'TODO', 'quote': 'TODO'}, }

    return bags_dict 


def get_tick_spacing_for_fee(fee_percent):
    """
    Get the tick spacing for a given fee tier in Uniswap V3.
    
    :param fee_percent: The fee tier percentage (e.g., 0.3 for 0.3% fee tier).
    :return: The tick spacing associated with the fee tier.
    """
    fee_to_spacing = {
        0.05: 10,  # Example value, adjust based on Uniswap V3 specification
        0.3: 60,   # Commonly known tick spacing for 0.3% fee tier
        # Add other fee tiers and their respective spacings as needed
    }

    return fee_to_spacing.get(fee_percent)


def get_current_price_and_tick(pool_contract):
    """
    Fetch the current price and tick from a Uniswap V3 pool contract.

    :param pool_contract: The Web3 contract instance of the Uniswap V3 pool.
    :return: A tuple containing the current digital price and the current tick.
    """
    # Fetching slot0 which contains the current price and other data
    slot0 = pool_contract.functions.slot0().call()
    current_sqrt_price_x96 = slot0[0]
    current_tick = slot0[1]  # The current tick index

    return current_sqrt_price_x96, current_tick


def calculate_tick_from_price(price):
    """Calculate the tick index for a given price."""
    return int(math.log(price) / math.log(1.0001))


def calculate_price_from_tick(tick):
    """Calculate the price for a given tick index."""
    return 1.0001 ** tick


def get_tick_range(current_tick, price_range_percent, tick_spacing):
    """Calculate the tick range around the current tick within the given price range."""
    # Calculate price multiplier for the given percentage range
    price_multiplier = 1 + price_range_percent / 100

    # Calculate upper and lower price bounds
    current_human_price = 1.0001 ** current_tick   # note this calculates current_price as a 
    upper_human_price = current_human_price * price_multiplier
    lower_human_price = current_human_price / price_multiplier

    # Calculate the corresponding ticks for the upper and lower prices
    upper_tick = calculate_tick_from_price(upper_human_price)
    lower_tick = calculate_tick_from_price(lower_human_price)

    # Adjust ticks to be multiples of tick_spacing
    upper_tick = upper_tick - (upper_tick % tick_spacing)
    lower_tick = lower_tick - (lower_tick % tick_spacing)

    # Create a range of ticks from lower to upper
    return range(lower_tick, upper_tick + 1, tick_spacing)



def convert_sqrt_price_x96_to_human(sqrt_price_x96, base_decimals=18, quote_decimals=18):
    """ Convert a digital price from Uniswap V3 format to a human-readable price ratio.
    """
    
    # Convert sqrtPriceX96 to the actual square root of the price ratio
    sqrt_price_ratio = sqrt_price_x96 / 2**96
    price_ratio = sqrt_price_ratio ** 2

    # Adjust for token decimals
    decimal_difference = base_decimals - quote_decimals
    human_price = price_ratio / 10**decimal_difference

    return human_price






# end of file to lengthen 



