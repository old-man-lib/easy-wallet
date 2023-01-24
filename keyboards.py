from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Menu Keyboard
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.row(
	KeyboardButton('Получить📥'),
	KeyboardButton('Профиль👤'),
	KeyboardButton('Отправить📤')
)
menu.row(
	KeyboardButton('История транзакций🧾')
)
menu.row(
	KeyboardButton('API🔧'),
	KeyboardButton('Настройки⚙'),
	KeyboardButton('Справка📑')
)

# Buy Keyboard
accept_or_cancel = ReplyKeyboardMarkup(resize_keyboard=True)
accept_or_cancel.row(
	KeyboardButton('Подтвердить✔️'),
	KeyboardButton('Отмена❌')
)

# Cencel Keyboard
cancel = ReplyKeyboardMarkup(resize_keyboard=True).row(
	KeyboardButton('Отмена❌')
)