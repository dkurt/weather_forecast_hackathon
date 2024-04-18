import os
import argparse
import telebot
from telebot import apihelper
import pandas as pd
import io
import sklearn.metrics


def compute_score(solution: pd.DataFrame, submission: pd.DataFrame, row_id_column_name = "ID") -> float:
    del submission[row_id_column_name]
    return sklearn.metrics.mean_absolute_percentage_error(solution, submission)


parser = argparse.ArgumentParser()
parser.add_argument('--token', help='Telegram bot token', required=True)
args = parser.parse_args()

# Load solution file
solution = pd.read_csv("solution.csv")
del solution["Usage"]
del solution["ID"]

bot = telebot.TeleBot(args.token)

chat_id_team = {}
submissions = {}
leaderboard = {}

if os.path.exists("teams.txt"):
    with open("teams.txt", "rt") as f:
        for line in f.readlines():
            chat_id_team[int(line[:line.find(" ")])] = line[line.find(" ") + 1:].strip()

if os.path.exists("submissions.txt"):
    with open("submissions.txt", "rt") as f:
        for line in f.readlines():
            team_name = line[:line.rfind(" ")]
            score = float(line[line.rfind(" ") + 1:])
            submissions[team_name] = submissions.get(team_name, []) + [score]
            leaderboard[team_name] = min(score, leaderboard.get(team_name, score))


@bot.message_handler(commands=['start'])
def start_message(message):
    chat_id = int(message.chat.id)
    welcome_message = "Напишите название команды новым сообщением в виде\n/team НАЗВАНИЕ\n\nДля просмотра доски результатов, отправьте /leaderboard"
    bot.send_message(chat_id, welcome_message)


@bot.message_handler(commands=['team'])
def process_team_name(message):
    chat_id = message.chat.id
    if chat_id in chat_id_team:
        bot.send_message(chat_id, f"Команда уже выбрана: {chat_id_team[chat_id]}")
        return

    team_name = message.text[message.text.find(" ") + 1:]
    apihelper.unpin_all_chat_messages(args.token, chat_id=chat_id)
    apihelper.pin_chat_message(args.token, chat_id=chat_id, message_id=message.id)
    chat_id_team[chat_id] = team_name
    with open("teams.txt", "at") as f:
        f.write(f"{chat_id} {team_name}\n")

@bot.message_handler(commands=['leaderboard'])
def print_leaderboard(message):
    resp = []
    for i, (team_name, score) in enumerate(sorted(leaderboard.items(), key=lambda x:x[1])):
        resp.append(f"{i + 1}. {score:.4f} - {team_name  }")
    bot.send_message(message.chat.id, "\n".join(resp))


@bot.message_handler(content_types=['document'])
def process_solution(message):
    chat_id = message.chat.id

    if not chat_id in chat_id_team:
        bot.send_message(chat_id, "Требуется указать название команды в виде сообщения:\n/team НАЗВАНИЕ")
        return
    team_name = chat_id_team[chat_id]

    document = message.document
    file_id = document.file_id
    file = bot.get_file(file_id)
    data = bot.download_file(file.file_path)

    data = pd.read_csv(io.StringIO(data.decode("utf-8")))
    if len(data) != 4500:
        bot.send_message(chat_id, f"Требуется 4500 строк, в файле {document.file_name} только {len(data)} строк")

    columns = ["ID", "temperature", "pressure", "humidity", "wind_speed", "wind_dir", "cloud_cover"]
    if len(data.columns) != len(columns) or any(data.columns != columns):
        bot.send_message(chat_id, f"Ожидаемые столбцы: {columns}")

    score = compute_score(solution, data)

    submissions[team_name] = submissions.get(team_name, []) + [score]
    leaderboard[team_name] = min(score, leaderboard.get(team_name, score))
    with open("submissions.txt", "at") as f:
        f.write(f"{team_name} {score}\n")

    bot.send_message(chat_id, f"Оценка MAPE для {document.file_name}: {score} (меньше - лучше)")

bot.polling()
