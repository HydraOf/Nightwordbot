import random
from aiogram import Bot, Dispatcher, types
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.filters import Command

from config import BOT_TOKEN, ADMIN_ID
from database import init_db, append_value, get_user_stats

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Запоминаем активные чаты: user_id → operator
active_chats = {}


# ------------------------ УТИЛИТЫ ------------------------
def get_support_phrase():
    with open("data/support_phrases.txt", "r", encoding="utf-8") as f:
        return random.choice(f.readlines()).strip()


end_chat_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Завершить общение ❌", callback_data="end_chat")]
    ]
)

rate_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="1", callback_data="rate_1"),
            InlineKeyboardButton(text="2", callback_data="rate_2"),
            InlineKeyboardButton(text="3", callback_data="rate_3"),
            InlineKeyboardButton(text="4", callback_data="rate_4"),
            InlineKeyboardButton(text="5", callback_data="rate_5"),
        ]
    ]
)


# ------------------------ START ------------------------
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(
        "🌙 Добро пожаловать в **Night Word**\n"
        "Тихое пространство для мыслей, поддержки и истории.\n\n"
        "Введи /help чтобы узнать все возможности."
    )


# ------------------------ HELP ------------------------
@dp.message(Command("help"))
async def help_cmd(message: types.Message):
    await message.answer(
        "🕯 **Список команд:**\n\n"
        "/help — описание всех функций\n"
        "/about — о проекте Night Word\n"
        "/thought — случайная мысль\n"
        "/quote — поддерживающая фраза\n"
        "/my_story — отправить свою историю\n"
        "/feel — оценить своё состояние\n"
        "/feedback — оставить отзыв\n"
        "/support — связь с поддержкой\n"
        "/human_support — общение с живым человеком\n\n"
        "/ai — AI-компаньон *(в разработке)*\n"
        "/ai_support — AI-поддержка *(в разработке)*"
    )


# ------------------------ ABOUT ------------------------
@dp.message(Command("about"))
async def about_cmd(message: types.Message):
    await message.answer(
        "🌘 **Night Word** — пространство, где каждый может поделиться собой.\n"
        "Мы создаём место истории, поддержки, мыслей и безопасного общения."
    )


# ------------------------ THOUGHT ------------------------
@dp.message(Command("thought"))
async def thought_cmd(message: types.Message):
    await message.answer("💭 Мысль дня:\n" + get_support_phrase())


# ------------------------ QUOTE ------------------------
@dp.message(Command("quote"))
async def quote_cmd(message: types.Message):
    await message.answer("✨ " + get_support_phrase())


# ------------------------ STORY ------------------------
@dp.message(Command("my_story"))
async def story_cmd(message: types.Message):
    await message.answer(
        "📝 Отправь свою историю одним сообщением.\n"
        "Мы сохраним её в тишине Night Word."
    )


# ------------------------ FEEL ------------------------
@dp.message(Command("feel"))
async def feel_cmd(message: types.Message):
    await message.answer("Как ты себя чувствуешь от 1 до 10?")
    # далее можно что-то добавить


# ------------------------ FEEDBACK ------------------------
@dp.message(Command("feedback"))
async def feedback_cmd(message: types.Message):
    await message.answer("✍ Напиши свой отзыв. Он важен.")


# ------------------------ SUPPORT ------------------------
@dp.message(Command("support"))
async def support_cmd(message: types.Message):
    await message.answer("Связь с поддержкой: @your_support_username")


# ------------------------ AI / AI_SUPPORT ------------------------
@dp.message(Command("ai"))
async def ai_cmd(message: types.Message):
    await message.answer("🤖 AI-компаньон пока находится в разработке.")


@dp.message(Command("ai_support"))
async def ai_s_cmd(message: types.Message):
    await message.answer("🤖 AI-поддержка скоро появится.")


# ------------------------ ЧЕЛОВЕК-ПОДДЕРЖКА ------------------------
@dp.message(Command("human_support"))
async def human_support(message: types.Message):
    user_id = message.from_user.id

    active_chats[user_id] = ADMIN_ID

    await message.answer(
        "🔗 Ты подключён к живому человеку.\n"
        "Можешь писать. Я передам сообщение оператору.",
        reply_markup=end_chat_kb,
    )

    await bot.send_message(
        ADMIN_ID,
        f"🟢 Новый диалог с пользователем {user_id}.",
    )


# ------------------------ ПЕРЕДАЧА СООБЩЕНИЙ ------------------------
@dp.message()
async def relay_messages(message: types.Message):
    user_id = message.from_user.id

    if user_id in active_chats:  # пользователь пишет оператору
        await bot.send_message(
            ADMIN_ID,
            f"Сообщение от {user_id}:\n{message.text}",
        )
        return

    if message.from_user.id == ADMIN_ID and message.reply_to_message:
        # оператор отвечает пользователю
        text = message.text
        reply_user = int(message.reply_to_message.text.split()[3])
        await bot.send_message(reply_user, "💬 Ответ оператора:\n" + text)


# ------------------------ ЗАВЕРШИТЬ ОБЩЕНИЕ ------------------------
@dp.callback_query(lambda c: c.data == "end_chat")
async def end_chat(call: types.CallbackQuery):
    user_id = call.from_user.id

    if user_id in active_chats:
        del active_chats[user_id]

    await call.message.answer(
        "❌ Общение завершено.\n\n"
        "Поставьте оценку:", reply_markup=rate_kb
    )


# ------------------------ ОЦЕНКА ------------------------
@dp.callback_query(lambda c: c.data.startswith("rate_"))
async def rating(call: types.CallbackQuery):
    user_id = call.from_user.id
    rating = call.data.split("_")[1]

    append_value(user_id, "ratings", rating)

    await call.message.answer("Спасибо! Напиши отзыв:")
    await call.answer()


# ------------------------ СТАРТ БОТА ------------------------
async def main():
    init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
