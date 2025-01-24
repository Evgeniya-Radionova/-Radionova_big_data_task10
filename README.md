# Radionova_big_data_task10

## Приложение для перевода Trados с английского на русский
Это простое Flask приложение. **игрушечный Trados**, в котором можно вносить перевод предложения, слова, а также получить топ 3 перевода из базы данных. В нём можно вводить текст, сопоставлять его с глоссарием слов и базой данных переводов предложений, а также получать лучшие совпадения на основе оценок схожести.

### Возможности: 
1. **Перевод слов.** Вы можетет ввести слово и получить его лучшее совпадение из глоссария переводов. Если совпадение не найдено, будут предложены предложения с этим словом или похожим на него.

2. **Добавление перевода слов.** Вы можете ввести перевод вручную, если этого слова нет в глассарии и оно не встретилось в тексте.

3. **Перевод предложений.** Вы можете ввести целое предложение, и приложение предоставит лучшие совпадения переводов из базы данных предложений.

4. **Добавление перевода предложения.** Вы можете добавить перевод предложения в базу данных, еслипредложенные переводы вам не подходять.

5. **Редактирование переводов.** Если вы совершили ошибку при вводе перевода вручную, то его можно исправить, указав индекс этого предложения.

6. **Просмотр базы переводов.** Вы можете посмотреть все переводы предложений, которые есть в базе.


### Настройка базы данных
Не забудбте создать виртуальное окружение и установить все библиотеки через файл *requirements.txt*
>***pip install -r requirements.txt***

Также слоит учесть, что это приложение использует базу данных SQLite *translations.db* для хранения переводов слов и предложений. Скачайте её и добавьте в папку с кодом .py

База данных игрушечная, в глоссарии введены 50 слов английских слов и их переводов с буквы а.

В таблице переводов предложений введены первые 100 предложений из базы с этого сайта: https://tatoeba.org/ru/downloads

По факту их меньше, потому что в этих первых 100 файлах были повторы предложений на английском с немного отличающимися переводами на русский (I переводилось как Я и как МНЕ), и строки с повторами были удалены.

Полный файл *eng_rus_texts.tsv* с переводами предложений также прикрепляю для наглядности.

**Пути:**
>translation_app/                   # Корневая папка проекта
│-- .venv/                           # Виртуальное окружение
│-- app.py                            # Основной файл приложения Flask
│-- translations.db                    # База данных SQLite
│-- requirements.txt                   # Зависимости проекта
│-- static/                             # Статические файлы (CSS)
│   └-- styles.css                  # Стили для веб-интерфейса
│-- templates/                          # HTML-шаблоны приложения
│   └-- index.html                       # Главный шаблон интерфейса пользователя




### Как это работает?
**- Перевод слова.** Когда вводится слово, приложение пытается найти лучшее совпадение в глоссарии. Если оценка совпадения превышает заданный порог, возвращается перевод. В противном случае приложение ищет  предложения с этим словом в базе данных переводов предложений.

**- Добавление перевода слова.** Если в глоссарии нет искомого вами слова, то это слово и его перевод можно внести в глоссарий вручную.

**- Перевод предложения.** Когда вводится предложение, приложение разбивает его на отдельные слова и ищет лучшие совпадения в глоссарии если слова из предложения есть в глоссарии, то они выводятся вместе с переводом. Затем введённое предложение сравнивается с записями в таблице переводов предложений и возвращает 3 лучшие совпадения на основе схожести.

**- Добавление перевода предложения.** Если вам не понравились те предложения, которые вывелись, то можно добавить перевод искомого предложения в базу данных вручную. После добавления эти переводы будут доступны для будущих запросов. Все предложения в базе данных можно посмотреть после нажатия на кнопку "Посмотреть все переводы".

**- Редактирование переводов.** Вы можете заменить перевод любого из предложений, указав ID перевода. Приложение найдет перевод по ID и предложит возможность изменить английскую и русскую версии предложения.


## Комментарий
<ins>При желании данное приложение можн подстроить под любой язык, внося в базу данных глоссарий (переводы слов) и переводы предложений.</ins>
