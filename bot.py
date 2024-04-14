# -*- coding:utf-8-*-

from ast import keyword
from email import message
from xml import dom
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import asyncio
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from config import password, token, token_api
import time

#инициализируем бота
bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())

import psycopg2
import urllib.parse as up

#подключаемся к бд
up.uses_netloc.append("postgres")
db = psycopg2.connect(f"dbname='cohgnoux' user='cohgnoux' host='ruby.db.elephantsql.com' password={password}")
cursor = db.cursor()

user_id = ''
domain_list = []
calldata_list = []
buttons = []

@dp.message_handler(regexp='Подписаться на рассылку 🚀')
@dp.message_handler(commands=['sub'])
async def reg_sub(message):

    global user_id
    user_id = str(message.from_user.id)
    global buttons
    global domain_list
    global calldata_list

    cursor.execute(f"SELECT id FROM users WHERE id = {user_id}")
    result = cursor.fetchone()

    if result is None:
        cursor.execute("INSERT INTO users DEFAULT VALUES")
        db.commit()

        cursor.execute(f"UPDATE users SET id = '{user_id}' WHERE id = '0'")
        db.commit() 

    domain_list = []
    cursor.execute(f"SELECT name FROM news ORDER BY num")
    result = cursor.fetchall()
    for row in result:
        for x in row:    
            domain_list.append(x)
    
    i=0

    buttons = []

    while i < len(domain_list): 
        calldata_list = []
        for domain in domain_list:
            letters = []
            for letter in domain:
                letters.append(letter)
            h = ''
            if letters[0] == '#':
                h = 1
            try:
                letters.remove('#')
            except:
                pass
            try:
                letters.remove('.')
            except:
                pass
            try:
                letters.remove('_')
            except:
                pass
            try:
                letters.remove('-')
            except:
                pass
            calldata =  "".join(letters)

            if h == 1:
                calldata_list.append(calldata.lower()+'_h')
            else:
                calldata_list.append(calldata.lower()+'_d')

        cursor.execute(f"SELECT {calldata_list[i]} FROM users WHERE id = {user_id}")
        user_sub_status = []
        all_sub_status = cursor.fetchone()
        for status in all_sub_status:
            user_sub_status.append(status)

        if user_sub_status[0] == '0':
            buttons.append(f'{domain_list[i]}'+" ❌")

        elif user_sub_status[0] == '1':
            buttons.append(f'{domain_list[i]}'+" ✅")

        i = i + 1
        
    keyboard = types.InlineKeyboardMarkup(row_width = 1)
    button_list = [types.InlineKeyboardButton(text=button, callback_data=data) for (button, data) in zip(buttons, calldata_list)]
    keyboard.add(*button_list)
    await bot.send_message(message.chat.id, text = "Ваши подписки:", reply_markup = keyboard)


@dp.callback_query_handler(lambda call: True)
async def callback_inline(call):

    global user_id
    global buttons
    global domain_list
    global calldata_list

    i = 0
    while i < len(domain_list):
        if call.message:
            if call.data == calldata_list[i]:

                if buttons[i] == f'{domain_list[i]}'+" ❌":
                    buttons[i] = f'{domain_list[i]}'+" ✅"

                    cursor.execute(f"UPDATE users SET {calldata_list[i]} = '1' WHERE id = {user_id}")
                    db.commit()
        
                    keyboard = types.InlineKeyboardMarkup(row_width = 1)
                    button_list = [types.InlineKeyboardButton(text=button, callback_data=data) for (button, data) in zip(buttons, calldata_list)]
                    keyboard.add(*button_list)
                    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ваши подписки:", reply_markup=keyboard)
                    await bot.send_message(user_id, text = f"Вы подписались на {domain_list[i]}")

                elif buttons[i] == f'{domain_list[i]}'+" ✅":
                    buttons[i] = f'{domain_list[i]}'+" ❌"

                    cursor.execute(f"UPDATE users SET {calldata_list[i]} = '0' WHERE id = {user_id}")
                    db.commit()
        
                    keyboard = types.InlineKeyboardMarkup(row_width = 1)
                    button_list = [types.InlineKeyboardButton(text=button, callback_data=data) for (button, data) in zip(buttons, calldata_list)]
                    keyboard.add(*button_list)
                    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ваши подписки:", reply_markup=keyboard)
                    await bot.send_message(user_id, text = f"Вы отписались от {domain_list[i]}")
        i+=1


    global user_message
    global buttons_red
    global domain_list_red
    global calldata_list_red

    i = 0
    while i < len(domain_list_red):
        if call.message:
            if call.data == calldata_list_red[i]:

                if buttons_red[i] == f'{domain_list_red[i]}'+" ❌":
                    buttons_red[i] = f'{domain_list_red[i]}'+" ✅"

                    cursor.execute(f"UPDATE users SET {calldata_list_red[i]} = '1' WHERE id = {user_message}")
                    db.commit()
        
                    keyboard = types.InlineKeyboardMarkup(row_width = 1)
                    button_list = [types.InlineKeyboardButton(text=button, callback_data=data) for (button, data) in zip(buttons_red, calldata_list_red)]
                    keyboard.add(*button_list)
                    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ваши подписки:", reply_markup=keyboard)
                    await bot.send_message(user_id, text = f"Пользователь {user_message} подписан на {domain_list_red[i]}")

                elif buttons_red[i] == f'{domain_list_red[i]}'+" ✅":
                    buttons_red[i] = f'{domain_list_red[i]}'+" ❌"

                    cursor.execute(f"UPDATE users SET {calldata_list_red[i]} = '0' WHERE id = {user_message}")
                    db.commit()
        
                    keyboard = types.InlineKeyboardMarkup(row_width = 1)
                    button_list = [types.InlineKeyboardButton(text=button, callback_data=data) for (button, data) in zip(buttons_red, calldata_list_red)]
                    keyboard.add(*button_list)
                    await bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Ваши подписки:", reply_markup=keyboard)
                    await bot.send_message(user_id, text = f"Пользователь {user_message} отписан от {domain_list_red[i]}")
        i+=1

@dp.message_handler(regexp='🔑 Команды админа')
@dp.message_handler(commands=['admin_commands'])
async def admin(message: types.Message):
    global user_id
    user_id = str(message.from_user.id)

    cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
    result = cursor.fetchone()
    for right in result:
        if right == '0':
            await bot.send_message(user_id, 'Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...')
        elif right == '1':
            button_usersettings = KeyboardButton('🔑 Настройки пользователя')
            button_add_domain = KeyboardButton('🔑 Добавить группу')
            button_del_domain = KeyboardButton('🔑 Удалить группу')
            button_add_hashtag = KeyboardButton('🔑 Добавить хэштэг')
            button_del_hashtag = KeyboardButton('🔑 Удалить хэштэг')
            button_lastnew = KeyboardButton('🔑 Изменить последнюю новость')

            greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
            greet_kb.add(button_usersettings, button_add_domain, button_del_domain, button_add_hashtag, button_del_hashtag, button_lastnew)
            await bot.send_message(user_id, 'Команды администратора:', reply_markup=greet_kb)

user_message = ''

#Админ: настройки пользователя
class user_settings_class(StatesGroup):
    otvet = State()

@dp.message_handler(regexp='🔑 Настройки пользователя')
async def user_settings_process(message: types.Message):
    global user_message
    global user_id
    user_id = str(message.from_user.id)

    cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
    result = cursor.fetchone()
    for right in result:
        if right == '0':
            await bot.send_message(user_id, 'Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...')
        elif right == '1':
            await user_settings_class.otvet.set() 

            button_stop = KeyboardButton('🔑 Стоп')
            greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
            greet_kb.add(button_stop)
            await message.reply("Введите id пользователя", reply_markup=greet_kb)

@dp.message_handler(state=user_settings_class.otvet)
async def user_settings_process2(message: types.Message, state: FSMContext):
    global user_message
    global user_id
    user_id = str(message.from_user.id)

    users_list = []
    cursor.execute(f"SELECT id FROM users")
    result = cursor.fetchall()
    for row in result:
        for x in row:    
            users_list.append(str(x))
    
    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        if user_message == '🔑 Стоп':
            await bot.send_message(user_id, 'Хорошо, команда "Стоп" понята')
            await state.finish()
        elif user_message in users_list:

            button_usersettings_id = KeyboardButton('🔑 Изменить id пользователя')
            button_usersettings_sub = KeyboardButton('🔑 Изменить подписки пользователя')
            button_usersettings_del = KeyboardButton('🔑 Удалить пользователя')

            button_usersettings_adm = ''
            cursor.execute(f"SELECT rights FROM users WHERE id = {user_message}")
            result = cursor.fetchone()
            for right in result:
                if right == '0':
                    button_usersettings_adm = KeyboardButton('🔑 Сделать админом')
                elif right == '1':
                    button_usersettings_adm = KeyboardButton('🔑 Убрать роль админа')

            greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
            greet_kb.add(button_usersettings_id, button_usersettings_sub, button_usersettings_del, button_usersettings_adm)
            await bot.send_message(user_id, 'Пользователь найден', reply_markup=greet_kb)
            await state.finish()
        else:
            await bot.send_message(user_id, 'Пользователя с таким id не существует')
            await user_settings_process(message)


#Админ: настройки пользователя (id)
class user_settings_class_id(StatesGroup):
    otvet = State()

@dp.message_handler(regexp='🔑 Изменить id пользователя')
async def user_settings_process_id(message: types.Message):
    global user_message 
    global user_id
    user_id = str(message.from_user.id)

    cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
    result = cursor.fetchone()
    for right in result:
        if right == '0':
            await bot.send_message(user_id, 'Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...')
        elif right == '1':
            await user_settings_class_id.otvet.set() 
            button_stop = KeyboardButton('🔑 Стоп')
            greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
            greet_kb.add(button_stop)
            await message.reply("Введите новое id пользователя",reply_markup=greet_kb)

@dp.message_handler(state=user_settings_class_id.otvet)
async def user_settings_process2_id(message: types.Message, state: FSMContext):
    global user_message
    global user_id
    user_id = str(message.from_user.id)
    
    async with state.proxy() as data:
        data['text'] = message.text
        user_message_id = data['text']
        if user_message_id == '🔑 Стоп':
            await bot.send_message(user_id, 'Хорошо, команда "Стоп" понята')
            await state.finish()
        else:
            cursor.execute(f"UPDATE users SET id = '{user_message_id}' WHERE id = '{user_message}'")
            db.commit()
            await bot.send_message(user_id, 'id пользователя обновлено')
            user_message = user_message_id
            await state.finish()


#Админ: настройки пользователя (delete)

@dp.message_handler(regexp='🔑 Удалить пользователя')
async def user_settings_process_del(message: types.Message):
    global user_message
    global user_id
    user_id = str(message.from_user.id)

    cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
    result = cursor.fetchone()
    for right in result:
        if right == '0':
            await bot.send_message(user_id, 'Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...')
        elif right == '1':
            cursor.execute(f"DELETE FROM users WHERE id = '{user_message}'")
            db.commit()
            await bot.send_message(user_id, f'Пользователь с id {user_message} удален')

#Админ: настройки пользователя (admin)

