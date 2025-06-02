from flask import Flask


app = Flask(__name__)

@app.route('/')
def ola_mundo():
    return 'Olá, Mundo com Flask e Poetry! Meu sistema de controle de estoque está no ar!'


if __name__ == '__main__':
    app.run(debug=True)

