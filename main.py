import keyboards, config, networks_imports
import json, requests, asyncio, threading, orjson

from random import randint
from threading import Thread
from datetime import datetime

# -------------------- Parametrs -------------------- #
BOT_TOKEN = config.token # Telegram Bot Token
BOT_VERSION = config.bot_version # Telegram Bot Version
DEFAULT_LANGUAGE = config.default_language # Bot Default Language

DB_HOST = config.db_host # DataBase Host IP
DB_USER = config.db_user # DataBase User
DB_PASSWORD = config.db_password # DataBase User Password
DATABASE_NAME = config.database_name # DataBase Name

# -------------------- Telegram Bot -------------------- #
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=MemoryStorage())

# -------------------- Setup DataBase -------------------- #
import pymysql.cursors

def CreateDB_Connection():
	global DB_HOST, DB_USER, DB_PASSWORD, DATABASE_NAME

	connection = pymysql.connect(
		host=DB_HOST,
		user=DB_USER,
		password=DB_PASSWORD,
		database=DATABASE_NAME
	)

	return connection

def DataBaseExecute(request, params=()):
	connection = CreateDB_Connection()

	data = None
	cursor = connection.cursor()
	sql = request.replace('?', '%s')
	cursor.execute(sql, params)
	connection.commit()
	data = cursor.fetchall()
	connection.close()

	return data

# -------------------- Crypto Wallet -------------------- #
from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from web3.gas_strategies.rpc import rpc_gas_price_strategy

from py_crypto_hd_wallet import HdWalletBip44Coins, HdWalletBipWordsNum, \
	HdWalletBipLanguages, HdWalletBipFactory, HdWalletBipDataTypes, HdWalletBipChanges

json_file = './data/networks_list.json'
with open(json_file, "r", encoding='utf-8') as file:
	networks_json = orjson.loads(file.read())

def GetListOfNetworks() -> list:
	networks = []
	for network in networks_json:
		networks.append(network)

	return networks

def CrateWalletFactory(network='ethereum'):
	hd_wallet_fact = HdWalletBipFactory(networks_imports.networks[network])

	return hd_wallet_fact

def GenerateUserMnemonic(user_id) -> str:
	wallet_fact = CrateWalletFactory()
	user_wallet = wallet_fact.CreateRandom(str(user_id), HdWalletBipWordsNum.WORDS_NUM_12)

	return user_wallet.ToDict()['mnemonic']

def ImportUserWallet(user_id):
	wallet_fact = CrateWalletFactory()
	mnemonic = GetUserMnemonic(user_id)
	wallet = wallet_fact.CreateFromMnemonic(str(user_id), mnemonic)

	return wallet

def UserTransactions(wallet_adress, network):
	pass

def GetUserAddress(user_id):
	wallet = ImportUserWallet(user_id)
	wallet.Generate(acc_idx=0, change_idx=HdWalletBipChanges.CHAIN_EXT, addr_num=1, addr_off=0)
	addresses = wallet.GetData(HdWalletBipDataTypes.ADDRESS)

	address = addresses[0].ToDict()['address']

	return address

def InitWeb3Network(network_rpc):
	web3 = Web3(HTTPProvider(network_rpc))
	web3.middleware_onion.inject(geth_poa_middleware, layer=0)

	return web3

def GetWalletMainBalance(web3, address, network_rpc):
	balance = float(web3.fromWei(web3.eth.getBalance(address), "ether"))

	return balance

