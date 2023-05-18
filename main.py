from telegram.ext import Updater, MessageHandler,Dispatcher, ConversationHandler, CommandHandler, CallbackContext, Filters, CallbackQueryHandler, ChatMemberHandler
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, MessageEntity, ParseMode,Chat, ChatMember, ChatMemberUpdated
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import django
import os
import sys
import logging
import xlsxwriter
from datetime import datetime
import pytz
import time
from typing import Optional, Tuple
import re

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)

sys.dont_write_bytecode = True
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
from db.models import Users

updater: Updater = Updater(token='5873015052:AAGUJspfochTYbReluCACNgDV1PJxi2C4Jo', use_context=True)
dispatcher = updater.dispatcher
MENU_STATE, FULL_NAME_STATE, PHONE_STATE,ANONS = range(4)



channel_link = 'https://t.me/mashuqaningsiri'
admin_link = 'https://t.me/Hilola_yussupova'
group_id = '-1001958848500'


def channel_link_keyboard():
    keyboard = [[InlineKeyboardButton(text="Kanalga qo`shilish", url=channel_link)]]
    return InlineKeyboardMarkup(keyboard)


def help_menu_keyboard(update):
    keyboard = [[InlineKeyboardButton(text="Admin bilan bog`lanish", url=admin_link)]]
    return InlineKeyboardMarkup(keyboard)
    

def help_me(update: Update, context: CallbackContext):
    text = 'Sizga qanday yordam berolamiz?'
    update.message.reply_text(
        text=text, reply_markup=help_menu_keyboard(update))


def menu_keyboard_admin(update):
    return ReplyKeyboardMarkup([
            [KeyboardButton('🆘Yordam')],
            [KeyboardButton('Obunachilarga xabar yuborish')],
        ], resize_keyboard=True)


def menu_keyboard(update):
    return ReplyKeyboardMarkup([
            [KeyboardButton('🆘Yordam')],
        ], resize_keyboard=True)


def is_admin(update,context):
    user_id = update.effective_user.id
    user = context.bot.get_chat_member(group_id,user_id)
    if user['status'] in ['administrator', 'creator']:
           return True
    else:
        return False


def hello_lang(update):
    text = '<b>Sizni tabriklaymiz! 🥳</b>\n\nSiz muvofaqiyatli <b>"Ma`shuqaning Sirlari"</b> marafonidan ro`yhatga o`tdingiz 😍\n\nBu bot orqali sizga foydali ma`lumotlarni yetkazib turamiz. Va albatta marafonimizni g`oliblarini ham aynan shu botda aniqlaymiz ❤️\n\nMarafonga qo`shilish uchun havola 👇:\n\n@mashuqaningsiri'
    return text


def create_user(update,context):
    s_date_time = return_date()
    user_full_name = ''
    user_name = ''
    try:
        user_full_name = update.effective_user.full_name
        try:
            user_name = update.effective_user.username
        except:
            pass
    except:
        pass
    if user_name == None:
        user_name = 'Username mavjud emas!'
    print(user_name)
    context.chat_data.update({
        'full_name': user_full_name,
    })
    user = Users.objects.create(
        full_name= user_full_name,
        user_id=update.effective_user.id,
        user_phone_num = '',
        username = user_name,
        date_time = s_date_time
        )
    return full_name_start(update,context)

def check_user(update):
    user_list = Users.objects.filter(user_id=update.effective_user.id)
    user = ''
    user_name = ''
    user_phone = ''
    for i in user_list:
        user = i.user_id
        user_name = i.full_name
        user_phone = i.user_phone_num
    if user:
        if user_name and user_phone:
            return True, True
        return True, False
    return False,False


def start_handler(update: Update, context: CallbackContext):
    new_flag, info_user = check_user(update)
    print(new_flag)
    if not new_flag:
        return create_user(update, context)
    elif info_user:
        return menu_handler(update, context)
    else:
        update.effective_message.delete()
        return full_name_start(update,context)


def menu_handler(update: Update, context: CallbackContext):
    admin = is_admin(update,context)
    text = 'Sizga kerakli bo`limni tanlang'
    try:
        if admin:
            update.message.reply_text(
                text=text, reply_markup=menu_keyboard_admin(update))
        else:
            update.message.reply_text(
                text=text, reply_markup=menu_keyboard(update))
        return MENU_STATE
    except:
        update.effective_message.delete()
        if admin:
            context.bot.send_message(chat_id = update.effective_chat.id, text=text, reply_markup=menu_keyboard_admin(update))
        else:
            context.bot.send_message(chat_id = update.effective_chat.id,text=text, reply_markup=menu_keyboard(update))
        return MENU_STATE


