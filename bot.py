import asyncio
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.enums import ChatMemberStatus
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

# 🔐 Токен і канал
TOKEN = '8375905059:AAFoEzuuBxEUtK-JsSda4cO1kw4xn8wvQog'
CHANNEL_ID = '@streets_wont_forget'

# ⚙️ Ініціалізація
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# 📌 Перевірка підписки
async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR]
    except Exception as e:
        print(f"Помилка перевірки підписки: {e}")
        return False

# 🎛 Клавіатура для підписки
subscribe_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🔔 Підписатися", url="https://t.me/streets_wont_forget")],
    [InlineKeyboardButton(text="🔍 Перевірити підписку", callback_data="check_subscription")]
])

# 🎮 Клавіатура трансляцій
match_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Полісся - Фіорентінат", callback_data="match1")],
    [InlineKeyboardButton(text="Шахтар - Серветтен", callback_data="match2")],
    [InlineKeyboardButton(text="Динамо Київ - Маккабі", callback_data="match3")]
])

# 🚀 Старт
@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        "Щоб отримати доступ до трансляцій, спочатку підпишіться на канал 👇",
        reply_markup=subscribe_keyboard
    )

# 🔍 Обробка перевірки підписки
@router.callback_query(F.data == "check_subscription")
async def check_subscription_handler(callback: CallbackQuery):
    user_id = callback.from_user.id

    if await check_subscription(user_id):
        await callback.message.delete()  # 🧹 Видаляємо стартове повідомлення
        await callback.message.answer("✅ Ви підписані! Оберіть матч для перегляду:", reply_markup=match_keyboard)
    else:
        await callback.message.answer("❌ Ви ще не підписані. Підпишіться та натисніть «Перевірити підписку» ще раз.")

    await callback.answer()

# 📺 Обробка вибору матчу
@router.callback_query(F.data.in_({"match1", "match2", "match3"}))
async def match_handler(callback: CallbackQuery):
    await callback.message.delete()  # 🧹 Видаляємо повідомлення з вибором матчів

    match_data = {
        "match1": "🏟 <b>🇺🇦Полісся - Фіорентінат🇮🇹</b>\n🕘 21:00\n📍 Прип'ять, Futbal Tatran Arena",
        "match2": "🏟 <b>🇺🇦Шахтар - Серветтен🇨🇭</b>\n🕘 21:00\n📍 Харків, Стадіон 'Віца'",
        "match3": "🏟 <b>🇺🇦Динамо Київ - Маккабі🇮🇱</b>\n🕘 21:00\n📍 Баскет-Тополя, TSC Arena"
    }

    stream_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Дивитися трансляцію", url="https://t.me/streets_wont_forget")],
        [InlineKeyboardButton(text="🔙 Повернутися", callback_data="back_to_matches")]
    ])

    await callback.message.answer(match_data[callback.data], reply_markup=stream_keyboard)
    await callback.answer()

# 🔙 Обробка повернення до вибору матчів
@router.callback_query(F.data == "back_to_matches")
async def back_handler(callback: CallbackQuery):
    await callback.message.delete()  # 🧹 Видаляємо повідомлення з трансляцією
    await callback.message.answer("⚽️ Оберіть матч для перегляду:", reply_markup=match_keyboard)
    await callback.answer()

# 🔄 Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())