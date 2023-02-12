from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

import config, json

DEFAULT_LANGUAGE = config.default_language

json_file = './data/language.json'
with open(json_file, 'r', encoding='utf-8') as file:
	language_json = json.load(file)

def GetTextByTagAndLanguage(language_json, language, tag) -> list:
	if not(language in language_json):
		language = DEFAULT_LANGUAGE

	language_text = language_json[language][tag]

	return language_text

def GetLanguageList() -> list:
	languages = []
	for language in language_json:
		languages.append(language)

	return languages

def GetMenuKeyboard(language):
	menu_keyboard_text = GetTextByTagAndLanguage(language_json, language, 'menu_keyboard')

	# Menu Keyboard
	menu = ReplyKeyboardMarkup(resize_keyboard=True)
	menu.row(
		KeyboardButton(menu_keyboard_text['get']),
		KeyboardButton(menu_keyboard_text['profile']),
		KeyboardButton(menu_keyboard_text['send'])
	)
	menu.row(
		KeyboardButton(menu_keyboard_text['transaction_history'])
	)
	menu.row(
		KeyboardButton(menu_keyboard_text['api']),
		KeyboardButton(menu_keyboard_text['settings']),
		KeyboardButton(menu_keyboard_text['reference'])
	)

	return menu

def GetBuyKeyboard(language):
	buy_keyboard_text = GetTextByTagAndLanguage(language_json, language, 'buy_keyboard')
	
	# Buy Keyboard
	accept_or_cancel = ReplyKeyboardMarkup(resize_keyboard=True)
	accept_or_cancel.row(
		KeyboardButton(buy_keyboard_text['accept']),
		KeyboardButton(buy_keyboard_text['cancel'])
	)

	return accept_or_cancel

def GetCancelKeyboard(language):
	cancel_keyboard_text = GetTextByTagAndLanguage(language_json, language, 'cancel_keyboard')

	# Cencel Keyboard
	cancel = ReplyKeyboardMarkup(resize_keyboard=True).row(
		KeyboardButton(cancel_keyboard_text['cancel'])
	)

	return cancel