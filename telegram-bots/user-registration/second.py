from aiogram import Bot, Dispatcher, types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import asyncio
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.utils.keyboard import InlineKeyboardBuilder

# БД
engine = create_engine("sqlite:///users.db")
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True)
    name = Column(String)
    age = Column(Integer)


Base.metadata.create_all(engine)


# FSM
class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    confirmation = State()


# Бот
session_proxy = AiohttpSession(proxy='http://192.168.0.104:10809')

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, session=session_proxy)
dp = Dispatcher()
router = Router()


def add_user(user_id, name, age):
    with Session(engine) as session:
        user = User(
            user_id=user_id,
            name=name,
            age=age
        )
        session.add(user)
        session.commit()


def get_user(user_id):
    with Session(engine) as session:
        return session.query(User).filter_by(user_id=user_id).first()


@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    user = get_user(message.from_user.id)

    if user:
        await message.answer(
            f"Добро пожаловать обратно, {user.name}! 🎉"
        )
        return

    await message.answer("Привет! Как тебя зовут?")
    await state.set_state(RegistrationStates.waiting_for_name)


@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)

    await message.answer("Сколько тебе лет?")
    await state.set_state(RegistrationStates.waiting_for_age)


@router.message(RegistrationStates.waiting_for_age)
async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Возраст должен быть числом.")
        return

    age = int(message.text)

    await state.update_data(age=age)
    data = await state.get_data()

    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Да", callback_data="confirm_yes")
    builder.button(text="❌ Нет", callback_data="confirm_no")

    await message.answer(
        f"Имя: {data['name']}\n"
        f"Возраст: {age}\n\n"
        "Всё верно?",
        reply_markup=builder.as_markup()
    )

    await state.set_state(RegistrationStates.confirmation)


@router.callback_query(F.data.in_(["confirm_yes", "confirm_no"]))
async def process_confirmation(query: types.CallbackQuery, state: FSMContext):
    if query.data == "confirm_yes":
        data = await state.get_data()

        add_user(
            query.from_user.id,
            data["name"],
            data["age"]
        )

        await state.clear()

        await query.message.edit_text(
            "🎉 Регистрация успешно завершена!"
        )

    else:
        await state.clear()
        await query.message.edit_text(
            "Хорошо, начнем сначала.\n\nКак тебя зовут?"
        )
        await state.set_state(RegistrationStates.waiting_for_name)

    await query.answer()


dp.include_router(router)


async def main():
    print("Бот регистрации запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())