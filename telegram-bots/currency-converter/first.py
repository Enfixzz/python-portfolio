from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from dotenv import load_dotenv
import os
from aiogram.client.session.aiohttp import AiohttpSession

session = AiohttpSession(proxy='http://192.168.0.104:10809')
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN, session=session)
dp = Dispatcher()

# Текущие курсы (можно заменить на реальные из API)
RATES = {
    "USD": 100,
    "EUR": 110,
    "GBP": 130,
}

# Храним состояние: какую валюту выбрал пользователь
user_selected = {}


# Главное меню с кнопками выбора валюты
def get_menu_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💵 Доллар", callback_data="currency_USD"),
            InlineKeyboardButton(text="💶 Евро", callback_data="currency_EUR"),
        ],
        [
            InlineKeyboardButton(text="💷 Фунт", callback_data="currency_GBP"),
        ]
    ])
    return kb


# Клавиатура "Вернуться в меню"
def get_back_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="← Вернуться в меню", callback_data="back_to_menu")]
    ])
    return kb


@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Привет! Я конвертер валют.\n"
        "Выбери валюту, которую хочешь конвертировать в рубли:",
        reply_markup=get_menu_keyboard()
    )


@dp.callback_query()
async def button_click(query: types.CallbackQuery):
    user_id = query.from_user.id

    if query.data.startswith("currency"):
        currency = query.data.split("_")[1]
        user_selected[user_id] = currency

        await query.message.edit_text(
            f'Введи сумму в {currency} :',
            reply_markup=get_back_keyboard()
        )
    elif query.data == "back_to_menu":
         user_selected.pop(user_id, None)
         await query.message.edit_text(
            'Выбери валюту, которую хочешь конвертирвать в рубли:',
            reply_markup=get_menu_keyboard()
        )
    await query.answer()



@dp.message()
async def convert(message: types.Message):
        user_id = message.from_user.id

        if user_id not in user_selected:
            await message.answer('Сначала выбери валюту через /start')
            return
        currency = user_selected[user_id]

        try:
            amount = float(message.text.replace(',', '.'))
        except ValueError:
            await message.answer(f'Это не похоже на число. Введи сумму в {currency}:')
            return

        rate = RATES[currency]
        rub = amount * rate

        await message.answer(
            f'{amount:g} {currency} = {rub:g} RUB',
            reply_markup=get_back_keyboard()
        )



async def main():
    print("Бот конвертера запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
