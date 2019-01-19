from service import app, web, loop

if __name__ == '__main__':
    web.run_app(app, port=8080)
