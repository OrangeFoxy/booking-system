from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule

class Router:
    def __init__(self, controller):
        self.url_map = Map([
            Rule("/events", endpoint="events"),
            Rule("/events/active", endpoint="events_active"),
            Rule("/bookings", endpoint="bookings"),
            Rule("/bookings/telegram/<int:telegram_id>", endpoint="bookings_telegram"),
            Rule("/events/<int:event_id>", endpoint="event"),
            Rule("/bookings/<int:booking_id>", endpoint="booking"),
            Rule("/events/<int:event_id>/bookings", endpoint="event_bookings"),
        ])
        self.controller = controller

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        endpoint, values = adapter.match()

        if request.method == "OPTIONS":
            response = Response("OK", status=200)
            response.headers.add("Access-Control-Allow-Methods", "*")
            response.headers.add("Access-Control-Allow-Headers", "*")
            return response

        if endpoint == "events":
            if request.method == "GET":
                return self.controller.get_events(request)
            elif request.method == "POST":
                return self.controller.create_event(request)
            
        if endpoint == "events_active":
            if request.method == "GET":
                return self.controller.get_events_active(request)
            
        elif endpoint == "event":
            if request.method == "GET":
                return self.controller.get_event(request, values["event_id"])
            elif request.method == "PUT":
                return self.controller.update_event(request, values["event_id"])
            elif request.method == "DELETE":
                return self.controller.delete_event(request, values["event_id"])
            
        elif endpoint == "bookings":
            if request.method == "GET":
                return self.controller.get_bookings(request)
            elif request.method == "POST":
                return self.controller.create_booking(request)
            
        elif endpoint == "booking":
            if request.method == "GET":
                return self.controller.get_booking(request, values["booking_id"])
            elif request.method == "PUT":
                return self.controller.update_booking(request, values["booking_id"])
            elif request.method == "DELETE":
                return self.controller.delete_booking(request, values["booking_id"])
            
        elif endpoint == "event_bookings":
            if request.method == "GET":
                return self.controller.get_event_bookings(request, values["event_id"])
            
        elif endpoint == "bookings_telegram":
            if request.method == "GET":
                return self.controller.get_bookings_telegram(request, values["telegram_id"])

        return Response("Not Found", status=404)

    def __call__(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        response.headers.add("Access-Control-Allow-Origin", "*")

        return response(environ, start_response)

