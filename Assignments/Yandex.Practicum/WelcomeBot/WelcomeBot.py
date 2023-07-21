import logging
import os
import random

import freeGPT
import pyttsx3
import soundfile as sf
import speech_recognition as sr
from telegram import Update, constants
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler

from helpers import components, constants as const_text


class WelcomeBot:
    def __init__(self, TELEGRAM_API_KEY):
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)

        self.r = sr.Recognizer()
        self.app = Application.builder().token(TELEGRAM_API_KEY).build()

    async def handle_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_photo(
            photo=os.getcwd() + "//data//images//start.jpg",
            caption=const_text.REPLY_START,
            reply_markup=components.MENU_START_KB
        )

    async def handle_nextstep_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(const_text.REPLY_NEXT_STEP_TEXT)

    async def handle_github_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(const_text.REPLY_GITHUB_TEXT + const_text.GITHUB_LINK)

    async def menu_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        match query.data:
            case "PHOTO_1":
                await context.bot.send_chat_action(chat_id=query.message.chat_id,
                                                   action=constants.ChatAction.UPLOAD_PHOTO)
                await query.message.reply_photo(
                    photo=os.getcwd() + "\\data\\images\\selfie.png",
                    caption=const_text.CMD_PHOTO_SELFIE_DESC,
                    reply_markup=components.MENU_PHOTO_KB)
                await query.delete_message()
            case "PHOTO_2":
                await context.bot.send_chat_action(chat_id=query.message.chat_id,
                                                   action=constants.ChatAction.UPLOAD_PHOTO)

                await query.message.reply_photo(
                    photo=os.getcwd() + "//data//images//school.jpg",
                    caption=const_text.CMD_PHOTO_SCHOOL_DESC,
                    reply_markup=components.MENU_PHOTO_KB)
                await query.delete_message()

            case "VOICE_1":
                await context.bot.send_chat_action(chat_id=query.message.chat_id,
                                                   action=constants.ChatAction.RECORD_VOICE)
                await query.message.reply_voice(voice=open(os.getcwd() + "//data//voices//grandgpt.m4a", 'rb'),
                                                caption=const_text.CMD_VOICE_GRAND_GPT,
                                                reply_markup=components.MENU_VOICE_KB)
                await query.delete_message()
            case "VOICE_2":
                await context.bot.send_chat_action(chat_id=query.message.chat_id,
                                                   action=constants.ChatAction.RECORD_VOICE)
                await query.message.reply_voice(voice=open(os.getcwd() + "//data//voices//sql_nosql.m4a", 'rb'),
                                                caption=const_text.CMD_VOICE_SQL_NOSQL,
                                                reply_markup=components.MENU_VOICE_KB)
                await query.delete_message()
            case "VOICE_3":
                await context.bot.send_chat_action(chat_id=query.message.chat_id,
                                                   action=constants.ChatAction.RECORD_VOICE)
                await query.message.reply_voice(voice=open(os.getcwd() + "//data//voices//heartbreak.m4a", 'rb'),
                                                caption=const_text.CMD_VOICE_HEARTBREAK,
                                                reply_markup=components.MENU_VOICE_KB)
                await query.delete_message()

            case "BACK":
                await query.message.reply_text(text=const_text.CMD_BACK_TEXT, reply_markup=components.MENU_START_KB)

            case _:
                pass

    async def handle_voice_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await context.bot.send_chat_action(chat_id=update.message.chat_id,
                                           action=constants.ChatAction.TYPING)
        # Получаем объект аудио и скачиваем аудиофайл
        file_id = update.message.voice.file_id
        new_file = await context.bot.get_file(file_id)
        path = await new_file.download_to_drive()

        # Формируем пути для корректной работы методов из библиотеки soundfile
        oga_path = os.getcwd() + "\\" + str(path)
        wav_path = oga_path.replace(".oga", ".wav")

        # Конвертируем из oga (ogg) в wav, т.к. SpeechRecognition не умеет читать ogg
        data, samplerate = sf.read(oga_path)
        sf.write(wav_path, data, samplerate)

        with sr.AudioFile(wav_path) as source:
            audio = self.r.record(source)
        try:

            await context.bot.send_chat_action(chat_id=update.message.chat_id,
                                               action=constants.ChatAction.TYPING)
            # Распознаем речь с помощью Google Speech Recognition
            text = self.r.recognize_google(audio, language="ru-RU")

            # Если повезёт, то пользователю отправится шутка, шутки ради :)
            if random.choice(range(10)) % 10 == 0:
                joke = random.sample(const_text.REPLY_VOICE_JOKES).replace("@s", text)
                await update.message.reply_text(joke)

            # Используем бесплатную LLM из библиотеки freeGPT для генерации ответа
            resp = await getattr(freeGPT, "gpt3").Completion.create(text)

            await context.bot.send_chat_action(chat_id=update.message.chat_id,
                                               action=constants.ChatAction.RECORD_VOICE)
            # Генерируем голосовой ответ
            engine = pyttsx3.init()
            engine.save_to_file(resp, 'response_voice_message.ogg')
            engine.runAndWait()

            # Отправляем голосовой ответ пользователю
            await context.bot.send_chat_action(chat_id=update.message.chat_id,
                                               action=constants.ChatAction.UPLOAD_VOICE)
            await update.message.reply_voice(voice=open('response_voice_message.ogg', 'rb'),
                                             reply_to_message_id = update.message.message_id)
            os.remove(os.getcwd() + '\\response_voice_message.ogg')

        except sr.UnknownValueError:
            await update.message.reply_text("Не удалось распознать речь")
        except sr.RequestError as e:
            await update.message.reply_text("Ошибка сервиса распознавания речи: {0}".format(e))
            os.remove(oga_path)
            os.remove(wav_path)
        except freeGPT.gpt3.exceptions.RequestException as e:
            await update.message.reply_text("Сетевая ошибка : {0}".format(e))
        try:
            os.remove(oga_path)
            os.remove(wav_path)
        except OSError:
            pass

    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        match update.message.text:
            case const_text.CMD_START_MENU_PHOTO:
                await update.message.reply_photo(
                    photo=os.getcwd() + "//data//images//holder.jpg",
                    reply_markup=components.MENU_PHOTO_KB
                )
            case const_text.CMD_START_MENU_STORY:
                await update.message.reply_text(
                    text=const_text.REPLY_STORY_FULL,
                    reply_markup=components.BACK_TO_MENU
                )
            case const_text.CMD_START_MENU_VOICE:
                await update.message.reply_text(
                    text=const_text.CMD_VOICE_DESCRIPTION,
                    reply_markup=components.MENU_VOICE_KB
                )
            case const_text.CMD_START_MENU_VCHAT:
                await update.message.reply_text(
                    text=const_text.REPLY_VOICE,
                    reply_markup=components.BACK_TO_MENU
                )
            case _:
                await update.message.reply_text(const_text.REPLY_ERROR_RETRY)

    def start(self):
        self.app.add_handler(CommandHandler("start", self.handle_start_command))
        self.app.add_handler(CommandHandler("nextstep", self.handle_nextstep_command))
        self.app.add_handler(CommandHandler("github", self.handle_github_command))

        self.app.add_handler(CallbackQueryHandler(self.menu_callback))

        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        self.app.add_handler(MessageHandler(filters.VOICE, self.handle_voice_message))

        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
