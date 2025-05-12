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
from aiogram import F

logging.basicConfig(level=logging.INFO)

API_TOKEN = '7579489878:AAGY0EHYu8zcHHBAPbHb-E1itOvvisNDj5o'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

languyage = 'pl' #pl ja
users_settings = {}


conversation_history = {}

def trim_history(history, max_length=4096):
    current_length = sum(len(message["content"]) for message in history)
    while history and current_length > max_length:
        removed_message = history.pop(0)
        current_length -= len(removed_message["content"])
    return history

def text_to_speech(text):
    res = gTTS(text=text, lang=languyage) 
    filename = "output.mp3"
    res.save(filename)

def audio_to_text(audio):
    r = sr.Recognizer()
    message = sr.AudioFile(audio)
    with message as source:
        audio = r.record(source)
    result = r.recognize_google(audio, language="ru_RU")
    return result

@dp.message(Command("start"))
async def start_change(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_settings:
        users_settings[user_id] = {'audioanswers': True, 'base_bot_settings': ''}
    if user_id not in conversation_history:
        conversation_history[user_id] = []


@dp.message(F.text.startswith('/set'))
async def settt(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_settings:
        users_settings[user_id] = {'audioanswers': True, 'base_bot_settings': ''}
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    user_id = message.from_user.id
    botset = message.text.replace(message.text.split()[0],'').strip()
    users_settings[user_id]['base_bot_settings'] = botset
    await message.reply(f'Настройка бота установлена: {botset}')


@dp.message(Command("audio"))
async def audio_change(message: types.Message):
    user_id = message.from_user.id
    
    if user_id not in users_settings:
        users_settings[user_id] = {'audioanswers': True, 'base_bot_settings': ''}
    if user_id not in conversation_history:
        conversation_history[user_id] = []


    if users_settings[user_id]['audioanswers']:
        users_settings[user_id]['audioanswers'] = False
        await message.reply("Аудиоответы отключены")
    else:
        users_settings[user_id]['audioanswers'] = True
        await message.reply("Аудиоответы включены")

    print(users_settings[user_id]['audioanswers'])

@dp.message(Command("clear"))
async def process_clear_command(message: types.Message):
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    user_id = message.from_user.id
    conversation_history[user_id] = []
    await message.reply("История очищена")

@dp.message()
async def baza(message: types.Message):

    user_id = message.from_user.id

    if user_id not in conversation_history:
        conversation_history[user_id] = []
    if user_id not in users_settings:
        users_settings[user_id] = {'audioanswers': True, 'base_bot_settings': ''}
    
    if message.content_type == ContentType.VOICE:
        try:
            file_id = message.voice.file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path
            await bot.download_file(file_path, "input.oga")
            print(file_path)
            process = subprocess.run(['ffmpeg', '-i', 'input.oga', 'outp.wav'],shell=True)

            audio = os.path.join(os.path.dirname(os.path.realpath(__file__)), "outp.wav")
            user_input = audio_to_text(audio)
            print(user_input)
            try:
                os.remove('input.oga')
                os.remove('outp.wav')
            except:
                pass
        except:
            try:
                os.remove('input.oga')
                os.remove('outp.wav')
            except:
                pass
            await message.answer('Произошла ошибка, но это не важно')
            return
    else:
        user_input = message.text

    conversation_history[user_id].append({"role": "user", "content": user_input})
    conversation_history[user_id] = trim_history(conversation_history[user_id])

    chat_history = conversation_history[user_id][:]
    chat_history.insert(0,{"role": "system", "content": users_settings[user_id]['base_bot_settings']})

    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.blackboxai,
            messages=chat_history,
        )
        chat_gpt_response = response
    except Exception as e:
        await message.reply(f"{str(g4f.Provider.__name__)}: {e}")
        chat_gpt_response = "Извините, произошла ошибка."

    conversation_history[user_id].append({"role": "assistant", "content": chat_gpt_response})
    print(conversation_history)
    length = sum(len(message["content"]) for message in conversation_history[user_id])
    print(length)

    if users_settings[user_id]['audioanswers']:
        text_to_speech(chat_gpt_response.replace('*','').replace('\\n','').replace('#',''))
        audio_file = FSInputFile("output.mp3")
        await message.answer_voice(voice=audio_file)
    else:
        await message.answer(chat_gpt_response)



async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
