
# Flask 
from flask import Flask, render_template, jsonify, request, redirect, make_response
app = Flask(__name__)

# pyjwt
import jwt

# jwt를 위한 비밀키
from var import SECRET_KEY

# Port 번호
from var import PORT

# IP
from var import IP

# MongoDB ID/PW
from var import ID
from var import PW
from var import DBPORT

# pymongo DB 연결 pip in
from pymongo import MongoClient 
# client = MongoClient('mongodb://' + ID + ':' + PW + '@' + IP, DBPORT)
client = MongoClient('localhost', 27017)
db = client.jungleBob

# Global 변수
global userData

# 메인 페이지
from datetime import datetime

import time

# 인덱스화면에서 로그인화면으로
@app.route("/", methods=['GET'])
def toLogin() : 
    return redirect('http://' + IP + ":" + str(PORT) + '/login')

def tokenCheck() :
    accessToken = request.cookies.get('access_token')
    
    try :
        if accessToken : 
            payload = jwt.decode(accessToken, SECRET_KEY, "HS256")
            if int(payload['time']) < int(time.time() * 1000) : 
                print('토큰 만료')
                return False
            else :
                print('토큰 유효')
                return payload
        else :
            print("토큰 없음")
            return False
    except jwt.exceptions.DecodeError :
        return False 

def getDate():
    date = ""
    date += str(datetime.today().year) + "-"
    month = datetime.today().month
    if (month < 10):
        date += "0" + str(month) + "-"
    else:
        date += str(month) + "-"
    date += str(datetime.today().day)

    return date

@app.route("/today", methods=['GET'])
def today() : 

    # 토큰 여부 확인
    result = tokenCheck()
    if result == False :
        return redirect('http://' + IP + ":" + str(PORT) + '/login')
    print(result)


    ######### 금일 메뉴 데이터

    # 시스템 날짜 가져와 년-월-일 출력
    # 이후 날짜 비교를 위해 date 변수 그대로 사용
    date = getDate()
    daydate = date
    day = datetime.today().weekday() ## 요일
    if day == 0: daydate += "(월)"
    elif day == 1: daydate += "(화)"
    elif day == 2: daydate += "(수)"
    elif day == 3: daydate += "(목)"
    elif day == 4: daydate += "(금)"
    elif day == 5: daydate += "(토)"
    elif day == 6: daydate += "(일)"
    
    ## 기숙사 식당 메뉴 가져오기
    ### 점심
    dt_l_record = db.menus.find_one({"date": date, "place": "경기드림타워", "lunch": True})
    try:
        dt_l_menu = dt_l_record['menu']
        dt_l_menu = dt_l_menu.replace('\r\n', ', ')
    except:
        print("No Menu")
    
    ### 저녁
    dt_d_record = db.menus.find_one({"date": date, "place": "경기드림타워", "lunch": False})
    try:
        dt_d_menu = dt_d_record['menu']
        dt_d_menu = dt_d_menu.replace('\r\n', ', ')
    except:
        print("No Menu")

    # 경슐랭 메뉴 
    kcl_menu = "돈가스, 김밥, 덮밥, 한식, 햄버거, 타코"

    # E-스퀘어 메뉴
    esq_menu = "라면, 김밥, 덮밥, 국수, 돈까스, 아이스크림"


    ######### 이름판 데이터 
    
    # 경기드림타워 이름판
    ## 점심
    dtpeople = db.logs.find({"place": "경기드림타워", "lunch": "true", "date": date})
    dt_lunch_list = []
    for p in dtpeople:
        dt_lunch_list.append(p['name'])
    ## 저녁
    dtpeople = db.logs.find({"place": "경기드림타워", "lunch": "false", "date": date})
    dt_dinner_list = []
    for p in dtpeople:
        dt_dinner_list.append(p['name'])
    
    # 경슐랭 이름판
    ## 점심
    kclpeople = db.logs.find({"place": "경슐랭", "lunch": "true", "date": date})
    kcl_lunch_list = []
    for p in kclpeople:
        kcl_lunch_list.append(p['name'])
    ## 저녁
    kclpeople = db.logs.find({"place": "경슐랭", "lunch": "false", "date": date})
    kcl_dinner_list = []
    for p in kclpeople:
        kcl_dinner_list.append(p['name'])

    # 이스퀘어 이름판
    ## 점심
    esqpeople = db.logs.find({"place": "이스퀘어", "lunch": "true", "date": date})
    esq_lunch_list = []
    for p in esqpeople:
        esq_lunch_list.append(p['name'])
    ## 저녁
    esqpeople = db.logs.find({"place": "이스퀘어", "lunch": "false", "date": date})
    esq_dinner_list = []
    for p in esqpeople:
        esq_dinner_list.append(p['name'])

    # name = userData['name']
    name = result['name']

    return render_template('today.html', 
                           template_date = daydate,
                        #    template_dt_lunch_menu = dt_l_menu, template_dt_dinner_menu = dt_d_menu,
                           template_kcl_menu = kcl_menu, template_esq_menu = esq_menu,
                           template_dt_lunch_people = dt_lunch_list, template_dt_dinner_people = dt_dinner_list, 
                           template_kcl_lunch_people = kcl_lunch_list, template_kcl_dinner_people = kcl_dinner_list, 
                           template_esq_lunch_people = esq_lunch_list, template_esq_dinner_people = esq_dinner_list,
                           template_userName = name)


