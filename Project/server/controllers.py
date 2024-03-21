from werkzeug.wrappers import Response
import json
import datetime

class Controller:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def get_events(self, request):
        with self.db_connection.cursor() as cursor:
            try:
                cursor.execute("SELECT id, name, data_type, close_date, active, check_date, max_bookings FROM events ORDER BY id DESC")
                events = cursor.fetchall()

                # Формирование JSON-ответа
                response_data = []
                for event in events:
                    event_dict = {
                        'id': event[0],
                        'name': event[1],
                        'data_type': event[2],
                        'close_date': event[3].isoformat(),
                        'active': event[4],
                        'check_date': event[5].isoformat(),
                        'max_bookings': event[6]
                    }
                    response_data.append(event_dict)
                return Response(json.dumps(response_data), status=200, mimetype='application/json')
            
            except Exception as e:
                return self._response_error(e)
    
    def get_events_active(self, request):
        with self.db_connection.cursor() as cursor:
            try:
                cursor.execute("SELECT e.id, e.name, e.data_type, e.close_date, e.active, e.check_date, e.max_bookings \
                               FROM events e \
                               LEFT JOIN ( \
                               SELECT event_id, COUNT(*) as booking_count \
                               FROM bookings GROUP BY event_id \
                               ) b ON e.id = b.event_id \
                               WHERE (b.booking_count < e.max_bookings OR b.booking_count IS NULL) AND e.active = TRUE AND LOCALTIMESTAMP < e.close_date \
                               ORDER BY e.id DESC")
                
                events = cursor.fetchall()

                # Формирование JSON-ответа
                response_data = []
                for event in events:
                    event_dict = {
                        'id': event[0],
                        'name': event[1],
                        'data_type': event[2],
                        'close_date': event[3].isoformat(),
                        'active': event[4],
                        'check_date': event[5].isoformat(),
                        'max_bookings': event[6]
                    }
                    response_data.append(event_dict)
                return Response(json.dumps(response_data), status=200, mimetype='application/json')
            
            except Exception as e:
                return self._response_error(e)
    

    def create_event(self, request):
        try:
            data = request.get_json(force=True)
            name = data.get('name')
            data_type = data.get('data_type', '')
            close_date = data.get('close_date', datetime.datetime.now())
            active = data.get('active', False)
            max_bookings = data.get('max_bookings', 0)

            with self.db_connection.cursor() as cursor:
                cursor.execute("INSERT INTO events (name, data_type, close_date, active, max_bookings) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                            (name, json.dumps(data_type), close_date, active, max_bookings))
                event_id = cursor.fetchone()[0]
                self.db_connection.commit()

            return Response(json.dumps({'event_id': event_id}), status=201, mimetype='application/json')

        except ValueError:
            return Response(json.dumps({'error': 'Invalid JSON format'}), status=400, mimetype='application/json')

        except Exception as e:
            return self._response_error(e)

    def get_event(self, request, event_id):
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT id, name, data_type, close_date, active, check_date, max_bookings FROM events WHERE id = %s", (event_id,))
                event = cursor.fetchone()

                if event:
                    event_dict = {
                        'id': event[0],
                        'name': event[1],
                        'data_type': event[2],
                        'close_date': event[3].isoformat(),
                        'active': event[4],
                        'check_date': event[5].isoformat(),
                        'max_bookings': event[6]
                    }
                    return Response(json.dumps(event_dict), status=200, mimetype='application/json')
                else:
                    return Response(json.dumps({'error': 'Event not found'}), status=404, mimetype='application/json')
            
        except Exception as e:
            return self._response_error(e)

    def update_event(self, request, event_id):
        try:
            data = request.get_json()
            name = data.get('name')
            data_type = data.get('data_type')
            close_date = data.get('close_date')
            active = data.get('active')
            max_bookings = data.get('max_bookings')

            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT id, name, data_type, close_date, active, max_bookings FROM events WHERE id = %s", (event_id,))
                event = cursor.fetchone()

                if event:
                    # Если в запросе отсутствует какое-либо поле, оставляем текущее значение из базы данных
                    name = name if name else event[1]
                    data_type = data_type if data_type else event[2]
                    close_date = close_date if close_date else event[3]
                    active = active if active is not None else event[4]
                    max_bookings = max_bookings if max_bookings else event[5]

                    cursor.execute("UPDATE events SET name = %s, data_type = %s, close_date = %s, active = %s, max_bookings = %s WHERE id = %s",
                                (name, json.dumps(data_type), close_date, active, max_bookings, event_id))
                    self.db_connection.commit()

                    return Response(json.dumps({'message': 'Event updated successfully'}), status=200, mimetype='application/json')
                else:
                    return Response(json.dumps({'error': 'Event not found'}), status=404, mimetype='application/json')
            
        except Exception as e:
            return self._response_error(e)

    def delete_event(self, request, event_id):
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT id FROM events WHERE id = %s", (event_id,))
                event = cursor.fetchone()

                if event:
                    cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
                    self.db_connection.commit()

                    return Response(json.dumps({'message': 'Event deleted successfully'}), status=204, mimetype='application/json')
                else:
                    return Response(json.dumps({'error': 'Event not found'}), status=404, mimetype='application/json')
            
        except Exception as e:
            return self._response_error(e)

    def get_bookings(self, request):
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT id, telegram_id, event_id, data, checked, active FROM bookings")
                bookings = cursor.fetchall()

                response_data = []
                for booking in bookings:
                    booking_dict = {
                        'id': booking[0],
                        'telegram_id': booking[1],
                        'event_id': booking[2],
                        'data': booking[3],
                        'checked': booking[4],
                        'active': booking[5]
                    }
                    response_data.append(booking_dict)

                return Response(json.dumps(response_data), status=200, mimetype='application/json')
            
        except Exception as e:
            return self._response_error(e)


    def create_booking(self, request):
        try:
            data = request.get_json()
            telegram_id = data.get('telegram_id')
            event_id = data.get('event_id')
            booking_data = data.get('data')

            with self.db_connection.cursor() as cursor:

                cursor.execute("SELECT max_bookings FROM events WHERE id = %s", (event_id,))
                max_bookings = cursor.fetchone()[0]

                cursor.execute("SELECT count(id) FROM bookings WHERE event_id = %s", (event_id,))
                current_bookings = cursor.fetchone()[0]

                if current_bookings < max_bookings:
                    cursor.execute("INSERT INTO bookings (telegram_id, event_id, data) VALUES (%s, %s, %s) RETURNING id",
                                (telegram_id, event_id, json.dumps(booking_data)))
                    booking_id = cursor.fetchone()[0]
                    self.db_connection.commit()
                    return Response(json.dumps({'booking_id': booking_id}), status=201, mimetype='application/json')
                else:
                    return Response(json.dumps({'error': 'No place'}), status=406, mimetype='application/json')

        
        except ValueError:
            return Response(json.dumps({'error': 'Invalid JSON format'}), status=400, mimetype='application/json')

        except Exception as e:
            return self._response_error(e)


    def get_booking(self, request, booking_id):
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT id, telegram_id, event_id, data, checked, active FROM bookings WHERE id = %s", (booking_id,))
                booking = cursor.fetchone()

                if booking:
                    booking_dict = {
                        'id': booking[0],
                        'telegram_id': booking[1],
                        'event_id': booking[2],
                        'data': booking[3],
                        'checked': booking[4],
                        'active': booking[5]
                    }
                    return Response(json.dumps(booking_dict), status=200, mimetype='application/json')
                else:
                    return Response(json.dumps({'error': 'Booking not found'}), status=404, mimetype='application/json')
            
        except Exception as e:
            return self._response_error(e)


    def update_booking(self, request, booking_id):
        try:
            data = request.get_json()
            telegram_id = data.get('telegram_id')
            event_id = data.get('event_id')
            booking_data = data.get('data')
            checked = data.get('checked')
            active = data.get('active')

            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT id FROM bookings WHERE id = %s", (booking_id,))
                booking = cursor.fetchone()

                if booking:
                    # Если в запросе отсутствует какое-либо поле, оставляем текущее значение из базы данных
                    telegram_id = telegram_id if telegram_id else booking[1]
                    event_id = event_id if event_id else booking[2]
                    booking_data = booking_data if booking_data else booking[3]
                    checked = checked if checked is not None else booking[4]
                    active = active if active is not None else booking[5]

                    cursor.execute("UPDATE bookings SET telegram_id = %s, event_id = %s, data = %s, checked = %s, active = %s WHERE id = %s",
                                (telegram_id, event_id, json.dumps(booking_data), checked, active, booking_id))
                    self.db_connection.commit()

                    return Response(json.dumps({'message': 'Booking updated successfully'}), status=200, mimetype='application/json')
                else:
                    return Response(json.dumps({'error': 'Booking not found'}), status=404, mimetype='application/json')
            
        except Exception as e:
            return self._response_error(e)


    def delete_booking(self, request, booking_id):
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT id FROM bookings WHERE id = %s", (booking_id,))
                booking = cursor.fetchone()

                if booking:
                    cursor.execute("DELETE FROM bookings WHERE id = %s", (booking_id,))
                    self.db_connection.commit()

                    return Response(json.dumps({'message': 'Booking deleted successfully'}), status=204, mimetype='application/json')
                else:
                    return Response(json.dumps({'error': 'Booking not found'}), status=404, mimetype='application/json')
            
        except Exception as e:
            return self._response_error(e)

    
    def get_event_bookings(self, request, event_id):
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT id, telegram_id, event_id, data, checked, active FROM bookings WHERE event_id = %s", (event_id,))
                bookings = cursor.fetchall()

                response_data = []
                for booking in bookings:
                    booking_dict = {
                        'id': booking[0],
                        'telegram_id': booking[1],
                        'event_id': booking[2],
                        'data': booking[3],
                        'checked': booking[4],
                        'active': booking[5]
                    }
                    response_data.append(booking_dict)

                return Response(json.dumps(response_data), mimetype='application/json')
            
        except Exception as e:
            return self._response_error(e)

    def get_bookings_telegram(self, request, telegram_id):
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("SELECT b.id, b.telegram_id, b.event_id, b.data, b.checked, b.active, e.name, e.close_date \
                                FROM bookings b \
                                LEFT JOIN events e ON b.event_id = e.id \
                                WHERE telegram_id = %s AND e.active = TRUE", (telegram_id, ))
                bookings = cursor.fetchall()

                response_data = []
                for booking in bookings:
                    booking_dict = {
                        'id': booking[0],
                        'telegram_id': booking[1],
                        'event_id': booking[2],
                        'data': booking[3],
                        'checked': booking[4],
                        'active': booking[5],
                        'event_name': booking[6],
                        'date': booking[7].strftime("%d-%m-%Y")
                    }
                    response_data.append(booking_dict)

                return Response(json.dumps(response_data), status=200, mimetype='application/json')
            
        except Exception as e:
            return self._response_error(e)

    def _response_error(self, e):
        print(e)
        return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')