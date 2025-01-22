import re
from flask import Flask, render_template, request
from fuzzywuzzy import fuzz
import sqlite3

app = Flask(__name__)

# Подключаемся к базе данных SQLite
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Инициализация базы данных
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sentences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original TEXT,
            translated TEXT
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original TEXT,
            translated TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Функция для определения, является ли строка предложением
def is_sentence(text):
    # Проверяем, есть ли знаки препинания
    punctuation_marks = r'[.,!?;:()]'
    if re.search(punctuation_marks, text):
        return True  # Это предложение
    
    # Если нет знаков препинания, проверяем количество слов
    words_count = len(text.split())
    return words_count > 2  # Если слов больше двух, это предложение

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None

    if request.method == 'POST':
        original = request.form.get('original')
        translated = request.form.get('translated')

        if original and translated:
            # Определяем таблицу для записи
            if is_sentence(original):
                table = 'sentences'
            else:
                table = 'words'

            conn = get_db_connection()
            conn.execute(f'INSERT INTO {table} (original, translated) VALUES (?, ?)', (original, translated))
            conn.commit()
            conn.close()
            message = "Данные внесены"

        elif 'add_file' in request.form:
            original_file = request.files['original_file']
            translated_file = request.files['translated_file']

            if original_file and translated_file:
                original_text = original_file.read().decode('utf-8')
                translated_text = translated_file.read().decode('utf-8')

                original_sentences = original_text.split('\n')
                translated_sentences = translated_text.split('\n')

                conn = get_db_connection()
                for original, translated in zip(original_sentences, translated_sentences):
                    conn.execute('INSERT INTO sentences (original, translated) VALUES (?, ?)', (original.strip(), translated.strip()))
                conn.commit()
                conn.close()
                message = "Данные внесены"

        elif 'translate' in request.form:
            original_input = request.form['original_input']

            conn = get_db_connection()
            if is_sentence(original_input):
                translations = conn.execute('SELECT * FROM sentences').fetchall()
            else:
                translations = conn.execute('SELECT * FROM words').fetchall()
            conn.close()

            top_translations = []

            for translation in translations:
                score = fuzz.ratio(original_input, translation['original'])
                top_translations.append((score, translation['translated']))

            top_translations.sort(reverse=True, key=lambda x: x[0])

            return render_template('index.html', top_translations=top_translations[:3], original_input=original_input, message=message)

    return render_template('index.html', top_translations=None, message=message)

if __name__ == '__main__':
    app.run(debug=True)