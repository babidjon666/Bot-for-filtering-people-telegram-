import telebot
import json
import os
from threading import Timer

TOKEN = ''

bot = telebot.TeleBot(TOKEN)

USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as file:
            return json.load(file)
    return []

def save_users(users):
    with open(USERS_FILE, 'w') as file:
        json.dump(users, file, indent=4)

def delete_message(bot, chat_id, message_id):
    bot.delete_message(chat_id, message_id)

def reply_and_schedule_deletion(message, text):
    try:
        sent_message = bot.reply_to(message, text)
        Timer(5, delete_message, args=(bot, message.chat.id, sent_message.message_id)).start()
    except Exception as e:
        print(f"Failed to send or schedule deletion: {e}")

# Команда /start с инструкцией по использованию бота
@bot.message_handler(commands=['start'])
def start(message):
    instructions = (
        "Перешлите мне сообщение, чтобы проверить или добавить пользователя в список."
    )
    reply_and_schedule_deletion(message, instructions)

# Обработка пересланных сообщений для проверки и добавления ID отправителя
@bot.message_handler(content_types=['text', 'photo', 'audio', 'video', 'document', 'sticker', 'voice', 'location', 'contact', 'venue', 'animation', 'video_note', 'new_chat_members', 'left_chat_member', 'new_chat_title', 'new_chat_photo', 'delete_chat_photo', 'group_chat_created', 'supergroup_chat_created', 'channel_chat_created', 'migrate_to_chat_id', 'migrate_from_chat_id', 'pinned_message'])
def handle_forwarded_messages(message):
    if message.forward_from:
        user_id = message.forward_from.id

        # Загружаем список пользователей
        users = load_users()

        # Проверяем, есть ли пользователь в списке
        if user_id not in users:
            users.append(user_id)
            save_users(users)
            response = f'✅ Пользователь с ID {user_id} был добавлен в список.'
        else:
            response = f'❌ Пользователь с ID {user_id} уже в списке.'

        reply_and_schedule_deletion(message, response)
    else:
        reply_and_schedule_deletion(message, "❌ скрытый профиль.")

# Запуск бота
bot.polling(none_stop=True)