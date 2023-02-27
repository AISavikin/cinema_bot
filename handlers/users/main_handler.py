from aiogram import types
from states.states import CinemaState
from utils.find_movies import find_movies
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from keyboards.inline.keyboards import kbrd_y_n, main_keyboard
import aiogram.utils.markdown as fmt
from utils.db_api.database import Movie

from loader import dp


@dp.callback_query_handler(Text(equals='show_movies'))
async def show_movie(call: types.CallbackQuery):
    await call.answer()
    kbrd = types.InlineKeyboardMarkup()
    for mov in Movie.select():
        kbrd.add(types.InlineKeyboardButton(mov.title, url=mov.url))
    await dp.bot.send_message(call.from_user.id, 'Список фильмов', reply_markup=kbrd)


@dp.callback_query_handler(Text(equals='add_movie'))
async def add_movie(call: types.CallbackQuery):
    await CinemaState.add_movie.set()
    await dp.bot.send_message(call.from_user.id, 'Предлагай, напиши название фильма')


@dp.message_handler(state=CinemaState.add_movie)
async def find_movie(msg: types.Message, state: FSMContext):
    title = msg.text
    movies = find_movies(title)
    if movies is None:
        await msg.answer('Я ничего не нашёл, попробуй ещё')
        return
    await state.update_data(data=movies)
    await msg.answer('Это он?')
    await msg.answer(f'{fmt.hide_link(movies["top_result"][1])}', reply_markup=kbrd_y_n,
                     parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(Text(equals='yes'), state=CinemaState.add_movie)
async def add_movie(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    movies = await state.get_data()
    try:
        Movie.create(title=movies['top_result'][0], url=movies['top_result'][1], user=call.from_user.id)
        await dp.bot.send_message(call.from_user.id, 'Фильм добавлен в базу', reply_markup=main_keyboard)
        await state.finish()
    except:
        await dp.bot.send_message(call.from_user.id, 'Такой фильм уже добавлен, попробуй что-нибудь ещё')


@dp.callback_query_handler(Text(equals='no'), state=CinemaState.add_movie)
async def show_more(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    movies = await state.get_data()
    buttons = []
    for mov in movies['results']:
        buttons.append([types.InlineKeyboardButton(mov, url=movies['results'][mov]),
                        types.InlineKeyboardButton('Выбрать', callback_data=movies['results'][mov])])
    kbrd = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    await dp.bot.send_message(call.from_user.id, 'Может что-то из этого?', reply_markup=kbrd)


@dp.callback_query_handler(state=CinemaState.add_movie)
async def select_movie(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    movies = await state.get_data()
    if call.data in movies['results'].values():
        title = ''
        for t, url in movies['results'].items():
            if url == call.data:
                title = t
        try:
            Movie.create(title=title, url=call.data, user=call.from_user.id)
            await dp.bot.send_message(call.from_user.id, 'Фильм добавлен в базу', reply_markup=main_keyboard)
            await state.finish()
        except:
            await dp.bot.send_message(call.from_user.id, 'Такой фильм уже добавлен')
