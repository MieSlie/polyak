import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import FSInputFile, ContentType, File, Message
import g4f
import os
from gtts import gTTS
import speech_recognition as sr
import subprocess

from a import *




logging.basicConfig(level=logging.INFO)

API_TOKEN = '7579489878:AAGY0EHYu8zcHHBAPbHb-E1itOvvisNDj5o'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

baseSett = f"ты асистент"


conversation_history = {}

def trim_history(history, max_length=4096):
    current_length = sum(len(message["content"]) for message in history)
    while history and current_length > max_length:
        removed_message = history.pop(1)
        current_length -= len(removed_message["content"])
    return history


@dp.message(Command("start"))
async def start_change(message: types.Message):
    user_id = message.from_user.id
    if user_id not in conversation_history:
        conversation_history[user_id] = [{'role': 'system', 'content': baseSett}]



@dp.message(Command("clear"))
async def process_clear_command(message: types.Message):
    if user_id not in conversation_history:
        conversation_history[user_id] = [{'role': 'system', 'content': baseSett}]
    
    user_id = message.from_user.id
    conversation_history[user_id] = [{'role': 'system', 'content': baseSett}]
    await message.reply("История очищена")


@dp.message()
async def baza(message: types.Message):

    await message.answer('вижу')

    user_id = message.from_user.id

    if user_id not in conversation_history:
        conversation_history[user_id] = [{'role': 'system', 'content': baseSett}]
    
    user_input = message.text

    conversation_history[user_id].append({"role": "user", "content": user_input})
    #conversation_history[user_id] = trim_history(conversation_history[user_id])

    chat_history = conversation_history[user_id]

    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.gpt_4,
            messages=chat_history
        )
        chat_gpt_response = response
    except Exception as e:
        print(f"{g4f.Provider.__name__}:", e)
        chat_gpt_response = "Извините, произошла ошибка."

    conversation_history[user_id].append({"role": "assistant", "content": chat_gpt_response})
    print(conversation_history)
    length = sum(len(message["content"]) for message in conversation_history[user_id])
    print(length)

    await message.answer(chat_gpt_response)


   
    

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
