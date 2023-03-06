from aiogram.dispatcher.filters.state import StatesGroup, State


class CinemaState(StatesGroup):
    add_movie = State()
    select_movie = State()
    rate = State()

class AdminState(StatesGroup):
    send_all = State()
    del_movie = State()
    voting = State()
