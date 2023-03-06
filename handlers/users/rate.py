from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from keyboards.keyboard_generator import keyboard_show_all
from utils.db_api.database import Movie, Rating, User
from states.states import CinemaState
import logging
from loader import dp


@dp.callback_query_handler(Text(contains='grade'), state=None)
async def choose_rate(call: types.CallbackQuery):
    logging.info(f'{call.from_user.full_name} {call.data=}')
    movie_id = call.data.split('|')[1]
    await CinemaState.rate.set()
    kbrd = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton("⭐" * i, callback_data=str(i))] for i in range(1, 6)])
    await call.message.edit_text(Movie.get_by_id(movie_id), reply_markup=kbrd)


@dp.callback_query_handler(state=CinemaState.rate)
async def change_rate(call: types.CallbackQuery, state: FSMContext):
    logging.info(f'{call.from_user.full_name} {call.data=}')
    user = User.get(User.telegram_id == call.from_user.id)
    movie = Movie.get(Movie.title == call.message.text)
    Rating.update(grade=call.data).where(Rating.user == user, Rating.movie == movie).execute()
    await call.answer('Оценка изменена')
    await state.finish()
    kbrd = keyboard_show_all(user)
    await call.message.edit_text('Список фильмов', reply_markup=kbrd)