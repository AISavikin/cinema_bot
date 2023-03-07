from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from utils.db_api.database import User, Movie, Rating
from keyboards.default.keyboards import main_keyboard
from loader import dp


@dp.message_handler(CommandStart(), state='*')
async def bot_start(message: types.Message):
    telegram_id = message.from_user.id
    try:
        name = User.get(telegram_id=telegram_id).name
        await message.answer(f'Привет, {name}!', reply_markup=main_keyboard)
    except:
        name = message.from_user.full_name
        user = User.create(telegram_id=telegram_id, name=name)
        for movie in Movie.select():
            Rating.create(movie=movie, user=user, grade=0)
        await message.answer(f'Привет, {name}!\nДобро пожаловать к нам!', reply_markup=main_keyboard)