#################################### 회원가입 

# 회원가입 화면 출력 
@app.route("/signIn", methods=['GET'])
def signInGet() : 
    return render_template("signin.html")

# 회원가입 요청 
@app.route("/signIn", methods=['POST'])
def signInPost() :
    userId = request.form['signinID'].strip()
    userPw = request.form['signinPW'].strip()
    userName = request.form['signinName'].strip()
    
    userData = db.users.find_one({"id":userId})
    
    if userData == None :
        result = db.users.insert_one({"id":userId, "pw":userPw, "name":userName})
        print(result)
        return jsonify({"msg":"signin success"})
    else :
        return jsonify({"msg":"Fail"})
        
#####################################

#################################### 로그인 
# 로그인 창 띄우기 
@app.route("/login", methods=['GET'])
def loginGet() :
    # 토큰 여부 확인
    result = tokenCheck()
    if result != False :
        return redirect('http://' + IP + ":" + str(PORT) + '/today')
    print(result)

    return render_template("login.html")

# 로그인 시도 
@app.route("/login", methods=['POST'])
def loginPost() :
    print("Try login")
    userId = request.form['userId'].strip()
    userPw = request.form['userPw'].strip()

    # 토큰 가져오기 
    accessToken = request.cookies.get('access_token')
    
    try :
        if accessToken : 
            payload = jwt.decode(accessToken, SECRET_KEY, "HS256")
            if int(payload['time']) < int(time.time() * 1000) : 
                print('토큰 만료')
                pass
            else :
                if userId == payload['id'] :
                    print('토큰 유효')
                    return jsonify({"msg":"token auth success"})
                pass
    except jwt.exceptions.DecodeError :
        pass
        
    # 2. 토큰이 없다면 로그인을 시도하는 사람이므로 로그인 ID, PW를 확인 후 토큰을 발행한다.

    global userData
    
    userData = db.users.find_one({"id":userId},{"_id":False})

    print('ㅎㅇ', userData)
    if userData == None :
        return jsonify({"msg":'Login Fail'})
    # 로그인 정보 없음 
    elif userId != userData['id'] or userPw != userData['pw'] :
        return jsonify({"msg":"Login Fail"})
    
    payload = {
        # 토큰 유효 시간 1시간 -  Unix 타임 스탬프 사용
        'time': int(time.time() * 1000) + 60 * 10 * 1000, 
        'id':userData['id'],
        'name':userData['name']
    }

    token =  jwt.encode(payload , SECRET_KEY , "HS256")

    # 토큰을 발행해서 클라이언트 쿠키에 저장 
    reps = make_response()
    reps.set_cookie('access_token', token)
    return reps

#################################### 유저 식사 저장
@app.route("/api/selectedMenu", methods=['GET'])
def selectedMenu() :
    place = request.args.get('place_give')
    lunch = request.args.get('lunch_give')
    date = getDate()

    # name = userData['name'] # 이렇게 하면 이름이 마지막 로그인 한 사람으로 바뀜
    result = tokenCheck()
    if result == False :
        return redirect('http://' + IP + ":" + str(PORT) + '/login')
    
    name = result['name']

    if lunch == 'true':
        logs_lunch_user = db.logs.find_one({'name': name, 'lunch': 'true', 'date':date})

        if logs_lunch_user != None and logs_lunch_user['name'] == name:
            db.logs.delete_one({'name': name, 'lunch': 'true', 'date':date})
            print('점심 유저 데이터 삭제 성공')
        else:
            print('점심 유저 데이터 삭제 실패')
    else:
        logs_dinner_user = db.logs.find_one({'name': name, 'lunch': 'false', 'date':date})

        if logs_dinner_user != None and logs_dinner_user['name'] == name:
            db.logs.delete_one({'name': name, 'lunch': 'false', 'date':date})
            print('점심 유저 데이터 삭제 성공')
        else:
            print('점심 유저 데이터 삭제 실패')

    result = db.logs.insert_one({'name': name,
                                 'lunch': lunch,
                                 'place': place,
                                 'date': date})

    if result.acknowledged:
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail'})

    #####################################
    
