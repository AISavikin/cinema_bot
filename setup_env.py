import os


def setup():
    if os.path.exists('conf.env'):
        return
    token = input('Токен для бота: ')
    admin = input('id админа: ')
    with open('conf.env', 'w', encoding='utf-8') as f:
        f.write(f'BOT_TOKEN={token}\nADMINS={admin}\nip=localhost')

setup()