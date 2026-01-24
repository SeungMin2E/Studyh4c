from flask import Flask, render_template, request, redirect 
import pymysql
import os
from dotenv import load_dotenv # os: 환경 변수 읽기, load_dotenv : .env 파일을 환경변수로 로딩 
from flask import session
from werkzeug.utils import secure_filename
from flask import send_from_directory
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
import uuid
from flask import abort


load_dotenv()  # .env 파일 불러오기

app = Flask(__name__) # flask 가 파일 위치를 알기 위해 사용 


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 폴더 없으면 자동 생성
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



# 세션 키
app.secret_key = "secret-key"  # 아무 문자열

# DB 연결
def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"), # mysql 서버주소 
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),  # 하드코딩 제거
        db=os.getenv("DB_NAME"),
        charset="utf8",
        cursorclass=pymysql.cursors.DictCursor
    )

# 메인
@app.route("/")
def main():
    return render_template("main.html")

# READ (목록)
@app.route("/notice")
def notice():
    if "user_id" not in session:
        return redirect("/") # 로그인 안했으면 메인으로 
    
    conn = get_connection()
    cursor = conn.cursor() # sql 실행 도구 생성 
    
    cursor.execute("""
        SELECT board.*, users.id AS user_id
        FROM board
        JOIN users ON board.writer = users.username
        ORDER BY board.id DESC
    """) # 게시글(board)을 가져오는데 그 글을 쓴 사람(users)의 id도 같이 가져와라
    posts = cursor.fetchall() # 결과를 리스트 형태로 저장 
    conn.close() 
    return render_template("notice.html", posts=posts)

# CREATE
@app.route("/write", methods=["GET", "POST"]) # 기본은 GET만 허용, 폼 제출은 POST 
def write():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        writer = session["username"]
        post_password = request.form.get("post_password")

        filename = None
        file = request.files.get("file")
        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO board (title, content, writer, post_password, filename) VALUES (%s, %s, %s, %s, %s)", #sql injection 방지를 위해서 %s 사용 , 
            (title, content, writer, post_password, filename)
        )
        conn.commit()
        conn.close()
        return redirect("/notice")

    return render_template("write.html")

# UPDATE
@app.route("/edit/<int:id>", methods=["GET", "POST"]) # int:id 는 url 파라미터 
def edit(id): # 사용자가 수정버튼을 누르면 ex) 1. edit/3에 들어옴 
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST": # post일때 (폼 제출) 
        title = request.form["title"]
        content = request.form["content"]
        cursor.execute(
            "UPDATE board SET title=%s, content=%s WHERE id=%s",
            (title, content, id)
        )
        conn.commit()
        conn.close()
        return redirect("/notice")

    cursor.execute("SELECT * FROM board WHERE id=%s", (id,)) # 2. 이 게시글을 꺼냄 
    post = cursor.fetchone() # 3. 꺼낸 게시글을 post라는 곳에 담는다 
    conn.close()
    return render_template("edit.html", post=post) # 4. 게시글의 내용을 수정화면에서 보여줘라 

# DELETE
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM board WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect("/notice")