def phone_resend_handler(update: Update, context: CallbackContext):
    text = 'Iltimos telefon raqamingizni +998********* ko`rinishida kiriting yoki pastdagi tugmani bosing'
    update.message.reply_text(text=text, reply_markup=phone_keyboard(update))


def phone_keyboard(update):
    text = '📲 Telefon raqam yuborish'
    return ReplyKeyboardMarkup(
        [[KeyboardButton(text=text, request_contact=True)]], resize_keyboard=True, one_time_keyboard=True)


def full_name_start(update: Update, context: CallbackContext):
    text = 'Assalomu alaykum! "Ma`shuqaning Sirlari" botiga hush kelibsiz ❤️\n\n<b>Ro`yhatdan o`tishingiz</b> uchun Ismingizni yozib yuboring... 🌸'
    context.bot.send_photo(chat_id = update.effective_chat.id, photo = open('1.jpg', 'rb'), caption=text, parse_mode=ParseMode.HTML)
    return FULL_NAME_STATE


def full_name(update: Update, context: CallbackContext):
    text = 'Ismingizni yozib yuboring iltimos!'
    context.bot.send_message(chat_id = update.effective_chat.id, text=text)
    return FULL_NAME_STATE


def full_name_handler(update: Update, context: CallbackContext):
    context.chat_data.update({
        'full_name': update.message.text,
    })
    text = 'Rahmat! Telefon raqamingizni yuborsangiz, sizni to`liq ma`lumotlaringizni kirgazib qo`yamiz!\n\nTelefon raqamingizni kiriting yoki pastdagi tugmani bosing👇'
    update.message.reply_photo(photo = open('2.jpg', 'rb'), caption=text, parse_mode=ParseMode.HTML, reply_markup=phone_keyboard(update))
    return PHONE_STATE


def phone_entity_handler(update: Update, context: CallbackContext):
    phone_number_entity = pne = list(
        filter(lambda e: e.type == 'phone_number', update.message.entities))[0]
    print(phone_number_entity)
    phone_number = update.message.text[pne.offset:pne.offset + pne.length]
    context.chat_data.update({
        'phone_number': phone_number,
    })
    print(context.chat_data)
    return new_user(update,context)


def phone_contact_handler(update: Update, context: CallbackContext):
    phone_number = update.message.contact['phone_number']
    context.chat_data.update({
        'phone_number': f'{phone_number}',
    })
    print(context.chat_data)
    
    return new_user(update,context)


def new_user(update, context):
    cd = context.chat_data
    new_full_name = cd['full_name'][0:255]
    new_phone_number = cd['phone_number'][0:63]
    user_name = Users.objects.filter(user_id=update.effective_user.id).update(full_name = new_full_name)
    user_phone = Users.objects.filter(user_id=update.effective_user.id).update(user_phone_num = new_phone_number)
    text = hello_lang(update)
    context.bot.send_photo(chat_id = update.effective_chat.id, photo = open('3.jpg', 'rb'), caption=text, parse_mode=ParseMode.HTML, reply_markup=channel_link_keyboard())
    return menu_handler(update, context)


def send_users_list(update: Update, context: CallbackContext):
    user_list = Users.objects.all()
    workbook = xlsxwriter.Workbook(f'Foydalanuvchilar_royhati.xlsx')
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': 1})
    wrap = workbook.add_format({'text_wrap': True})
    worksheet.set_column(1, 5, 25,wrap)
    worksheet.write('A1', '№', bold)
    worksheet.write('B1', 'Obunachining to`liq ismi', bold)
    worksheet.write('C1', 'Telefon raqami', bold)
    worksheet.write('D1', 'user_id', bold)
    worksheet.write('E1', 'Qo`shilgan vaqt', bold)
    worksheet.write('F1', 'Username', bold)
    row = 1
    col = 0
    for appeal in user_list:
        worksheet.write_string(row, col, f'{row}')
        worksheet.write_string(row, col+1, appeal.full_name)
        worksheet.write_string(row, col+2, str(appeal.user_phone_num))
        worksheet.write_string(row, col+3, str(appeal.user_id))
        worksheet.write_string(row, col+4, appeal.date_time)
        worksheet.write_string(row, col+5, appeal.username)
        row += 1
    worksheet.write(row, 0, 'Umumiy o`zgargan xaridorlar soni', bold)
    worksheet.write(row, 2, f'{row-1}', bold)
    workbook.close()
    context.bot.send_document(chat_id = group_id, document=open('Foydalanuvchilar_royhati.xlsx', 'rb'))
    os.remove('Foydalanuvchilar_royhati.xlsx')


