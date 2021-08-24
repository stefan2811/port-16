import uvicorn

from port_16.asgi import app

APP_HOST = 'localhost'
APP_PORT = 8016


if __name__ == '__main__':
    uvicorn.run(
        app=app,
        host=APP_HOST,
        port=APP_PORT,
        debug=True
    )
