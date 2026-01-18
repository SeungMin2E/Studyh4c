from flask import Flask, render_template, request, redirect 
import pymysql
import os
from dotenv import load_dotenv # os: 환경 변수 읽기, load_dotenv : .env 파일을 환경변수로 로딩 

load_dotenv()  # .env 파일 불러오기

app = Flask(__name__) # flask 가 파일 위치를 알기 위해 사용 

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
    conn = get_connection()
    cursor = conn.cursor() # sql 실행 도구 생성 
    cursor.execute("SELECT * FROM board ORDER BY id DESC")
    posts = cursor.fetchall() # 결과를 리스트 형태로 저장 
    conn.close() 
    return render_template("notice.html", posts=posts)

# CREATE
@app.route("/write", methods=["GET", "POST"]) # 기본은 GET만 허용, 폼 제출은 POST 
def write():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        writer = request.form["writer"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO board (title, content, writer) VALUES (%s, %s, %s)", #sql injection 방지를 위해서 %s 사용 , 
            (title, content, writer)
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
@app.route("/view/<int:id>")
def view(id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM board WHERE id=%s", (id,))
    post = cursor.fetchone()
    conn.close()
    return render_template("view.html", post=post)

if __name__ == "__main__":
    app.run(debug=True)