@dp.message_handler(regexp='🔑 Сделать админом')
@dp.message_handler(regexp='🔑 Убрать роль админа')
async def user_settings_process_adm(message: types.Message):
    global user_message
    global user_id
    user_id = str(message.from_user.id)

    cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
    result = cursor.fetchone()
    for right in result:
        if right == '0':
            await bot.send_message(user_id, 'Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...')
        elif right == '1':
            cursor.execute(f"SELECT rights FROM users WHERE id = {user_message}")
            result = cursor.fetchone()
            for right in result:
                if right == '0':
                    cursor.execute(f"UPDATE users SET rights = '1' WHERE id = '{user_message}'")
                    db.commit()
                    await bot.send_message(user_id, f"{user_message} теперь админ")
                elif right == '1':
                    cursor.execute(f"UPDATE users SET rights = '0' WHERE id = '{user_message}'")
                    db.commit()
                    await bot.send_message(user_id, f"{user_message} больше не админ")


    
#Админ: настройки пользователя (subscriptions)
domain_list_red_red = []
calldata_list_red = []
buttons_red = []
@dp.message_handler(regexp='🔑 Изменить подписки пользователя')
async def user_settings_process_sub(message: types.Message):
    global user_message
    global user_id
    user_id = str(message.from_user.id)
    global buttons_red
    global domain_list_red
    global calldata_list_red

    cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
    result = cursor.fetchone()
    for right in result:
        if right == '0':
            await bot.send_message(user_id, 'Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...')
        elif right == '1':
            domain_list_red = []
            cursor.execute(f"SELECT name FROM news ORDER BY num")
            result = cursor.fetchall()
            for row in result:
                for x in row:    
                    domain_list_red.append(x)

            i=0
            buttons_red = []
            while i < len(domain_list_red): 
                calldata_list_red = []
                for domain in domain_list_red:
                    letters = []
                    for letter in domain:
                        letters.append(letter)
                    h = ''
                    if letters[0] == '#':
                        h = 1
                    try:
                        letters.remove('#')
                    except:
                        pass
                    try:
                        letters.remove('.')
                    except:
                        pass
                    try:
                        letters.remove('_')
                    except:
                        pass
                    try:
                        letters.remove('-')
                    except:
                        pass
                    calldata =  "".join(letters)

                    if h == 1:
                        calldata_list_red.append(calldata.lower()+'_h')
                    else:
                        calldata_list_red.append(calldata.lower()+'_d')

                cursor.execute(f"SELECT {calldata_list_red[i]} FROM users WHERE id = {user_message}")
                all_sub_status = cursor.fetchone()
                user_sub_status = []
                for status in all_sub_status:
                    user_sub_status.append(status)

                if user_sub_status[0] == '0':
                    buttons_red.append(f'{domain_list_red[i]}'+" ❌")

                elif user_sub_status[0] == '1':
                    buttons_red.append(f'{domain_list_red[i]}'+" ✅")

                i = i + 1

            keyboard = types.InlineKeyboardMarkup(row_width = 1)
            button_list = [types.InlineKeyboardButton(text=button, callback_data=data) for (button, data) in zip(buttons_red, calldata_list_red)]
            keyboard.add(*button_list)
            await bot.send_message(message.chat.id, text = f"Подписки пользователя {user_message}", reply_markup = keyboard)


#Админ: добавление группы
class add_domain_class(StatesGroup):
    otvet = State()

@dp.message_handler(regexp='🔑 Добавить группу')
async def add_domain_process(message: types.Message):

    global user_id
    user_id = str(message.from_user.id)
    
    cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
    result = cursor.fetchone()
    for right in result:
        if right == '0':
            await bot.send_message(user_id, 'Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...')
        elif right == '1':
            domain_list = []
            cursor.execute(f"SELECT name FROM news ORDER BY num")
            result = cursor.fetchall()
            for row in result:
                for x in row:    
                    result = x
                    test = []
                    for letters in x:
                        test.append(letters) 
                    if test[0] != '#':
                        domain_list.append(x)
            if len(domain_list) > 20:
                await bot.send_message(user_id, 'Групп не может быть больше 20')
            else:
                await add_domain_class.otvet.set() 
                button_stop = KeyboardButton('🔑 Стоп')
                greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
                greet_kb.add(button_stop)
                await message.reply("Введите название группы", reply_markup=greet_kb)

@dp.message_handler(state=add_domain_class.otvet)
async def add_domain_process_2(message: types.Message, state: FSMContext):
    
    global user_id
    user_id = str(message.from_user.id)

    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
        result = cursor.fetchone()
        for right in result:
            if right == '0':
                await bot.send_message(user_id, 'Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...')
            elif right == '1':
                if user_message == '🔑 Стоп':
                    await bot.send_message(user_id, 'Хорошо, команда "Стоп" понята')
                    await state.finish()
                else:
                    letters = []
                    for letter in user_message:
                        letters.append(letter)
                    if letters[0] != '#':
                        domain_list = []
                        cursor.execute(f"SELECT name FROM news ORDER BY num")
                        result = cursor.fetchall()
                        for row in result:
                            for x in row:    
                                result = x
                                test = []
                                for letters in x:
                                    test.append(letters) 
                                if test[0] != '#':
                                    domain_list.append(x)
                        if len(domain_list) > 20:
                            await bot.send_message(user_id, 'Групп не может быть больше 20')
                            await state.finish()
                        else:

                            request = requests.get(f'https://vk.com/{user_message}')

                            if user_message in domain_list:
                                await bot.send_message(user_id, 'Такой домен уже существует')
                                await add_domain_process(message)
                            elif request.status_code == 200:
                                print('Web site exists')
                                res = []
                                letters = []
                                for letter in user_message:
                                    letters.append(letter)
                                try:
                                    letters.remove('#')
                                except:
                                    pass
                                try:
                                    letters.remove('.')
                                except:
                                    pass
                                try:
                                    letters.remove('_')
                                except:
                                    pass
                                try:
                                    letters.remove('-')
                                except:
                                    pass
                                calldata =  "".join(letters)
                                res.append(calldata.lower())

                                sel = res[0] + '_d'
                                cursor.execute(f"ALTER TABLE ONLY users ADD COLUMN {sel} varchar(30) DEFAULT '0'")
                                cursor.execute(f'''CREATE TABLE {sel} (id_news INT, body VARCHAR, url VARCHAR, date VARCHAR); ''')

                                spis = []
                                cursor.execute(f"SELECT num FROM news")
                                result = cursor.fetchall()
                                for row in result:
                                    for x in row:    
                                        spis.append(x)

                                num_res = max(spis) + 1

                                sql = "INSERT INTO news (id_news, body, url, name, date, num) VALUES (%s, %s, %s, %s, %s, %s)"
                                val = (0, '', '', user_message, '', num_res)
                                cursor.execute(sql, val)
                                db.commit()

                                otvet_klienty = 'Группа успешно добавлена'
                                await bot.send_message(
                                    message.from_user.id,
                                    otvet_klienty ,
                                    parse_mode='HTML',
                                )
                                await state.finish()
                            else:
                                print('Web site does not exist')
                                await bot.send_message(user_id, 'Группы с таким доменом не существует')
                                await add_domain_process(message)

                    else:
                        await bot.send_message(user_id, 'Домен не начинается с "#"')
                        await add_domain_process(message)

#Админ: удаление группы
class delete_domain_class(StatesGroup):
    otvet = State()

@dp.message_handler(regexp='🔑 Удалить группу')
async def delete_domain_process(message: types.Message):


    global user_id
    user_id = str(message.from_user.id)
    
    cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
    result = cursor.fetchone()
    for right in result:
        if right == '0':
            await bot.send_message(user_id, 'Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...')
        elif right == '1':
            domain_list = []
            cursor.execute(f"SELECT name FROM news ORDER BY num")
            result = cursor.fetchall()
            for row in result:
                for x in row:    
                    result = x
                    test = []
                    for letters in x:
                        test.append(letters) 
                    if test[0] != '#':
                        domain_list.append(x)
            if len(domain_list) > 0:

                keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
                button_list = [KeyboardButton(f'{domain}') for domain in domain_list]
                keyboard.add(KeyboardButton('🔑 Стоп'))
                keyboard.add(*button_list)
                
                await delete_domain_class.otvet.set() 
              
                await message.reply("Введите название группы", reply_markup=keyboard)
            else:
                await bot.send_message(user_id, 'В базе и так нет ни одного домена :с')
    

@dp.message_handler(state=delete_domain_class.otvet)
async def delete_domain_process_2(message: types.Message, state: FSMContext):
    
    global user_id
    user_id = str(message.from_user.id)

    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
        result = cursor.fetchone()
        for right in result:
            if right == '0':
                await bot.send_message(user_id, 'Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...')
            elif right == '1':
                if user_message == '🔑 Стоп':
                    await bot.send_message(user_id, 'Хорошо, команда "Стоп" понята')
                    await state.finish()
                else:
                    letters = []
                    for letter in user_message:
                        letters.append(letter)
                    if letters[0] != '#':
                        domain_list = []
                        cursor.execute(f"SELECT name FROM news ORDER BY num")
                        result = cursor.fetchall()
                        for row in result:
                            for x in row:    
                                result = x
                                test = []
                                for letters in x:
                                    test.append(letters) 
                                if test[0] != '#':
                                    domain_list.append(x)
                        if user_message in domain_list:
                            res = []
                            letters = []
                            for letter in user_message:
                                letters.append(letter)
                            try:
                                letters.remove('#')
                            except:
                                pass
                            try:
                                letters.remove('.')
                            except:
                                pass
                            try:
                                letters.remove('_')
                            except:
                                pass
                            try:
                                letters.remove('-')
                            except:
                                pass
                            calldata =  "".join(letters)
                            res.append(calldata.lower())

                            sel = res[0] + '_d'
                            cursor.execute(f"ALTER TABLE users DROP COLUMN {sel}")
                            cursor.execute(f''' DROP TABLE {sel}; ''')
                            cursor.execute(f"DELETE FROM news WHERE name='{user_message}'")
                            db.commit()
                            otvet_klienty = 'Группа успешно удалена'
                            await bot.send_message(
                                message.from_user.id,
                                otvet_klienty ,
                                parse_mode='HTML',
                            )
                            await state.finish()
                        else:
                            await bot.send_message(user_id, 'Такого домена итак не существует')
                            await delete_domain_process(message)

                    else:
                        await bot.send_message(user_id, 'Домен не начинается с "#"')
                        await delete_domain_process(message)

#Админ: добавление хэштэга
class add_hashtag_class(StatesGroup):
    otvet = State()

@dp.message_handler(regexp='🔑 Добавить хэштэг')
async def add_hashtag_process(message: types.Message):

    global user_id
    user_id = str(message.from_user.id)
    
    cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
    result = cursor.fetchone()
    for right in result:
        if right == '0':
            await bot.send_message(user_id, 'Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...')
        elif right == '1':
            hashtags = []
            cursor.execute(f"SELECT name FROM news ORDER BY num")
            result = cursor.fetchall()
            for row in result:
                for x in row:    
                    result = x
                    test = []
                    for letters in x:
                        test.append(letters) 
                    if test[0] == '#':
                        hashtags.append(x)
            if len(hashtags) > 20:
                await bot.send_message(user_id, 'Хэштэгов не может быть больше 20')
            else:
                await add_hashtag_class.otvet.set() 
                button_stop = KeyboardButton('🔑 Стоп')
                greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
                greet_kb.add(button_stop)
                await message.reply("Введите название хэштэга", reply_markup=greet_kb)

    
