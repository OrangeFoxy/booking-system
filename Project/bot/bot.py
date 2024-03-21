import telebot
from static.session import Session
from handlers import commands
from handlers import creating
from static import config as c

session = Session(c.BASE_URL)

# Словарь для сохранения состояний бота
user_states = {}

bot = telebot.TeleBot(c.TOKEN, parse_mode=None)

# Проверки для обработчиков
def get_status(message):
    if message.chat.id in user_states:
        return user_states[message.chat.id]['status']
    
# Обработчик команды /start
bot.message_handler(commands=['start']) \
    (lambda m: commands.send_welcome(m, bot))

# Обработчик команды /events
bot.message_handler(commands=['events']) \
    (lambda m: commands.send_events(m, user_states, session, bot))

# Обработчик команды /bookings
bot.message_handler(commands=['bookings']) \
    (lambda m: commands.send_bookings(m, user_states, session, bot))

# Обработчик для выбора мероприятия
bot.message_handler(func=lambda m: get_status(m) == c.SELECT) \
    (lambda m: creating.handle_select(m, user_states, session, bot))

# Обработчик сбора ответов на вопросы
bot.message_handler(func=lambda m: get_status(m) == c.CREATE) \
    (lambda m: creating.handle_create(m, user_states, session, bot))

# Обработчик подтверждения вопросов
bot.message_handler(func=lambda m: get_status(m) == c.CONFIRM) \
    (lambda m: creating.handle_confirm(m, user_states, session, bot))

# Обработчик изменения вопросов
bot.message_handler(func=lambda m: get_status(m) == c.EDIT) \
    (lambda m: creating.handle_edit(m, user_states, session, bot))

# Обратный вызов на подтверждение вопросов
bot.callback_query_handler(func=lambda call: get_status(call.message) == c.CONFIRM) \
    (lambda call: creating.handle_callback_confirm(call, user_states, session, bot))

if __name__ == '__main__':
    try:
        print("Бот запущен")
        bot.infinity_polling(timeout=10, long_polling_timeout = 5)
    except:
        bot.infinity_polling(timeout=10, long_polling_timeout = 5)