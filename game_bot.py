import json

import logging
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler

from constants import *


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


class GameBot:

    def __init__(self, name="chapter_1"):
        self.quest_run = True
        self.chapter_data = dict()
        self.updater = Updater(TOKEN)
        self.dp = self.updater.dispatcher

        with open(f"Chapters/{name}.json", "r", encoding="utf-8") as json_file:
            self.chapter_data = json.load(json_file)
            json_file.close()

        self.now_node = self.chapter_data["head"]
        self.show_node = False

        self.function_data = {
            "Action": self.action_take_answer,
            "Password": self.password_take_answer
        }

    def start(self, update, context):
        update.message.reply_text("Квест начинается!")
        self.now_node = self.chapter_data["head"]
        self.show_node = True
        self.give_command(update, context)

    def give_command(self, update, context):
        if self.show_node:
            self.show_node = False
            update.message.reply_text(f"Текущее положение: {self.now_node['name']}\n"
                                      f"Сообщение: {self.now_node['message']}")

            # Костыль --------------------------------------------------------------------------------------------------
            try:
                answers = "".join(list(map(lambda x:
                                           f'{x}) {self.now_node["answers"][x]["text"]}\n',
                                           self.now_node["answers"])))
                if self.now_node["type"] == "Action":
                    update.message.reply_text(f"Действия:\n"
                                              f"{answers}")
            except Exception:
                pass
            # Костыль --------------------------------------------------------------------------------------------------

            if self.now_node["help"]:
                update.message.reply_text(f"Подсказка: {self.now_node['help']}")
        else:
            self.function_data[self.now_node["type"]](update, context, update.message.text)

    def action_take_answer(self, update, context, answer):
        if answer not in self.now_node["answers"]:
            update.message.reply_text("Неверно указан номер действия!")
        else:
            key_next_node = self.now_node["answers"][answer]["next_node"]
            if key_next_node != "null":
                self.now_node = self.chapter_data[key_next_node]
                self.show_node = True
                self.give_command(update, context)
            else:
                update.message.reply_text("Квест закончен!")

    def password_take_answer(self, update, context, answer):
        if answer == "отмена":
            self.now_node = self.chapter_data[self.now_node["prev_node"]]
            self.show_node = True
            self.give_command(update, context)
        elif answer != self.now_node["right_password"]:
            update.message.reply_text("Неверный пароль!")
        else:
            key_next_node = self.now_node["next_node"]
            if key_next_node != "null":
                self.now_node = self.chapter_data[key_next_node]
                self.show_node = True
                self.give_command(update, context)
            else:
                update.message.reply_text("Квест закончен!")

    def main(self):
        self.dp.add_handler(CommandHandler("start", self.start))
        text_handler = MessageHandler(Filters.text & ~Filters.command, self.give_command)
        self.dp.add_handler(text_handler)

        self.updater.start_polling()
        self.updater.idle()


if __name__ == "__main__":
    bot = GameBot()
    bot.main()
