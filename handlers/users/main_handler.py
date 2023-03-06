from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from keyboards.keyboard_generator import keyboard_show_all
import aiogram.utils.markdown as fmt
from utils.db_api.database import Movie, User
import logging
from asyncio import sleep

from loader import dp


@dp.message_handler(Text(equals='🎞️ Посмотреть предложенное'), state='*', )
async def show_movie(msg: types.Message, state: FSMContext):
    logging.info(f'{msg.from_user.full_name} Попал в хендлер show_movie')
    await state.finish()
    user = User.get(User.telegram_id == msg.from_user.id)
    kbrd = keyboard_show_all(user)
    await msg.answer('Список фильмов', reply_markup=kbrd)
    await msg.delete()


@dp.callback_query_handler(Text(contains='vote'))
async def voting(call: types.CallbackQuery):
    movie_id = call.data.split('|')[1]
    movie = Movie.get_by_id(movie_id)
    movie.update(vote=movie.vote + 1).where(Movie.id == movie).execute()
    await call.answer('Ваш голос учтён!')
    logging.info(f'{call.from_user.full_name} проголосовал за {movie.title}')
    await call.message.edit_text(f'Вы проголосовали за фильм:\n\n"{fmt.bold(movie.title)}"',
                                 parse_mode=types.ParseMode.MARKDOWN,
                                 reply_markup=types.InlineKeyboardMarkup())


@dp.callback_query_handler(Text(equals='result'))
async def result(call: types.CallbackQuery):
    await call.message.edit_reply_markup(types.InlineKeyboardMarkup())
    results = Movie.select().where(Movie.vote > 0).order_by(-Movie.vote)
    if not results:
        await call.message.edit_text('В данный момент победитель не определён')
        return
    text = 'И победителем становится'
    message_text = text[0]
    await call.message.edit_text(message_text)
    for let in text[1:]:
        message_text += let
        await call.message.edit_text(message_text + '...')
    await sleep(2)
    await call.message.edit_text(f'🎉🎉🎉🎉🎉\n"{fmt.bold(results[0].title)}"!', parse_mode=types.ParseMode.MARKDOWN)
