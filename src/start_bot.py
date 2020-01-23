import logging
import pytz

from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime, timedelta
from database import actions as db
from configs import tg_config as tg

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def job_buse(bot, job):
    print(job.context)
    today = datetime.now(pytz.timezone('Europe/Moscow'))
    print(today.strftime("%Y-%m-%d %H:%M:%S"))
    tdelta = int(job.context[1])
    snc_time = today - timedelta(hours=tdelta)
    print(snc_time.strftime("%Y-%m-%d %H:%M:%S"))
    uralTanks = db.db_fetch(snc_time.strftime("%Y-%m-%d %H:%M:%S"), today.strftime("%Y-%m-%d %H:%M:%S"))
    if len(uralTanks) != 0:
        msg = str(len(uralTanks)) + " новых новостей: "
        bot.send_message(chat_id=job.context[0], text = msg)
        for i in uralTanks:
            print(i)
            bot.send_message(chat_id=job.context[0], text= str(i[0]))
        bot.send_message(chat_id=job.context[0], text="Больше новостей нет. К счастью?")
    else:
        bot.send_message(chat_id=job.context[0], text="На данный момент новых новостей нет.")

def abuse(bot, update):
    today = datetime.now(pytz.timezone('Europe/Moscow'))
    print(today.strftime("%Y-%m-%d %H:%M:%S"))
    snc_time = today - timedelta(days=1)
    uralTanks = db.db_fetch(snc_time.strftime("%Y-%m-%d %H:%M:%S"), today.strftime("%Y-%m-%d %H:%M:%S"))
    if len(uralTanks) != 0:
        msg = str(len(uralTanks)) + " новых новостей: "
        bot.send_message(chat_id=update.message.chat_id, text = msg)
        for i in uralTanks:
            print(i)
            bot.send_message(chat_id=update.message.chat_id, text= str(i[0]))
        bot.send_message(chat_id=update.message.chat_id, text="Больше новостей нет. К счастью?")
    else:
        bot.send_message(chat_id=update.message.chat_id, text = "На данный момент новых новостей нет.")

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Сейчас польётся поток абьюза")

def set_abuse(bot, update):
    keyboard = [[InlineKeyboardButton("\U0001F553 4 часа", callback_data='4'),
                 InlineKeyboardButton("\U0001F557 8 часов", callback_data='8')],
                [InlineKeyboardButton("\U0001F55B 12 часов", callback_data='12'),
                 InlineKeyboardButton("\U0001F4C6 Сутки", callback_data='24')],
                [InlineKeyboardButton("\U0001F515 Отключить обновления", callback_data='666')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Укажите интервал обновлений', reply_markup=reply_markup)

def button(bot, update, job_queue, chat_data):
    query = update.callback_query
    option = int(query.data)
    print(dir(query.from_user))
    context_args = list()
    context_args.append(query.message.chat_id)
    context_args.append(option)
    if option == 4:
        job_queue.run_repeating(job_buse, 14400, first=0, context=context_args)
    elif option == 8 :
        job_queue.run_repeating(job_buse, 28800, first=0, context=context_args)
    elif option == 12 :
        job_queue.run_repeating(job_buse, 57600, first=0, context=context_args)
    elif option == 24 :
        timee = datetime.time(hour=14, minute=0, second=0)
        job_queue.run_daily(job_buse, timee, context=context_args)
    elif option == 666 :
        if 'job' not in chat_data:
            bot.send_message(chat_id=query.message.chat_id, text="У вас не включены обновления.")
            return
        job = chat_data['job']
        job.schedule_removal()
        del chat_data['job']
        bot.send_message(chat_id=query.message.chat_id, text="Обновления успешно отключены")

def police(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Официальные пресс-релизы СК РФ за последние 12 часов:")

def get_info(bot, update):
    user = update.message.from_user
    msg = "id: " + str(update.message.chat_id) + "\n" + "username: " + str(user.username) + "\n" + "language: " + str(user.language_code)
    bot.sendMessage(update.message.chat_id, msg)

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():

    """TG API"""
    updater = Updater(token=tg.telegram['token'])
    dispatcher = updater.dispatcher

    """Commands"""
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('abuse', abuse))
    dispatcher.add_handler(CommandHandler('set_abuse', set_abuse))
    dispatcher.add_handler(CallbackQueryHandler(button, pass_job_queue=True, pass_chat_data=True))
    dispatcher.add_handler(CommandHandler('police', police))
    dispatcher.add_handler(CommandHandler('get_info', get_info))

    """Start"""
    updater.start_polling()

if __name__ == '__main__':
    main()