import json
from telebot import types
from static import config as c
from static import scripts as s

# Выбор мероприятия для создания брони
def handle_select(message, user_states, session, bot):
    state = user_states[message.chat.id]
    try:
        event_id = int(message.text)
    except ValueError:
        bot.reply_to(message, "Пожалуйста, введите корректный номер мероприятия.")
        return

    response = session.get(f'/events/{event_id}')
    event = response.json()

    if event:
        state['event_id'] = event['id']
        state['data_type'] = event['data_type']
        state['status'] = c.CREATE
        bot.reply_to(message, f"Вы выбрали мероприятие '{event['name']}'.")
        # Следующий шаг
        handle_create(message, user_states, session, bot)
    else:
        bot.reply_to(message, "Мероприятие не найдено. Пожалуйста, выберите мероприятие из списка.")

# Начальные кнопки
def get_keyboard():
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button1 = types.KeyboardButton("/events")
    button2 = types.KeyboardButton("/bookings")
    keyboard.add(button1, button2)
    return keyboard

# Формирование вопроса
def get_text_question(q):
    if q['type'] == 'text':
        return f'{q['question']}'
    elif q['type'] == 'option':
        text = f'{q['question']}\n'
        for i, item in enumerate(q['options'], start=1):
            text += f'{i}. {item}\n'
        return text

# Получение ответа в зависимости от типа
def get_answer(message, q):
    answer = ''
    if q['type'] == 'text':
        if s.check_regex(q['mask'], message.text):
            answer = message.text
        else:
            raise Exception("Пожалуйста, введите корректный ответ.")
        
    elif q['type'] == 'option':
        try:
            ans_num = int(message.text)
            if ans_num - 1 < 0: raise Exception("Отрицательное")
            answer = q['options'][ans_num - 1]
        except:
            raise Exception("Пожалуйста, введите корректный номер ответа.")
        
    return answer

# Создание брони через ответы на вопросы
def handle_create(message, user_states, session, bot):
    state = user_states[message.chat.id]
    questions = state['data_type']

    # Первоначальные настройки
    if 'q_number' not in state:
        state['q_number'] = 0
        state['is_quest'] = True
        state['data'] = []

    q = questions[state['q_number']]
    answer = ''
    
    # Вывод вопроса
    if state['is_quest']:
        bot.send_message(message.chat.id, get_text_question(q))
        state['is_quest'] = False

    # Обработка ответа на вопрос
    else:
        try:
            answer = get_answer(message, q)
        except Exception as e:
            bot.reply_to(message, str(e))
            return
            
        state['is_quest'] = True
        state['q_number'] += 1
        state['data'].append(answer)
        # Заданы все вопросы
        if state['q_number'] >= len(questions):
            state['status'] = c.CONFIRM
            print(state['data'])
            print(state)
            # Следующий шаг
            handle_confirm(message, user_states, session, bot)
            return

        # Продолжение вопросов
        handle_create(message, user_states, session, bot)

# Подтверждение правильности введеных ответов
def handle_confirm(message, user_states, session, bot):    
    state = user_states[message.chat.id]
    text = 'Проверьте правильность ответов:\n'

    for i, item in enumerate(state['data_type'], start=0):
        text += f'{i + 1}. {item['question']}: {state['data'][i]}\n'

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    button_create = types.InlineKeyboardButton("Верно", callback_data="create")
    button_change = types.InlineKeyboardButton("Изменить", callback_data="change")
    keyboard.add(button_create, button_change)
    bot.send_message(message.chat.id, text, reply_markup=keyboard)

# Изменение введеных ответов
def handle_edit(message, user_states, session, bot):
    state = user_states[message.chat.id]
    questions = state['data_type']
    
    if 'q_number' not in state:
        try:
            state['q_number'] = int(message.text) - 1
            if state['q_number'] < 0: raise Exception("Отрицательное")
            if state['q_number'] >= len(questions): raise Exception("Выход за массив")
        except:
            bot.reply_to(message, "Пожалуйста, введите корректный номер мероприятия.")
            return
    q = questions[state['q_number']]
    answer = ''
    # Вывод вопроса
    if state['is_quest']:
        bot.send_message(message.chat.id, get_text_question(q))
        state['is_quest'] = False

    # Обработка ответа на вопрос
    else:
        try:
            answer = get_answer(message, q)
        except Exception as e:
            bot.reply_to(message, str(e))
            return
            
        state['data'][state['q_number']] = answer
        state['is_quest'] = True
        state['status'] = c.CONFIRM
        handle_confirm(message, user_states, session, bot)

# Обработка кнопок на изменение или сохранение при подтверждении
def handle_callback_confirm(call, user_states, session, bot):
    if call.data == "create":
        try:
            state = user_states[call.message.chat.id]
            headers = {"Content-Type": "application/json"}
            data = {
                'event_id': state['event_id'],
                'data': state['data'],
                'telegram_id': call.message.chat.id
            }
            json_data = json.dumps(data)
            response = session.post('/bookings', data=json_data, headers=headers)
            if response.status_code == 406:
                bot.send_message(call.message.chat.id, text="Места закончились.", reply_markup=get_keyboard())
            else:
                bot.send_message(call.message.chat.id, text="Бронь создана.", reply_markup=get_keyboard())
            bot.delete_message(call.message.chat.id, call.message.message_id)
            del user_states[call.message.chat.id]

        except:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, text="Произошла ошибка, повторите позже.", reply_markup=get_keyboard())
    
    if call.data == "change":
        state = user_states[call.message.chat.id]
        bot.delete_message(call.message.chat.id, call.message.message_id)
        state['status'] = c.EDIT
        state['is_quest'] = True
        text = 'Выберите вопрос для изменения:\n'
        for i, item in enumerate(state['data_type'], start=0):
            text += f'{i + 1}. {item['question']}: {state['data'][i]}\n'
        del state['q_number']
        bot.send_message(call.message.chat.id, text=text, reply_markup=get_keyboard())