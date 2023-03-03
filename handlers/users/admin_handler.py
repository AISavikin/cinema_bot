import logging

from aiogram import types
from aiogram.dispatcher.filters.builtin import Command
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import ChatNotFound

from utils.db_api.database import Movie, User
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


@dp.callback_query_handler(Text(equals='start_voting'))
async def start_voting(call: types.CallbackQuery, results=None):
    await call.answer()
    for movie in Movie.select():
        movie.update(vote=0).execute()
    for user in User.select():
        loop = asyncio.get_event_loop()

        if results:
            loop.create_task(timer(user, results))
        else:
            loop.create_task(timer(user))


@dp.callback_query_handler(Text(equals='second_tour'))
async def second_tour(call: types.CallbackQuery):
    results = [i for i in Movie.select().where(Movie.vote > 0).order_by(-Movie.vote)]
    results = [mov for mov in results if mov.vote == results[0].vote]
    await start_voting(call, results)


@dp.callback_query_handler(Text(equals='inter_result'))
async def inter_result(call: types.CallbackQuery):
    votes = [f'{i.title} - {i.vote}' for i in Movie.select().where(Movie.vote > 0).order_by(-Movie.vote)]
    await call.message.answer('\n'.join(votes))


@dp.callback_query_handler(Text(equals='del'))
async def del_winner(call: types.CallbackQuery):
    await call.answer()
    winner = Movie.select().where(Movie.vote > 0).order_by(-Movie.vote)
    if len(winner) > 0:
        Movie.delete().where(Movie.id == winner[0].id).execute()
