from aiogram import types
from states.states import CinemaState
from utils.find_movies import find_movies
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from keyboards.inline.keyboards import kbrd_y_n
import aiogram.utils.markdown as fmt
from utils.db_api.database import Movie, User, Rating

from loader import dp


async def movie_to_db(call: types.CallbackQuery, state: FSMContext, data: tuple):
    title, url = data
    user_id = call.from_user.id
    try:
        movie = Movie.create(title=title, url=url, user=user_id)
        for user in User.select():
            Rating.create(movie=movie.id, user=user.id, grade=0)
        await call.answer('Фильм добавлен в базу.', show_alert=True)
        await call.message.edit_text(f'Вы добавили:\n"{fmt.bold(title)}"',
                                     parse_mode=types.ParseMode.MARKDOWN_V2,
                                     reply_markup=types.InlineKeyboardMarkup())
        await state.finish()
    except Exception as e:
        if str(e) == 'UNIQUE constraint failed: movie.url':
            await call.answer('Такой фильм уже добавлен, попробуй что-нибудь ещё.', show_alert=True)
        else:
            await call.message.answer(f'Неожиданная ошибка! {e}')


@dp.message_handler(state='*')
async def add_movie(msg: types.Message, state: FSMContext):
    await CinemaState.add_movie.set()
    title = msg.text
    movies = find_movies(title)
    if movies is None:
        await msg.answer('Я ничего не нашёл, попробуй ещё')
        await msg.delete()
        return
    await state.update_data(data=movies)
    await msg.answer(f'Это он?\n{fmt.hide_link(movies["top_result"][1])}', reply_markup=kbrd_y_n,
                     parse_mode=types.ParseMode.HTML)
    await msg.delete()




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
        await call.answer('Сейчас недоступно')
        await call.message.delete()
