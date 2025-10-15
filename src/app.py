import asyncio
from loader import bot, dp, logger
from handlers import user_handlers, callback_handlers
from aiogram import F
from aiogram.filters import Command


async def main():
    """Основная функция запуска бота"""
    logger.info("🤖 Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())