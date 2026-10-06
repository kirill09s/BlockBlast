"""Telegram-бот для игры Block Blast Mini App.

Функционал:
- /start — предлагает варианты игры
- /play — начинает новую игру
- Поддержка Mini App (требует HTTPS)
- Возможность открыть HTML-файл в браузере

Переменные окружения:
  BOT_TOKEN   — токен от @BotFather
  WEBAPP_URL  — https-адрес, где лежит index.html (опционально)
"""
import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    WebAppInfo,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8752782918:AAGypTFZt74iVd_i2xtG-VL1u04GPyqS4Kc")
# WEBAPP_URL указывать только если есть HTTPS-доступ (для реального мини-приложения)
WEBAPP_URL = os.environ.get("WEBAPP_URL")  # Например: "https://block-blast.vercel.app"

dp = Dispatcher()

def get_start_keyboard() -> ReplyKeyboardMarkup:
    """
    Возвращает клавиатуру для /start:
    - Если есть рабочий WEBAPP_URL (HTTPS) — кнопка WebApp
    - Иначе — кнопка с ссылкой на HTML файл и текстовая инструкция
    """
    buttons = []

    # Вариант 1: Попытка открыть WebApp (может работать на некоторых устройствах)
    if WEBAPP_URL and WEBAPP_URL.startswith("https"):
        buttons.append([KeyboardButton(text="🎮 Открыть игру в Telegram", web_app=WebAppInfo(url=WEBAPP_URL))])

    # Всегда предоставляем вариант с HTML файлом (работает везде)
    buttons.append([KeyboardButton(text="📄 Получить HTML файл для браузера")])

    # Инструкция
    buttons.append([KeyboardButton(text="📚 Инструкция по деплою")])

    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_play_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура во время игры."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔄 Новая игра")],
            [KeyboardButton(text="◀️ В меню")],
        ],
        resize_keyboard=True,
    )


@dp.message(CommandStart())
async def start(message: Message) -> None:
    """Обработчик команды /start."""
    user = message.from_user
    text = (
        f"👋 Привет, {user.first_name}!\\n\\n"
        "🎮 **Block Blast** — это мини-приложение (Mini App) в Telegram.\n"
        "Ваша задача — ставить фигуры на поле 8×8 и собирать полные строки/столбцы.\n"
        "Заполненные линии исчезают, давая вам больше места и очки.\n\n"
        "Выберите, как хотите сыграть:\\n"
    )
    await message.answer(
        text,
        reply_markup=get_start_keyboard(),
        parse_mode="Markdown",
    )


@dp.message(Command("play"))
async def cmd_play(message: Message) -> None:
    """Обработчик команды /play — начинает новую игру."""
    # Можно здесь инициализировать состояние игры, если нужно
    await message.answer(
        "🔄 Начинаю новую игру...",
        reply_markup=get_play_keyboard(),
    )


@dp.message(Command("help"))
async def help_(message: Message) -> None:
    """Справка по игре."""
    await message.answer(
        "📖 **Как играть в Block Blast:**\\n"
        "1. Фигуры падают снизу\\n"
        "2. Перетащите фигуру на поле 8×8\\n"
        "3. Заполните всю строку или столбец — она исчезнет\\n"
        "4. Старайтесь набирать как можно больше очков\\n"
        "5. Игра заканчивается, когда не поместится ни одна фигура\\n\n"
        "/play — начать новую игру\\n"
        "/score — показать ваш счет",
    )


@dp.message(lambda m: m.text == "🎮 Открыть игру в Telegram")
async def open_webapp(message: Message) -> None:
    """Открыть игру через WebApp (требует HTTPS)."""
    if not WEBAPP_URL or not WEBAPP_URL.startswith("https"):
        await message.answer(
            "❌ WebApp недоступен: для работы нужна HTTPS-ссылка.\n"
            "Используйте вариант 'Получить HTML файл'.",
            reply_markup=get_start_keyboard(),
        )
        return

    await message.answer(
        "🎮 Открываю игру в Telegram...",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="◀️ В меню")]], resize_keyboard=True
        ),
    )
    # Здесь aiogram сам передаст обновление с WebApp-событием
    # Пользователю нажмут кнопку "Открыть", и Mini App запустится


@dp.message(lambda m: m.text == "📄 Получить HTML файл для браузера")
async def send_html_file(message: Message) -> None:
    """Отправка HTML-файла игры пользователю."""
    html_path = "/home/Kirill_Sechkin/Загрузки/Tgbot/index.html"
    try:
        with open(html_path, "rb") as f:
            html_content = f.read()
        await message.answer_document(
            document=html_content,
            filename="block_blast_mini_app.html",
            caption=(
                "📄 **Block Blast HTML файл**\\n\\n"
                "1. Откройте файл в браузере (нажмите кнопку 'Открыть в браузере' в Telegram)\\n"
                "2. Для лучшего опыта нажмите 'Добавить в домашний экран' (Add to Home Screen)\\n"
                "3. Теперь игра будет как независимое мини-приложение!\\n\\n"
                "🎯 Управление: перетаскивайте фигуры из нижней панели на игровое поле\\n"
                "🎯 Заполняйте строки и столбцы, чтобы их очистить\\n"
                "🎯 Играйте с любого устройства, где есть Telegram!"
            ),
            parse_mode="Markdown",
        )
    except FileNotFoundError:
        await message.answer(
            "❌ Файл index.html не найден. Убедитесь, что он находится в папке Tgbot.",
        )


@dp.message(lambda m: m.text == "📚 Инструкция по деплою")
async def deploy_instruction(message: Message) -> None:
    """Инструкция по Deploy бота с рабочим WebApp."""
    instruction = (
        "🚀 **Как сделать бота рабочим с других устройств (Mini App):**\\n\\n"
        "1. **Разверните сервер с index.html**:\\n"
        "   - Бесплатные варианты: PythonAnywhere, Render, Vercel, Netlify, Hostinger\\n"
        "   - Или оставьте сервер running на своем компьютере с публичным IP\\n\\n"
        "2. **Получите HTTPS-ссылку**:\\n"
        "   - На хостинге обычно дается бесплатный SSL-сертификат\\n"
        "   - Или используйте ngrok: `ngrok http 8000` (откроет https-туннель)\\n\\n"
        "3. **Установите переменную окружения WEBAPP_URL**:\\n"
        "   `export WEBAPP_URL=https://your-domain.com` или `WEBAPP_URL=https://abcd1234.ngrok.io`\\n\\n"
        "4. **Перезапустите бота**:\\n"
        "   `python3 bot.py`\\n\\n"
        "5. **Нажмите /start** в Telegram и нажмите '🎮 Открыть игру в Telegram'\\n\\n"
        "💡 **Совет**: Для теста можно использовать ngrok, но для постоянной работы "
        "рекомендуетсяDeploy на хостинг.\n"
    )
    await message.answer(instruction)


async def main() -> None:
    """Запуск бота."""
    logging.basicConfig(level=logging.INFO)
    bot = Bot(BOT_TOKEN)

    # Устанавливаем меню приложения с кнопкой "Играть" (если есть WebApp URL)
    if WEBAPP_URL and WEBAPP_URL.startswith("https"):
        try:
            await bot.set_chat_menu_button(
                menu_button=MenuButtonWebApp(text="Играть", web_app=WebAppInfo(url=WEBAPP_URL))
            )
            logging.info(f"Set web app menu button with URL: {WEBAPP_URL}")
        except Exception as e:
            logging.warning(f"Could not set web app menu: {e}")

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")