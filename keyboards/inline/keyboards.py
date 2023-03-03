from aiogram import types

main_keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
main_keyboard.add('🎞️ Посмотреть предложенное')
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
    [types.InlineKeyboardButton('Начать голосование', callback_data='start_voting'),
     types.InlineKeyboardButton('Второй тур', callback_data='second_tour')],
    [types.InlineKeyboardButton('Промежуточные результаты', callback_data='inter_result'),
     types.InlineKeyboardButton('Убрать просмотр', callback_data='del')],
    [types.InlineKeyboardButton('Отправить всем сообщение', callback_data='send_all')],
]
kbrd_admin = types.InlineKeyboardMarkup(inline_keyboard=buttons)
