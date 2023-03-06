from aiogram import types


buttons = [
    [
        types.InlineKeyboardButton('Да', callback_data='yes'),
        types.InlineKeyboardButton('Нет', callback_data='no')
    ],
    [types.InlineKeyboardButton('Отмена', callback_data='hide')]
    ,
]
kbrd_y_n = types.InlineKeyboardMarkup(inline_keyboard=buttons)

buttons = [
    [types.InlineKeyboardButton('Промежуточные результаты', callback_data='inter_result')],
    [types.InlineKeyboardButton('Отправить всем сообщение', callback_data='send_all')],
    [types.InlineKeyboardButton('Удалить фильм', callback_data='del_movie')],
    [types.InlineKeyboardButton('Отправить результаты', callback_data='send_result')],
]
kbrd_admin = types.InlineKeyboardMarkup(inline_keyboard=buttons)
