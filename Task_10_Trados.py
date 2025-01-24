from flask import Flask, render_template, request
from fuzzywuzzy import fuzz, process
import sqlite3

app = Flask(__name__)


# Определяем функцию для получения данных из таблицы "glossary" базы данных
def get_my_glossary()-> list[tuple[int, str, str]]:
    conn = sqlite3.connect("translations.db")  # Подключение к базе данных
    cursor = conn.cursor()  # Создание курсора для выполнения SQL-запросов
    cursor.execute(
        "SELECT * FROM glossary"
    )  # Запрос на получение всех записей из таблицы "glossary"
    my_glossary = cursor.fetchall()  # Для получения всех строк результата SQL-запроса
    conn.close()  # Закрываем соединение с базой данных
    return my_glossary  # Возвращаем список записей


# Функция для получения данных из таблицы sentence_translation
def get_sentence_translations()-> list[tuple[int, str, str]]:
    conn = sqlite3.connect("translations.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sentence_translation")
    translations = cursor.fetchall()
    conn.close()
    return translations


# Определяем маршрут главной страницы "/"
@app.route("/", methods=["GET", "POST"])  # Указываем, что маршрут поддерживает GET и POST запросы
def index(): # Обрабатывает действия пользователя (перевод текста, добавление слов, редактирование)
    if (request.method == "POST"):  # Проверяем, является ли запрос POST (данные отправлены пользователем)
        action_type = request.form["action_type"]  # Определяем тип действия из формы

        if action_type == "translate_sentence":  # Перевод предложения
            text_input = request.form["text_input"]  # Получаем введённое предложение
            my_glossary = get_my_glossary()  # Загружаем глоссарий из базы данных
            sentence_translation = get_sentence_translations()  # Загружаем переводы предложений

            # Фильтрация слов: пропуск коротких слов (например, 'I', 'a', 'of' и т.д.)
            words = text_input.split()  # Разделяем предложение на слова
            matched_words = []
            for word in words:
                # Фильтрация слов длиной меньше 2 символов (можно настраивать порог)
                if len(word) < 2:
                    continue

                # Находим лучший перевод из глоссария для каждого слова
                best_match = process.extractOne(
                    word, [entry[1] for entry in my_glossary]
                ) #Для сравнения строки со строками из списка используется модуль process, если нужен только первый, то extractOne
                if best_match and best_match[1] > 80:  # Порог схожести
                    # Получаем перевод соответствующего слова
                    english_word = best_match[0]  # Найденное слово на английском
                    russian_translation = next(
                        (entry[2] for entry in my_glossary if entry[1] == english_word),
                        None,
                    ) # Функция next() извлекает первый элемент из итерируемого объекта
                    matched_words.append(
                        (word, english_word, russian_translation, best_match[1])
                    )

            # Поиск наиболее похожих предложений и получение переводов
            # Список для хранения наиболее похожих переводов
            top_translations = []

            # Процесс нахождения наиболее похожих предложений и их переводов
            for entry in sentence_translation:
                # Сравниваем введённый текст с английским предложением
                score = fuzz.ratio(text_input, entry[1]) #Самое простое сравнение.
                top_translations.append(
                    (score, entry[1], entry[2])
                )  # Добавляем в список кортеж с оценкой, английским и русским переводом

            # Сортируем по оценке сходства (в убывающем порядке)
            top_translations.sort(reverse=True, key=lambda x: x[0])

            # Отбираем 3 наиболее похожих перевода
            top_translations = top_translations[:3]

            # Отправляем результат в шаблон
            return render_template( # Позволяет рендерить HTML-шаблон (вернуть результат, который отображается в браузере пользователя)
                "index.html",
                text_input=text_input,
                matched_words=matched_words,
                best_matches=top_translations,
                my_glossary=my_glossary,
            )

        elif action_type == "translate_word":
            word_input = request.form["word_input"]
            my_glossary = get_my_glossary()
            best_match = process.extractOne(
                word_input, [entry[1] for entry in my_glossary]
            ) # По улолчанию process.extract выодик 5 соответствий и % совпадения, для одного .extractOne

            if best_match and best_match[1] > 80:
                for entry in my_glossary:
                    if entry[1] == best_match[0]:
                        word_translation = (entry[1], entry[2])
                        return render_template(
                            "index.html", word_translation=word_translation
                        )
            else:
                sentence_translation = get_sentence_translations()
                top_sentences = []
                for entry in sentence_translation:
                    score = fuzz.partial_ratio(word_input.lower(), entry[1].lower()) # Частичное сравнение, этот вид во всей второй строке ищет совпадение с начальной
                    if score > 50:
                        top_sentences.append((score, entry[1], entry[2])) # Ищет слово вне его положения в предложении

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
                "index.html", success_message="Слово добавлено в глоссарий!",
            )

        elif action_type == "sentence_translate":
            english_sentence = request.form["english_sentence"]
            russian_sentence = request.form["russian_sentence"]

            conn = sqlite3.connect("translations.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sentence_translation (english_sentence, russian_sentence) VALUES (?, ?)",
                (english_sentence, russian_sentence),
            ) # Чтобы вставить данные в таблицу sentence_translation
            conn.commit()
            conn.close()

            return render_template("index.html", success_message="Перевод сохранён!")

        elif action_type == "load_translation_for_editing":
            translation_id = request.form["translation_id"]

            try:
                translation_id = int(translation_id) # Пытаемся преобразовать значение ID в целое число. Если пользователь ввёл нечисло, то произойдёт ошибка
                conn = sqlite3.connect("translations.db")
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM sentence_translation WHERE id = ?", (translation_id,)
                ) # Чтобы выбрать запись из таблицы sentence_translation, где ID совпадает с переданным.
                translation = cursor.fetchone()
                conn.close()

                if translation: # Проверяем, не пустой ли результат запроса, то есть найден липеревод с таким ID.
                    return render_template(
                        "index.html",
                        translation_to_edit=translation,
                        sentence_translations=get_sentence_translations(),
                    )
                else: # Если перевод с таким ID не найден в базе данных
                    return render_template(
                        "index.html", # Возвращаем шаблон с сообщением об ошибке:
                        error_message="Перевод с таким ID не найден.",
                        sentence_translations=get_sentence_translations(),
                    )
            except ValueError: # Если произошла ошибка при преобразовании ID в число
                return render_template(
                    "index.html", # Сообщение об ошибке при вводе некорректного ID
                    error_message="Некорректный ID. Введите число.",
                    sentence_translations=get_sentence_translations(),
                )

        elif action_type == "update_translation": # Опция обновления перевода
            translation_id = int(request.form["translation_id"]) # Озвлекаем ID перевода, который нужно обновить, и преобразуем его в целое число
            updated_english = request.form["updated_english"] # Получаем новое английское предложение.
            updated_russian = request.form["updated_russian"] # Получаем новый русский перевод.

            conn = sqlite3.connect("translations.db")
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE sentence_translation SET english_sentence = ?, russian_sentence = ? WHERE id = ?",
                (updated_english, updated_russian, translation_id),
            ) # Выполняем запрос на обновление перевода в базе данных
            conn.commit() # Подтверждаем изменения в базе данных
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
