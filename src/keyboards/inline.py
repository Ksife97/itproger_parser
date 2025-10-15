from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_articles_grid_keyboard(articles, current_page=1, total_pages=84):
    """Создает сетку статей 2x2 как на скриншоте"""
    builder = InlineKeyboardBuilder()

    # Создаем кнопки для статей в формате 2x2
    buttons = []
    for i in range(min(len(articles), 10)):
        buttons.append(InlineKeyboardButton(
            text=f"Статья {i + 1}",
            callback_data=f"article_{i}"
        ))

    # Распределяем кнопки по 2 в ряд
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            builder.row(buttons[i], buttons[i + 1])
        else:
            builder.row(buttons[i])

    # Кнопки навигации
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data="prev_page"))

    nav_buttons.append(InlineKeyboardButton(text="Обновить", callback_data="refresh"))

    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Далее ➡️", callback_data="next_page"))

    builder.row(*nav_buttons)

    return builder.as_markup()


def get_article_detail_keyboard(article_index, total_articles, article_link):
    """Создает клавиатуру для детальной страницы статьи как на скриншоте"""
    builder = InlineKeyboardBuilder()

    # Кнопки навигации между статьями
    nav_buttons = []
    if article_index > 0:
        nav_buttons.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"article_{article_index - 1}"
        ))

    nav_buttons.append(InlineKeyboardButton(
        text="📖 Полная статья",
        callback_data="full_content"
    ))

    if article_index < total_articles - 1:
        nav_buttons.append(InlineKeyboardButton(
            text="Вперед ➡️",
            callback_data=f"article_{article_index + 1}"
        ))

    builder.row(*nav_buttons)

    # Кнопка возврата к списку
    builder.row(InlineKeyboardButton(
        text="🔄 Обновить список",
        callback_data="refresh"
    ))

    return builder.as_markup()