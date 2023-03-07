from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp
from keyboards.default.keyboards import main_keyboard

from loader import dp


@dp.message_handler(CommandHelp(), state='*')
async def bot_help(message: types.Message):
    text = ('Пиши название фильма и действуй',
            "Список команд: ",
            "/start - Начать диалог",
            "/help - Получить справку")

    await message.answer("\n".join(text), reply_markup=main_keyboard)
