from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Orbit Project is Running on Vercel!</h1>"

if __name__ == '__main__':
    app.run()