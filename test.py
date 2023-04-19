import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = 'YOUR_BOT_TOKEN'
CHAT_ID = 'YOUR_CHAT_ID'

def release_member(context):
    user_id = context.job.context['user_id']
    chat_id = context.job.context['chat_id']
    context.bot.kick_chat_member(chat_id, user_id)
    context.bot.send_message(chat_id, f"User {user_id} has been automatically released due to inactivity.")

def new_member(update, context):
    join_date = datetime.datetime.fromtimestamp(update.message.date)
    release_date = join_date + datetime.timedelta(days=30)
    current_date = datetime.datetime.now()

    if current_date >= release_date:
        context.bot.kick_chat_member(update.message.chat_id, update.message.from_user.id)
        context.bot.send_message(update.message.chat_id, f"User {update.message.from_user.id} has been automatically released due to inactivity.")
    else:
        job = context.job_queue.run_once(release_member, release_date - current_date, context={'user_id': update.message.from_user.id, 'chat_id': update.message.chat_id})
        context.chat_data['job'] = job

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
