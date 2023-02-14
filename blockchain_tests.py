import json, asyncio, orjson

from web3 import Web3, HTTPProvider, AsyncHTTPProvider
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.rpc import rpc_gas_price_strategy

from web3._utils.contracts import encode_abi
from web3._utils.abi import get_abi_output_types
from web3.types import HexBytes

from web3.eth import AsyncEth

from aioethereum.rpc import Ethereum
from aioethereum.utils import to_checksum_address
from aioethereum.contract import Contract

from py_crypto_hd_wallet import HdWalletBip44Coins, HdWalletBipWordsNum, \
	HdWalletBipLanguages, HdWalletBipFactory, HdWalletBipDataTypes, HdWalletBipChanges

"""
def BalanceERC20_Token(token_contract, address, network_rpc):
	web3 = Web3(HTTPProvider(network_rpc))
	web3.middleware_onion.inject(geth_poa_middleware, layer=0)

	ERC20_ABI = [{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]

	erc20_contract = web3.eth.contract(token_contract, abi=ERC20_ABI)
	balance = erc20_contract.functions.balanceOf(address).call()

	print(balance)


BalanceERC20_Token(
	'0xC51FceEc013cD34aE2e95E6D64E9858F2aC28fFf',
	'0x91b1E63e844c84Ebe729050941f17B22BF25714F',
	'https://eth-goerli.api.onfinality.io/public' 
)
"""

"""
json_file = './data/networks_list.json'

with open(json_file, 'r', encoding='utf-8') as file:
	networks_json = json.load(file)
with open(json_file, "r", encoding='utf-8') as file:
	networks_json = orjson.loads(file.read())

def GetListOfNetworks() -> list:
	networks = []
	for network in networks_json:
		networks.append(network)

	return networks

def GetNetworkRPC(network):
	return networks_json[network]['rpc_url']

def GetUserAddress():
	return '0x91b1E63e844c84Ebe729050941f17B22BF25714F'

def InitAsyncWeb3Network(network_rpc):
	async_web3 = Web3(
		AsyncHTTPProvider(network_rpc),
		modules={"eth": (AsyncEth, )},
		middlewares=[]
	)

	return async_web3

def InitWeb3Network(network_rpc):
	web3 = Web3(HTTPProvider(network_rpc))
	web3.middleware_onion.inject(geth_poa_middleware, layer=0)

	return web3

async def AsyncGetWalletMainBalance(async_web3, address, network):
	balance = await async_web3.eth.get_balance(address)
	balance = float(async_web3.fromWei(balance, "ether"))

	return {network : balance}

def CreateERC20_Contract(ethereum, token_contract):
	ERC20_ABI = [
		{
			"constant": True,
			"inputs": [{"name": "_owner", "type": "address"}],
			"name": "balanceOf",
			"outputs": [{"name": "balance", "type": "uint256"}],
			"payable": False,
			"type": "function"
		}
	]
	erc20_contract = Contract(ethereum, token_contract, ERC20_ABI)

	return erc20_contract

async def GetWalletTokenBalance(async_web3, ethereum, address, token_contract, network, token_name):
	erc20_contract = CreateERC20_Contract(ethereum, token_contract)
	balance = await erc20_contract.functions.balanceOf(to_checksum_address(address)).call()
	balance = float(async_web3.fromWei(balance, "ether"))

	return {f"{network}_{token_name}" : balance}

async def GetAllBalances():
	balances = []

	address = GetUserAddress()
	networks = GetListOfNetworks()

	tasks = []
	for network in networks:
		network_rpc = GetNetworkRPC(network)
		async_web3 = InitAsyncWeb3Network(network_rpc)
		tasks.append(AsyncGetWalletMainBalance(async_web3, address, network))
	balances = await asyncio.gather(*tasks)

	tasks = []
	for network in networks:
		network_rpc = GetNetworkRPC(network)
		async_web3 = InitAsyncWeb3Network(network_rpc)
		web3 = InitWeb3Network(network_rpc)
		ethereum = Ethereum(network_rpc)

		network_erc20tokens = networks_json[network]['erc20tokens']
		for erc20token in network_erc20tokens:
			token_contract = erc20token['token_contract']
			token_name = erc20token['token']
			tasks.append(GetWalletTokenBalance(async_web3, ethereum, address, token_contract, network, token_name))
	balances = await asyncio.gather(*tasks)

	balances.append(
		{
			network : GetWalletMainBalance(web3, address, network_rpc),
			'network_type' : network_type,
			'tokens_balances' : tokens_balances
		}
	)

	return balances

async def main():
	print('start')
	balances = await GetAllBalances()

	print(balances)

asyncio.run(main())
"""