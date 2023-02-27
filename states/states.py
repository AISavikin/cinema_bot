from aiogram.dispatcher.filters.state import StatesGroup, State

class CinemaState(StatesGroup):
    add_movie = State()
    select_movie = State()
    show_movies = State()

class AdminState(StatesGroup):
    main_state = State()

