from datetime import datetime
from zoneinfo import ZoneInfo
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

# Названия месяцев на русском
MONTHS = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}

def get_current_activity(now_time: datetime) -> str:
    """Определяет текущее событие по режиму дня «Орловчанки»"""
    minutes_now = now_time.hour * 60 + now_time.minute

    # Переводим расписание в минуты от начала дня
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
    """Формирует текст сообщения с датой, временем и статусом"""
    # Получаем текущее время по МСК (UTC+3)
    msk_time = datetime.now(ZoneInfo("Europe/Moscow"))
    
    day = msk_time.day
    month = MONTHS[msk_time.month]
    year = msk_time.year
    time_str = msk_time.strftime("%H:%M:%S")

    activity = get_current_activity(msk_time)

    text = (
        f"🕒 **Текущее время (МСК):**\n"
        f"📅 **Дата:** {day} {month} {year} года\n"
        f"⏰ **Время:** `{time_str}`\n\n"
        f"{activity}\n\n"
        f"🔄 *Нажми кнопку ниже, чтобы обновить секундную стрелку!*"
    )
    return text

def get_refresh_keyboard() -> InlineKeyboardMarkup:
    """Кнопка для обновления данных"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Обновить данные", callback_data="refresh_data")]
        ]
    )

# Команда /time или сообщение "Время"
@router.message(F.text.in_({"/time", "🕒 Время", "время", "Время"}))
async def send_time_info(message: Message):
    await message.answer(
        text=build_status_text(),
        parse_mode="Markdown",
        reply_markup=get_refresh_keyboard()
    )

# Обработчик нажатия на кнопку "Обновить данные"
@router.callback_query(F.data == "refresh_data")
async def refresh_time_handler(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            text=build_status_text(),
            parse_mode="Markdown",
            reply_markup=get_refresh_keyboard()
        )
        # Всплывающее уведомление над кнопкой
        await callback.answer("Данные обновлены! ✅", show_alert=False)
    except Exception:
        # Исключение срабатывает, если текст сообщения не изменился (нажали в ту же секунду)
        await callback.answer("Время уже актуально! ⚡", show_alert=False)
