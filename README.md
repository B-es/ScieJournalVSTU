# Научный журнал ВолгГТУ (ScieJournalVSTU)

Платформа управления научным журналом: подача статей авторами, проверка комплектности и тематики, рецензирование, редакционные решения, публикация с DOI и публичный сайт открытого доступа (Open Access).

Полная постановка задачи — в `specification/` (`PRD.md`, `TS.md`, `DS.md`).

## Стек

| Слой | Технологии |
|---|---|
| Backend | Python 3.12, Django 5.1, Django REST Framework, SimpleJWT |
| Frontend | Nuxt 3 (SSR), Vue 3, Pinia, @nuxtjs/i18n |
| БД | SQLite (по умолчанию для локальной разработки) / PostgreSQL (docker-compose, продакшен) |
| Файлы | Django `FileField`/`ImageField`, локальное хранилище `media/` |

## Архитектура

### Backend (`backend/`)

Django-проект `config/` + набор приложений в `apps/`, каждое — одна предметная область:

| Приложение | Отвечает за |
|---|---|
| `users` | Кастомная модель `User` (логин по email, UUID PK), роли (`author`, `reviewer`, `chief_editor`, `tech_editor`) через M2M `Role`/`UserRole`, JWT-аутентификация, регистрация/логин/refresh |
| `articles` | Модель `Article` (7 статусов: `draft` → `submitted` → `needs_revision`/`rejected`/`in_review` → `accepted` → `published`), версии рукописи (`ArticleVersion`), соавторы (`ArticleAuthor`), сопроводительные документы (`ArticleDocument`); вся бизнес-логика жизненного цикла статьи — в `services.py` |
| `reviews` | Назначение рецензентов, приглашения (принять/отклонить), форма рецензии |
| `editorial` | История редакционных решений (`EditorialDecision`) на всех этапах (проверка комплектности, тематики, итоговое решение) |
| `issues` | Выпуски журнала (`Issue`) — номер, год, обложка, публикация |
| `notifications` | Модель уведомлений (см. «Известные ограничения» — API поверх неё не реализовано) |
| `journal_settings` | Синглтон настроек журнала (название, ISSN, текст «О журнале», редколлегия, требования к авторам) — редактируется только через Django Admin |
| `public` | Публичный read-only API без авторизации: списки/поиск опубликованных статей, выпуски, экспорт библиографической ссылки, настройки журнала |

**Архитектурный паттерн статусной модели**: набор статусов статьи закрытый (7 значений), намеренно не расширяется под каждый под-этап процесса. Разные подсостояния одного статуса (например, «отправлена и ждёт проверки комплектности» vs «прошла комплектность и ждёт проверки тематики» — оба формально `submitted`) различаются через вспомогательные nullable-поля (`completeness_approved_at`, `published_at`) или через наличие/отсутствие связанных объектов (`Review`).

**Паттерн бизнес-логики**: каждое действие редактора (одобрить, вернуть на доработку, отклонить, присвоить DOI, опубликовать) — отдельная функция в `apps/<app>/services.py`, вызываемая из двух мест: REST-эндпоинта (для API) и action'а Django Admin (для технического редактора, у которого по ТЗ нет личного кабинета — весь его флоу через `/admin`).

**Публичный API** (`apps/public/`) — единственное место с `AllowAny`, всё остальное по умолчанию требует JWT (`DEFAULT_PERMISSION_CLASSES = IsAuthenticated` в `config/settings.py`). Доступ по ролям — через `apps/users/permissions.py::HasRole`.

Полная карта API-эндпоинтов — `backend/config/urls.py` и `urls.py` каждого приложения:
```
/api/auth/{register,login,logout,refresh,password-reset,me}
/api/users/reviewers
/api/articles/{draft,"",<id>,<id>/submit,<id>/versions,<id>/completeness-check,
                <id>/topic-check,<id>/reviewers,<id>/decision,<id>/doi,<id>/publish}
/api/reviews/{"",<id>/respond,<id>/reassign,<id>/submit}
/api/issues/  (POST — создание выпуска техредом)
/api/public/{articles,articles/<id>,articles/<id>/citation,issues,issues/<id>,settings}
```

### Frontend (`frontend/`)

Nuxt 3 (SSR включён по умолчанию — нужен для индексируемости публичных страниц). Файловая маршрутизация в `src/pages/`:

```
pages/
├── index.vue, archive/, article/[id].vue, search.vue,   # публичный Open Access сайт
│   about.vue, for-authors.vue                            # (без авторизации)
├── login.vue, register.vue
└── cabinet/                                              # личный кабинет (после входа)
    ├── author/            # подача статьи, мои статьи
    ├── reviewer/          # приглашения, рецензирование
    └── chief-editor/      # проверка тематики, приглашения, решения
```

Два layout'а (`src/layouts/`): `public.vue` (шапка/подвал для гостя) и `cabinet.vue` (боковое меню для авторизованных). У технического редактора личного кабинета нет — его интерфейс полностью в Django Admin.

Состояние — Pinia (`src/stores/`, ключевое — `auth.ts`: JWT в cookie, автообновление токена при 401). Запросы к API — тонкая обёртка `src/api/http.ts` (`apiFetch`), поверх неё — по одному файлу на предметную область в `src/api/` (`articles.ts`, `public.ts`, `reviews.ts`, `auth.ts`).

