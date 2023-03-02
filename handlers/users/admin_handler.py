from aiogram import types
from aiogram.dispatcher.filters.builtin import Command
from aiogram.dispatcher.filters import Text
from utils.db_api.database import Movie, User, Voting
from aiogram.dispatcher import FSMContext
from keyboards.inline.keyboards import *
from states.states import AdminState, CinemaState
from loader import dp
import aiogram.utils.markdown as fmt
import asyncio


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
            await dp.bot.send_message(user.telegram_id, data['text_message'])
            await state.finish()
    if call.data == 'no':
        await state.finish()
        await dp.bot.send_message(call.from_user.id, 'Сообщение не отправлено')


@dp.callback_query_handler(Text(equals='start_voting'))
async def start_voting(call: types.CallbackQuery, results=None):
    for movie in Movie.select():
        movie.update(vote=0).execute()
    for user in User.select():
        message = await dp.bot.send_message(user.telegram_id, 'Голосование открыто!\nДо конца голосования:')
        loop = asyncio.get_event_loop()
        if results:
            loop.create_task(timer(message, results))
        else:
            loop.create_task(timer(message))


async def timer(message: types.Message, results=None):
    kbrd = types.InlineKeyboardMarkup(row_width=2)
    if results is None:
        for movie in Movie.select().where(Movie.user != message.chat.id):
            kbrd.insert(types.InlineKeyboardButton(movie.title, url=movie.url))
            kbrd.insert(types.InlineKeyboardButton('Проголосовать', callback_data=movie.id))
    else:
        for movie in results:
            kbrd.insert(types.InlineKeyboardButton(movie.title, url=movie.url))
            kbrd.insert(types.InlineKeyboardButton('Проголосовать', callback_data=movie.id))

    choise_msg = await message.answer('Выберите фильм', reply_markup=kbrd)
    sec = 20
    while sec != 0:
        h = sec // 3600
        sec -= h * 3600
        m, s = divmod(sec, 60)
        if h > 0:
            countdown = f'{h}:{m:02d}:{s:02d}'
        else:
            countdown = f'{m:02d}:{s:02d}'
        await message.edit_text(f'Голосование открыто!\nДо конца голосования:\n{fmt.bold(countdown)}',
                                parse_mode=types.ParseMode.MARKDOWN)
        await asyncio.sleep(1)
        sec -= 1

    await choise_msg.edit_reply_markup(reply_markup=types.InlineKeyboardMarkup())
    results = Movie.select().where(Movie.vote > 0).order_by(-Movie.vote)
    if len(results) > 1:
        winners = '\n'.join([mov.title for mov in results if mov.vote == results[0].vote])
        await message.edit_text(f'Явного победителя нет.\nВо второй тур проходят:\n\n{fmt.bold(winners)}',
                                parse_mode=types.ParseMode.MARKDOWN, )
    else:
        result_kbrd = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Результаты', callback_data='result'))
        await message.edit_text(f'Голосование завершено!\n{fmt.bold("Время вышло")}',
                                parse_mode=types.ParseMode.MARKDOWN,
                                reply_markup=result_kbrd)


@dp.callback_query_handler(Text(equals='result'))
async def result(call: types.CallbackQuery):
    results = Movie.select().where(Movie.vote > 0).order_by(-Movie.vote)
    text = 'И победителем становится'
    message_text = text[0]
    msg = await call.message.answer(message_text)
    for let in text[1:]:
        message_text += let
        await msg.edit_text(message_text + '...')
    await asyncio.sleep(2)
    await msg.edit_text(f'🎉🎉🎉🎉🎉\n"{results[0].title}"!')


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