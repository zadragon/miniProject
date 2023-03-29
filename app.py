from flask import Flask, render_template, request, jsonify, redirect, url_for
app = Flask(__name__)
from pymongo import MongoClient
import certifi

ca = certifi.where()
client = MongoClient('mongodb+srv://sparta:test@cluster0.ottleza.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)

db = client.miniProject

# JWT 토큰을 만들 때 필요한 비밀문자열입니다. 아무거나 입력해도 괜찮습니다.
# 이 문자열은 서버만 알고있기 때문에, 내 서버에서만 토큰을 인코딩(=만들기)/디코딩(=풀기) 할 수 있습니다.
SECRET_KEY = 'GROUP6'

# JWT 패키지를 사용합니다. (설치해야할 패키지 이름: PyJWT)
import jwt

# 토큰에 만료시간을 줘야하기 때문에, datetime 모듈도 사용합니다.
import datetime

# 회원가입 시엔, 비밀번호를 암호화하여 DB에 저장해두는 게 좋습니다.
# 그렇지 않으면, 개발자(=나)가 회원들의 비밀번호를 볼 수 있으니까요.^^;
import hashlib

@app.route('/')
def home():
   token_receive = request.cookies.get('mytoken')
   try:
      payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
      user_info = db.user.find_one({"id": payload['id']})
      return render_template('index.html', nickname=user_info["nick"])
   except jwt.ExpiredSignatureError:
      return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
   except jwt.exceptions.DecodeError:
      return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
   return render_template('login.html')

# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.
@app.route('/api/login', methods=['POST'])
def api_login():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']

   # 회원가입 때와 같은 방법으로 pw를 암호화합니다.
   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
   
   # id, 암호화된pw을 가지고 해당 유저를 찾습니다.
   result = db.user.find_one({'id': id_receive, 'pw': pw_hash})
   
   if result is not None:
        # JWT 토큰에는, payload와 시크릿키가 필요합니다.
        # 시크릿키가 있어야 토큰을 디코딩(=풀기) 해서 payload 값을 볼 수 있습니다.
        # 아래에선 id와 exp를 담았습니다. 즉, JWT 토큰을 풀면 유저ID 값을 알 수 있습니다.
        # exp에는 만료시간을 넣어줍니다. 만료시간이 지나면, 시크릿키로 토큰을 풀 때 만료되었다고 에러가 납니다.
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=4444)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        # token을 줍니다.
        return jsonify({'result': 'success', 'token': token})
   # 찾지 못하면
   else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않거나 가입정보가 없습니다.'})


@app.route('/register')
def register():
   return render_template('register.html')

@app.route('/api/register', methods=['POST'])
def api_register():
   id_receive = request.form['id_give']
   pw_receive = request.form['pw_give']
   nickname_receive = request.form['nickname_give']

   pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

   db.user.insert_one({'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})

   return jsonify({'result': 'success'})
    

@app.route("/articleAdd", methods=["POST"])
def articleAdd_post():
    comment_receive = request.form['comment_give']
    commentId_receive = request.form['comment_id']
    commentfile_receive = request.files['comment_image']


    extension = commentfile_receive.filename.split('.')[-1]
    today = datetime.datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    filename = f'img-{mytime}'
    save_to = f'static/{filename}.{extension}'
    commentfile_receive.save(save_to)

    token_receive = request.cookies.get('mytoken')    
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    doc = {
        'comment':comment_receive,
        'comment_id':commentId_receive,        
        'user_id':payload['id'],
        'img':f'{filename}.{extension}'
    }
    db.flower.insert_one(doc)

    return jsonify({'msg': '저장완료!'})

@app.route("/articleAdd", methods=["GET"])
def articleAdd_get():
    token_receive = request.cookies.get('mytoken')    
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    
    all_comments = list(db.flower.find({},{'_id':False}))
    return jsonify({'result': all_comments,'user_id':payload['id']})

@app.route("/articleOneGet", methods=["GET"])
def articleOneGet():
    token_receive = request.cookies.get('mytoken')    
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    comment_id = request.args.get('comment_id')
    comment = list(db.flower.find({'comment_id':comment_id,'user_id':payload['id']},{'_id':False}))
    return jsonify({'result': comment})

@app.route("/articleModify", methods=["PUT"])
def articleModify():
    token_receive = request.cookies.get('mytoken')    
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    
    comment_receive = request.form['comment_give']
    comment_id_receive = request.form['commentId_give']
    doc = {'comment':comment_receive}
    db.flower.update_one({'comment_id':comment_id_receive,'user_id':payload['id']},{'$set':doc})
    
    return jsonify({'msg': '수정 완료!'})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)