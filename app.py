from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'supersecretkey2026')

# Настройка базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Пароль админа (из переменных окружения или по умолчанию)
admin_password = os.environ.get('ADMIN_PASSWORD', '123456')
ADMIN_PASSWORD_HASH = hashlib.sha256(admin_password.encode()).hexdigest()

# Модели базы данных
class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    books = db.relationship('Book', backref='author', lazy=True)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    summary = db.Column(db.Text)
    book_link = db.Column(db.String(500))
    summary_link = db.Column(db.String(500))
    film_link = db.Column(db.String(500))
    ai_explanation = db.Column(db.Text)

# Создание таблиц
with app.app_context():
    db.create_all()

# ========== ПУБЛИЧНАЯ ЧАСТЬ ==========

@app.route('/')
def index():
    authors = Author.query.all()
    return render_template('index.html', authors=authors)

@app.route('/author/<int:author_id>')
def author_books(author_id):
    author = Author.query.get_or_404(author_id)
    return render_template('author.html', author=author)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book.html', book=book)

# ========== АДМИН-ПАНЕЛЬ ==========

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form['password']
        if hashlib.sha256(password.encode()).hexdigest() == ADMIN_PASSWORD_HASH:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return 'Неверный пароль', 403
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    authors = Author.query.all()
    return render_template('admin_dashboard.html', authors=authors)

@app.route('/admin/add_author', methods=['POST'])
def add_author():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    name = request.form['name']
    if name:
        author = Author(name=name)
        db.session.add(author)
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_book/<int:author_id>', methods=['POST'])
def add_book(author_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    book = Book(
        title=request.form['title'],
        author_id=author_id,
        summary=request.form['summary'],
        book_link=request.form['book_link'],
        summary_link=request.form['summary_link'],
        film_link=request.form['film_link'],
        ai_explanation=request.form['ai_explanation']
    )
    db.session.add(book)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_book/<int:book_id>', methods=['GET', 'POST'])
def edit_book(book_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    book = Book.query.get_or_404(book_id)
    if request.method == 'POST':
        book.title = request.form['title']
        book.summary = request.form['summary']
        book.book_link = request.form['book_link']
        book.summary_link = request.form['summary_link']
        book.film_link = request.form['film_link']
        book.ai_explanation = request.form['ai_explanation']
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_book.html', book=book)

@app.route('/admin/delete_author/<int:author_id>')
def delete_author(author_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    author = Author.query.get_or_404(author_id)
    db.session.delete(author)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_book/<int:book_id>')
def delete_book(book_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
