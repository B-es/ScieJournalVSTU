# Юнит-тесты бэкенда

## Требуемые библиотеки

- `pytest` — запуск и удобное описание тестов;
- `pytest-django` — тестовая база данных, фикстуры и интеграция pytest с Django;
- `pytest-cov` — отчёт о покрытии кода.

Основные зависимости проекта также устанавливаются автоматически через
`requirements-test.txt`.

## Установка

Из корня проекта:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r backend/requirements-test.txt
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r backend/requirements-test.txt
```

## Один общий запуск

Из корня проекта:

```bash
python backend/run_tests.py
```

Скрипт сам переходит в каталог бэкенда, запускает все тесты и печатает
покрытие. Аргументы pytest тоже поддерживаются:

```bash
python backend/run_tests.py -x
python backend/run_tests.py -k citation
```

Альтернативный запуск из каталога `backend`:

```bash
pytest
```

Тесты используют временную SQLite-базу и временный каталог для загружаемых
файлов. Для изоляции юнит-тестов таблицы создаются по текущим Django-моделям
без применения исторических миграций. Рабочая база и файлы проекта не
изменяются.
