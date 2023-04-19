from bdb import effective
from telegram.ext import Updater, MessageHandler,Dispatcher, ConversationHandler, CommandHandler, CallbackContext,Filters
from telegram import Update
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)

updater: Updater = Updater(token='5297525222:AAGxaFDCEMjjnc9xE_dGz_GUfTCHCWX1XrQ')
dispatcher = updater.dispatcher

def hello(update: Update, context: CallbackContext):
    context.bot.send_message( chat_id = 1261601625 , text="salom")

dispatcher.add_handler(MessageHandler(Filters.all, hello))


updater.start_polling(timeout=600)
updater.idle()