@dp.message_handler(state=add_hashtag_class.otvet)
async def add_hashtag_process_2(message: types.Message, state: FSMContext):
    
    global user_id
    user_id = str(message.from_user.id)

    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
        result = cursor.fetchone()
        for right in result:
            if right == '0':
                await bot.send_message(user_id, 'Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...')
            elif right == '1':
                if user_message == '🔑 Стоп':
                    await bot.send_message(user_id, 'Хорошо, команда "Стоп" понята')
                    await state.finish()
                else:
                    letters = []
                    for letter in user_message:
                        letters.append(letter)
                    if letters[0] == '#':
                        hashtags = []
                        cursor.execute(f"SELECT name FROM news ORDER BY num")
                        result = cursor.fetchall()
                        for row in result:
                            for x in row:    
                                result = x
                                test = []
                                for letters in x:
                                    test.append(letters) 
                                if test[0] == '#':
                                    hashtags.append(x)
                        if len(hashtags) > 20:
                            await bot.send_message(user_id, 'Хэштэгов не может быть больше 20')
                            await state.finish()
                        else:
                            if user_message in hashtags:
                                await bot.send_message(user_id, 'Такой хэштэг уже существует')
                                await add_hashtag_process(message)
                            else:
                                res = []
                                letters = []
                                for letter in user_message:
                                    letters.append(letter)
                                try:
                                    letters.remove('#')
                                except:
                                    pass
                                try:
                                    letters.remove('.')
                                except:
                                    pass
                                try:
                                    letters.remove('_')
                                except:
                                    pass
                                try:
                                    letters.remove('-')
                                except:
                                    pass
                                calldata =  "".join(letters)
                                res.append(calldata.lower())

                                sel = res[0] + '_h'
                                cursor.execute(f"ALTER TABLE ONLY users ADD COLUMN {sel} varchar(30) DEFAULT '0'")
                                cursor.execute(f'''CREATE TABLE {sel} (id_news INT, body VARCHAR, url VARCHAR, date VARCHAR); ''')

                                spis = []
                                cursor.execute(f"SELECT num FROM news")
                                result = cursor.fetchall()
                                for row in result:
                                    for x in row:    
                                        spis.append(x)
                                num_res = max(spis)+1

                                sql = "INSERT INTO news (id_news, body, url, name, date, num) VALUES (%s, %s, %s, %s, %s, %s)"
                                val = (0, '', '', user_message, '', num_res)

                                cursor.execute(sql, val)
                                db.commit()

                                otvet_klienty = 'Хэштэг успешно добавлен'
                                await bot.send_message(
                                    message.from_user.id,
                                    otvet_klienty ,
                                    parse_mode='HTML',
                                )
                                await state.finish()

                    else:
                        await bot.send_message(user_id, 'Хэштэг начинается с "#"')
                        await add_hashtag_process(message)

        
#Админ: удаление хэштэга
class delete_hashtag_class(StatesGroup):
    otvet = State()

@dp.message_handler(regexp='🔑 Удалить хэштэг')
async def delete_hashtag_process(message: types.Message):

    global user_id
    user_id = str(message.from_user.id)
    
    cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
    result = cursor.fetchone()
    for right in result:
        if right == '0':
            await bot.send_message(user_id, 'Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...')
        elif right == '1':
            hashtags = []
            cursor.execute(f"SELECT name FROM news ORDER BY num")
            result = cursor.fetchall()
            for row in result:
                for x in row:    
                    result = x
                    test = []
                    for letters in x:
                        test.append(letters) 
                    if test[0] == '#':
                        hashtags.append(x)
            if len(hashtags) > 0:

                keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
                button_list = [KeyboardButton(f'{hashtag}') for hashtag in hashtags]
                keyboard.add(KeyboardButton('🔑 Стоп'))
                keyboard.add(*button_list)

                await delete_hashtag_class.otvet.set() 
                await message.reply("Введите название хэштэга", reply_markup=keyboard)
            else:
                await bot.send_message(user_id, 'В базе и так нет ни одного хэштэга :с')

@dp.message_handler(state=delete_hashtag_class.otvet)
async def delete_hashtag_process_2(message: types.Message, state: FSMContext):
    
    global user_id
    user_id = str(message.from_user.id)

    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
        result = cursor.fetchone()
        for right in result:
            if right == '0':
                await bot.send_message(user_id, 'Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...')
            elif right == '1':
                if user_message == '🔑 Стоп':
                    await bot.send_message(user_id, 'Хорошо, команда "Стоп" понята')
                    await state.finish()
                else:
                    letters = []
                    for letter in user_message:
                        letters.append(letter)
                    if letters[0] == '#':
                        hashtags = []
                        cursor.execute(f"SELECT name FROM news ORDER BY num")
                        result = cursor.fetchall()
                        for row in result:
                            for x in row:    
                                result = x
                                test = []
                                for letters in x:
                                    test.append(letters) 
                                if test[0] == '#':
                                    hashtags.append(x)

                        if user_message in hashtags:
                            res = []
                            letters = []
                            for letter in user_message:
                                letters.append(letter)
                            try:
                                letters.remove('#')
                            except:
                                pass
                            try:
                                letters.remove('.')
                            except:
                                pass
                            try:
                                letters.remove('_')
                            except:
                                pass
                            try:
                                letters.remove('-')
                            except:
                                pass
                            calldata =  "".join(letters)
                            res.append(calldata.lower())

                            sel = res[0] + '_h'
                            cursor.execute(f"ALTER TABLE users DROP COLUMN {sel}")
                            cursor.execute(f''' DROP TABLE {sel}; ''')
                            cursor.execute(f"DELETE FROM news WHERE name='{user_message}'")
                            db.commit()
                            otvet_klienty = 'Хэштэг успешно удалён'
                            await bot.send_message(
                                message.from_user.id,
                                otvet_klienty ,
                                parse_mode='HTML',
                            )
                            await state.finish()

                        else:
                            await bot.send_message(user_id, 'Такого хэштэга итак не существует')
                            await delete_domain_process(message)

                    else:
                        await bot.send_message(user_id, 'Хэштэг начинается с "#"')
                        await delete_hashtag_process(message)

#Админ: изменить последнюю новость
class redlastnew_class(StatesGroup):
    otvet = State()

class redlastnew2_class(StatesGroup):
    otvet = State()

@dp.message_handler(regexp='🔑 Изменить последнюю новость')
async def redlastnew_process(message: types.Message):
    global domain_list
    domain_list = []
    cursor.execute(f"SELECT name FROM news ORDER BY num")
    result = cursor.fetchall()
    for row in result:
        for x in row:    
            domain_list.append(x)
    
  
    keyboard = ReplyKeyboardMarkup(row_width = 1, resize_keyboard=True, one_time_keyboard=True)
    button_list = [KeyboardButton(f'🔑 По подписке {domain}') for domain in domain_list]
    keyboard.add(*button_list)
    keyboard.add(KeyboardButton('🔑 Стоп'))
    await redlastnew_class.otvet.set() 
    await bot.send_message(message.from_user.id, "Последнюю запись по какой подписке Вы желаете изменить?", reply_markup=keyboard)


body_red = ''
lst_red = []
name_red = ''

