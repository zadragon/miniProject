from flask import Flask, render_template, request, jsonify
app = Flask(__name__)
from pymongo import MongoClient
import certifi

ca = certifi.where()
client = MongoClient('mongodb+srv://sparta:test@cluster0.ottleza.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)

db = client.miniProject

@app.route('/')
def home():
   return render_template('index.html')

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/join')
def join():
   return render_template('join.html')

@app.route("/guestbook", methods=["POST"])
def guestbook_post():
   
    
    return jsonify({'msg': '저장 완료!'})

@app.route("/guestbook", methods=["GET"])
def guestbook_get():
    return jsonify({'msg': '로드 완료!'})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5001, debug=True)