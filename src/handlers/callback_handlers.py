from aiogram import types, F
from loader import dp, user_sessions, bot
from parser.itproger_parser import ITProgerParser
from keyboards.inline import get_articles_grid_keyboard, get_article_detail_keyboard

parser = ITProgerParser()

@dp.callback_query(F.data == "refresh")
async def handle_callback_refresh(callback: types.CallbackQuery):
    """Обработчик инлайн кнопки 'Обновить'"""
    user_id = callback.from_user.id
    current_page = user_sessions.get(user_id, {}).get('current_page', 1)
    await show_articles_grid(callback.message, page=current_page)
    await callback.answer("Обновлено!")

@dp.callback_query(F.data == "next_page")
async def handle_callback_next_page(callback: types.CallbackQuery):
    """Обработчик инлайн кнопки 'Следующая страница'"""
    user_id = callback.from_user.id
    current_page = user_sessions.get(user_id, {}).get('current_page', 1)
    total_pages = user_sessions.get(user_id, {}).get('total_pages', 84)

    if current_page < total_pages:
        await show_articles_grid(callback.message, page=current_page + 1)
    else:
        await callback.answer("Вы уже на последней странице!")
    await callback.answer()

@dp.callback_query(F.data == "prev_page")
async def handle_callback_prev_page(callback: types.CallbackQuery):
    """Обработчик инлайн кнопки 'Предыдущая страница'"""
    user_id = callback.from_user.id
    current_page = user_sessions.get(user_id, {}).get('current_page', 1)
    if current_page > 1:
        await show_articles_grid(callback.message, page=current_page - 1)
    else:
        await callback.answer("Вы уже на первой странице!")
    await callback.answer()

@dp.callback_query(F.data.startswith("article_"))
async def handle_callback_article(callback: types.CallbackQuery):
    """Обработчик инлайн кнопки статьи"""
    article_index = int(callback.data.split("_")[1])
    await show_article_detail(callback, article_index)
    await callback.answer()

@dp.callback_query(F.data == "full_content")
async def handle_full_content(callback: types.CallbackQuery):
    """Обработчик кнопки полного содержимого"""
    await callback.answer("Скоро!", show_alert=True)

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

async def show_article_detail(callback: types.CallbackQuery, article_index: int):
    """Отображение детальной информации о статье"""
    user_id = callback.from_user.id
    current_page = user_sessions.get(user_id, {}).get('current_page', 1)
    articles = parser.parse_articles(current_page)

    if not articles or article_index >= len(articles):
        await callback.message.answer("❌ Статья не найдена!")
        return

    article = articles[article_index]

    # Создаем карточку статьи
    article_text = f"<b>{article['title']}</b>\n\n"

    if article['description']:
        article_text += f"{article['description']}\n\n"

    if article.get('meta'):
        article_text += f"📊 {article['meta']}\n"

    # Отправляем изображение если есть
    if article['image']:
        try:
            await callback.message.answer_photo(
                photo=article['image'],
                caption=article_text,
                reply_markup=get_article_detail_keyboard(
                    article_index,
                    len(articles),
                    article['link']
                )
            )
            return
        except Exception as e:
            from loader import logger
            logger.error(f"Error sending photo: {e}")

    # Если изображение не отправилось, отправляем только текст
    await callback.message.answer(
        article_text,
        reply_markup=get_article_detail_keyboard(
            article_index,
            len(articles),
            article['link']
        )
    )