@dp.message_handler(state=redlastnew_class.otvet)
async def redlastnew_process_2(message: types.Message, state: FSMContext):
    global body_red
    global lst_red
    global name_red

    global user_id
    user_id = str(message.from_user.id)

    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
        result = cursor.fetchone()
        for right in result:
            if right == '0':
                await bot.send_message(user_id, 'Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...')
            elif right == '1':
                if user_message == '🔑 Стоп':
                    await bot.send_message(user_id, 'Хорошо, команда "Стоп" понята')
                    await state.finish()
                else:
                    res = user_message.replace('🔑 По подписке ', '')
                    cursor.execute(f"SELECT id_news FROM news WHERE name = '{res}'")
                    result = cursor.fetchone()
                    if result is not None:
                        for id in result:
                            try:
                                print(int(id))
                                if id is not None or id != '':
                                    try:
                                        hashtags = []
                                        cursor.execute(f"SELECT name FROM news ORDER BY num")
                                        result = cursor.fetchall()
                                        for row in result:
                                            for x in row:    
                                                hashtags.append(x)

                                        i = 0
                                        while i < len(hashtags):
                                            try:
                                                if user_message == '🔑 По подписке '+hashtags[i]:
                                                    name_red = hashtags[i]
                                                    try:
                                                        cursor.execute(f"SELECT date FROM news WHERE name = '{hashtags[i]}'")
                                                        data_reg1 = cursor.fetchall()
                                                        date = []
                                                        for x in data_reg1:
                                                            listdate = list(x)
                                                            date_str = "".join(listdate)
                                                            dt = date_str
                                                            date.append(dt)
                                                        data_reg = date[0]

                                                        cursor.execute(f"SELECT url FROM news WHERE name = '{hashtags[i]}'")
                                                        url = cursor.fetchone()
                                                        cursor.execute(f"SELECT body FROM news WHERE name = '{hashtags[i]}'")
                                                        body0 = cursor.fetchone()
                                                        body_lst = []
                                                        list1 = list(body0)
                                                        body_str = "".join(list1)
                                                        pic = body_str
                                                        body_lst.append(pic)
                                                        body_red = body_lst[0]

                                                        try:
                                                            lst1 = []
                                                            err = 0
                                                            for url1 in url:
                                                                list1 = list(url1)
                                                                if len(list1) == 2 and list1[0] == '{' and list1[1] == '}':
                                                                    err = 1
                                                                else:
                                                                    if list1[1] == '"' and list1[-2] == '"':
                                                                        list1.remove('{')
                                                                        list1.remove('}')
                                                                        list1.remove('"')
                                                                        list1.remove('"')
                                                                        url_str = "".join(list1)
                                                                        pic = url_str
                                                                        lst1.append(pic)
                                                                    else:
                                                                        list1.remove('{')
                                                                        list1.remove('}')
                                                                        url_str = "".join(list1)
                                                                        pic = url_str
                                                                        lst1.append(pic)

                                                            if err == 0:
                                                                lst_red = lst1[0].split(',')
                                                                media = types.MediaGroup()
                                                                x = 0
                                                                y = 0

                                                                markup = types.InlineKeyboardMarkup()
                                                                photo = []
                                                                for type in lst_red:
                                                                    if 'vk.com/video' in type or 'youtube.com/' in type:
                                                                        def short_url():
                                                                            token = token_api
                                                                            version = 5.131
                                                                            url_vk = type
                                                                            response = requests.get('https://api.vk.com/method/utils.getShortLink?', 
                                                                                                    params = {
                                                                                                        'access_token':token,
                                                                                                        'v':version,
                                                                                                        'url':url_vk
                                                                                                    }
                                                                                                    )
                                                                            data = response.json()['response']['short_url']
                                                                            return data
                                                                        data = short_url()

                                                                        button = types.InlineKeyboardButton("Ссылка на видео", url=data)
                                                                        markup.add(button)
                                                                        x = x + 1
                                                                    else:
                                                                        if body_red == 'None' or body_red == '':
                                                                            media.attach_photo(type)
                                                                        else:
                                                                            photo.append(type)
                                                                            if photo.index(type) == 0:
                                                                                media.attach_photo(type, body_red)
                                                                            else:
                                                                                media.attach_photo(type)
                                                                        y = y + 1

                                                                try:
                                                                    try:
                                                                        button_text = KeyboardButton('🔑 Изменить текст')
                                                                        button_addmedia = KeyboardButton('🔑 Добавить медиа')
                                                                        button_delmedia = KeyboardButton('🔑 Удалить медиа')
                                                                        button_date = KeyboardButton('🔑 Изменить дату публикации')


                                                                        greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
                                                                        greet_kb.add(button_text, button_addmedia, button_delmedia, button_date)
                                                                        greet_kb.add(KeyboardButton('🔑 Стоп'))
                                                                        if x > 0 and y == 0: #значит в новости присутствует только видео
                                                                            await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                            await bot.send_message(user_id, body_red, reply_markup=markup)

                                                                            await state.finish()
                                                                            await redlastnew2_class.otvet.set() 
                                                                            await bot.send_message(user_id, "Что желаете изменить?",reply_markup=greet_kb)
                                                                        elif x == 0 and y > 0:#значит в новости присутствует только фото
                                                                            await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                            await bot.send_media_group(user_id, media=media)

                                                                            await state.finish()
                                                                            await redlastnew2_class.otvet.set() 
                                                                            await bot.send_message(user_id, "Что желаете изменить?",reply_markup=greet_kb)
                                                                        elif x > 0 and y > 0:
                                                                            await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                            await bot.send_media_group(user_id, media=media)
                                                                            await bot.send_message(user_id, "Прикрепленное(-ые) видео:", reply_markup=markup)

                                                                            await state.finish()
                                                                            await redlastnew2_class.otvet.set() 
                                                                            await bot.send_message(user_id, "Что желаете изменить?",reply_markup=greet_kb)
                                                                    except: #если текст слишком большой для caption
                                                                        button_text = KeyboardButton('🔑 Изменить текст')
                                                                        button_addmedia = KeyboardButton('🔑 Добавить медиа')
                                                                        button_delmedia = KeyboardButton('🔑 Удалить медиа')
                                                                        button_date = KeyboardButton('🔑 Изменить дату публикации')


                                                                        greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
                                                                        greet_kb.add(button_text, button_addmedia, button_delmedia, button_date)
                                                                        greet_kb.add(KeyboardButton('🔑 Стоп'))
                                                                        media = types.MediaGroup()
                                                                        for type in lst_red:
                                                                            media.attach_photo(type)
                                                                        if x > 0 and y == 0: #значит в новости присутствует только видео
                                                                            await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                            await bot.send_message(user_id, body_red)
                                                                            await bot.send_message(user_id, "Прикрепленное(-ые) видео:", reply_markup=markup)

                                                                            await state.finish()
                                                                            await redlastnew2_class.otvet.set() 
                                                                            await bot.send_message(user_id, "Что желаете изменить?",reply_markup=greet_kb)
                                                                        elif x == 0 and y > 0:#значит в новости присутствует только фото
                                                                            await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                            await bot.send_message(user_id, body_red)
                                                                            await bot.send_media_group(user_id, media=media)

                                                                            await state.finish()
                                                                            await redlastnew2_class.otvet.set() 
                                                                            await bot.send_message(user_id, "Что желаете изменить?",reply_markup=greet_kb)
                                                                        elif x > 0 and y > 0:
                                                                            await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                            await bot.send_message(user_id, body_red)
                                                                            await bot.send_media_group(user_id, media=media)
                                                                            await bot.send_message(user_id, "Прикрепленное(-ые) видео:", reply_markup=markup)

                                                                            await state.finish()
                                                                            await redlastnew2_class.otvet.set() 
                                                                            await bot.send_message(user_id, "Что желаете изменить?",reply_markup=greet_kb)

                                                                except:
                                                                    button_text = KeyboardButton('🔑 Изменить текст')
                                                                    button_addmedia = KeyboardButton('🔑 Добавить медиа')
                                                                    button_delmedia = KeyboardButton('🔑 Удалить медиа')
                                                                    button_date = KeyboardButton('🔑 Изменить дату публикации')


                                                                    greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
                                                                    greet_kb.add(button_text, button_addmedia, button_delmedia, button_date)
                                                                    greet_kb.add(KeyboardButton('🔑 Стоп'))
                                                                    print('There is no text in the news')
                                                                    if x > 0 and y == 0: #значит в новости присутствует только видео
                                                                        await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                        await bot.send_message(user_id, "Прикрепленное(-ые) видео:", reply_markup=markup)

                                                                        await state.finish()
                                                                        await redlastnew2_class.otvet.set() 
                                                                        await bot.send_message(user_id, "Что желаете изменить?",reply_markup=greet_kb)
                                                                    elif x == 0 and y > 0:#значит в новости присутствует только фото
                                                                        await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                        await bot.send_media_group(user_id, media=media)

                                                                        await state.finish()
                                                                        await redlastnew2_class.otvet.set() 
                                                                        await bot.send_message(user_id, "Что желаете изменить?",reply_markup=greet_kb)
                                                                    elif x > 0 and y > 0:
                                                                        await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                        await bot.send_media_group(user_id, media=media)
                                                                        await bot.send_message(user_id, "Прикрепленное(-ые) видео:", reply_markup=markup)

                                                                        await state.finish()
                                                                        await redlastnew2_class.otvet.set() 
                                                                        await bot.send_message(user_id, "Что желаете изменить?",reply_markup=greet_kb)
                                                            elif err == 1:
                                                                button_text = KeyboardButton('🔑 Изменить текст')
                                                                button_addmedia = KeyboardButton('🔑 Добавить медиа')
                                                                button_delmedia = KeyboardButton('🔑 Удалить медиа')
                                                                button_date = KeyboardButton('🔑 Изменить дату публикации')


                                                                greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
                                                                greet_kb.add(button_text, button_addmedia, button_delmedia, button_date)
                                                                greet_kb.add(KeyboardButton('🔑 Стоп'))
                                                                print('There is no media in the news')
                                                                await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                await bot.send_message(user_id, body_red)

                                                                await state.finish()
                                                                await redlastnew2_class.otvet.set() 
                                                                await bot.send_message(user_id, "Что желаете изменить?",reply_markup=greet_kb)
                                                        except ValueError:
                                                            button_text = KeyboardButton('🔑 Изменить текст')
                                                            button_addmedia = KeyboardButton('🔑 Добавить медиа')
                                                            button_delmedia = KeyboardButton('🔑 Удалить медиа')
                                                            button_date = KeyboardButton('🔑 Изменить дату публикации')


                                                            greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
                                                            greet_kb.add(button_text, button_addmedia, button_delmedia, button_date)
                                                            greet_kb.add(KeyboardButton('🔑 Стоп'))
                                                            print('There is no media in the news')
                                                            await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                            await bot.send_message(user_id, body_red)

                                                            await state.finish()
                                                            await redlastnew2_class.otvet.set() 
                                                            await bot.send_message(user_id, "Что желаете изменить?",reply_markup=greet_kb)

                                                    except:
                                                        print('There are no users in the list, or the user has blocked the chatbot')
                                            except:
                                                pass
                                            db.commit()
                                            i = i + 1
                                    except:
                                        db.rollback()
                                else:
                                    await bot.send_message(user_id, f"По данной подписке не найдено новости")
                                    await redlastnew_process(message)
                            except:
                                await bot.send_message(user_id, f"По данной подписке не найдено новости")
                                await redlastnew_process(message)
                    else:
                        await bot.send_message(user_id, f"По данной подписке не найдено новости")
                        await redlastnew_process(message)

class redtext_class(StatesGroup):
    otvet = State()
class addmedia_class(StatesGroup):
    otvet = State()
class delmedia_class(StatesGroup):
    otvet = State()
class reddate_class(StatesGroup):
    otvet = State()

