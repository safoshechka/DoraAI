import telebot
from telebot import types
import time
from datetime import datetime

from talker import Talker
from video_parser import VideoParser


class DoraAI:
    def __init__(self, config):
        self.config = config
        self.videos_adder = self.config['videos_adder']
        self.bot = telebot.TeleBot(self.config['bot_id'])
        self.video_parser = VideoParser(self.config)
        self.talker = Talker(self.config)

    def run_bot(self):
        # @self.bot.message_handler(commands=['start'])
        # def send_welcome(message):
        #     msg = self.bot.send_message(message.chat.id, 'Тебя ебет или интересует?')
        #     self.bot.register_next_step_handler(msg, get_query)

        @self.bot.message_handler(commands=['start'])
        def get_query(message):
            run_query = True

            if message.text == '/start':
                run_query = False
                msg = self.bot.send_message(message.chat.id, f'Задайте мне вопрос!')

            if message.from_user.id == self.videos_adder:
                message_splitted = message.text.split()

                if len(message_splitted) == 2 and message_splitted[0] == 'add_new_video_by_link':
                    added = self.video_parser.add_video(message_splitted[1])
                    if added:
                        msg = self.bot.send_message(message.chat.id, f'Video added successfully')
                        self.talker.boot()
                    else:
                        msg = self.bot.send_message(message.chat.id, f"Video wasn't added, check link")

                    run_query = False

            if run_query:
                answer = self.talker.pretty_answer(message.text)
                msg = self.bot.send_message(message.from_user.id, answer)

            self.bot.register_next_step_handler(msg, get_query)

        while True:
            try:
                self.bot.infinity_polling(timeout=10**7)
            except Exception as e:
                print(f"{datetime.now()}: {e}")
                time.sleep(5)
                continue
