from environs import Env
from aiogram import executor, Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
from aiogram import types
from aiogram.utils.exceptions import CantParseEntities


import sqlite3

env = Env()
env.read_env()

BOT_TOKEN = env.str("TOKEN")
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
logging.basicConfig(level=logging.INFO)

async def set_default_commands(dp):
    await bot.set_my_commands(
        [
            types.BotCommand('start', 'Запустити бота'),
            types.BotCommand('add_user', 'додати користувача'),
            types.BotCommand('get_users', 'перелянути всіх користувачів')
        ]
    )

async def on_startup(dp):
    await set_default_commands(dp)
    
with sqlite3.connect('users.dp') as db:
        cr = db.cursor()
        cr.execute("""
                   CREATE TABLE IF NOT EXISTS users(
                       id INTEGER NOT NULL PRIMARY KEY,
                       username TEXT NOT NULL,
                       first_name TEXT NOT NULL,
                       last_name TEXT NOT NULL
                   )
                   """)    

@dp.message_handler(commands=['add_user'])
async def add_user(message: types.Message):
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    username = message.from_user.username
    id = message.from_user.id
    with sqlite3.connect('users.dp') as db:
        cr = db.cursor()
        try:
            cr.execute("""
                   INSERT INTO users(id, username, first_name, last_name) 
                   VALUES(?, ?, ?, ?)
                   """, (id, username, first_name, last_name))
            await message.answer("Користувача додано")
        except:
            await message.answer("Щось пішло не так")
            
        
@dp.message_handler(commands=['get_users'])
async def get_users(message: types.Message):
    with sqlite3.connect('users.dp') as db:
        cr = db.cursor()
        cr.execute("""
                   SELECT * FROM users
                   """)
        users = cr.fetchall()
        res = ""
        if users:
        
            for user_data in users:
                res += f"ID -- {user_data[0]}, Username -- @{user_data[1]}, Ім'я -- {user_data[2]}, Прізвище -- {user_data[3]}"   
        else:
            res += "уууу, а тут пусто"
        
        await message.answer(res)
        
if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)