@dp.message_handler(state=redlastnew2_class.otvet)
async def redlastnew_process_3(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        if user_message == '🔑 Стоп':
            await bot.send_message(user_id, 'Хорошо, команда "Стоп" понята')
            await state.finish()
        elif user_message == '🔑 Изменить текст':
            await state.finish()
            await redtext_class.otvet.set() 
            await bot.send_message(user_id, "Введите новый текст")

        elif user_message == '🔑 Добавить медиа':
            await state.finish()
            await addmedia_class.otvet.set() 
            await bot.send_message(user_id, "Введите новую ссылку")  

        elif user_message == '🔑 Удалить медиа':
            await state.finish()
            await delmedia_class.otvet.set() 

            if len(lst_red) == 0:
                await bot.send_message(user_id, 'В новости итак нет медиа')
                await state.finish()
            else:
                keyboard = ReplyKeyboardMarkup(row_width = 1, resize_keyboard=True, one_time_keyboard=True)
                button_list = [KeyboardButton(f'{url}') for url in lst_red]
                keyboard.add(*button_list)
                await bot.send_message(user_id, "Выберете ссылку, которую нужно удалить, возможно, ссылку придется напечатать вручную, без использования кнопки 👇", reply_markup=keyboard)

        elif user_message == '🔑 Изменить дату публикации':
            await state.finish()
            await reddate_class.otvet.set() 
            await bot.send_message(user_id, "Введите новую дату публикации поста (дд.мм.гггг)")

#редактировать body     
@dp.message_handler(state=redtext_class.otvet)
async def redtext_process(message: types.Message, state: FSMContext):
    global body_red
    global name_red
    global user_id
    user_id = str(message.from_user.id)

    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        cursor.execute(f"UPDATE news SET body = '{user_message}' WHERE name = '{name_red}'")
        db.commit() 

        cursor.execute(f"SELECT id_news FROM news WHERE name = '{name_red}'")
        id_prev = cursor.fetchone()
        id_list = []
        for id in id_prev:
            id_list.append(id)

        res = []
        letters = []
        for letter in name_red:
            letters.append(letter)
        try:
            letters.remove('#')
        except:
            pass
        try:
            letters.remove('.')
        except:
            pass
        try:
            letters.remove('_')
        except:
            pass
        try:
            letters.remove('-')
        except:
            pass
        calldata =  "".join(letters)
        res.append(calldata.lower())

        letters = []
        for letter in name_red:
            letters.append(letter)
        if letters[0] == '#':
            sel = res[0] + '_h'
        else:
            sel = res[0] + '_d'
        
        cursor.execute(f"UPDATE {sel} SET body = '{user_message}' WHERE id_news = '{id_list[0]}'")
        db.commit() 

        await bot.send_message(user_id, f"Текст последней нововсти подписки {name_red} успешно изменён!")  
        await state.finish()
        await redinformation(message)


#добавить url
@dp.message_handler(state=addmedia_class.otvet)
async def addmedia_process(message: types.Message, state: FSMContext):
    global lst_red
    global name_red
    global user_id
    user_id = str(message.from_user.id)

    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        try:
            request = requests.get(f'{user_message}')

            if user_message in lst_red:
                await bot.send_message(user_id, 'Такая ссылка уже существует, попробуйте еще раз')
                await redlastnew_process_3(message, state)
            elif request.status_code == 200:
                lst_red.append(user_message)
                new_url1 = ','.join(lst_red)
                new_url = '{' + new_url1 + '}'
                cursor.execute(f"UPDATE news SET url = '{new_url}' WHERE name = '{name_red}'")
                db.commit() 

                cursor.execute(f"SELECT id_news FROM news WHERE name = '{name_red}'")
                id_prev = cursor.fetchone()
                id_list = []
                for id in id_prev:
                    id_list.append(id)

                res = []
                letters = []
                for letter in name_red:
                    letters.append(letter)
                try:
                    letters.remove('#')
                except:
                    pass
                try:
                    letters.remove('.')
                except:
                    pass
                try:
                    letters.remove('_')
                except:
                    pass
                try:
                    letters.remove('-')
                except:
                    pass
                calldata =  "".join(letters)
                res.append(calldata.lower())

                letters = []
                for letter in name_red:
                    letters.append(letter)
                if letters[0] == '#':
                    sel = res[0] + '_h'
                else:
                    sel = res[0] + '_d'

                cursor.execute(f"UPDATE {sel} SET url = '{new_url}' WHERE id_news = '{id_list[0]}'")
                db.commit() 

                await bot.send_message(user_id, f"Медиа последней нововсти подписки {name_red} успешно обновлена!")  
                await state.finish()
                await redinformation(message)
            else:
                await bot.send_message(user_id, 'Такой ссылки не существует, попробуйте еще раз')
                await redlastnew_process_3(message, state)
        except:
            await bot.send_message(user_id, 'Такой ссылки не существует, попробуйте еще раз')
            await redlastnew_process_3(message, state)


#удалить url  
@dp.message_handler(state=delmedia_class.otvet)
async def delmedia_process(message: types.Message, state: FSMContext):
    global lst_red
    global name_red
    global user_id
    user_id = str(message.from_user.id)

    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        if user_message in lst_red:
            lst_red.remove(user_message)
            new_url1 = ','.join(lst_red)
            new_url = '{' + new_url1 + '}'
            cursor.execute(f"UPDATE news SET url = '{new_url}' WHERE name = '{name_red}'")
            db.commit() 

            cursor.execute(f"SELECT id_news FROM news WHERE name = '{name_red}'")
            id_prev = cursor.fetchone()
            id_list = []
            for id in id_prev:
                id_list.append(id)

            res = []
            letters = []
            for letter in name_red:
                letters.append(letter)
            try:
                letters.remove('#')
            except:
                pass
            try:
                letters.remove('.')
            except:
                pass
            try:
                letters.remove('_')
            except:
                pass
            try:
                letters.remove('-')
            except:
                pass
            calldata =  "".join(letters)
            res.append(calldata.lower())

            letters = []
            for letter in name_red:
                letters.append(letter)
            if letters[0] == '#':
                sel = res[0] + '_h'
            else:
                sel = res[0] + '_d'

            cursor.execute(f"UPDATE {sel} SET url = '{new_url}' WHERE id_news = '{id_list[0]}'")
            db.commit() 

            await bot.send_message(user_id, f"Медиа последней нововсти подписки {name_red} успешно обновлена!")  
            await state.finish()
            await redinformation(message)
        else:
            await bot.send_message(user_id, 'Такой ссылки итак не существует, попробуйте еще раз')
            await redlastnew_process_3(message, state)


#редактировать date
@dp.message_handler(state=reddate_class.otvet)
async def reddate_process(message: types.Message, state: FSMContext):
    global lst_red
    global name_red
    global user_id
    user_id = str(message.from_user.id)

    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']

        try:
            valid_date = time.strptime(user_message, '%d.%m.%Y')

            cursor.execute(f"UPDATE news SET date = '{user_message}' WHERE name = '{name_red}'")
            db.commit() 

            cursor.execute(f"SELECT id_news FROM news WHERE name = '{name_red}'")
            id_prev = cursor.fetchone()
            id_list = []
            for id in id_prev:
                id_list.append(id)

            res = []
            letters = []
            for letter in name_red:
                letters.append(letter)
            try:
                letters.remove('#')
            except:
                pass
            try:
                letters.remove('.')
            except:
                pass
            try:
                letters.remove('_')
            except:
                pass
            try:
                letters.remove('-')
            except:
                pass
            calldata =  "".join(letters)
            res.append(calldata.lower())

            letters = []
            for letter in name_red:
                letters.append(letter)
            if letters[0] == '#':
                sel = res[0] + '_h'
            else:
                sel = res[0] + '_d'

            cursor.execute(f"UPDATE {sel} SET date = '{user_message}' WHERE id_news = '{id_list[0]}'")
            db.commit() 

            await bot.send_message(user_id, f"Дата последней нововсти подписки {name_red} успешно обновлена!")  
            await state.finish()
            await redinformation(message)

        except ValueError:
            await bot.send_message(user_id, f"Неверный формат даты, попробуйте снова (дд.мм.гггг)")  
            await redlastnew_process_3(message, state)




async def redinformation(message):
    global name_red

    id = []
    letters = []
    predres = []
    for letter in name_red:
        letters.append(letter)
    h = ''
    if letters[0] == '#':
        h = 1
    try:
        letters.remove('#')
    except:
        pass
    try:
        letters.remove('.')
    except:
        pass
    try:
        letters.remove('_')
    except:
        pass
    try:
        letters.remove('-')
    except:
        pass

    calldata = "".join(letters)
    if h == 1:
        predres.append(calldata.lower() + '_h')
    else:
        predres.append(calldata.lower() + '_d')

    hashtags_search = predres[0]
    cursor.execute(f"SELECT id FROM users WHERE {hashtags_search} = '1'")
    result = cursor.fetchall()
    for row in result:
        for x in row:
            id.append(x)
    print(id)

    for user in id:
        try:
            cursor.execute(f"SELECT url FROM news WHERE name = '{name_red}'")
            url = cursor.fetchone()
            cursor.execute(f"SELECT body FROM news WHERE name = '{name_red}'")
            body0 = cursor.fetchone()
            body_lst = []
            list1 = list(body0)
            body_str = "".join(list1)
            pic = body_str
            body_lst.append(pic)
            body = body_lst[0]

            try:
                lst1 = []
                err = 0
                for url1 in url:
                    list1 = list(url1)
                    if len(list1) == 2 and list1[0] == '{' and list1[1] == '}':
                        err = 1
                    else:
                        if list1[1] == '"' and list1[-2] == '"':
                            list1.remove('{')
                            list1.remove('}')
                            list1.remove('"')
                            list1.remove('"')
                            url_str = "".join(list1)
                            pic = url_str
                            lst1.append(pic)
                        else:
                            list1.remove('{')
                            list1.remove('}')
                            url_str = "".join(list1)
                            pic = url_str
                            lst1.append(pic)

                if err == 0:
                    lst = lst1[0].split(',')
                    media = types.MediaGroup()
                    x = 0
                    y = 0

                    markup = types.InlineKeyboardMarkup()
                    photo = []
                    for type in lst:
                        if 'vk.com/video' in type or 'youtube.com/' in type:
                            def short_url():
                                token = token_api
                                version = 5.131
                                url_vk = type
                                response = requests.get('https://api.vk.com/method/utils.getShortLink?', 
                                                        params = {
                                                            'access_token':token,
                                                            'v':version,
                                                            'url':url_vk
                                                        }
                                                        )
                                data = response.json()['response']['short_url']
                                return data
                            data = short_url()

                            button = types.InlineKeyboardButton("Ссылка на видео", url=data)
                            markup.add(button)
                            x = x + 1
                        else:
                            if body == 'None' or body == '':
                                media.attach_photo(type)
                            else:
                                photo.append(type)
                                if photo.index(type) == 0:
                                    media.attach_photo(type, body)
                                else:
                                    media.attach_photo(type)
                            y = y + 1

                    try:
                        try:
                            if x > 0 and y == 0: #значит в новости присутствует только видео
                                await bot.send_message(user, f"Новость по подписке {name_red} изменена!")
                                await bot.send_message(user, body, reply_markup=markup)
                            elif x == 0 and y > 0:#значит в новости присутствует только фото
                                await bot.send_message(user, f"Новость по подписке {name_red} изменена!")
                                await bot.send_media_group(user, media=media)
                            elif x > 0 and y > 0:
                                await bot.send_message(user, f"Новость по подписке {name_red} изменена!")
                                await bot.send_media_group(user, media=media)
                                await bot.send_message(user, "Прикрепленное(-ые) видео:", reply_markup=markup)
                        except: #если текст слишком большой для caption
                            media = types.MediaGroup()
                            for type in lst:
                                media.attach_photo(type)
                            if x > 0 and y == 0: #значит в новости присутствует только видео
                                await bot.send_message(user, f"Новость по подписке {name_red} изменена!")
                                await bot.send_message(user, body)
                                await bot.send_message(user, "Прикрепленное(-ые) видео:", reply_markup=markup)
                            elif x == 0 and y > 0:#значит в новости присутствует только фото
                                await bot.send_message(user, f"Новость по подписке {name_red} изменена!")
                                await bot.send_message(user, body)
                                await bot.send_media_group(user, media=media)
                            elif x > 0 and y > 0:
                                await bot.send_message(user, f"Новость по подписке {name_red} изменена!")
                                await bot.send_message(user, body)
                                await bot.send_media_group(user, media=media)
                                await bot.send_message(user, "Прикрепленное(-ые) видео:", reply_markup=markup)

                    except:
                        print('There is no text in the news')
                        if x > 0 and y == 0: #значит в новости присутствует только видео
                            await bot.send_message(user, f"Новость по подписке {name_red} изменена!")
                            await bot.send_message(user, "Прикрепленное(-ые) видео:", reply_markup=markup)
                        elif x == 0 and y > 0:#значит в новости присутствует только фото
                            await bot.send_message(user, f"Новость по подписке {name_red} изменена!")
                            await bot.send_media_group(user, media=media)
                        elif x > 0 and y > 0:
                            await bot.send_message(user, f"Новость по подписке {name_red} изменена!")
                            await bot.send_media_group(user, media=media)
                            await bot.send_message(user, "Прикрепленное(-ые) видео:", reply_markup=markup)
                elif err == 1:
                    print('There is no media in the news')
                    await bot.send_message(user, f"Новость по подписке {name_red} изменена!")
                    await bot.send_message(user, body)
            except ValueError:
                print('There is no media in the news')
                await bot.send_message(user, f"Новость по подписке {name_red} изменена!")
                await bot.send_message(user, body)

        except:
            print('There are no users in the list, or the user has blocked the chatbot')





#lastnew
class lastnew_class(StatesGroup):
    otvet = State()

@dp.message_handler(regexp='Последняя новость по подписке 🔎✨')
@dp.message_handler(commands=['lastnew'])
async def lastnew_process(message: types.Message):
    global domain_list
    domain_list = []
    cursor.execute(f"SELECT name FROM news ORDER BY num")
    result = cursor.fetchall()
    for row in result:
        for x in row:    
            domain_list.append(x)
    
    keyboard = ReplyKeyboardMarkup(row_width = 1, resize_keyboard=True, one_time_keyboard=True)
    button_list = [KeyboardButton(f'По подписке {domain}') for domain in domain_list]
    keyboard.add(*button_list)
    await lastnew_class.otvet.set() 
    await bot.send_message(message.from_user.id, "Последнюю запись по какой подписке Вы желаете посмотреть?", reply_markup=keyboard)

@dp.message_handler(state=lastnew_class.otvet)
async def lastnew_process_2(message: types.Message, state: FSMContext):
    global user_id
    user_id = str(message.from_user.id)

    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']
        
        res = user_message.replace('По подписке ', '')
        cursor.execute(f"SELECT id_news FROM news WHERE name = '{res}'")
        result = cursor.fetchone()
        print(res)
        if result is not None:
            for id in result:
                try:
                    print(int(id))
                    if id is not None or id != '':
                        try:
                            hashtags = []
                            cursor.execute(f"SELECT name FROM news ORDER BY num")
                            result = cursor.fetchall()
                            for row in result:
                                for x in row:    
                                    hashtags.append(x)

                            i = 0
                            while i < len(hashtags):
                                
                                try:
                                    if user_message == 'По подписке '+hashtags[i]:
                                        try:
                                            cursor.execute(f"SELECT date FROM news WHERE name = '{hashtags[i]}'")
                                            data_reg1 = cursor.fetchall()
                                            date = []
                                            for x in data_reg1:
                                                listdate = list(x)
                                                date_str = "".join(listdate)
                                                dt = date_str
                                                date.append(dt)
                                            data_reg = date[0]

                                            cursor.execute(f"SELECT url FROM news WHERE name = '{hashtags[i]}'")
                                            url = cursor.fetchone()
                                            cursor.execute(f"SELECT body FROM news WHERE name = '{hashtags[i]}'")
                                            body0 = cursor.fetchone()
                                            body_lst = []
                                            list1 = list(body0)
                                            body_str = "".join(list1)
                                            pic = body_str
                                            body_lst.append(pic)
                                            body = body_lst[0]

                                            try:
                                                lst1 = []
                                                err = 0
                                                for url1 in url:
                                                    list1 = list(url1)
                                                    if len(list1) == 2 and list1[0] == '{' and list1[1] == '}':
                                                        err = 1
                                                    else:
                                                        if list1[1] == '"' and list1[-2] == '"':
                                                            list1.remove('{')
                                                            list1.remove('}')
                                                            list1.remove('"')
                                                            list1.remove('"')
                                                            url_str = "".join(list1)
                                                            pic = url_str
                                                            lst1.append(pic)
                                                        else:
                                                            list1.remove('{')
                                                            list1.remove('}')
                                                            url_str = "".join(list1)
                                                            pic = url_str
                                                            lst1.append(pic)

                                                if err == 0:
                                                    lst = lst1[0].split(',')
                                                    media = types.MediaGroup()
                                                    x = 0
                                                    y = 0

                                                    markup = types.InlineKeyboardMarkup()
                                                    photo = []
                                                    for type in lst:
                                                        if 'vk.com/video' in type or 'youtube.com/' in type:
                                                            def short_url():
                                                                token = token_api
                                                                version = 5.131
                                                                url_vk = type
                                                                response = requests.get('https://api.vk.com/method/utils.getShortLink?', 
                                                                                        params = {
                                                                                            'access_token':token,
                                                                                            'v':version,
                                                                                            'url':url_vk
                                                                                        }
                                                                                        )
                                                                data = response.json()['response']['short_url']
                                                                return data
                                                            data = short_url()

                                                            button = types.InlineKeyboardButton("Ссылка на видео", url=data)
                                                            markup.add(button)
                                                            x = x + 1
                                                        else:
                                                            if body == 'None' or body == '':
                                                                media.attach_photo(type)
                                                            else:
                                                                photo.append(type)
                                                                if photo.index(type) == 0:
                                                                    media.attach_photo(type, body)
                                                                else:
                                                                    media.attach_photo(type)
                                                            y = y + 1

                                                    try:
                                                        try:
                                                            if x > 0 and y == 0: #значит в новости присутствует только видео
                                                                await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                await bot.send_message(user_id, body, reply_markup=markup)
                                                                await state.finish()
                                                            elif x == 0 and y > 0:#значит в новости присутствует только фото
                                                                await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                await bot.send_media_group(user_id, media=media)
                                                                await state.finish()
                                                            elif x > 0 and y > 0:
                                                                await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                await bot.send_media_group(user_id, media=media)
                                                                await bot.send_message(user_id, "Прикрепленное(-ые) видео:", reply_markup=markup)
                                                                await state.finish()
                                                        except: #если текст слишком большой для caption
                                                            media = types.MediaGroup()
                                                            for type in lst:
                                                                media.attach_photo(type)
                                                            if x > 0 and y == 0: #значит в новости присутствует только видео
                                                                await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                await bot.send_message(user_id, body)
                                                                await bot.send_message(user_id, "Прикрепленное(-ые) видео:", reply_markup=markup)
                                                                await state.finish()
                                                            elif x == 0 and y > 0:#значит в новости присутствует только фото
                                                                await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                await bot.send_message(user_id, body)
                                                                await bot.send_media_group(user_id, media=media)
                                                                await state.finish()
                                                            elif x > 0 and y > 0:
                                                                await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                                await bot.send_message(user_id, body)
                                                                await bot.send_media_group(user_id, media=media)
                                                                await bot.send_message(user_id, "Прикрепленное(-ые) видео:", reply_markup=markup)
                                                                await state.finish()

                                                    except:
                                                        print('There is no text in the news')
                                                        if x > 0 and y == 0: #значит в новости присутствует только видео
                                                            await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                            await bot.send_message(user_id, "Прикрепленное(-ые) видео:", reply_markup=markup)
                                                            await state.finish()
                                                        elif x == 0 and y > 0:#значит в новости присутствует только фото
                                                            await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                            await bot.send_media_group(user_id, media=media)
                                                            await state.finish()
                                                        elif x > 0 and y > 0:
                                                            await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                            await bot.send_media_group(user_id, media=media)
                                                            await bot.send_message(user_id, "Прикрепленное(-ые) видео:", reply_markup=markup)
                                                            await state.finish()
                                                elif err == 1:
                                                    print('There is no media in the news')
                                                    await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                    await bot.send_message(user_id, body)
                                                    await state.finish()
                                            except ValueError:
                                                print('There is no media in the news')
                                                await bot.send_message(user_id, f"Последняя новость новость по подписке {hashtags[i]}!\nДата публикации: {data_reg}")
                                                await bot.send_message(user_id, body)
                                                await state.finish()

                                        except:
                                            print('There are no users in the list, or the user has blocked the chatbot')
                                except:
                                    pass
                                db.commit()
                                i = i + 1
                                await state.finish()
                        except:
                            db.rollback()
                    else:
                        await bot.send_message(user_id, f"По данной подписке не найдено новости")
                        await lastnew_process(message)
                except:
                    await bot.send_message(user_id, f"По данной подписке не найдено новости")
                    await lastnew_process(message)
        else:
            await bot.send_message(user_id, f"По данной подписке не найдено новости")
            await lastnew_process(message)



#start
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):

    global user_id
    user_id = str(message.from_user.id)

    cursor.execute(f"SELECT id FROM users WHERE id = {user_id}")
    result = cursor.fetchone()
    if result is None:
        sql = f"INSERT INTO users (id, nauchimonline_d) VALUES (%s, %s)"
        val = (user_id, '1')
        cursor.execute(sql, val)
        db.commit()
    
    cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
    result = cursor.fetchone()
    for right in result:
        if right == '0':
            button_info = KeyboardButton('О нас 🪐')
            button_subscription = KeyboardButton('Подписаться на рассылку 🚀')
            button_lastfive = KeyboardButton('Последние пять новостей по подписке 🔎✨')
            button_lastnew = KeyboardButton('Последняя новость по подписке 🔎✨')
            button_website = KeyboardButton('Посетить сайт 🌐')
            button_survey = KeyboardButton('Отзыв ⭐')
            greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
            greet_kb.add(button_info, button_subscription, button_lastfive, button_lastnew, button_survey, button_website)
        elif right == '1':
            button_admin = KeyboardButton('🔑 Команды админа')
            button_info = KeyboardButton('О нас 🪐')
            button_subscription = KeyboardButton('Подписаться на рассылку 🚀')
            button_lastfive = KeyboardButton('Последние пять новостей по подписке 🔎✨')
            button_lastnew = KeyboardButton('Последняя новость по подписке 🔎✨')
            button_website = KeyboardButton('Посетить сайт 🌐')
            button_survey = KeyboardButton('Отзыв ⭐')
            greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
            greet_kb.add(button_admin, button_info, button_subscription, button_lastfive, button_lastnew, button_survey, button_website)

    await bot.send_message(message.from_user.id, "Здравствуйте " + message.from_user.first_name + ", что бы вы хотели узнать?")
    await bot.send_sticker(message.from_user.id, r'CAACAgIAAxkBAAED3IRiApWU-mTOpPRoVp7a0c9Lg5UYvQACAQEAAladvQoivp8OuMLmNCME', reply_markup=greet_kb)



