import logging

from aiogram import types
from aiogram.dispatcher.filters.builtin import Command
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import ChatNotFound

from utils.db_api.database import Movie, User, Rating
from aiogram.dispatcher import FSMContext
from keyboards.inline.keyboards import *
from states.states import AdminState
from utils.timer import timer

import asyncio

from loader import dp


@dp.message_handler(Command('admin'), state='*')
async def admin_main(msg: types.Message, state: FSMContext):
    await state.finish()
    if msg.from_user.id != 298325596:
        await msg.answer('У вас нет прав администратора')
    else:
        await msg.answer('Панель админа', reply_markup=kbrd_admin)


@dp.callback_query_handler(Text(equals='send_all'))
async def send_all_create_msg(call: types.CallbackQuery, state: FSMContext):
    await AdminState.send_all.set()
    await dp.bot.send_message(call.from_user.id, 'Напиши сообщение')


@dp.message_handler(state=AdminState.send_all)
async def send_all_confirm(msg: types.Message, state: FSMContext):
    await state.set_data({'text_message': msg.text})
    await msg.answer(f'Отправить всем сообщение:\n{msg.text}', reply_markup=kbrd_y_n)


@dp.callback_query_handler(state=AdminState.send_all)
async def send_all(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    if call.data == 'yes':
        data = await state.get_data()
        for user in User.select():
            try:
                await dp.bot.send_message(user.telegram_id, data['text_message'])
                await state.finish()
            except ChatNotFound:
                logging.warning(f'{user.name} не открыл чат с ботом')

    if call.data == 'no':
        await state.finish()
        await dp.bot.send_message(call.from_user.id, 'Сообщение не отправлено')


@dp.callback_query_handler(Text(equals='yes'), state=AdminState.voting)
async def start_voting(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.answer()
    rating = get_rating()
    leaders = [i[0] for i in rating if i[1] == rating[0][1]]
    for user in User.select():
        loop = asyncio.get_event_loop()
        loop.create_task(timer(user, leaders))


@dp.callback_query_handler(Text(equals='inter_result'))
async def inter_result(call: types.CallbackQuery):
    rating = get_rating()
    leader = rating[0]
    rating = [f'{i[0]}: {i[1]}' for i in rating]
    await call.answer()
    await call.message.edit_text(f'Лидер: {leader[0]}\n' + '\n'.join(rating))



@dp.callback_query_handler(Text(equals='del_movie'))
async def del_movie(call: types.CallbackQuery, state: FSMContext):
    await AdminState.del_movie.set()
    kbrd = types.InlineKeyboardMarkup()
    for movie in Movie.select():
        kbrd.add(types.InlineKeyboardButton(movie.title, callback_data=movie.id))
    await call.message.edit_text('Фильмы', reply_markup=kbrd)


@dp.callback_query_handler(state=AdminState.del_movie)
async def del_movie(call: types.CallbackQuery, state: FSMContext):
    Rating.delete().where(Rating.movie == call.data).execute()
    Movie.delete().where(Movie.id == call.data).execute()
    await call.answer('Фильм удален')
    kbrd = types.InlineKeyboardMarkup()
    for movie in Movie.select():
        kbrd.add(types.InlineKeyboardButton(movie.title, callback_data=movie.id))
    await call.message.edit_reply_markup(kbrd)


@dp.callback_query_handler(Text(equals='send_result'))
async def send_result(call: types.CallbackQuery):
    for movie in Movie.select():
        movie.update(vote=0).execute()
    rating = get_rating()
    leaders = [i for i in rating if i[1] == rating[0][1]]
    result_kbrd = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Результаты', callback_data='result'))
    if len(leaders) == 1:
        Movie.update(vote=100).where(Movie.id == leaders[0][0]).execute()
        for user in User.select():
            await dp.bot.send_message(user.telegram_id, f'У нас есть победитель!', reply_markup=result_kbrd)
    else:
        await AdminState.voting.set()
        await call.message.edit_text('Победитель не определен, начать голование?', reply_markup=kbrd_y_n)


def get_rating():
    rating = [[movie, sum(i.grade for i in Rating.select().where(Rating.movie == movie.id))] for movie in
              Movie.select()]
    rating = sorted(rating, key=lambda x: x[1], reverse=True)
    return rating
