from flask import Flask, render_template, request, redirect
from db import get_connection

app = Flask(__name__)

# 메인
@app.route('/')
def main():
    return render_template('main.html')

# 게시판 목록 + 검색
@app.route('/notice')
def notice():
    keyword = request.args.get('keyword', '')

    conn = get_connection()
    cursor = conn.cursor()

    if keyword:
        sql = "SELECT * FROM board WHERE title LIKE %s ORDER BY id DESC"
        cursor.execute(sql, ('%' + keyword + '%',))
    else:
        sql = "SELECT * FROM board ORDER BY id DESC"
        cursor.execute(sql)

    boards = cursor.fetchall()
    conn.close()

    return render_template('notice.html', boards=boards)

# 글쓰기 페이지
@app.route('/write')
def write():
    return render_template('write.html')

# 글 저장 (Create)
@app.route('/create', methods=['POST'])
def create():
    title = request.form['title']
    content = request.form['content']

    conn = get_connection()
    cursor = conn.cursor()

    sql = "INSERT INTO board (title, content) VALUES (%s, %s)"
    cursor.execute(sql, (title, content))
    conn.commit()
    conn.close()

    return redirect('/notice')

# 글 상세 (Read)
@app.route('/detail/<int:id>')
def detail(id):
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT * FROM board WHERE id=%s"
    cursor.execute(sql, (id,))
    board = cursor.fetchone()

    conn.close()
    return render_template('detail.html', board=board)

# 수정 페이지
@app.route('/edit/<int:id>')
def edit(id):
    conn = get_connection()
    cursor = conn.cursor()

    sql = "SELECT * FROM board WHERE id=%s"
    cursor.execute(sql, (id,))
    board = cursor.fetchone()

    conn.close()
    return render_template('edit.html', board=board)

# 수정 처리 (Update)
@app.route('/update/<int:id>', methods=['POST'])
def update(id):
    title = request.form['title']
    content = request.form['content']

    conn = get_connection()
    cursor = conn.cursor()

    sql = "UPDATE board SET title=%s, content=%s WHERE id=%s"
    cursor.execute(sql, (title, content, id))
    conn.commit()
    conn.close()

    return redirect('/detail/' + str(id))

# 삭제 (Delete)
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_connection()
    cursor = conn.cursor()

    sql = "DELETE FROM board WHERE id=%s"
    cursor.execute(sql, (id,))
    conn.commit()
    conn.close()

    return redirect('/notice')

app.run(debug=True)
