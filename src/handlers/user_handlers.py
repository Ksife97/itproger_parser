from aiogram import types, F
from aiogram.filters import Command
from loader import dp, user_sessions
from parser.itproger_parser import ITProgerParser
from keyboards.reply import get_main_keyboard
from keyboards.inline import get_articles_grid_keyboard

parser = ITProgerParser()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    user_sessions[user_id] = {'current_page': 1}

    welcome_text = (
        "🤖 Добро пожаловать в IT Proger News Bot!\n\n"
        "Я помогу вам следить за последними IT-новостями с itproger.com\n\n"
        "Используйте кнопки ниже для навигации:"
    )

    await message.answer(welcome_text, reply_markup=get_main_keyboard())

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = """
📚 **Помощь по использованию бота:**

• **📰 Последние новости** - показать свежие статьи в виде сетки
• **🔄 Обновить** - обновить список статей
• **ℹ️ Помощь** - показать эту справку

**Навигация:**
• Статьи отображаются в виде сетки 2x2
• Используйте кнопки "Далее ➡️" и "⬅️ Назад" для перехода по страницам
• Нажмите на статью для просмотра деталей
• В детальном просмотре используйте кнопки для навигации между статьями

Для начала работы нажмите "📰 Последние новости"!
    """

    await message.answer(help_text, reply_markup=get_main_keyboard())

@dp.message(Command("latest"))
async def cmd_latest(message: types.Message):
    """Обработчик команды /latest"""
    await show_articles_grid(message, page=1)

@dp.message(F.text == "📰 Последние новости")
async def handle_latest_news(message: types.Message):
    """Обработчик кнопки 'Последние новости'"""
    await show_articles_grid(message, page=1)

@dp.message(F.text == "🔄 Обновить")
async def handle_refresh(message: types.Message):
    """Обработчик кнопки 'Обновить'"""
    user_id = message.from_user.id
    current_page = user_sessions.get(user_id, {}).get('current_page', 1)
    await show_articles_grid(message, page=current_page)

@dp.message(F.text == "ℹ️ Помощь")
async def handle_help(message: types.Message):
    """Обработчик кнопки 'Помощь'"""
    await cmd_help(message)

@dp.message()
async def handle_other_messages(message: types.Message):
    """Обработчик остальных сообщений"""
    await message.answer(
        "🤖 Используйте кнопки для навигации!\n"
        "Нажмите /start чтобы начать или 'ℹ️ Помощь' для справки.",
        reply_markup=get_main_keyboard()
    )

async def show_articles_grid(message: types.Message, page=1):
    """Отображение сетки статей как в дизайне"""
    user_id = message.from_user.id

    # Инициализируем сессию пользователя если нужно
    if user_id not in user_sessions:
        user_sessions[user_id] = {}

    # Получаем общее количество страниц
    if 'total_pages' not in user_sessions[user_id]:
        total_pages = parser.get_total_pages()
        user_sessions[user_id]['total_pages'] = total_pages
        from loader import logger
        logger.info(f"Total pages for user {user_id}: {total_pages}")

    user_sessions[user_id]['current_page'] = page
    total_pages = user_sessions[user_id]['total_pages']

    # Парсим статьи
    articles = parser.parse_articles(page)

    if not articles:
        await message.answer("❌ Не удалось загрузить статьи. Попробуйте позже.")
        return

    # Создаем сообщение с заголовком страницы и списком статей
    message_text = f"📄 Страница {page} из {total_pages}\n\n"

    # Формируем список статей как в дизайне
    for i, article in enumerate(articles[:10]):  # Ограничиваем 10 статьями
        message_text += f"{i + 1}. {article['title']}\n"
        if article['description']:
            message_text += f"   {article['description']}\n"
        message_text += "\n"

    # Отправляем сообщение с сеткой кнопок
    await message.answer(
        message_text,
        reply_markup=get_articles_grid_keyboard(articles, page, total_pages)
    )