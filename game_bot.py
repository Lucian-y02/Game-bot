import json
from random import randrange

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

        with open("save_data.json", "r", encoding="utf-8") as json_file:
            self.save_data = json.load(json_file)
            json_file.close()

        with open(f"Chapters/{name}.json", "r", encoding="utf-8") as json_file:
            self.chapter_data = json.load(json_file)
            json_file.close()

        self.now_node = self.chapter_data["head"]
        self.now_node_name = "head"
        self.show_node = False
        self.save = None
        self.inventory = list()

        self.function_data = {
            "Action": [self.action_take_answer, self.show_action],
            "Password": [self.password_take_answer, self.show_password],
            "Use_node": [self.use_take_answer, self.show_action]
        }

    def start(self, update, context):
        save_number = "0"
        update.message.reply_text("Квест начинается!")
        if len(update.message.text.split()) == 2:
            if update.message.text.split()[1] in self.save_data:
                save_number = update.message.text.split()[1]
            else:
                update.message.reply_text("Сохранение не найдено! "
                                          "Квест начнётся с самого начала!")
        self.save = self.save_data[save_number]
        self.now_node = self.chapter_data[self.save["node_name"]]
        self.now_node_name = self.save["node_name"]
        self.inventory = self.save["inventory"]
        self.show_node = True
        self.give_command(update, context)

    def give_command(self, update, context):
        if self.show_node:
            self.show_node = False
            update.message.reply_text(f"Текущее положение: {self.now_node['name']}\n"
                                      f"Сообщение: {self.now_node['message']}")

            self.function_data[self.now_node["type"]][1](update, context)

            if self.now_node["help"]:
                update.message.reply_text(f"Подсказка: {self.now_node['help']}")
        else:
            self.function_data[self.now_node["type"]][0](update, context, update.message.text)

    # Take answer ---------------------------------------------------------------------------------
    def action_take_answer(self, update, context, answer):
        if answer not in self.now_node["answers"]:
            update.message.reply_text("Неверно указан номер действия!")
        else:
            key_next_node = self.now_node["answers"][answer]["next_node"]
            if key_next_node == "save":
                with open("save_data.json", "w", encoding="utf-8") as file:
                    while str(save_number := randrange(1000, 10000)) in self.save_data:
                        pass
                    self.save_data[str(save_number)] = {
                        "node_name": self.now_node_name,
                        "inventory": self.inventory
                    }
                    update.message.reply_text(f"Сохранено! Ваш номер сохранения: {save_number}")
                    json.dump(self.save_data, file)
                    file.close()

            elif key_next_node != "null":
                self.now_node = self.chapter_data[key_next_node]
                self.now_node_name = key_next_node
                self.show_node = True
                self.give_command(update, context)
            else:
                update.message.reply_text("Квест закончен!")

    def password_take_answer(self, update, context, answer):
        if answer == "отмена":
            self.now_node_name = self.now_node["prev_node"]
            self.now_node = self.chapter_data[self.now_node["prev_node"]]
            self.show_node = True
            self.give_command(update, context)
        elif answer != self.now_node["right_password"]:
            update.message.reply_text("Неверный пароль!")
        else:
            key_next_node = self.now_node["next_node"]
            if key_next_node != "null":
                self.now_node_name = key_next_node
                self.now_node = self.chapter_data[key_next_node]
                self.show_node = True
                self.give_command(update, context)
            else:
                update.message.reply_text("Квест закончен!")

    def use_take_answer(self, update, context, answer):
        if answer == "1" and self.now_node["need_thing"] in self.inventory:
            self.inventory.remove(self.now_node["need_thing"])
            self.now_node_name = self.now_node["next_node"]
            self.now_node = self.chapter_data[self.now_node["next_node"]]
            self.show_node = True
            self.give_command(update, context)
        elif answer == "1":
            update.message.reply_text("У вас нет подходящего предмета!")
        elif answer == "2":
            self.now_node_name = self.now_node["prev_node"]
            self.now_node = self.chapter_data[self.now_node["prev_node"]]
            self.show_node = True
            self.give_command(update, context)
        else:
            update.message.reply_text("Неверно указан номер действия!")

    # Show node -----------------------------------------------------------------------------------
    def show_action(self, update, context):
        answers = "".join(list(map(lambda x:
                                   f'{x}) {self.now_node["answers"][x]["text"]}\n',
                                   self.now_node["answers"])))
        update.message.reply_text(f"Действия:\n"
                                  f"{answers}")

    def show_password(self, update, context):
        pass

    def main(self):
        self.dp.add_handler(CommandHandler("start", self.start))
        text_handler = MessageHandler(Filters.text & ~Filters.command, self.give_command)
        self.dp.add_handler(text_handler)

        self.updater.start_polling()
        self.updater.idle()


if __name__ == "__main__":
    bot = GameBot()
    bot.main()