#info
@dp.message_handler(regexp='О нас 🪐')
@dp.message_handler(commands=['info'])
async def process_info_command(message: types.Message):
    global user_id
    user_id = str(message.from_user.id)
    cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
    result = cursor.fetchone()
    for right in result:
        if right == '0':
            button_subscription = KeyboardButton('Подписаться на рассылку 🚀')
            button_lastfive = KeyboardButton('Последние пять новостей по подписке 🔎✨')
            button_lastnew = KeyboardButton('Последняя новость по подписке 🔎✨')
            button_website = KeyboardButton('Посетить сайт 🌐')
            button_survey = KeyboardButton('Отзыв ⭐')
            greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
            greet_kb.add(button_subscription, button_lastfive, button_lastnew, button_survey, button_website)
        elif right == '1':
            button_admin = KeyboardButton('🔑 Команды админа')
            button_subscription = KeyboardButton('Подписаться на рассылку 🚀')
            button_lastfive = KeyboardButton('Последние пять новостей по подписке 🔎✨')
            button_lastnew = KeyboardButton('Последняя новость по подписке 🔎✨')
            button_website = KeyboardButton('Посетить сайт 🌐')
            button_survey = KeyboardButton('Отзыв ⭐')
            greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
            greet_kb.add(button_admin, button_subscription, button_lastfive, button_lastnew, button_survey, button_website)

    await bot.send_message(message.chat.id, "*Привет! Если у вас возникли какие-либо вопросы, то вот наши контакты:*\n\n*Группа ВКонтакте Научим.online* https://vk.com/nauchim.online\n*Сайт с мероприятиями* https://www.научим.online ", reply_markup=greet_kb, parse_mode= "Markdown")
    await bot.send_message(message.chat.id, "Для того, чтобы быть в курсе новостей, подпишись на рассылку! Напиши /sub или нажми на кнопку 👇")

#survey
class survey_comment_class(StatesGroup):
    otvet = State()
class survey_class(StatesGroup):
    otvet = State()

