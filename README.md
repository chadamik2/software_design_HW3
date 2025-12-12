# Система «Антиплагиат» для НИУ ВШЭ
- Учебный проект по конструированию ПО на Python
- Цель: смоделировать микросервисную архитектуру серверной части веб-приложения для определения раабот на плагиат
  
## Описание

Система предназначена для:
- хранения работ студентов (файлов) с фиксацией факта сдачи в СУБД
- анализа работ на заимствования (антиплагиат)
- предоставления преподавателю отчетов по контрольным работам
- визуализации текста работы в виде облака слов

## Инструкция по запуску

1. Убедитесь, что у вас установлен docker
```

docker --version

```

2. Скачайте репозиторий
```

git clone https://github.com/chadamik2/software_design_HW3.git
cd software_design_HW3/src

```

3. Запустите сервисы
```

docker compose up --build

````

4. Используйте http://localhost:8000/docs для работы микросервисов

## Архитектура

Система состоит из трёх микросервисов:

1. **API Gateway**
   - Принимает все входящие HTTP-запросы от клиентов
   - Обрабатывает загрузку работы (файл + метаданные)
   - Вызывает File Storing Service для сохранения файла
   - Вызывает File Analysis Service для анализа сохранённого файла
   - Предоставляет отчеты по работам для преподавателя
   - Реализует обработку ошибок при падении или недоступности одного из микросервисов

2. **File Storing Service**
   - Отвечает только за хранение файлов и метаданных о сдаче
   - Принимает файл, сохраняет его на файловую систему
   - Сохраняет информацию о сдаче в СУБД (SQLite): кто/когда/по какому заданию
   - Позволяет получать файл по `file_id`

3. **File Analysis Service**
   - Отвечает за анализ работ и выдачу отчетов
   - Получает от API Gateway информацию о новой сдаче и URL для скачивания файла
   - Скачивает файл из File Storing Service
   - Запускает алгоритм определения признаков плагиата
   - Формирует отчет и сохраняет его в своей БД (SQLite)
   - Предоставляет отчеты по всем сдачам для конкретной контрольной работы
   - Генерирует URL для облака слов с помощью сервиса quickchart.io

### User flow

#### Отправка работы студентом

1. Студент отправляет запрос `POST /api/works/submit` на API Gateway
2. API Gateway:
   - передает файл и метаданные в File Storing Service `POST /files/submit`
   - получает `submission_id` и `file_id`
   - формирует `file_download_url` и вызывает File Analysis Service `POST /internal/analyze`
   - возвращает клиенту комбинированный ответ (данные о сдаче + отчет)

#### Запрос аналитики преподавателем

1. Преподаватель отправляет запрос `GET /api/works/{assignment_id}/reports` на API Gateway
2. API Gateway обращается к File Analysis Service `GET /reports/assignment/{assignment_id}`
3. Клиент получает JSON-список отчетов с флагом плагиата и ссылками на облако слов

## Алгоритм определения плагиата

1. File Analysis Service скачивает содержимое файла по `file_download_url`
2. Из содержимого файла формируется строка (текст)
3. Вычисляется хэш содержимого: SHA-256 (`content_hash`)
4. В БД микросервиса Analysis хранятся отчеты с полями:
   - `assignment_id`
   - `student_id`
   - `submission_id`
   - `content_hash`
   - `is_plagiarism`
   - `plagiarism_source_submission_id`
5. Для новой сдачи:
   - выбираются все отчеты с тем же `assignment_id` и `content_hash`
   - из выборки исключаются отчеты того же `student_id`
   - если есть хотя бы одна более ранняя сдача другим студентом —
     новая сдача помечается как плагиат (`is_plagiarism = true`),
     а `plagiarism_source_submission_id` содержит идентификатор исходной сдачи
   - иначе `is_plagiarism = false`

Это соответствует простому варианту: плагиат присутствует, если существует более ранняя сдача
(другим студентом) присланной работы

## Визуализация в виде облака слов

Для визуализации текста работы используется внешний API:

- `https://quickchart.io/wordcloud?text=<URL-encoded text>`

File Analysis Service:
- формирует URL для облака слов на основе текстового представления файла
- хранит этот URL в отчетах
- отдаёт URL клиенту, который может открыть ссылку и увидеть PNG с облаком слов

## Синхронное межсервисное взаимодействие

- API Gateway синхронно обращается к File Storing Service и File Analysis Service
- File Analysis Service синхронно скачивает файл из File Storing Service по HTTP
- Ответ клиенту возвращается после завершения всех необходимых операций
  (либо после фиксации ошибки у одного из микросервисов)

## Обработка ошибок

- Если File Storing Service недоступен:
  - API Gateway возвращает ошибку 503 Service Unavailable
  - файл и метаданные не сохраняются, анализ не выполняется

- Если File Analysis Service недоступен:
  - API Gateway сохраняет файл через File Storing Service
  - возвращает клиенту сведения о сдаче и признак того, что анализ не выполнен

- Если File Analysis Service не может скачать файл (ошибка в File Storing Service):
  - анализ прерывается, формируется ошибка
  - клиенту возвращается соответствующий HTTP-статус и сообщение

## Контейнеризация

Каждый микросервис упакован в отдельный Docker-образ:
- `gateway/Dockerfile`
- `file_storage_service/Dockerfile`
- `file_analysis_service/Dockerfile`

Развёртывание всех сервисов осуществляется одной командой:

```bash
docker compose up --build
````

Для использования api методов используется
[http://localhost:8000/docs](http://localhost:8000/docs)

## Архитектура проекта

```
software_design_HW3/
├── README.md
├── .gitignore
└── src/
    ├── docker-compose.yml
    ├── gateway/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── app/
    │       ├── config.py
    │       ├── schemas.py
    │       ├── clients.py
    │       └── main.py
    ├── file_storage_service/
    │   ├── Dockerfile
    │   ├── requirements.txt
    │   └── app/
    │       ├── config.py
    │       ├── database.py
    │       ├── models.py
    │       ├── schemas.py
    │       └── main.py
    └── file_analysis_service/
        ├── Dockerfile
        ├── requirements.txt
        └── app/
            ├── config.py
            ├── database.py
            ├── models.py
            ├── schemas.py
            ├── plagiarism.py
            ├── wordcloud.py
            ├── services.py
            └── main.py

```