# VIEW
@app.route("/view/<int:id>", methods=["GET", "POST"])
def view(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM board WHERE id=%s", (id,))
    post = cursor.fetchone()

    # 비밀글 처리
    if post["post_password"]:
        if request.method == "POST":
            input_pw = request.form["post_password"]
            if input_pw != post["post_password"]:
                conn.close()
                return render_template(
                    "password.html",
                    error="비밀번호가 틀렸습니다",
                    post_id=id
                )
        else:
            conn.close()
            return render_template("password.html", post_id=id)

    conn.close()
    return render_template("view.html", post=post)

# 검색 기능 
@app.route("/search")
def search():
    q = request.args.get("q", "")
    search_type = request.args.get("type", "title")

    conn = get_connection()
    cursor = conn.cursor()

    if search_type == "title":
        cursor.execute(
            "SELECT * FROM board WHERE title LIKE %s",
            ('%' + q + '%',)
        )

    elif search_type == "content":
        cursor.execute(
            "SELECT * FROM board WHERE content LIKE %s",
            ('%' + q + '%',)
        )

    else:  # title + content
        cursor.execute(
            "SELECT * FROM board WHERE title LIKE %s OR content LIKE %s",
            ('%' + q + '%', '%' + q + '%')
        )

    posts = cursor.fetchall()
    conn.close()

    return render_template("notice.html", posts=posts)

# 회원가입
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        name = request.form["name"]
        school = request.form["school"]

    
        conn = get_connection()
        cursor = conn.cursor()

        # 아이디 중복 체크
        cursor.execute(
            "SELECT id FROM users WHERE username=%s",
            (username,)
        )
        if cursor.fetchone():
            conn.close()
            return render_template(
                "register.html",
                error="이미 사용 중인 아이디입니다."
            )

        # 이메일 중복 체크
        cursor.execute(
            "SELECT id FROM users WHERE email=%s",
            (email,)
        )
        if cursor.fetchone():
            conn.close()
            return render_template(
                "register.html",
                error="이미 사용 중인 이메일입니다."
            )

        # 회원가입
        cursor.execute(
            "INSERT INTO users (username, password, email, name, school) VALUES (%s, %s, %s,%s,%s)",
            (username, password, email,name,school)
        )
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

#  로그인 


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE username=%s",
            (username,)
        )
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/")

        return render_template("login.html", error="아이디 또는 비밀번호가 틀렸습니다")

    return render_template("login.html")

# 로그아웃
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

#파일 다운로드 
@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if not os.path.exists(file_path):
        abort(404)

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )
# 찾기 페이지 
@app.route("/find")
def find():
    return render_template("find.html")


# 아이디 찾기 페이지
@app.route("/find_id", methods=["GET", "POST"])
def find_id():
    if request.method == "POST":
        email = request.form["email"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username FROM users WHERE email=%s",
            (email,)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            return render_template("find_id.html", username=user["username"])
        else:
            return render_template("find_id.html", error="해당 이메일로 가입된 계정이 없습니다.")

    return render_template("find_id.html")

# 비밀번호 찾기
@app.route("/find_pw", methods=["GET", "POST"])
def find_pw():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM users WHERE username=%s AND email=%s",
            (username, email)
        )
        user = cursor.fetchone()
        conn.close()

        if user:
            return render_template("reset_pw.html", username=username)
        else:
            return render_template(
                "find_pw.html",
                error="아이디 또는 이메일이 일치하지 않습니다"
            )

    return render_template("find_pw.html")

# 비밀번호 변경

@app.route("/reset_pw", methods=["POST"])
def reset_pw():
    username = request.form["username"]
    password = request.form["password"]

    hashed_pw = generate_password_hash(password)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password=%s WHERE username=%s",
        (hashed_pw, username)
    )
    conn.commit()
    conn.close()

    return redirect("/")

# 내 프로필 페이지 제작

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect("/login")

    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        school = request.form["school"]

        file = request.files.get("profile_image")
        filename = None

        if file and file.filename:
            ext = os.path.splitext(file.filename)[1]  # .jpg, .png
            filename = f"profile_{session['user_id']}_{uuid.uuid4().hex}{ext}"
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            cursor.execute(
                """
                UPDATE users
                SET name=%s, school=%s, profile_image=%s
                WHERE id=%s
                """,
                (name, school, filename, session["user_id"])
            )
        else:
            cursor.execute(
                """
                UPDATE users
                SET name=%s, school=%s
                WHERE id=%s
                """,
                (name, school, session["user_id"])
            )

        conn.commit()

    cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()
    conn.close()

    return render_template("profile.html", user=user)

# 다른사람 프로필 보기

@app.route("/user/<int:user_id>")
def user_profile(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT username, name, school, profile_image FROM users WHERE id=%s",
        (user_id,)
    )
    user = cursor.fetchone()
    conn.close()

    if not user:
        return "사용자 없음", 404

    return render_template("user_profile.html", user=user)



if __name__ == "__main__":
    app.run(debug=True)
