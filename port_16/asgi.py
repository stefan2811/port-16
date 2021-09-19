"""Module for main app definition. This is the main ASGI module."""
from fastapi import FastAPI

from port_16 import server
from port_16 import event_handler

app = FastAPI(version='1.0.0', title='port-16')
server.attach_routes(app=app)
server.attach_error_handlers(app=app)
app.add_event_handler('startup', event_handler.startup_handler)
app.add_event_handler('shutdown', event_handler.shutdown_handler)
