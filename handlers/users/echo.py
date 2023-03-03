import logging
from aiogram import types
from aiogram.dispatcher import FSMContext
from .main_handler import voting, change_vote

from loader import dp


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    await message.answer(f"Эхо без состояния."
                         f"Сообщение:\n"
                         f"{message.text}")


# Эхо хендлер, куда летят ВСЕ сообщения с указанным состоянием
@dp.message_handler(state="*", content_types=types.ContentTypes.ANY)
async def bot_echo_all(message: types.Message, state: FSMContext):
    state = await state.get_state()
    await message.answer(f"Эхо в состоянии <code>{state}</code>.\n"
                         f"\nСодержание сообщения:\n"
                         f"<code>{message}</code>")


@dp.callback_query_handler(state="*")
async def clean_callback_query(call: types.CallbackQuery):
    logging.info('Попали в эхо-хендлер, clean_callback_query')
    if 'Выберите фильм' in call.message.text:
        await voting(call)
        return
    elif 'Вы проголосовали за фильм' in call.message.text:
        await change_vote(call)
        return
    elif call.data == 'hide':
        await call.message.delete()
    else:
        await call.answer('Сейчас недоступно')
        await call.message.delete()
