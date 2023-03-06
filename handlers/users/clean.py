from aiogram import types
import logging
from loader import dp


@dp.callback_query_handler(state="*")
async def clean_callback_query(call: types.CallbackQuery):
    logging.info('Попали в хендлер-очистку, clean_callback_query')
    if call.data == 'hide':
        await call.message.delete()
    else:
        await call.answer('Сейчас недоступно')
        await call.message.delete()