@dp.message_handler(regexp='Отзыв ⭐')
async def process_survey1(message: types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    itembtn1 = types.KeyboardButton('Оставить отзыв ✅')
    itembtn2 = types.KeyboardButton('Удалить отзыв ❌')
    markup.add(itembtn1, itembtn2)
    await bot.send_message(message.chat.id, 'Я с радостью выслушаю Вашу критику!', reply_markup=markup)


@dp.message_handler(regexp='Оставить отзыв ✅')
async def process_survey2(message: types.Message):

    cursor.execute(f"SELECT id FROM survey WHERE id = {message.from_user.id}")
    result = cursor.fetchone()
    if result is None:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        itembtn1 = types.KeyboardButton('⭐️')
        itembtn2 = types.KeyboardButton('⭐️⭐️')
        itembtn3 = types.KeyboardButton('⭐️⭐️⭐️')
        itembtn4 = types.KeyboardButton('⭐️⭐️⭐️⭐️')
        itembtn5 = types.KeyboardButton('⭐️⭐️⭐️⭐️⭐️')
        itembtn_stop = types.KeyboardButton('Стоп')
        markup.add(itembtn1, itembtn2, itembtn3, itembtn4, itembtn5, itembtn_stop)
        await bot.send_message(message.chat.id, 'Поставьте чат-боту оценку от 1 до 5', reply_markup=markup)
        await survey_class.otvet.set() 
    else:
        cursor.execute(f"SELECT grade FROM survey WHERE id = {message.from_user.id}")
        result = cursor.fetchone()
        reslst = []
        for res in result:
            reslst.append(res)
        cursor.execute(f"SELECT comment FROM survey WHERE id = {message.from_user.id}")
        com = cursor.fetchone()
        comlst = []
        for com1 in com:
            comlst.append(com1)
        
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        itembtn1 = types.KeyboardButton('Удалить отзыв ❌')
        markup1.add(itembtn1)
        await bot.send_message(message.chat.id, f'У вас уже есть оставленный отзыв\ngrade: {reslst[0]}\ncomment: {comlst[0]}', reply_markup=markup1)

@dp.message_handler(regexp='Удалить отзыв ❌')
async def process_survey(message: types.Message):
    cursor.execute(f"SELECT id FROM survey WHERE id = {message.from_user.id}")
    result = cursor.fetchone()
    if result is None:
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        itembtn1 = types.KeyboardButton('Оставить отзыв ✅')
        markup1.add(itembtn1)
        await bot.send_message(message.chat.id, f'У вас итак нет оставленного отзыва', reply_markup=markup1)
    else:
        cursor.execute(f"DELETE FROM survey WHERE id = '{message.from_user.id}'")
        db.commit()
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        itembtn1 = types.KeyboardButton('Оставить отзыв ✅')
        markup1.add(itembtn1)
        await bot.send_message(user_id, f'Ваш отзыв удален', reply_markup=markup1)


survey_grade = ''
survey_comment = ''
@dp.message_handler(state=survey_class.otvet)
async def survey1_class(message: types.Message, state: FSMContext):
    global survey_grade
    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']  
        if user_message == '⭐️' or user_message == '1':
            survey_grade = 1
            markup = types.ReplyKeyboardRemove(selective=False)
            await bot.send_message(message.chat.id, 'Оставьте комментарий к работе чат-бота', reply_markup=markup)
            await state.finish()
            await survey_comment_class.otvet.set() 
        elif user_message == '⭐️⭐️' or user_message == '2':
            survey_grade = 2
            markup = types.ReplyKeyboardRemove(selective=False)
            await bot.send_message(message.chat.id, 'Оставьте комментарий к работе чат-бота', reply_markup=markup)
            await state.finish()
            await survey_comment_class.otvet.set() 
        elif user_message == '⭐️⭐️⭐️' or user_message == '3':
            survey_grade = 3
            markup = types.ReplyKeyboardRemove(selective=False)
            await bot.send_message(message.chat.id, 'Оставьте комментарий к работе чат-бота', reply_markup=markup)
            await state.finish()
            await survey_comment_class.otvet.set() 
        elif user_message == '⭐️⭐️⭐️⭐️' or user_message == '4':
            survey_grade = 4
            markup = types.ReplyKeyboardRemove(selective=False)
            await bot.send_message(message.chat.id, 'Оставьте комментарий к работе чат-бота', reply_markup=markup)
            await state.finish()
            await survey_comment_class.otvet.set() 
        elif user_message == '⭐️⭐️⭐️⭐️⭐️' or user_message == '5':
            survey_grade = 5
            markup = types.ReplyKeyboardRemove(selective=False)
            await bot.send_message(message.chat.id, 'Оставьте комментарий к работе чат-бота', reply_markup=markup)
            await state.finish()
            await survey_comment_class.otvet.set() 
        elif user_message == 'Стоп':
            cursor.execute(f"SELECT rights FROM users WHERE id = {user_id}")
            result = cursor.fetchone()
            for right in result:
                if right == '0':
                    button_info = KeyboardButton('О нас 🪐')
                    button_subscription = KeyboardButton('Подписаться на рассылку 🚀')
                    button_lastfive = KeyboardButton('Последние пять новостей по подписке 🔎✨')
                    button_lastnew = KeyboardButton('Последняя новость по подписке 🔎✨')
                    button_website = KeyboardButton('Посетить сайт 🌐')
                    button_survey = KeyboardButton('Отзыв ⭐')
                    greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
                    greet_kb.add(button_info, button_subscription, button_lastfive, button_lastnew, button_survey, button_website)
                elif right == '1':
                    button_admin = KeyboardButton('🔑 Команды админа')
                    button_info = KeyboardButton('О нас 🪐')
                    button_subscription = KeyboardButton('Подписаться на рассылку 🚀')
                    button_lastfive = KeyboardButton('Последние пять новостей по подписке 🔎✨')
                    button_lastnew = KeyboardButton('Последняя новость по подписке 🔎✨')
                    button_website = KeyboardButton('Посетить сайт 🌐')
                    button_survey = KeyboardButton('Отзыв ⭐')
                    greet_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width = 1, one_time_keyboard=True)
                    greet_kb.add(button_admin, button_info, button_subscription, button_lastfive, button_lastnew, button_survey, button_website)

            await bot.send_message(user_id, 'Хорошо, команда "Стоп" понята', reply_markup=greet_kb)
            await state.finish()
        else:
            await bot.send_message(message.from_user.id, 'Неверно указана оценка')
            await bot.send_sticker(message.from_user.id, r'CAACAgIAAxkBAAED3IZiApXO9J5lnSwElgcGxXHAYC5N-QAC-QADVp29CpVlbqsqKxs2IwQ')
            await process_survey2(message)

@dp.message_handler(state=survey_comment_class.otvet)
async def process_survey_comment(message: types.Message, state: FSMContext):
    global survey_comment
    global survey_grade
    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text'] 
        survey_comment = user_message
        sql = f"INSERT INTO survey (id, grade, comment) VALUES ('{message.from_user.id}', %s, %s)"
        val = (survey_grade, survey_comment)
        cursor.execute(sql, val)
        db.commit()
        await bot.send_message(message.chat.id, 'Спасибо за отзыв!')
        await state.finish()



