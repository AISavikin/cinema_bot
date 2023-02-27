from aiogram import types

main_keyboard = types.InlineKeyboardMarkup(row_width=1)
main_keyboard.add(types.InlineKeyboardButton('Предложить фильм', callback_data='add_movie'))
main_keyboard.add(types.InlineKeyboardButton('Посмотреть предложенное', callback_data='show_movies'))
btn_y = types.InlineKeyboardButton('Да', callback_data='yes')
btn_n = types.InlineKeyboardButton('Нет', callback_data='no')
buttons = [
        [
            types.InlineKeyboardButton('Да', callback_data='yes'),
            types.InlineKeyboardButton('Нет', callback_data='no')
        ],
    ]
kbrd_y_n = types.InlineKeyboardMarkup(inline_keyboard=buttons)

buttons = [
    [types.InlineKeyboardButton('Отправить викторину', callback_data='send_poll')]
]
kbrd_admin = types.InlineKeyboardMarkup(inline_keyboard=buttons)