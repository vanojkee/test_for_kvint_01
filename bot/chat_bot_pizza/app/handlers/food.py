from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

available_food_names = ["Пиццу", "Спагетти"]
available_food_sizes = ["Большую", "Маленькую"]
available_payment = ["Наличкой", "Безналом"]


class OrderFood(StatesGroup):
    waiting_for_food_name = State()
    waiting_for_food_size = State()
    waiting_for_payment = State()


async def food_start(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in available_food_names:
        keyboard.add(name)
    await message.answer("Выберите блюдо:", reply_markup=keyboard)
    await OrderFood.waiting_for_food_name.set()


async def food_chosen(message: types.Message, state: FSMContext):
    if message.text.title() not in available_food_names:
        await message.answer("Пожалуйста, выберите блюдо, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_food=message.text.title())

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for size in available_food_sizes:
        keyboard.add(size)
    await OrderFood.next()
    await message.answer("Теперь выберите размер порции:", reply_markup=keyboard)


async def food_size_chosen(message: types.Message, state: FSMContext):
    if message.text.title() not in available_food_sizes:
        await message.answer("Пожалуйста, выберите размер порции, используя клавиатуру ниже.")
        return
    await state.update_data(chosen_size=message.text.title())
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for method in available_payment:
        keyboard.add(method)
    await OrderFood.next()
    await message.answer("Теперь выберите способ оплаты:", reply_markup=keyboard)


async def payment_chosen(message: types.Message, state: FSMContext):
    if message.text.title() not in available_payment:
        await message.answer("Как вы будете оплачивать? Выберите способ, используя клавиатуру ниже.")
        return
    user_data = await state.get_data()
    await message.answer(f"Вы заказали {user_data['chosen_size']} {user_data['chosen_food']}, оплата"
                         f" {message.text.title()}.\n"
                         f"Спасибо за заказ!", reply_markup=types.ReplyKeyboardRemove())
    await state.finish()


def register_handlers_food(dp: Dispatcher):
    dp.register_message_handler(food_start, commands="food", state="*")
    dp.register_message_handler(food_chosen, state=OrderFood.waiting_for_food_name)
    dp.register_message_handler(food_size_chosen, state=OrderFood.waiting_for_food_size)
    dp.register_message_handler(payment_chosen, state=OrderFood.waiting_for_payment)
