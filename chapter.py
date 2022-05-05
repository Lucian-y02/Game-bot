import json

from telegram.ext import Updater, CommandHandler, Filters, MessageHandler


class Chapter:

    def __init__(self, name):
        self.quest_run = True
        self.chapter_data = dict()

        with open(f"Chapters/{name}.json", "r", encoding="utf-8") as json_file:
            self.chapter_data = json.load(json_file)

        self.now_node = self.chapter_data["head"]

        self.function_data = {
            "Action": [self.action_show, self.action_take_answer],
            "Password": [self.password_show, self.password_take_answer]
        }

    def action_show(self):
        print(f"<{self.now_node['name']}>\n"
              f"Сообщение: {self.now_node['message']}")

        for key in self.now_node["answers"]:
            print(f"{key}) {self.now_node['answers'][key]['text']}")

    def password_show(self):
        print(f"<{self.now_node['name']}>\n"
              f"Сообщение: {self.now_node['message']}")

    def action_take_answer(self):
        while (answer := input("Ваше решение: ")) not in self.now_node["answers"]:
            print("Такого решение нет!")

        if self.now_node["answers"][answer]["next_node"] == "null":
            self.quest_run = False
        else:
            self.now_node = self.chapter_data[self.now_node["answers"][answer]["next_node"]]

    def password_take_answer(self):
        while (password := input("Пароль: ")) != self.now_node["right_password"]:
            if password == "отмена":
                self.now_node = self.chapter_data[self.now_node["prev_node"]]
            break

        if password != "отмена":
            self.now_node = self.chapter_data[self.now_node["next_node"]]

    def play_chapter(self):
        while self.quest_run:
            self.function_data[self.now_node["type"]][0]()

            if self.now_node["help"]:
                print(f"Подсказка: {self.now_node['help']}")
            if self.now_node["advice"]:
                print(f"Совет: {self.now_node['advice']}")

            self.function_data[self.now_node["type"]][1]()
            print()