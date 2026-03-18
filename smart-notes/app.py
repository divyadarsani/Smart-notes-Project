from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_mysqldb import MySQL
import os
from config import *
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)
app.config.from_object('config')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

mysql = MySQL(app)

# =============================
# HOME
# =============================
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM notes ORDER BY created_at DESC")
    notes = cur.fetchall()
    return render_template('index.html', notes=notes)

# =============================
# ADD NOTE
# =============================
@app.route('/add', methods=['GET', 'POST'])
def add_note():
    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        tags = request.form['tags']
        priority = request.form['priority']

        image_file = request.files['image']
        image_name = ''

        if image_file and image_file.filename != '':
            image_name = image_file.filename
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_name))

        cur = mysql.connection.cursor()
        cur.execute("""INSERT INTO notes(title, category, content, tags, priority, image)
                       VALUES(%s,%s,%s,%s,%s,%s)""",
                    (title, category, content, tags, priority, image_name))
        mysql.connection.commit()
        return redirect(url_for('index'))

    return render_template('add_note.html')

# =============================
# VIEW NOTE
# =============================
@app.route('/note/<int:id>')
def view_note(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM notes WHERE id=%s", (id,))
    note = cur.fetchone()
    return render_template('view_note.html', note=note)

# =============================
# EDIT NOTE
# =============================
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_note(id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        title = request.form['title']
        category = request.form['category']
        content = request.form['content']
        tags = request.form['tags']
        priority = request.form['priority']

        cur.execute("""UPDATE notes 
                       SET title=%s, category=%s, content=%s, tags=%s, priority=%s 
                       WHERE id=%s""",
                    (title, category, content, tags, priority, id))
        mysql.connection.commit()
        return redirect(url_for('index'))

    cur.execute("SELECT * FROM notes WHERE id=%s", (id,))
    note = cur.fetchone()
    return render_template('edit_note.html', note=note)

# =============================
# DELETE NOTE
# =============================
@app.route('/delete/<int:id>')
def delete_note(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM notes WHERE id=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('index'))

# =============================
# SEARCH
# =============================
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    cur = mysql.connection.cursor()
    cur.execute("""SELECT * FROM notes 
                   WHERE title LIKE %s OR content LIKE %s""",
                ('%' + query + '%', '%' + query + '%'))
    notes = cur.fetchall()
    return render_template('index.html', notes=notes)

# =============================
# EXPORT PDF
# =============================
@app.route('/export/<int:id>')
def export_pdf(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM notes WHERE id=%s", (id,))
    note = cur.fetchone()

    file_path = f"note_{id}.pdf"
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []
    content.append(Paragraph(note[1], styles['Title']))
    content.append(Paragraph(note[3], styles['BodyText']))

    doc.build(content)

    return send_file(file_path, as_attachment=True)

# =============================
# EXPLAIN NOTE (AI-LIKE)
# =============================
@app.route('/explain/<int:id>')
def explain_note(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT content FROM notes WHERE id=%s", (id,))
    note = cur.fetchone()

    text = note[0]
    sentences = text.split('.')
    summary = '.'.join(sentences[:2])

    return f"<h2>Summary:</h2><p>{summary}</p><br><a href='/'>Back</a>"

# =============================
# REMINDER
# =============================
@app.route('/reminder')
def reminder():
    return "Reminder: Study your important notes today!"

# =============================
# RUN
# =============================
if __name__ == '__main__':
    app.run(debug=True)