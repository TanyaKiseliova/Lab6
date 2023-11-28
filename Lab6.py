import telebot
import sqlite3
from telebot import types

bot = telebot.TeleBot('6720885231:AAFruqzL4mbMEgm92WcfhrDqzZihHLZ1VTA')
user_data = {}

def create_Table():
    conn = sqlite3.connect('dogs.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS 
                      dogs(id INTEGER PRIMARY KEY, 
                      name TEXT NOT NULL, description TEXT)''')

    conn.commit()
    conn.close()

def create_rec(name, description):
    conn = sqlite3.connect('dogs.db')
    cursor = conn.cursor()

    cursor.execute('''INSERT INTO dogs (name, description) VALUES (?, ?)''', (name, description))
    conn.commit()
    conn.close()

def get_all():
    conn = sqlite3.connect('dogs.db')
    cursor = conn.cursor()
    cursor.execute(('''SELECT * from dogs'''))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_item(id):
    conn = sqlite3.connect('dogs.db')
    cursor = conn.cursor()
    cursor.execute('''DELETE FROM dogs WHERE id = ?''', (id,))
    conn.commit()
    conn.close()

create_Table()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btnViewAll = types.KeyboardButton(text="Каталог пород")
    btnAdd = types.KeyboardButton("Добавить запись")
    btnDelete = types.KeyboardButton("Удалить запись")
    markup.add(btnViewAll)
    markup.add(btnAdd)
    markup.add(btnDelete)
    bot.send_message(message.from_user.id, 'Доброго времени суток, давайте изучать породы собак вместе!', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Каталог пород")
def getAll(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    rows = get_all()
    for i, row in enumerate(rows):
        bot.send_message(message.from_user.id, f"{i+1}. {row[1]}:\n{row[2]}", reply_markup=markup)

    if not len(rows):
        bot.send_message(message.from_user.id, "Пока список пород пуст(((", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Добавить запись")
def add(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    sent = bot.send_message(message.chat.id, "Введите название породы:")
    bot.register_next_step_handler(sent, ask_description)

def ask_description(message):
    user_data[message.chat.id] = {'name': message.text}
    sent = bot.send_message(message.chat.id, "Введите описание породы:")
    bot.register_next_step_handler(sent, save_breed)


def save_breed(message):
    user_data[message.chat.id]['description'] = message.text
    create_rec(user_data[message.chat.id]['name'], user_data[message.chat.id]['description'])

    bot.send_message(message.chat.id, "Запись успешно добавлена!")

@bot.message_handler(func=lambda message: message.text == "Удалить запись")
def delete(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    rows = get_all()
    if not len(rows):
        bot.send_message(message.chat.id, "Список пород пуст!!")
        return

    sent = bot.send_message(message.chat.id, "Введите номер записи:")
    bot.register_next_step_handler(sent, ask_index)

def ask_index(message):
    user_data[message.chat.id] = {'id': message.text}

    rows = get_all()

    isDeleted = False
    for i, row in enumerate(rows):
        if i == int(user_data[message.chat.id]['id'])-1:
            delete_item(row[0])
            isDeleted = True

    if isDeleted:
        bot.send_message(message.chat.id, "Запись успешно удалена!")
    else:
        bot.send_message(message.chat.id, "Некорретный ввод!")

bot.polling(none_stop=True, interval=0)