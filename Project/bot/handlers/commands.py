from static import config as c
from telebot import types

# Команда /start - начало беседы с ботом
def send_welcome(message, bot):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = types.KeyboardButton("/events")
    button2 = types.KeyboardButton("/bookings")
    keyboard.add(button1, button2)
    bot.send_message(message.chat.id, "Команды для работы:\n/events - доступные мероприятия для бронирования\n/bookings - ваши брони", reply_markup=keyboard)

# Команда /events - начало создания брони
def send_events(message, user_states, session, bot):
    if message.chat.id in user_states:
        del user_states[message.chat.id]

    response = session.get('/events/active')
    events = response.json()
    event_list_message = "Выберите мероприятие указав номер:\n"
    for event in events:
        event_list_message += f"{event['id']}. {event['name']}\n"

    user_states[message.chat.id] = {'status': c.SELECT}
    bot.reply_to(message, event_list_message)

# Команда /bookings - просмотр и изменение броней
def send_bookings(message, user_states, session, bot):
    if message.chat.id in user_states:
        del user_states[message.chat.id]

    response = session.get(f'/bookings/telegram/{message.chat.id}')
    bookings = response.json()
    bookings_list = "Ваши брони:\n"
    for i, booking in enumerate(bookings, 1):
        bookings_list += f"{i}. {booking['event_name']} - {booking['date']}\n"
    bot.reply_to(message, bookings_list)