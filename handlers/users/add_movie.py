import logging

from aiogram import types
from states.states import CinemaState
from utils.find_movies import find_movies
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from keyboards.inline.keyboards import kbrd_y_n, main_keyboard
import aiogram.utils.markdown as fmt
from utils.db_api.database import Movie
# from .echo import clean_callback_query

from loader import dp


async def movie_to_db(call: types.CallbackQuery, state: FSMContext, data: tuple):
    title, url = data
    user_id = call.from_user.id
    try:
        Movie.create(title=title, url=url, user=user_id)
        await call.answer('Фильм добавлен в базу.', show_alert=True)
        await call.message.edit_text(f'Вы добавили:\n"{fmt.bold(title)}"\nк списку для просмотра',
                                     parse_mode=types.ParseMode.MARKDOWN,
                                     reply_markup=types.InlineKeyboardMarkup())
        await state.finish()
    except Exception as e:
        if str(e) == 'UNIQUE constraint failed: movie.url':
            await call.answer('Такой фильм уже добавлен, попробуй что-нибудь ещё.', show_alert=True)
        else:
            await call.message.answer(f'Неожиданная ошибка! {e}')


@dp.message_handler(Text(equals='➕ Предложить фильм'), state='*')
async def add_movie(msg: types.Message):
    await CinemaState.add_movie.set()
    await msg.answer('Предлагай, напиши название фильма:')


@dp.message_handler(state=CinemaState.add_movie)
async def find_movie(msg: types.Message, state: FSMContext):
    title = msg.text
    movies = find_movies(title)
    if movies is None:
        await msg.answer('Я ничего не нашёл, попробуй ещё')
        return
    await state.update_data(data=movies)
    await msg.answer(f'Это он?\n{fmt.hide_link(movies["top_result"][1])}', reply_markup=kbrd_y_n,
                     parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(Text(equals='yes'), state=CinemaState.add_movie)
async def add_movie(call: types.CallbackQuery, state: FSMContext):
    movies = await state.get_data()
    title = movies['top_result'][0]
    url = movies['top_result'][1]
    await movie_to_db(call, state, (title, url))


@dp.callback_query_handler(Text(equals='no'), state=CinemaState.add_movie)
async def show_more(call: types.CallbackQuery, state: FSMContext):
    movies = await state.get_data()
    kbrd = types.InlineKeyboardMarkup(row_width=2)
    for mov in movies['results']:
        kbrd.insert(types.InlineKeyboardButton(mov, url=movies['results'][mov]))
        kbrd.insert(types.InlineKeyboardButton('Выбрать', callback_data=movies['results'][mov]))
    await CinemaState.select_movie.set()
    await call.message.edit_text('Может что-то из этого?', reply_markup=kbrd)


@dp.callback_query_handler(Text(contains='http'), state=CinemaState.select_movie)
async def select_movie(call: types.CallbackQuery, state: FSMContext):
    movies = await state.get_data()
    if call.data in movies['results'].values():
        title = ''
        for t, url in movies['results'].items():
            if url == call.data:
                title = t
        await movie_to_db(call, state, (title, call.data))

    else:
        print('SELECT MOVIE')
        await call.message.edit_reply_markup(reply_markup=types.InlineKeyboardMarkup())
        await call.answer('Сейчас недоступно')