#website
@dp.message_handler(regexp='Посетить сайт 🌐')
@dp.message_handler(commands=['website'])
async def website_process(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Ссылка на сайт", url='https://itfest2022flask.herokuapp.com/')
    markup.add(button)
    await bot.send_message(message.from_user.id, 'На сайте также можно следить за новыми новостями по подпискам!', reply_markup=markup)

#lastfivenews
@dp.message_handler(regexp='Последние пять новостей по подписке 🔎✨')
@dp.message_handler(commands=['lastfive'])
async def process_lastfive_command(message: types.Message):
    global domain_list
    domain_list = []
    cursor.execute(f"SELECT name FROM news ORDER BY num")
    result = cursor.fetchall()
    for row in result:
        for x in row:    
            domain_list.append(x)
    
  
    keyboard = ReplyKeyboardMarkup(row_width = 1, one_time_keyboard=True)
    button_list = [KeyboardButton(f'Последние пять новостей по подписке {domain}') for domain in domain_list]
    keyboard.add(*button_list)
    await bot.send_message(message.from_user.id, "Пять записей по какой подписке Вы желаете посмотреть?", reply_markup=keyboard)


@dp.message_handler()
async def echo_message(message: types.Message):
    global domain_list
    global calldata_list

    domain_list = []
    cursor.execute(f"SELECT name FROM news ORDER BY num")
    result = cursor.fetchall()
    for row in result:
        for x in row:    
            domain_list.append(x)

    calldata_list = []
    for domain in domain_list:
        letters = []
        for letter in domain:
            letters.append(letter)
        h = ''
        if letters[0] == '#':
            h = 1
        try:
            letters.remove('#')
        except:
            pass
        try:
            letters.remove('.')
        except:
            pass
        try:
            letters.remove('_')
        except:
            pass
        try:
            letters.remove('-')
        except:
            pass
        calldata =  "".join(letters)
        if h == 1:
            calldata_list.append(calldata.lower() + '_h')
        else:
            calldata_list.append(calldata.lower() + '_d')

    check = 0

    k = 0
    print(domain_list)
    while k < len(domain_list):

        if message.text == f'Последние пять новостей по подписке {domain_list[k]}':
            check = 1
        
            cursor.execute(f"SELECT * FROM {calldata_list[k]}")
            result_in_bd = cursor.fetchone()
            if result_in_bd is None:
                await bot.send_message(message.from_user.id, f"В группе не было ни одной новости😕")
            else:
                i = 0

                cursor.execute(f"SELECT date FROM {calldata_list[k]}")
                data_reg1 = cursor.fetchall()
                date = []
                for x in data_reg1:
                    listdate = list(x)
                    date_str = "".join(listdate)
                    dt = date_str
                    date.append(dt)

                cursor.execute(f"SELECT url FROM {calldata_list[k]}")
                url = cursor.fetchall()
                print(url)
                cursor.execute(f"SELECT body FROM {calldata_list[k]}")
                body0 = cursor.fetchall()
                body_lst = [] #список с содержанием текста последних пяти новостей
                for x in body0:
                    list1 = list(x)
                    body_str = "".join(list1)
                    pic = body_str
                    body_lst.append(pic)

                err = []
                lst1 = []
                for url2 in url:
                    for url1 in url2:
                        list1 = list(url1)
                        if len(list1) == 2 and list1[0] == '{' and list1[1] == '}':
                            lst1.append('')
                            err.append(1)
                        else:
                            try:
                                if list1[1] == '"' and list1[-2] == '"':
                                    list1.remove('{')
                                    list1.remove('}')
                                    list1.remove('"')
                                    list1.remove('"')
                                    url_str = "".join(list1)
                                    pic = url_str
                                    lst1.append(pic)
                                    err.append(0)
                                else:
                                    list1.remove('{')
                                    list1.remove('}')
                                    url_str = "".join(list1)
                                    pic = url_str
                                    lst1.append(pic)
                                    err.append(0)      
                            except:
                                lst1.append('')
                                err.append(1)


                while i < len(date):
                    overcaption = 0
                    data_reg = date[i]
                    body = body_lst[i]    
                    try:
                        if err[i] == 0:
                            lst = lst1[i].split(',')
                            media = types.MediaGroup()
                            x = 0
                            y = 0

                            markup = types.InlineKeyboardMarkup()
                            photo = []
                            for type in lst:
                                if 'vk.com/video' in type or 'youtube.com/' in type:
                                    def short_url():
                                        token = token_api
                                        version = 5.131
                                        url_vk = type
                                        response = requests.get('https://api.vk.com/method/utils.getShortLink?', 
                                                                params = {
                                                                    'access_token':token,
                                                                    'v':version,
                                                                    'url':url_vk
                                                                }
                                                                )
                                        data = response.json()['response']['short_url']
                                        return data
                                    data = short_url()

                                    button = types.InlineKeyboardButton("Ссылка на видео", url=data)
                                    markup.add(button)
                                    x = x + 1
                                else:   
                                    kol = []  
                                    for kolvo in body:
                                        kol.append(kolvo)
                                    if len(kol) < 918:
                                        if body_lst[i] == '':
                                            media.attach_photo(type)
                                        else:
                                            photo.append(type)
                                            if photo.index(type) == 0:
                                                media.attach_photo(type, body)
                                            else:
                                                media.attach_photo(type)
                                    else:
                                        media.attach_photo(type)
                                        overcaption = 1

                                    y = y + 1

                            if body_lst[i] != '':
                                print('body', body)
                                if x > 0 and y == 0: #значит в новости присутствует только видео
                                    if i == 0:
                                        await bot.send_message(message.from_user.id, f"Первая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 1:
                                        await bot.send_message(message.from_user.id, f"Вторая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 2:
                                        await bot.send_message(message.from_user.id, f"Третья новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 3:
                                        await bot.send_message(message.from_user.id, f"Четвертая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 4:
                                        await bot.send_message(message.from_user.id, f"Пятая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")

                                    await bot.send_message(message.from_user.id, body, reply_markup=markup)
                                elif x == 0 and y > 0:#значит в новости присутствует только фото
                                    if i == 0:
                                        await bot.send_message(message.from_user.id, f"Первая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 1:
                                        await bot.send_message(message.from_user.id, f"Вторая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 2:
                                        await bot.send_message(message.from_user.id, f"Третья новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 3:
                                        await bot.send_message(message.from_user.id, f"Четвертая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 4:
                                        await bot.send_message(message.from_user.id, f"Пятая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    if overcaption == 0:
                                        await bot.send_media_group(message.from_user.id, media=media)
                                    else:
                                        await bot.send_message(message.from_user.id, body)
                                        await bot.send_media_group(message.from_user.id, media=media)
                                elif x > 0 and y > 0:
                                    if i == 0:
                                        await bot.send_message(message.from_user.id, f"Первая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 1:
                                        await bot.send_message(message.from_user.id, f"Вторая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 2:
                                        await bot.send_message(message.from_user.id, f"Третья новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 3:
                                        await bot.send_message(message.from_user.id, f"Четвертая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 4:
                                        await bot.send_message(message.from_user.id, f"Пятая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    if overcaption == 0:
                                        await bot.send_media_group(message.from_user.id, media=media)
                                    else:
                                        await bot.send_message(message.from_user.id, body)
                                        await bot.send_media_group(message.from_user.id, media=media)
                                    await bot.send_message(message.from_user.id, "Прикрепленное(-ые) видео:", reply_markup=markup)
                                else:
                                    pass
                                
                            else:
                                print('There is no text in the news')
                                if x > 0 and y == 0: #значит в новости присутствует только видео
                                    if i == 0:
                                        await bot.send_message(message.from_user.id, f"Первая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 1:
                                        await bot.send_message(message.from_user.id, f"Вторая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 2:
                                        await bot.send_message(message.from_user.id, f"Третья новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 3:
                                        await bot.send_message(message.from_user.id, f"Четвертая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 4:
                                        await bot.send_message(message.from_user.id, f"Пятая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    await bot.send_message(message.from_user.id, "Прикрепленное(-ые) видео:", reply_markup=markup)
                                elif x == 0 and y > 0:#значит в новости присутствует только фото
                                    if i == 0:
                                        await bot.send_message(message.from_user.id, f"Первая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 1:
                                        await bot.send_message(message.from_user.id, f"Вторая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 2:
                                        await bot.send_message(message.from_user.id, f"Третья новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 3:
                                        await bot.send_message(message.from_user.id, f"Четвертая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 4:
                                        await bot.send_message(message.from_user.id, f"Пятая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    await bot.send_media_group(message.from_user.id, media=media)
                                elif x > 0 and y > 0:
                                    if i == 0:
                                        await bot.send_message(message.from_user.id, f"Первая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 1:
                                        await bot.send_message(message.from_user.id, f"Вторая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 2:
                                        await bot.send_message(message.from_user.id, f"Третья новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 3:
                                        await bot.send_message(message.from_user.id, f"Четвертая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    elif i == 4:
                                        await bot.send_message(message.from_user.id, f"Пятая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                                    await bot.send_media_group(message.from_user.id, media=media)
                                    await bot.send_message(message.from_user.id, "Прикрепленное(-ые) видео:", reply_markup=markup)
                                else:
                                    pass
                                
                        elif err[i] == 1:
                            print('There is no media in the news')
                            if i == 0:
                                await bot.send_message(message.from_user.id, f"Первая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                            elif i == 1:
                                await bot.send_message(message.from_user.id, f"Вторая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                            elif i == 2:
                                await bot.send_message(message.from_user.id, f"Третья новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                            elif i == 3:
                                await bot.send_message(message.from_user.id, f"Четвертая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                            elif i == 4:
                                await bot.send_message(message.from_user.id, f"Пятая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                            await bot.send_message(message.from_user.id, body)

                    except:
                        print('There is no media in the news')
                        if i == 0:
                            await bot.send_message(message.from_user.id, f"Первая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                        elif i == 1:
                            await bot.send_message(message.from_user.id, f"Вторая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                        elif i == 2:
                            await bot.send_message(message.from_user.id, f"Третья новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                        elif i == 3:
                            await bot.send_message(message.from_user.id, f"Четвертая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                        elif i == 4:
                            await bot.send_message(message.from_user.id, f"Пятая новость по подписке {domain_list[k]}! \nДата публикации: {data_reg}")
                        await bot.send_message(message.from_user.id, body)
                    i = i + 1     
        k+=1
    if check == 0:
        await bot.send_message(message.from_user.id, "Постарайся вводить то, что было предложено, я всего лишь глупая машина, не телепат...")


#проверка на наличие новой записи
async def distribution(message):
    while True:
        try:
            hashtags = []
            cursor.execute(f"SELECT name FROM news ORDER BY num")
            result = cursor.fetchall()
            for row in result:
                for x in row:    
                    hashtags.append(x)

            previous_id = []
            cursor.execute(f"SELECT id_news FROM news ORDER BY num")
            result = cursor.fetchall()
            for row in result:
                for x in row:    
                    previous_id.append(x)
            print(previous_id)

            await asyncio.sleep(10)

            new_id = []
            cursor.execute(f"SELECT id_news FROM news ORDER BY num")
            result = cursor.fetchall()
            for row in result:
                for x in row:    
                    new_id.append(x)
            print(new_id)

            mat1 = len(new_id) - len(previous_id)
            if mat1 > 0: 
                for i in range(0,mat1):
                    previous_id.append('')

            mat2 = len(previous_id) - len(new_id)
            if mat2 > 0: 
                for i in range(0,mat2):
                    new_id.append('')

            i = 0
            while i < len(hashtags):
                try:
                    if new_id[i] == previous_id[i]:
                        pass
                    else:
                        id = []
                        letters = []
                        predres = []
                        for letter in hashtags[i]:
                            letters.append(letter)
                        h = ''
                        if letters[0] == '#':
                            h = 1
                        try:
                            letters.remove('#')
                        except:
                            pass
                        try:
                            letters.remove('.')
                        except:
                            pass
                        try:
                            letters.remove('_')
                        except:
                            pass
                        try:
                            letters.remove('-')
                        except:
                            pass

                        calldata = "".join(letters)
                        if h == 1:
                            predres.append(calldata.lower() + '_h')
                        else:
                            predres.append(calldata.lower() + '_d')

                        hashtags_search = predres[0]

                        cursor.execute(f"SELECT id FROM users WHERE {hashtags_search} = '1'")
                        result = cursor.fetchall()
                        for row in result:
                            for x in row:
                                id.append(x)
                        print(id)

                        for user in id:
                            try:
                                cursor.execute(f"SELECT url FROM news WHERE name = '{hashtags[i]}'")
                                url = cursor.fetchone()
                                cursor.execute(f"SELECT body FROM news WHERE name = '{hashtags[i]}'")
                                body0 = cursor.fetchone()
                                body_lst = []
                                list1 = list(body0)
                                body_str = "".join(list1)
                                pic = body_str
                                body_lst.append(pic)
                                body = body_lst[0]

                                try:
                                    lst1 = []
                                    err = 0
                                    for url1 in url:
                                        list1 = list(url1)
                                        if len(list1) == 2 and list1[0] == '{' and list1[1] == '}':
                                            err = 1
                                        else:
                                            if list1[1] == '"' and list1[-2] == '"':
                                                list1.remove('{')
                                                list1.remove('}')
                                                list1.remove('"')
                                                list1.remove('"')
                                                url_str = "".join(list1)
                                                pic = url_str
                                                lst1.append(pic)
                                            else:
                                                list1.remove('{')
                                                list1.remove('}')
                                                url_str = "".join(list1)
                                                pic = url_str
                                                lst1.append(pic)

                                    if err == 0:
                                        lst = lst1[0].split(',')
                                        media = types.MediaGroup()
                                        x = 0
                                        y = 0

                                        markup = types.InlineKeyboardMarkup()
                                        photo = []
                                        for type in lst:
                                            if 'vk.com/video' in type or 'youtube.com/' in type:
                                                def short_url():
                                                    token = token_api
                                                    version = 5.131
                                                    url_vk = type
                                                    response = requests.get('https://api.vk.com/method/utils.getShortLink?', 
                                                                            params = {
                                                                                'access_token':token,
                                                                                'v':version,
                                                                                'url':url_vk
                                                                            }
                                                                            )
                                                    data = response.json()['response']['short_url']
                                                    return data
                                                data = short_url()

                                                button = types.InlineKeyboardButton("Ссылка на видео", url=data)
                                                markup.add(button)
                                                x = x + 1
                                            else:
                                                if body == 'None' or body == '':
                                                    media.attach_photo(type)
                                                else:
                                                    photo.append(type)
                                                    if photo.index(type) == 0:
                                                        media.attach_photo(type, body)
                                                    else:
                                                        media.attach_photo(type)
                                                y = y + 1

                                        try:
                                            try:
                                                if x > 0 and y == 0: #значит в новости присутствует только видео
                                                    await bot.send_message(user, f"Новая новость новость по подписке {hashtags[i]}!")
                                                    await bot.send_message(user, body, reply_markup=markup)
                                                elif x == 0 and y > 0:#значит в новости присутствует только фото
                                                    await bot.send_message(user, f"Новая новость новость по подписке {hashtags[i]}!")
                                                    await bot.send_media_group(user, media=media)
                                                elif x > 0 and y > 0:
                                                    await bot.send_message(user, f"Новая новость новость по подписке {hashtags[i]}!")
                                                    await bot.send_media_group(user, media=media)
                                                    await bot.send_message(user, "Прикрепленное(-ые) видео:", reply_markup=markup)
                                            except: #если текст слишком большой для caption
                                                media = types.MediaGroup()
                                                for type in lst:
                                                    media.attach_photo(type)
                                                if x > 0 and y == 0: #значит в новости присутствует только видео
                                                    await bot.send_message(user, f"Новая новость новость по подписке {hashtags[i]}!")
                                                    await bot.send_message(user, body)
                                                    await bot.send_message(user, "Прикрепленное(-ые) видео:", reply_markup=markup)
                                                elif x == 0 and y > 0:#значит в новости присутствует только фото
                                                    await bot.send_message(user, f"Новая новость новость по подписке {hashtags[i]}!")
                                                    await bot.send_message(user, body)
                                                    await bot.send_media_group(user, media=media)
                                                elif x > 0 and y > 0:
                                                    await bot.send_message(user, f"Новая новость новость по подписке {hashtags[i]}!")
                                                    await bot.send_message(user, body)
                                                    await bot.send_media_group(user, media=media)
                                                    await bot.send_message(user, "Прикрепленное(-ые) видео:", reply_markup=markup)

                                        except:
                                            print('There is no text in the news')
                                            if x > 0 and y == 0: #значит в новости присутствует только видео
                                                await bot.send_message(user, f"Новая новость новость по подписке {hashtags[i]}!")
                                                await bot.send_message(user, "Прикрепленное(-ые) видео:", reply_markup=markup)
                                            elif x == 0 and y > 0:#значит в новости присутствует только фото
                                                await bot.send_message(user, f"Новая новость новость по подписке {hashtags[i]}!")
                                                await bot.send_media_group(user, media=media)
                                            elif x > 0 and y > 0:
                                                await bot.send_message(user, f"Новая новость новость по подписке {hashtags[i]}!")
                                                await bot.send_media_group(user, media=media)
                                                await bot.send_message(user, "Прикрепленное(-ые) видео:", reply_markup=markup)
                                    elif err == 1:
                                        print('There is no media in the news')
                                        await bot.send_message(user, f"Новая новость новость по подписке {hashtags[i]}!")
                                        await bot.send_message(user, body)
                                except ValueError:
                                    print('There is no media in the news')
                                    await bot.send_message(user, f"Новая новость новость по подписке {hashtags[i]}!")
                                    await bot.send_message(user, body)

                            except:
                                print('There are no users in the list, or the user has blocked the chatbot')
                except:
                    pass
                db.commit()
                i = i + 1
        except:
            db.rollback()

if __name__ == '__main__':
    asyncio.get_event_loop().create_task(distribution(message))
    executor.start_polling(dp)