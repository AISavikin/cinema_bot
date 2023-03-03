from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ('Пиши название фильма и действуй',
            "Список команд: ",
            "/start - Начать диалог",
            "/help - Получить справку")

    await message.answer("\n".join(text),
                         reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add('🎞️ Посмотреть предложенное'))
