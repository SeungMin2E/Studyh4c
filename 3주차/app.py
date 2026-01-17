from flask import Flask, render_template, request, redirect
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일 불러오기

app = Flask(__name__)

# DB 연결
def get_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),  # ✅ 하드코딩 제거
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
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM board ORDER BY id DESC")
    posts = cursor.fetchall()
    conn.close()
    return render_template("notice.html", posts=posts)

# CREATE
@app.route("/write", methods=["GET", "POST"])
def write():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        writer = request.form["writer"]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO board (title, content, writer) VALUES (%s, %s, %s)",
            (title, content, writer)
        )
        conn.commit()
        conn.close()
        return redirect("/notice")

    return render_template("write.html")

# UPDATE
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        cursor.execute(
            "UPDATE board SET title=%s, content=%s WHERE id=%s",
            (title, content, id)
        )
        conn.commit()
        conn.close()
        return redirect("/notice")

    cursor.execute("SELECT * FROM board WHERE id=%s", (id,))
    post = cursor.fetchone()
    conn.close()
    return render_template("edit.html", post=post)

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
