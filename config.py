from dotenv import load_dotenv
from web3 import Web3, EthereumTesterProvider

load_dotenv()  # ###PAUL TODO: do i want to move this somewhere into the params hook? 

# keys = {'etherscan': get_secret("ETHERSCAN_API"), 
#         'arbiscan': get_secret("ARBISCAN_API")}

# ###PAUL TODO: need to add multi chain support to this one 
pool_addresses = { # example URL ----  GNS / ETH  %0.3 ---> https://info.uniswap.org/#/arbitrum/pools/0xc91b7b39bbb2c733f0e7459348fd0c80259c8471
                    'GNS/WETH_0.30': '0xc91b7b39bbb2c733f0e7459348fd0c80259c8471', 
                    'GNS/USDC': '0xaa9e653252ed9e87a9bd545b974efbfb2f389f3f',
                 } 


token_addresses = {'arbitrum': {'GNS': '0x18c11fd286c5ec11c3b683caa813b77f5163a122', 
                                'WETH': '0x82af49447d8a07e3bd95bd0d56f35241523fbab1'},
                    'polygon': {} 
                  }


routers = {'SwapRouter': '0xE592427A0AEce92De3Edee1F18E0157C05861564',
           'SwapRouter02': '0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45',
           'UniversalRouter': '0x3fC91A3afd70395Cd496C647d5a6CC9D4B2b7FAD'
           }


operating_wallets = {'GNS_ETH_2_90': {'wallet': 1,
                                      'network': 'arbitrum',
                                      'address': 'filled_in_automated_matter_not_hard_coded_for_security_reasons',
                                      'base': 'ETH',
                                      'quote': 'GNS',
                                      'pair': 'GNS/WETH_0.30',
                                      'pair_fee': 0.3, 
                                      'lp_width': 2, 
                                      'p_rebalance': 85, 
                                      },  

                    # 'GNS_USDC_2_90': {'wallet': 'NEED_TO_FIGURE_OUT_HOW_TO_HANDLE_THIS', 
                    #                   'base': 'USDC',  # THESE MAYBE SWAPPED (should be if pool setup right)
                    #                   'quote': 'GNS',  # THESE MAYBE SWAPPED (should be if pool setup right)
                    #                   'lp_width': 2, 
                    #                   'p_rebalance': 85, 
                    #                   }, 

                    'arbitrum_camelot_weth_usdc': {'wallet': 10,
                                                   'address': 'filled_in_automated_matter_not_hard_coded_for_security_reasons',
                                                   'base': 'WETH',
                                                   'quote': 'USDC',
                                                   'pair': 'WETH/USDC',
                                                   'pair_fee': 0.05, 
                                                   'lp_width': 2, 
                                                   'p_rebalance': 85, 
                                                   'add_liq_ui': 'https://app.camelot.exchange/liquidity/?type=v3&token1=0x82af49447d8a07e3bd95bd0d56f35241523fbab1&token2=0xaf88d065e77c8cc2239327c5edb3a432268e5831',
                                                   }, 
                    }

params = {}
# params ['keys'] = keys
params['pool_addresses'] = pool_addresses
params['token_addresses'] = token_addresses
params['operating_wallets'] = operating_wallets
