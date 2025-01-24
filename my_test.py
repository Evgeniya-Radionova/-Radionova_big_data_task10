from flask import Flask, render_template, request
from fuzzywuzzy import fuzz, process
import sqlite3

app = Flask(__name__)


# Функция для получения данных из таблицы glossary
def get_glossary():
    conn = sqlite3.connect("translations.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM glossary")
    glossary = cursor.fetchall()
    conn.close()
    return glossary


# Функция для получения данных из таблицы sentence_translation
def get_sentence_translations():
    conn = sqlite3.connect("translations.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sentence_translation")
    translations = cursor.fetchall()
    conn.close()
    return translations


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action_type = request.form["action_type"]

        if action_type == "translate_sentence":
            text_input = request.form["text_input"]
            # Перевод предложения
            glossary = get_glossary()
            sentence_translation = get_sentence_translations()

            # Фильтрация слов: пропуск коротких слов (например, 'I', 'a', 'of' и т.д.)
            words = text_input.split()
            matched_words = []
            for word in words:
                # Фильтрация слов длиной меньше 2 символов (можно настраивать порог)
                if len(word) < 2:
                    continue

                # Находим лучший перевод из глоссария для каждого слова
                best_match = process.extractOne(word, [entry[1] for entry in glossary])
                if best_match and best_match[1] > 80:  # Порог схожести
                    # Получаем перевод соответствующего слова
                    english_word = best_match[0]
                    russian_translation = next(
                        (entry[2] for entry in glossary if entry[1] == english_word),
                        None,
                    )
                    matched_words.append(
                        (word, english_word, russian_translation, best_match[1])
                    )

            # Поиск наиболее похожих предложений и получение переводов
            # Список для хранения наиболее похожих переводов
            top_translations = []

            # Процесс нахождения наиболее похожих предложений и их переводов
            for entry in sentence_translation:
                # Сравниваем введённый текст с английским предложением
                score = fuzz.ratio(text_input, entry[1])
                top_translations.append(
                    (score, entry[1], entry[2])
                )  # Добавляем в список кортеж с оценкой, английским и русским переводом

            # Сортируем по оценке сходства (в убывающем порядке)
            top_translations.sort(reverse=True, key=lambda x: x[0])

            # Отбираем 3 наиболее похожих перевода
            top_translations = top_translations[:3]

            # Отправляем результат в шаблон
            return render_template(
                "index.html",
                text_input=text_input,
                matched_words=matched_words,
                best_matches=top_translations,
                glossary=glossary,
            )
        
        elif action_type == "translate_word":
            word_input = request.form["word_input"]
            glossary = get_glossary()
            best_match = process.extractOne(
                word_input, [entry[1] for entry in glossary]
            )

            if best_match and best_match[1] > 80:
                for entry in glossary:
                    if entry[1] == best_match[0]:
                        word_translation = (entry[1], entry[2])
                        return render_template(
                            "index.html", word_translation=word_translation
                        )
            else:
                sentence_translation = get_sentence_translations()
                top_sentences = []
                for entry in sentence_translation:
                    score = fuzz.partial_ratio(word_input.lower(), entry[1].lower())
                    if score > 50:
                        top_sentences.append((score, entry[1], entry[2]))

                top_sentences.sort(reverse=True, key=lambda x: x[0])
                top_sentences = top_sentences[:3]

                return render_template(
                    "index.html", word_input=word_input, top_sentences=top_sentences
                )

        elif action_type == "add_word_translation":
            english_word = request.form["english_word"]
            russian_word = request.form["russian_word"]

            conn = sqlite3.connect("translations.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO glossary (english_word, russian_word) VALUES (?, ?)",
                (english_word, russian_word),
            )
            conn.commit()
            conn.close()

            return render_template(
                "index.html", success_message="Слово добавлено в глоссарий!"
            )

        elif action_type == "sentence_translate":
            english_sentence = request.form["english_sentence"]
            russian_sentence = request.form["russian_sentence"]

            conn = sqlite3.connect("translations.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sentence_translation (english_sentence, russian_sentence) VALUES (?, ?)",
                (english_sentence, russian_sentence),
            )
            conn.commit()
            conn.close()

            return render_template("index.html", success_message="Перевод сохранён!")

        elif action_type == "load_translation_for_editing":
            translation_id = request.form["translation_id"]

            try:
                translation_id = int(translation_id)
                conn = sqlite3.connect("translations.db")
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM sentence_translation WHERE id = ?", (translation_id,)
                )
                translation = cursor.fetchone()
                conn.close()

                if translation:
                    return render_template(
                        "index.html",
                        translation_to_edit=translation,
                        sentence_translations=get_sentence_translations(),
                    )
                else:
                    return render_template(
                        "index.html",
                        error_message="Перевод с таким ID не найден.",
                        sentence_translations=get_sentence_translations(),
                    )
            except ValueError:
                return render_template(
                    "index.html",
                    error_message="Некорректный ID. Введите число.",
                    sentence_translations=get_sentence_translations(),
                )

        elif action_type == "update_translation":
            translation_id = int(request.form["translation_id"])
            updated_english = request.form["updated_english"]
            updated_russian = request.form["updated_russian"]

            conn = sqlite3.connect("translations.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE sentence_translation SET english_sentence = ?, russian_sentence = ? WHERE id = ?",
                (updated_english, updated_russian, translation_id),
            )
            conn.commit()
            conn.close()

            return render_template(
                "index.html",
                success_message="Перевод обновлен!",
                sentence_translations=get_sentence_translations(),
            )

    return render_template(
        "index.html", sentence_translations=get_sentence_translations()
    )


if __name__ == "__main__":
    app.run(debug=True)
