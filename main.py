import keyboards, config

import json, requests, asyncio, threading, importlib
from random import randint
from datetime import datetime
from random import randint

# -------------------- Parametrs -------------------- #
BOT_TOKEN = config.token # Telegram Bot Token
BOT_VERSION = config.bot_version

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
import sqlite3, aiosqlite

async def AsyncDataBase(request, params=()):
	async with aiosqlite.connect('./data/database.db') as db:
		await db.execute(request, params)
		await db.commit()

def DataBaseExecute(request, params=()):
	threading.Thread(target=asyncio.run, args=(AsyncDataBase(request, params),)).start()

conn = sqlite3.connect('./data/database.db', check_same_thread=False)
cursor = conn.cursor()

# -------------------- Crypto Wallet -------------------- #
from web3 import Web3
from py_crypto_hd_wallet import HdWalletBip44Coins, HdWalletBipWordsNum, \
	HdWalletBipLanguages, HdWalletBipFactory, HdWalletBipDataTypes

"""
# Init Wallets Factory
hd_wallet_fact = HdWalletBipFactory('HdWalletBip44Coins.POLYGON')
# Load Wallet With Mnemonic
hd_wallet = hd_wallet_fact.CreateFromMnemonic('main', CRYPTO_MNEMONIC)
"""

def GetListOfNetworks():
	pass

def CrateWalletFactory():
	pass

def GenerateUserMnemonic():
	pass

# --------------------- Work With Crypto --------------------- # Rewrite All Function <- !!!
"""
def GenerateUserWallets(user_db_id):
	hd_wallet.Generate(addr_off=user_db_id, addr_num=1)
	walllet_json = hd_wallet.GetData(HdWalletBipDataTypes.ADDRESS).ToDict()
	address_name = f'address_{user_db_id}'

	return walllet_json[address_name]['address'], walllet_json[address_name]['raw_priv']
"""

def GetNetworkCoinPrice(network):
	url = 'https://api.coincap.io/v2/assets/'+network
	result = requests.request('GET', url).json()

	return float(result['data']['priceUsd'])

def GetUSDPrice():
	url = 'https://www.cbr-xml-daily.ru/daily_json.js'
	result = requests.request('GET', url).json()

	return float(result['Valute']['USD']['Value'])

# -------------------- Language List -------------------- #
json_file = './data/language.json'
with open(json_file, 'r', encoding='utf-8') as file:
	language_json = json.load(file)

def GetLanguageText(language_json, language, tag):
	language_text = language_json[language][tag]

	return language_text

# --------------------- Some Tools --------------------- #
def DateTimeNow() -> str:
	return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

def WorkInProgress():
	emojis = ["😔", "😳", "😓", "😐", "😥"]
	random_index = randint(0, 4)
	return "Данная команда находится в разработке и временно недоступна "+emojis[random_index]

def DayTimeText():
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

def on_startup():
	print("Bot Started!")

def shutdown_bot():
	print("Save DataBase...")
	conn.commit()
	print("DataBase Saved, bye!")

# --------------------- Work With Databse --------------------- #
def CheckAndRegUserInDB(message):
	user_id = message.from_user.id
	user_name = message.from_user.username

	data = cursor.execute('SELECT * FROM users WHERE tg_id = ?', (user_id, ))
	if not(CheckDataFromDB(data)):
		DataBaseExecute(
			'INSERT INTO users (tg_id, tg_username, wallet_mnemonic, language, reg_datetime, status_mes) VALUES (?, ?, ?, ?, ?, ?)',  \
			params=(user_id, user_name, '', 'russian', DateTimeNow(), 'menu', )
		)

def GetUserStatus(user_id):
	user_data = cursor.execute('SELECT status_mes FROM users WHERE tg_id = ?', (user_id, )).fetchall()[0]
	return user_data[7]

def GetUserInfo(user_id):
	user_data = cursor.execute('SELECT * FROM users WHERE tg_id = ?', (user_id, )).fetchall()[0]

	json_user_info = {
		'id' : user_data[0],
		'tg_id' : user_data[1],
		'tg_username' : user_data[2],
		'wallet_mnemonic' : user_data[3],
		'milling' : user_data[4],
		'language' : user_data[5],
		'reg_datetime' : user_data[6],
		'last_use' : user_data[7]
	}

	return json_user_info

def ChangeUserStatus(user_id, status_mes):
	DataBaseExecute(
		'UPDATE users SET status_mes = ? WHERE tg_id = ?',
		(status_mes, user_id, )
	)

def ChangeUserSettings(user_id, milling, language):
	DataBaseExecute(
		'UPDATE users SET milling = ?, language = ? WHERE tg_id = ?',
		(milling, language, user_id, )
	)

def CheckDataFromDB(data):
	data = data.fetchall()
	if data:
		return True
	else:
		return False

# --------------------- Main --------------------- #
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
	locale = message.from_user.locale
	user_language = locale.language

	CheckAndRegUserInDB(message)
	
	start_time_message_text = DayTimeText()

	answer = f"language: {}"

	await bot.send_message(message.from_user.id, answer, reply_markup=keyboards.menu)

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
	CheckAndRegUserInDB(message)

	await bot.send_message(message.from_user.id, WorkInProgress())

@dp.message_handler()
async def process_messages(message: types.Message):
	user_id = message.from_user.id
	user_status = GetUserStatus(user_id).split('_')

if __name__ == '__main__':
	executor.start_polling(dp, on_startup=on_startup())
	shutdown_bot()