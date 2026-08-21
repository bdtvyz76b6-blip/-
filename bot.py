import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message, 
    CallbackQuery, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardMarkup, 
    KeyboardButton
)

# ⚠️ Вставь сюда токен своего бота из @BotFather
BOT_TOKEN = "ВАШ_ТОКЕН_БOTA"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и роутера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Русские названия месяцев
MONTHS = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}

SCHEDULE_TEXT = """
⏰ **РЕЖИМ ДНЯ ДС «ОРЛОВЧАНКА»**

• 07:30 — Подъём, утренний туалет
• 07:45 — Зарядка
• 08:00–09:00 — Утренний туалет, уборка постели
• 🥣 09:00 — Завтрак
• 🌲 10:00–13:00 — Прогулки, кружки, мероприятия
• 🍲 13:00 — Обед
• 😴 14:00–16:00 — Тихий час
• 🍎 16:00 — Полдник
• 🎨 17:00–19:00 — Мероприятия, кружки, прогулки
• 🍝 19:00 — Ужин
• 🪩 20:00 — Дискотека / Фильмы
• 🥛 20:45 — Второй ужин
• 🕯 21:30 — Вечерний огонёк
• 🧼 22:00 — Подготовка ко сну
• 🌙 22:30 — Отбой

🩺 *Оздоровительные процедуры — по назначению врача.*
"""

# Главное меню (кнопки под строкой ввода)
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🕒 Время по МСК")],
        [KeyboardButton(text="📅 Весь режим дня")]
    ],
    resize_keyboard=True
)

def get_current_activity(now_time: datetime) -> str:
    """Сравнивает время со стендом Орловчанки"""
    minutes_now = now_time.hour * 60 + now_time.minute

    schedule = [
        (7*60 + 30, 7*60 + 45, "Подъём, утренний туалет 🌅"),
        (7*60 + 45, 8*60, "Зарядка 🤸"),
        (8*60, 9*60, "Утренний туалет, уборка постели 🧼"),
        (9*60, 10*60, "Завтрак 🥣"),
        (10*60, 13*60, "Прогулки, кружки, мероприятия 🌲"),
        (13*60, 14*60, "Обед 🍲"),
        (14*60, 16*60, "Тихий час 😴"),
        (16*60, 17*60, "Полдник 🍎"),
        (17*60, 19*60, "Мероприятия, кружки, прогулки 🎨"),
        (19*60, 20*60, "Ужин 🍝"),
        (20*60, 20*60 + 45, "Дискотека / Фильмы 🪩"),
        (20*60 + 45, 21*60 + 30, "Второй ужин 🥛"),
        (21*60 + 30, 22*60, "Вечерний огонёк 🕯"),
        (22*60, 22*60 + 30, "Подготовка ко сну 🧼"),
    ]

    for start, end, title in schedule:
        if start <= minutes_now < end:
            return f"📍 **Сейчас идёт:** {title}"
    
    return "🌙 **Сейчас:** Отбой и сон"

def build_status_text() -> str:
    """Генерирует плашку времени и статуса"""
    msk_time = datetime.now(ZoneInfo("Europe/Moscow"))
    
    day = msk_time.day
    month = MONTHS[msk_time.month]
    year = msk_time.year
    time_str = msk_time.strftime("%H:%M:%S")

    activity = get_current_activity(msk_time)

    return (
        f"🕒 **Текущее время (МСК):**\n"
        f"📅 **Дата:** {day} {month} {year} года\n"
        f"⏰ **Время:** `{time_str}`\n\n"
        f"{activity}\n\n"
        f"🔄 *Нажми кнопку ниже для обновления!*"
    )

def get_refresh_keyboard() -> InlineKeyboardMarkup:
    """Кнопка прямо под сообщением"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Обновить данные", callback_data="refresh_data")]
        ]
    )

# Хэндлер команды /start
@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Привет! Я бот-помощник смены ДС «Орловчанка». 🌲\n Выбирай нужный раздел на клавиатуре ниже:",
        reply_markup=main_kb
    )

# Хэндлер показа полного режима дня
@router.message(F.text.in_({"📅 Весь режим дня", "/schedule"}))
async def show_schedule(message: Message):
    await message.answer(SCHEDULE_TEXT, parse_mode="Markdown")

# Хэндлер показа времени по МСК
@router.message(F.text.in_({"🕒 Время по МСК", "/time", "Время", "время"}))
async def send_time_info(message: Message):
    await message.answer(
        text=build_status_text(),
        parse_mode="Markdown",
        reply_markup=get_refresh_keyboard()
    )

# Обработка нажатия на inline-кнопку "Обновить данные"
@router.callback_query(F.data == "refresh_data")
async def refresh_time_handler(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            text=build_status_text(),
            parse_mode="Markdown",
            reply_markup=get_refresh_keyboard()
        )
        await callback.answer("Обновлено! ✅")
    except Exception:
        await callback.answer("Время уже актуально! ⚡")

# Запуск бота
async def main():
    dp.include_router(router)
    # Пропуск накопленных апдейтов при выключенном боте
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
