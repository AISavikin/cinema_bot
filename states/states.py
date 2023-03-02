from aiogram.dispatcher.filters.state import StatesGroup, State


class CinemaState(StatesGroup):
    add_movie = State()
    select_movie = State()

class AdminState(StatesGroup):
    send_all = State()