### 점심 저녁 체크 여부
@app.route("/submit", methods=['GET'])
def checkLD():
    result = tokenCheck()
    if result == False :
        return redirect('http://' + IP + ":" + str(PORT) + '/login')
    
    isLD = request.form['btnradio']
    print(isLD)

@app.route("/mypage", methods=['GET'])
def mypage() :
    result = tokenCheck()
    if result == False :
        return redirect('http://' + IP + ":" + str(PORT) + '/login')
    
    lunch_menu = ''
    dinner_menu = ''
    lunch_place = ''
    dinner_place = ''

    now = int(time.time()) - 86400
    date = datetime.fromtimestamp(now).strftime('%Y-%m-%d')
    name = result['name']

    
    lunch = db.logs.find_one({'name':name,'date':date,'lunch':"true"})
    dinner = db.logs.find_one({'name':name,'date':date, 'lunch':"false"})

    if lunch is None and dinner is None:
        lunch_menu = "어제 먹은 점심이 없습니다."
        dinner_menu = "어제 먹은 저녁이 없습니다."
    elif lunch is None:
        lunch_menu = "어제 먹은 점심이 없습니다."
    elif dinner is None:
        dinner_menu = "어제 먹은 저녁이 없습니다."
    else:
        lunch_place = lunch['place']
        dinner_place = dinner['place']

        if lunch['place'] == '경기드림타워' :
            lunch_menu_rcd = db.menus.find_one({'place': '경기드림타워', 'date': date, 'lunch': True})
            if lunch_menu_rcd is not None:
                lunch_menu = lunch_menu_rcd['menu']
                lunch_menu = lunch_menu.replace('\r\n', ', ')
                lunch_place = lunch_menu_rcd['place']

        if dinner['place'] == '경기드림타워' :
            dinner_menu_rcd = db.menus.find_one({'place': '경기드림타워', 'date': date, 'lunch': False})
            if dinner_menu_rcd is not None:
                dinner_menu = dinner_menu_rcd['menu']
                dinner_menu = dinner_menu.replace('\r\n', ', ')
                dinner_place = dinner_menu_rcd['place']
    
        if lunch != None :
            if lunch['place'] == '경슐랭' :
                lunch_menu =  "돈가스, 김밥, 덮밥, 한식, 햄버거, 타코"
                lunch_place = '경슐랭'
            elif lunch['place'] == '이스퀘어' :
                lunch_menu = "라면, 김밥, 덮밥, 국수, 돈까스, 아이스크림"
                lunch_place = '이스퀘어'
            else :
                pass
        
        if dinner != None :
            if dinner['place'] == '경슐랭' :
                dinner_menu =  "돈가스, 김밥, 덮밥, 한식, 햄버거, 타코"
            elif dinner['place'] == '이스퀘어' :
                dinner_menu = "라면, 김밥, 덮밥, 국수, 돈까스, 아이스크림"
            else : 
                pass

    day = datetime.today().weekday() ## 요일
    if day == 0: date += "(일)"
    elif day == 1: date += "(월)"
    elif day == 2: date += "(화)"
    elif day == 3: date += "(수)"
    elif day == 4: date += "(목)"
    elif day == 5: date += "(금)"
    elif day == 6: date += "(토)"

    print(day)
    return render_template('mypage.html', payload = result,
                           template_lunch_menu = lunch_menu,
                           template_lunch_place = lunch_place,
                           template_dinner_menu = dinner_menu,
                           template_dinner_place = dinner_place,
                           template_my_name = result['name'],
                           template_date = date
                           )
@app.route('/map', methods=['GET'])
def map() :
    return render_template('map.html')
if __name__ == "__main__" :
    app.run("0.0.0.0", port=PORT, debug=True)

