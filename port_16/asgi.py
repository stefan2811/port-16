"""Module for main app definition. This is the main ASGI module."""

import inject
from fastapi import FastAPI


from port_16 import server
from port_16.ioc import production


inject.configure(production)

app = FastAPI(version='1.0.0', title='port-16')
server.attach_routes(app=app)
server.attach_error_handlers(app=app)
