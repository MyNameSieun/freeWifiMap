import pymysql
import hashlib
from datetime import datetime

# 데이터베이스 연결
db = pymysql.connect(
    host="220.67.115.32",
    port=11102,
    user="stdt106",
    password="stdt106",
    database="stdt106",
    charset="utf8"
)

cursor = db.cursor(pymysql.cursors.DictCursor)

# Initialize user_number
user_number = None


\
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def 로그인():
    print("~~~로그인~~~")

    # 사용자로부터 아이디와 비밀번호 입력 받기
    print("test id: sku, test password : sku123")
    id = input("아이디: ")
    password = input("비밀번호: ")

    # 입력받은 아이디를 MySQL에서 찾아 사용자 정보를 조회
    cursor.execute("SELECT * FROM member WHERE id = %s", (id,))

    # 조회된 결과 중 첫 번째 행을 가져와서 user 변수에 저장
    user = cursor.fetchone()

    if user:
        # 비밀번호 해싱 및 일치 여부 확인
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        if hashed_password == user["passWord"]:
            # 비밀번호가 일치하는 경우
            print(f"환영합니다, {id}님!")
            print("=======================================================")
            user_number = user["userNumber"]

            # 로그인 성공 시 사용자 번호 반환
            return user_number
        else:
            print("비밀번호가 일치하지 않습니다.")
            print("=======================================================")
    else:
        print("아이디를 잘못 입력하였거나, 사용자가 존재하지 않습니다.")
        print("=======================================================")

    return None

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def 공공와이파이_전체_조회():
    print("공공 와이파이 전체 조회")
    print("-------------")

    # 공공 와이파이 전체 조회
    cursor.execute("SELECT * FROM wifilocation LIMIT 100")

    wifi_locations = cursor.fetchall()

    if wifi_locations:
        for location in wifi_locations:
            print(f"와이파이 번호: {location['wifiNumber']}")
            print(f"주소: {location['address']}")
            print(f"위도: {location['wifiLatitude']}")
            print(f"경도: {location['wifiLongitude']}")
            print("-------------")
    else:
        print("조회된 공공 와이파이가 없습니다.")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def 공공와이파이_검색():
    print("~~~ 공공와이파이 검색 ~~~")
    address = input("검색할 주소를 입력하세요: ")

    # 공공 와이파이 조회
    cursor.execute("SELECT * FROM wifilocation WHERE address LIKE %s", ('%' + address + '%',))

    wifi_locations = cursor.fetchall()

    if wifi_locations:
        for location in wifi_locations:
            print(f"주소: {location['address']}")
            print(f"상세주소: {location['detailedAddress']}")
            print("-------------")
    else:
        print("검색된 공공와이파이가 없습니다.")
        print("=======================================================")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #      

def 가장_가까운_와이파이_조회():
    print("~~~ 가장 가까운 와이파이 조회 ~~~")
    
    # 사용자가 로그인 했는지 확인
    if user_number:
        # 로그인한 사용자의 위도와 경도 조회

        cursor.execute("SELECT userLatitude, userLongitude FROM user WHERE userNumber = %s", (user_number,))

        user_location = cursor.fetchone()

        # 사용자의 위치 정보가 있는 경우

        if user_location:
            user_latitude = user_location['userLatitude']
            user_longitude = user_location['userLongitude']


            # 가장 가까운 와이파이 5개 조회
            cursor.execute("SELECT wifiNumber, address "
                           "FROM wifilocation "
                           "ORDER BY "
                           "SQRT(POW(69.1 * (wifiLatitude - %s), 2) + POW(69.1 * (%s - wifiLongitude) * COS(wifiLatitude / 57.3), 2)) "
                           "LIMIT 5", (user_latitude, user_longitude))

            wifi_locations = cursor.fetchall()

            if wifi_locations:
                for location in wifi_locations:
                    print(f"와이파이 번호: {location['wifiNumber']}")
                    print(f"주소: {location['address']}")
                    print("-------------")
  
    else:
        print("로그인 후 이용 가능합니다.")
        print("=======================================================")  

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def 글_작성(user_number):
    if user_number is None:
        print("로그인 후 이용 가능합니다.")
        print("=======================================================")
        return

    print("~~~글 작성~~~")
    title = input("제목: ")
    content = input("내용: ")

    # 현재 날짜를 문자열로 가져옴
    writer_date = datetime.now().strftime("%Y-%m-%d")

    # 로그인한 사용자의 번호(user_number)와 아이디를 가져오기
    writer = user_number

    # MySQL에 글 정보 삽입
    cursor.execute(
        "INSERT INTO post (title, content, writer, writerDate, userNumber) VALUES (%s, %s, %s, %s, %s)",
        (title, content, writer, writer_date, user_number)
    )

    db.commit()
    print("글이 작성되었습니다.")
    print("=======================================================")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

def 글_확인():
    print("~~~ 글 확인 ~~~")

    # post 테이블과 member 테이블을 조인하여 작성자 정보를 가져옴
    cursor.execute("SELECT post.postNumber, post.title, post.content, post.writer, post.writerDate, member.id "
                   "FROM post "
                   "JOIN member ON post.writer = member.userNumber")


    posts = cursor.fetchall()

    for post in posts:
        print(f"글 번호: {post['postNumber']}")
        print(f"제목: {post['title']}")
        print(f"내용: {post['content']}")
        print(f"작성자 ID: {post['id']}")
        print(f"작성일: {post['writerDate']}")
        print("-------------")


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


while True:
    print("원하는 메뉴를 입력하세요")
    print("1. 로그인\n2. 공공와이파이 전체 조회\n3. 공공와이파이 검색\n4. 가장 가까운 와이파이 조회\n5. 글 작성\n6. 글 확인\n0. 종료하기")
    choice = input("===---------------------------------===\n")

    if choice == "1":
        user_number = 로그인()
    elif choice == "2":
        공공와이파이_전체_조회()
    elif choice == "3":
        공공와이파이_검색(),
    elif choice == "4":
        가장_가까운_와이파이_조회()
    elif choice == "5":
        글_작성(user_number)
    elif choice == "6":
        글_확인()
    elif choice == "0":
        break
    else:
        print("잘못된 접근입니다.")
        print("=======================================================")

# 데이터베이스 연결 닫기
db.close()

