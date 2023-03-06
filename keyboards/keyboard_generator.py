from aiogram import types

from utils.db_api.database import Rating


def keyboard_show_all(user):
    kbrd = types.InlineKeyboardMarkup(row_width=2)
    for mov in Rating.select().where(Rating.user == user):
        kbrd.insert(types.InlineKeyboardButton(mov.movie.title, url=mov.movie.url))
        if mov.grade == 0:
            kbrd.insert(types.InlineKeyboardButton('Нет оценки', callback_data=f'grade|{mov.movie.id}'))
        else:
            kbrd.insert(types.InlineKeyboardButton(f'{"⭐" * mov.grade}', callback_data=f'grade|{mov.movie.id}'))
    kbrd.add(types.InlineKeyboardButton('Скрыть', callback_data='hide'))
    return kbrd