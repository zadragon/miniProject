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

@app.route("/articleAdd", methods=["POST"])
def articleAdd_post():
    comment_receive = request.form['comment_give']

    
    
    doc = {
        'comment':comment_receive
    }
    db.flower.insert_one(doc)

    return jsonify({'msg': '저장완료!'})

@app.route("/articleAdd", methods=["GET"])
def articleAdd_get():
    all_comments = list(db.flower.find({},{'_id':False}))
    return jsonify({'result': all_comments})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5001, debug=True)