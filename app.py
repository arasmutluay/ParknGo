from website import create_app

app = create_app()
mail = app.extensions['mail']

if __name__ == '__main__':
    app.run(port=8000, debug=True)
