import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import pandas as pd
from aiogram.types import InputFile 

from gg import find_recipients_by_sender, add_period_column, draw_graph

API_TOKEN = ''
with open('token.txt', 'r') as fd: # Получение токена для бота
   API_TOKEN = fd.readline()

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot,  storage=MemoryStorage())

df = pd.read_excel('d.xlsx')
df = add_period_column(df)


class Form(StatesGroup):
   name_send = State()
   second_name_send= State()
   adres_give = State()
   period = State()
   name_give = State()
   second_name_give = State()
   adres_send = State()
   al = State()

@dp.message_handler(state='*', commands='cancel')
@dp.message_handler(Text(equals='отмена', ignore_case=True), state='*')
async def cancel_handler(message: types.Message, state: FSMContext):
   current_state = await state.get_state()
   if current_state is None:
      return

   await state.finish()
   await message.reply('ОК')


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
   await message.answer("Привет! Какое имя у отправителя")
   await Form.name_send.set()

@dp.message_handler(state=Form.name_send)
async def process_name(message: types.Message, state: FSMContext):
   async with state.proxy() as data:
      data['name_send'] = message.text
   await Form.second_name_send.set()
   await message.answer("Какая у отправителя фамилия?")

@dp.message_handler(state=Form.second_name_send)
async def process_name(message: types.Message, state: FSMContext):
   async with state.proxy() as data:
      data['second_name_send'] = message.text
   await Form.adres_send.set()
   await message.answer("Город отправления?")

@dp.message_handler(state=Form.adres_send)
async def process_name(message: types.Message, state: FSMContext):
   async with state.proxy() as data:
      data['adres_send'] = message.text
   await Form.name_give.set()
   await message.answer("Какое имя у получателя")


@dp.message_handler(state=Form.name_give)
async def process_name(message: types.Message, state: FSMContext):
   async with state.proxy() as data:
      data['name_give'] = message.text
   await Form.second_name_give.set()
   await message.answer("Какая фамилия у получателя")

@dp.message_handler(state=Form.second_name_give)
async def process_name(message: types.Message, state: FSMContext):
   async with state.proxy() as data:
      data['second_name_give'] = message.text
   await Form.adres_give.set()
   await message.answer("Адрес получателя?")

@dp.message_handler(state=Form.adres_give)
async def process_name(message: types.Message, state: FSMContext):
   async with state.proxy() as data:
      data['adres_give'] = message.text
   await Form.period.set()
   markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
   markup.add("1891-1916", "1917-1940", '1941-1965', '1966-1985', '1986-1992', '1993-2014')
   await message.answer("Укажи временной период(кнопкой)", reply_markup=markup)




# Сохраняем пол, выводим анкету
@dp.message_handler(state=Form.period)
async def process_gender(message: types.Message, state: FSMContext):
   async with state.proxy() as data:
      data['period'] = message.text
      markup = types.ReplyKeyboardRemove()
      result = find_recipients_by_sender(
        df,
        sender_name=data['name_send'],
        sender_address=None,
        recipient_index=None,
        recipient_name=data['name_give'],
        recipient_address=data['adres_give'],
        period=None
        )
      await bot.send_message(message.chat.id, result)
      draw_graph(result, 'graph.png') # Рисуем граф
      graph = InputFile("graph.png")
      await bot.send_photo(chat_id=message.chat.id, photo=graph)
      await bot.send_message(
         message.chat.id,
         md.text(
            md.text('Имя отправителя', data['name_send']),
            md.text('Фамилия отправителя', data['second_name_send']),
            md.text('Адрес отправления', data['adres_send']),
            md.text('Имя получателя', data['name_give']),
            md.text('Фамилия получателя', data['second_name_give']),
            md.text('Адрес получения', data['adres_give']),
            md.text('Временной период', data['period']),
            sep='\n',
         ),
         reply_markup=markup,
         parse_mode=ParseMode.MARKDOWN,
      )

   await state.finish()



if __name__ == '__main__':
   executor.start_polling(dp, skip_updates=True)