Локализация — `@nuxtjs/i18n`, `src/i18n/locales/{ru,en}.json`, переключение без потери контекста (`strategy: "no_prefix"`), контент статей/выпусков хранится билингвально в БД (`title_ru`/`title_en` и т.д.), а не переводится на лету.

## Как запустить локально

### Требования
- Python 3.12
- Node.js 20+ (соответствует версии, под которую собран `frontend/node_modules`)
- venv уже создан в корне репозитория (`venv/`); если его нет — `python -m venv venv`

### Backend

```bash
cd backend
../venv/Scripts/activate          # Windows; на Linux/macOS — source ../venv/bin/activate
pip install -r requirements.txt   # если venv свежий
cp .env.example .env              # локальные настройки (DEBUG=True, SQLite)
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

По умолчанию (`DATABASE_URL` не задан) используется SQLite (`backend/db.sqlite3`) — БД для разработки создаётся автоматически при первой миграции. Роли (`author`/`reviewer`/`chief_editor`/`tech_editor`) сеются миграцией `apps/users/migrations/0002_seed_roles.py` — руками создавать не нужно.

Для собственного администратора:
```bash
python manage.py createsuperuser
```
Django Admin — `http://127.0.0.1:8000/admin`. Роль пользователю назначается там же (`Users → выбрать пользователя → Roles`), либо через `POST /api/auth/register` + ручное добавление роли из админки (эндпоинт регистрации не принимает роль извне).

**Важно**: без `.env` (`DEBUG=False` по умолчанию) Django не отдаёт `media/` — все PDF статей и обложки выпусков будут 404. Для локальной разработки `.env` обязателен.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Открыть `http://localhost:3000`. Адрес backend API захардкожен в `nuxt.config.ts` (`runtimeConfig.public.apiBase = "http://127.0.0.1:8000/api"`) — при разворачивании на другом хосте поменять там же или вынести в `NUXT_PUBLIC_API_BASE`.

Полезные команды:
```bash
npm run lint            # ESLint
npx nuxi typecheck       # проверка типов (vue-tsc)
npm run build            # прод-сборка (SSR)
```

### Docker (только backend + PostgreSQL)

```bash
docker compose up --build
```

Поднимает `db` (Postgres 16) и `backend` (Django dev-сервер, не production WSGI-сервер — см. ограничения ниже). **Frontend в docker-compose не описан** — запускать отдельно через `npm run dev`/`npm run build && npm run preview`.

## Роли и доступ

| Роль | Личный кабинет | Основные действия |
|---|---|---|
| Автор (`author`) | `/cabinet/author/*` | Подача/черновики статей, загрузка исправленных версий |
| Рецензент (`reviewer`) | `/cabinet/reviewer/*` | Приглашения, форма рецензии |
| Главный редактор (`chief_editor`) | `/cabinet/chief-editor/*` | Проверка тематики, назначение рецензентов, итоговое решение |
| Технический редактор (`tech_editor`) | нет (по ТЗ) — только `/admin` | Проверка комплектности, присвоение DOI, публикация в выпуске, создание выпусков |
| Гость (не авторизован) | — | Публичный сайт: главная, архив, поиск, страница статьи, «О журнале», «Требования к авторам» |

## Известные ограничения (честно, для следующего разработчика)

Функционально весь цикл US-1…US-12 из `PRD.md` §4 реализован end-to-end, но по критериям приёмки самого проекта (`TS.md` §13, §16) есть незакрытые пункты:

- **Автотестов нет.** Всё проверялось вручную (curl-сценарии + Playwright из отдельного scratchpad, не входящего в репозиторий) на каждом модуле. `TS.md` §13 требует pytest/Vitest/Playwright с покрытием ≥70% — этого нет.
- **Модуль уведомлений — только модель**, без `views.py`/`serializers.py`/API. Счётчик непрочитанных в шапке кабинета — статичная заглушка (`stores/notifications.ts`).
- **Восстановление пароля не работает.** `PasswordResetView` валидирует email и всегда отвечает 200, реального письма не отправляет (email вообще нигде не настроен, `EMAIL_BACKEND` не задан).
- **DOI — сгенерированная заглушка** (`10.36622/vstu.<год>.<hex>`), не интеграция с CrossRef/НЭИКОН — осознанное временное решение, разрешённое `PRD.md` §8.
- **Нет CI/CD**, `docker-compose.yml` — только dev-сервер Django (не gunicorn/uvicorn) + Postgres, без Nginx и без сервиса фронтенда.
- **Sitemap/robots.txt не генерируются** (SSR по умолчанию включён, базовая индексируемость есть, но `PRD.md` §6 требует генерацию sitemap явно).
- Rate limiting на публичных эндпоинтах и антивирус-проверка загружаемых файлов — не реализованы (в `TS.md` §12 отмечены как готовые).

## Структура репозитория

```
backend/            Django-проект (см. выше)
frontend/            Nuxt3-проект (см. выше)
specification/       PRD.md, TS.md, DS.md — исходная постановка задачи
docs/, about/, prototype/   вспомогательные материалы (процессы, BPMN, ранние прототипы)
docker-compose.yml   Postgres + Django (dev-режим)
```