def CreateERC20_Contract(web3, token_contract, network_rpc):
	ERC20_ABI = [{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]
	erc20_contract = web3.eth.contract(token_contract, abi=ERC20_ABI)

	return erc20_contract

def GetWalletTokenBalance(web3, address, token_contract, network_rpc):
	erc20_contract = CreateERC20_Contract(web3, token_contract, network_rpc)
	balance = erc20_contract.functions.balanceOf(address).call()
	balance = float(web3.fromWei(balance, "ether"))

	return balance

def GetAllBalances(user_id):
	balances = []
	address = GetUserAddress(user_id)
	networks = GetListOfNetworks()

	for network in networks:
		network_rpc = networks_json[network]['rpc_url']
		network_erc20tokens = networks_json[network]['erc20tokens']
		web3 = InitWeb3Network(network_rpc)

		tokens_balances = {}
		for erc20token in network_erc20tokens:
			token_contract = erc20token['token_contract']
			token_name = erc20token['token']
			token_balance = GetWalletTokenBalance(web3, address, token_contract, network_rpc)

			tokens_balances.update({token_name : token_balance})

		network_type = 'main'
		if networks_json[network]['testnet']:
			network_type = 'test'

		balances.append(
			{
				network : GetWalletMainBalance(web3, address, network_rpc),
				'network_type' : network_type,
				'tokens_balances' : tokens_balances
			}
		)

	return balances

# --------------------- Work With Crypto --------------------- #
json_file = './data/coins_api_name.json'
with open(json_file, "r", encoding='utf-8') as file:
	coins_api_name = orjson.loads(file.read())

def GetNetworkCoinPrice(coin_name) -> float:
	api_name = coins_api_name[coin_name]

	url = 'https://api.coincap.io/v2/assets/'+api_name
	result = requests.request('GET', url).json()

	return float(result['data']['priceUsd'])

def GetUSDPrice() -> float:
	url = 'https://www.cbr-xml-daily.ru/daily_json.js'
	result = requests.request('GET', url).json()

	return float(result['Valute']['USD']['Value'])

def CurrecnyEmoji(currency='USD'):
	currency_emojis = {
		"USD" : "$",
		"RUB" : "₽"
	}

	return currency_emojis[currency]

# -------------------- Language List -------------------- #
json_file = './data/language.json'
with open(json_file, "r", encoding='utf-8') as file:
	language_json = orjson.loads(file.read())

def GetTextByTagAndLanguage(language_json, language, tag) -> str:
	language_text = language_json[language][tag]

	return language_text

def GetLanguageList() -> list:
	languages = []
	for language in language_json:
		languages.append(language)

	return languages

# --------------------- Some Tools --------------------- #
def DateTimeNow() -> str:
	return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def WorkInProgress() -> str:
	emojis = ["😔", "😳", "😓", "😐", "😥"]
	random_index = randint(0, 4)
	return "Данная команда находится в разработке и временно недоступна "+emojis[random_index]

def DayTimeText() -> str:
	day_time = ''
	hourse = int(datetime.now().strftime("%H"))

	if 0 <= hourse < 6:
		day_time = 'night'
	elif 6 <= hourse < 12:
		day_time = 'morning'
	elif 12 <= hourse < 18:
		day_time = 'day'
	elif 18 <= hourse < 24:
		day_time = 'evening'

	return day_time

def on_startup() -> None:
	print("Bot Started!")

def SendUserProfileInfo(bot_message, loop, user_id, profile_text):
	user_info = GetUserInfo(user_id)
	user_balances = GetAllBalances(user_id)

	header = profile_text['header']
	header = header.replace('{telegram_id}', str(user_info['tg_id']))
	header = header.replace('{count_of_trnsactions}', 'error')
	header = header.replace('{registration_data}', str(user_info['reg_datetime']))
		
	answer = header

	usd_balance = 0

	answer += f"┌ {profile_text['wallet'].capitalize()}\n"
	for x, network_balances in enumerate(user_balances):
		if x+1 == len(user_balances):
			network = list(network_balances.keys())[0]
			network_type = network_balances['network_type']
			main_coin = networks_json[network]['main_coin']
			answer += f"└ {profile_text['network'].capitalize()}: {network.title()}\n"
			answer += f"ㅤ├ {profile_text['networktype'].capitalize()} : {profile_text[network_type].capitalize()}\n"
			answer += f"ㅤ├ {profile_text['cryptocurrency'].capitalize()}\n"
			answer += f"ㅤ│ └ {main_coin} - {profile_text['balance'].capitalize()}: {network_balances[network]}\n"
			answer += f"ㅤ└ {profile_text['token'].capitalize()}\n"

			usd_balance += GetNetworkCoinPrice(main_coin)*network_balances[network]
			
			if len(network_balances['tokens_balances']) == 0:
				answer += f"ㅤㅤ └ {profile_text['none'].capitalize()}\n"
			else:
				tokens_balances = network_balances['tokens_balances']
				for y, token_name in enumerate(tokens_balances):
					if y+1 == len(network_balances['tokens_balances']):
						answer += f"ㅤㅤ└ {token_name} - {profile_text['balance'].capitalize()}: {tokens_balances[token_name]}\n"
					else:
						answer += f"ㅤㅤ├ {token_name} - {profile_text['balance'].capitalize()}: {tokens_balances[token_name]}\n"

					usd_balance += GetNetworkCoinPrice(token_name)*tokens_balances[token_name]
		
		else:
			network = list(network_balances.keys())[0]
			network_type = network_balances['network_type']
			main_coin = networks_json[network]['main_coin']
			answer += f"├ {profile_text['network'].capitalize()}: {network.title()}\n"
			answer += f"│ ├ {profile_text['networktype'].capitalize()} : {profile_text[network_type].capitalize()}\n"
			answer += f"│ ├ {profile_text['cryptocurrency'].capitalize()}\n"
			answer += f"│ │ └ {main_coin} - {profile_text['balance'].capitalize()}: {network_balances[network]}\n"
			answer += f"│ └ {profile_text['token'].capitalize()}\n"

			usd_balance += GetNetworkCoinPrice(main_coin)*network_balances[network]
			
			if len(network_balances['tokens_balances']) == 0:
				answer += f"│ㅤ └ {profile_text['none'].capitalize()}\n"
			else:
				tokens_balances = network_balances['tokens_balances']
				for y, token_name in enumerate(tokens_balances):
					if y+1 == len(network_balances['tokens_balances']):
						answer += f"│ㅤ └ {token_name} - {profile_text['balance'].capitalize()}: {tokens_balances[token_name]}\n"
					else:
						answer += f"│ㅤ ├ {token_name} - {profile_text['balance'].capitalize()}: {tokens_balances[token_name]}\n"

					usd_balance += GetNetworkCoinPrice(token_name)*tokens_balances[token_name]

		if x+1<len(user_balances):
			answer += "│\n"

	chat_id = bot_message.chat.id
	message_id = bot_message.message_id

	user_currency = user_info['main_currency']

	if user_currency == 'usd':
		balance = round(usd_balance, 2)
		answer = answer.replace('{balance_in_currency}', str(balance))
		answer = answer.replace('{currency}', CurrecnyEmoji('USD'))
	elif user_currency == 'rub':
		balance = round(usd_balance*GetUSDPrice(), 2)
		answer = answer.replace('{balance_in_currency}', str(balance))
		answer = answer.replace('{currency}', CurrecnyEmoji('RUB'))

	asyncio.run_coroutine_threadsafe(bot.edit_message_text(answer, chat_id, message_id), loop)

# --------------------- Work With Databse --------------------- #
def CheckAndRegUserInDB(message, language):
	user_id = message.from_user.id
	user_name = message.from_user.username

	data = DataBaseExecute('SELECT * FROM users WHERE tg_id = ?', (user_id))
	if not(CheckDataFromDB(data)):
		user_mnemonic = GenerateUserMnemonic(user_id)
		DataBaseExecute(
			'INSERT INTO users (tg_id, tg_username, wallet_mnemonic, language, main_currency, reg_datetime, status_mes, last_use) VALUES (?, ?, ?, ?, ?, ?, ?)',  \
			params=(user_id, user_name, user_mnemonic, language, 'usd', DateTimeNow(), 'menu', DateTimeNow())
		)

def GetUserStatus(user_id):
	user_data = DataBaseExecute('SELECT status_mes FROM users WHERE tg_id = ?', (user_id))[0]

	return user_data[0]

def GetUserLanguage(user_id):
	user_data = DataBaseExecute('SELECT language FROM users WHERE tg_id = ?', (user_id))[0]
	return user_data[0]

def GetUserMnemonic(user_id):
	user_data = DataBaseExecute('SELECT wallet_mnemonic FROM users WHERE tg_id = ?', (user_id))[0]

	return user_data[0]

def GetUserInfo(user_id):
	user_data = DataBaseExecute('SELECT * FROM users WHERE tg_id = ?', (user_id))[0]

	json_user_info = {
		'id' : user_data[0],
		'tg_id' : user_data[1],
		'tg_username' : user_data[2],
		'wallet_mnemonic' : user_data[3],
		'milling' : user_data[4],
		'language' : user_data[5],
		'main_currency' : user_data[6],
		'reg_datetime' : user_data[7],
		'last_use' : user_data[8]
	}

	return json_user_info

def ChangeUserStatus(user_id, status_mes):
	DataBaseExecute(
		'UPDATE users SET status_mes = ? WHERE tg_id = ?',
		(status_mes, user_id)
	)

def ChangeUserSettings(user_id, milling, language):
	DataBaseExecute(
		'UPDATE users SET milling = ?, language = ? WHERE tg_id = ?',
		(milling, language, user_id)
	)

def CheckDataFromDB(data):
	if data:
		return True
	else:
		return False

def UpdateLastUse(user_id): # <- Rewrite Functions For DataBase
	DataBaseExecute(
		'UPDATE users SET last_use = ? WHERE tg_id = ?',
		(DateTimeNow(), user_id)
	)

# --------------------- Main --------------------- #
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
	user_id = message.from_user.id
	locale = message.from_user.locale
	user_tg_language = locale.language

	start_time_message_text = DayTimeText()
	languages = GetLanguageList()

	user_language = ""

	if user_tg_language in languages:
		CheckAndRegUserInDB(message, user_tg_language)
		user_language = user_tg_language
	else:
		CheckAndRegUserInDB(message, DEFAULT_LANGUAGE)
		user_language = DEFAULT_LANGUAGE

	time_text = GetTextByTagAndLanguage(language_json, user_language, start_time_message_text+'_text')
	time_text = time_text.capitalize()
	start_message = GetTextByTagAndLanguage(language_json, user_language, 'start_text')
	answer = start_message.replace('{start_time_message}', time_text)

	UpdateLastUse(user_id)

	await bot.send_message(message.from_user.id, answer, reply_markup=keyboards.GetMenuKeyboard(user_language))

@dp.message_handler(commands=['update'])
async def process_update_command(message: types.Message):
	user_id = message.from_user.id

	UpdateLastUse(user_id)

	user_language = GetUserLanguage(user_id)

	await bot.send_message(message.from_user.id, "Ok", reply_markup=keyboards.GetMenuKeyboard(user_language))

@dp.message_handler(commands=['test'])
async def process_help_command(message: types.Message):
	user_id = message.from_user.id

@dp.message_handler()
async def process_messages(message: types.Message):
	user_id = message.from_user.id

	UpdateLastUse(user_id)

	user_language = GetUserLanguage(user_id)
	user_status = GetUserStatus(user_id).split('_')

	if user_status[0] == 'menu':
		if message.text in ['Профиль👤', 'Profile👤']:
			profile_text = GetTextByTagAndLanguage(language_json, user_language, 'profile_text')
			
			answer = profile_text['loading']
			bot_message = await bot.send_message(message.from_user.id, answer)

			loop = asyncio.get_event_loop()
			thread = Thread(target=SendUserProfileInfo, args=(bot_message, loop, user_id, profile_text, ))
			thread.start()

		if message.text in ['Получить📥', 'Get📥']:
			await bot.send_message(message.from_user.id, WorkInProgress())

		if message.text in ['Отправить📤', 'Send📤']:
			await bot.send_message(message.from_user.id, WorkInProgress())

		if message.text in ['История транзакций🧾', 'Transactions history🧾']:
			await bot.send_message(message.from_user.id, WorkInProgress())

		if message.text in ['API🔧']:
			await bot.send_message(message.from_user.id, WorkInProgress())

		if message.text in ['Настройки⚙', 'Settings⚙']:
			await bot.send_message(message.from_user.id, WorkInProgress())

		if message.text in ['Справка📑', 'Reference📑']:
			await bot.send_message(message.from_user.id, WorkInProgress())

if __name__ == '__main__':
	executor.start_polling(dp, on_startup=on_startup())