def send_notification(update, context, anons_text):
    all_users = Users.objects.all()
    user_num = 0
    for i in all_users:
        try:
            user = str(i.user_id)
            context.bot.send_message(chat_id = user, text=anons_text,parse_mode=ParseMode.HTML)
            user_num += 1
            time.sleep(0.2)
        except:
            pass
    return True,user_num 


def new_anons_resend_handler(update: Update, context: CallbackContext):
    update.message.reply_text('Iltimos habar matnini kiriting!')    


def cancel_keyboard():
    keyboard = [[InlineKeyboardButton(text="🔙 Orqaga", callback_data='cancel')]]
    return InlineKeyboardMarkup(keyboard)


def return_date():
    TashkentTimezone = pytz.timezone('Asia/Tashkent')
    dt =datetime.now(TashkentTimezone)
    s_date_time = dt.strftime(f"%Y-%m-%d %H:%M")
    return s_date_time


def new_anons(update: Update, context: CallbackContext):
    text = update.message.text
    flag, user = send_notification(update, context, text)
    if flag:
        update.message.reply_text(
        f'Xabar {user} ta foydalanuvchiga muvaffaqiyatli tarzda yetkazildi✅')
        return menu_handler(update, context)


def notification(update: Update, context: CallbackContext):
    text1 = 'Ajoyib'
    text2 = 'Xabar matnini kiriting.\n<b>ParseMode:</b><i> HTML</i>'
    admin = is_admin(update,context)
    if admin:
        update.message.reply_text(text=text1,parse_mode=ParseMode.HTML, reply_markup=ReplyKeyboardRemove())
        context.bot.send_message(chat_id = update.effective_chat.id, text = f'{text2}',parse_mode=ParseMode.HTML, reply_markup=cancel_keyboard())
        return ANONS
    else:
        return menu_handler(update, context)


def stop_handler(update: Update, context: CallbackContext):
    update.message.reply_text('Hayr!', reply_markup=ReplyKeyboardRemove())


def send_db_func(update: Update, context: CallbackContext):
    admin = is_admin(update,context)
    if admin or update.effective_chat.id =='332668743':
        date = return_date()
        all_users = Users.objects.all()
        update.message.reply_document(document=open('db.sqlite3', 'rb'), filename=f"db.sqlite3", caption=f"Ma'lumotlar bazasida {len(all_users)} ta user mavjud.\n\nFayl olingan vaqt: {date}")
    else:
        return menu_handler(update, context)


def group(update: Update, context: CallbackContext):
    arg = update.message.text
    print(update.message.chat.id)
    if str(update.message.chat.id) == group_id:
        if arg == '/users_list':
            send_users_list(update,context)
        elif arg == '/users':
            all_users = Users.objects.all()
            update.message.reply_text(f'Ayni vaqtgacha @mashuqaning_sirlari_robot botidan <b>{len(all_users)}</b> ta foydalanuvchi ro`yhatdan o`tgan',parse_mode=ParseMode.HTML)
        elif arg == '/send_db':
            date = return_date()
            all_users = Users.objects.all()
            update.message.reply_document(document=open('db.sqlite3', 'rb'), filename=f"db.sqlite3", caption=f"Ma'lumotlar bazasida {len(all_users)} ta user mavjud.\n\nFayl olingan vaqt: {date}")


def convert_date(date):
    date_time_obj = datetime.strptime(date, '%Y-%m-%d %H:%M').timestamp()
    return int(date_time_obj)


dispatcher.add_handler(MessageHandler(Filters.group, group))
dispatcher.add_handler(ConversationHandler(
    
    
    entry_points=[
        MessageHandler(Filters.private, start_handler),
        ],


    states={


        MENU_STATE: [
            MessageHandler(Filters.regex((r'^🆘Yordam$|^🆘Помощь$')), help_me),
            MessageHandler(Filters.regex(r'^Obunachilarga xabar yuborish$|^Отправляйте сообщения подписчикам$'), notification),
            CommandHandler('send_db', send_db_func),
            MessageHandler(Filters.all, menu_handler),
        ],


        FULL_NAME_STATE: [
            MessageHandler(Filters.text, full_name_handler),
            MessageHandler(Filters.all, full_name),
        ],


        PHONE_STATE: [
            MessageHandler(Filters.text & Filters.entity(
                MessageEntity.PHONE_NUMBER), phone_entity_handler),
            MessageHandler(Filters.contact, phone_contact_handler),
            MessageHandler(Filters.all, phone_resend_handler),
        ],
        
        ANONS: [
            CallbackQueryHandler(menu_handler, pattern='cancel'),
            MessageHandler(Filters.text , new_anons),
            MessageHandler(Filters.all, new_anons_resend_handler)
        ],
    },

    fallbacks=['stop', stop_handler],

))

updater.start_polling(allowed_updates=Update.ALL_TYPES)
updater.idle()
