from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
    return "MusicBot起動中"

def run():
    app.run(host="0.0.0.0", port=8080)

def start():
    server = Thread(target=run)
    server.start()