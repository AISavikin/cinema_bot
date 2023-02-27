from aiogram import types
from aiogram.dispatcher.filters.builtin import Command
from aiogram.dispatcher.filters import Text
from utils.db_api.database import Movie
from keyboards.inline.keyboards import kbrd_admin
from loader import dp

@dp.message_handler(Command('admin'), state='*')
async def admin_main(msg: types.Message):
    if msg.from_user.id != 298325596:
        await msg.answer('У вас нет прав администратора')
    else:
        await msg.answer('Панель админа', reply_markup=kbrd_admin)

@dp.callback_query_handler(Text(equals='send_poll'))
async def send_pol(call: types.CallbackQuery):
    await call.answer()

    options = [mov.title for mov in Movie.select()]
    if len(options) < 11:
        await dp.bot.send_poll(chat_id=-1001800046871, question='Выбираем кино!', options=options)
    if 10 < len(options) < 20:
        delimetr = len(options) // 2
        options1 = options[:delimetr]
        options2 = options[delimetr:]
        await dp.bot.send_poll(chat_id=-1001800046871, question='Выбираем кино!', options=options1)
        msg = await dp.bot.send_poll(chat_id=-1001800046871, question='Выбираем кино!', options=options2)
        print(msg)

@dp.poll_handler()
async def pols_for_movie(pol: types.Poll):
    print(pol)



