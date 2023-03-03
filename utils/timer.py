import logging

from aiogram.utils.exceptions import MessageNotModified, ChatNotFound
import aiogram.utils.markdown as fmt
from loader import dp
from .db_api.database import Movie
from aiogram import types
from asyncio import sleep


async def timer(user, results=None, sec=20):
    kbrd = types.InlineKeyboardMarkup(row_width=2)
    if results is None:
        for movie in Movie.select():
            kbrd.insert(types.InlineKeyboardButton(movie.title, url=movie.url))
            kbrd.insert(types.InlineKeyboardButton('Проголосовать', callback_data=movie.id))

    else:
        for movie in results:
            kbrd.insert(types.InlineKeyboardButton(movie.title, url=movie.url))
            kbrd.insert(types.InlineKeyboardButton('Проголосовать', callback_data=movie.id))

    try:
        if results is None:
            choise_msg = await dp.bot.send_message(user.telegram_id, 'Выберите фильм', reply_markup=kbrd)
        else:
            choise_msg = await dp.bot.send_message(user.telegram_id, 'Второй тур\nВыберите фильм', reply_markup=kbrd)
    except ChatNotFound:
        logging.warning(f'{user.name} не открыл чат с ботом')
        return
    except Exception as e:
        logging.warning(f'Ошибка текст ошибки {e}')
        return


    message = await dp.bot.send_message(user.telegram_id, 'Голосование Открыто!\nДо конца голосования:')

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
        await sleep(1)
        sec -= 1
    try:
        await choise_msg.edit_reply_markup(reply_markup=types.InlineKeyboardMarkup())
    except MessageNotModified:
        pass
    results = Movie.select().where(Movie.vote > 0).order_by(-Movie.vote)
    winners = [mov.title for mov in results if mov.vote == results[0].vote]
    if len(winners) > 1:
        winners = '\n'.join(winners)
        await message.edit_text(f'Явного победителя нет.\nВо второй тур проходят:\n\n{fmt.bold(winners)}',
                                parse_mode=types.ParseMode.MARKDOWN, )
    else:
        result_kbrd = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Результаты', callback_data='result'))
        await message.edit_text(f'Голосование завершено!\n{fmt.bold("Время вышло")}',
                                parse_mode=types.ParseMode.MARKDOWN,
                                reply_markup=result_kbrd)


async def timer2(user, results=None):
    kbrd = types.InlineKeyboardMarkup(row_width=2)
    try:
        if results is None:

            for movie in Movie.select().where(Movie.user != user.telegram_id):
                kbrd.insert(types.InlineKeyboardButton(movie.title, url=movie.url))
                kbrd.insert(types.InlineKeyboardButton('Проголосовать', callback_data=movie.id))
            choise_msg = await dp.bot.send_message(user.telegram_id, 'Выберите фильм', reply_markup=kbrd)

        else:
            for movie in results:
                kbrd.insert(types.InlineKeyboardButton(movie.title, url=movie.url))
                kbrd.insert(types.InlineKeyboardButton('Проголосовать', callback_data=movie.id))

            choise_msg = await dp.bot.send_message(user.telegram_id, 'Второй тур\nВыберите фильм', reply_markup=kbrd)
        message = await dp.bot.send_message(user.telegram_id, 'Голосование Открыто!\nДо конца голосования:')
    except Exception as e:
        print(type(e))
        print(e)
        return
    sec = 30
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
        await sleep(1)
        sec -= 1
    try:
        await choise_msg.edit_reply_markup(reply_markup=types.InlineKeyboardMarkup())
    except MessageNotModified:
        pass
    results = Movie.select().where(Movie.vote > 0).order_by(-Movie.vote)
    winners = [mov.title for mov in results if mov.vote == results[0].vote]
    if len(winners) > 1:
        winners = '\n'.join(winners)
        await message.edit_text(f'Явного победителя нет.\nВо второй тур проходят:\n\n{fmt.bold(winners)}',
                                parse_mode=types.ParseMode.MARKDOWN, )
    else:
        result_kbrd = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Результаты', callback_data='result'))
        await message.edit_text(f'Голосование завершено!\n{fmt.bold("Время вышло")}',
                                parse_mode=types.ParseMode.MARKDOWN,
                                reply_markup=result_kbrd)
