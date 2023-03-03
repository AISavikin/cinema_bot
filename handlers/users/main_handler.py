from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
import aiogram.utils.markdown as fmt
from utils.db_api.database import Movie
import logging

from loader import dp


@dp.message_handler(Text(equals='🎞️ Посмотреть предложенное'), state='*', )
async def show_movie(msg: types.Message, state: FSMContext):
    await state.finish()
    kbrd = types.InlineKeyboardMarkup()
    for mov in Movie.select():
        kbrd.add(types.InlineKeyboardButton(mov.title, url=mov.url))
    kbrd.add(types.InlineKeyboardButton('Скрыть', callback_data='hide'))
    await msg.answer('Список фильмов', reply_markup=kbrd)



@dp.callback_query_handler(Text(contains='change_vote'))
async def change_vote(call: types.CallbackQuery):
    logging.info(f'{call.from_user.full_name} Передумал!')
    movie_id = call.data.split('|')[-1]
    movie = Movie.get_by_id(movie_id)
    movie.update(vote=movie.vote - 1).where(Movie.id == movie).execute()
    kbrd = types.InlineKeyboardMarkup(row_width=2)
    for movie in Movie.select().where(Movie.user != call.message.chat.id):
        kbrd.insert(types.InlineKeyboardButton(movie.title, url=movie.url))
        kbrd.insert(types.InlineKeyboardButton('Проголосовать', callback_data=movie.id))
    await call.message.edit_text('Выберите фильм', reply_markup=kbrd)


@dp.callback_query_handler(Text(equals=[str(i) for i in range(100)]))
async def voting(call: types.CallbackQuery):
    movie = Movie.get_by_id(call.data)
    movie.update(vote=movie.vote + 1).where(Movie.id == movie).execute()
    await call.answer('Ваш голос учтён!')
    logging.info(f'{call.from_user.full_name} проголосовал за {movie.title}')
    await call.message.edit_text(f'Вы проголосовали за фильм:\n\n"{fmt.bold(movie.title)}"',
                                 parse_mode=types.ParseMode.MARKDOWN,
                                 reply_markup=types.InlineKeyboardMarkup().add(
                                     types.InlineKeyboardButton('Изменить решение',
                                                                callback_data=f'change_vote|{movie.id}')))
    if 'Второй тур' in call.message.text:
        await call.message.edit_reply_markup(types.InlineKeyboardMarkup())
