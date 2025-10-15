from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

def get_main_keyboard():
    """Создает основную клавиатуру как на скриншоте"""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📰 Последние новости"))
    builder.add(KeyboardButton(text="🔄 Обновить"))
    builder.add(KeyboardButton(text="ℹ️ Помощь"))
    builder.adjust(2, 1)
    return builder.as_markup(resize_keyboard=True)