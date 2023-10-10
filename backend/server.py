from flask import Flask
import requests

app = Flask(__name__)

@app.route('/word', methods = ['GET'])
def getRandomWord():
    url = 'https://random-word-api.vercel.app/api?words=1&length=5'
    word = requests.get(url)
    return word.content

app.run(port=3000)