from telegram.ext import Updater, MessageHandler,Dispatcher, ConversationHandler, CommandHandler, CallbackContext, Filters, CallbackQueryHandler
from telegram import Chat, Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, MessageEntity, ParseMode
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import django
import os
import sys
import logging
import xlsxwriter
import datetime
import time

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG)

sys.dont_write_bytecode = True
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
from db.models import Appeal
from db.models import users
from db.models import Seminars
from db.models import Consultation

updater: Updater = Updater(token='5873015052:AAFd-vPIUXsbY8IzWEM-zaL27iqyGJiSC08')
dispatcher = updater.dispatcher
MENU_STATE, FIRST_NAME_STATE, LAST_NAME_STATE, AGE_STATE, ADDRESS_STATE, PHONE_STATE, ANONS, MARKET_MENU,SEMINARS_MENU,ALL_SALE,ALL_SALE_SEM,ALL_SALE_CONS= range(12)


group_id = '-1001958848500'
channel_id = '-1001803300455'


flag = None


def main_lang_menu_keyboard():
  keyboard = [[InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data='uz_latin'),
            InlineKeyboardButton('🇷🇺 Русский', callback_data='rus')]]
  return InlineKeyboardMarkup(keyboard)


def help_menu_keyboard(update):
    lang = check_user_lang(update)
    if lang == 'uz_latin':
        keyboard = [[InlineKeyboardButton(text="Admin bilan bog`lanish", url='https://t.me/Deadorr')],
           [InlineKeyboardButton('Botdan foydalanish bo`yicha qo`llanma', callback_data='use_bot')]]
    elif lang =='ru':
        keyboard = [[InlineKeyboardButton(text="Связаться с администратором", url='https://t.me/Deadorr')],
           [InlineKeyboardButton('Инструкция по использованию бота', callback_data='use_bot')]]
    return InlineKeyboardMarkup(keyboard)


def setting(update: Update, context: CallbackContext):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = 'Tilni tanlang!'
    elif lang =='ru':
        text = 'Выберите язык!'
    update.message.reply_text(
        text=text, reply_markup=main_lang_menu_keyboard())
    

def help_me(update: Update, context: CallbackContext):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = 'Sizga qanday yordam berolamiz?'
    elif lang =='ru':
        text = 'Как мы можем вам помочь?'
    update.message.reply_text(
        text=text, reply_markup=help_menu_keyboard(update))


def use_bot(update: Update, context: CallbackContext):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = 'Shu habar o`rnida qo`llanma bo`lishi kerak edi😅🌚'
    elif lang =='ru':
        text = 'Вместо этого сообщения должен был быть инструкция😅🌚'
    update.callback_query.message.edit_text(text=text)


def is_subscribed(update,context):
    user_id = update.effective_user.id
    print('=====================')
    user = context.bot.get_chat_member(channel_id,user_id)
    print(user)
    if user['status'] in ['member', 'administrator','creator']:
           return True
    else:
        return False


def menu_keyboard_admin(update):
    lang = check_user_lang(update)
    if lang == 'uz_latin':
        return ReplyKeyboardMarkup([
            [KeyboardButton('Mashuqaning sirlari'),KeyboardButton('Seminarlar')],
            [KeyboardButton('⚙️Sozlash'),KeyboardButton('Konsultatsiya')],
            [KeyboardButton('Obunachilarga xabar yuborish'),KeyboardButton('🆘Yordam')],
        ], resize_keyboard=True)
    elif lang == 'ru':
        return ReplyKeyboardMarkup([
            [KeyboardButton('Mashuqaning sirlari'),KeyboardButton('Семинары')],
            [KeyboardButton('⚙️Настройка'),KeyboardButton('Консультация')],
            [KeyboardButton('Отправляйте сообщения подписчикам'),KeyboardButton('🆘Помощь')],
        ], resize_keyboard=True)


def menu_keyboard(update):
    lang = check_user_lang(update)
    if lang == 'uz_latin':
        return ReplyKeyboardMarkup([
            [KeyboardButton('Mashuqaning sirlari'),KeyboardButton('Seminarlar')],
            [KeyboardButton('⚙️Sozlash'),KeyboardButton('Konsultatsiya')],
            [KeyboardButton('🆘Yordam')],
        ], resize_keyboard=True)
    elif lang == 'ru':
        return ReplyKeyboardMarkup([
            [KeyboardButton('Mashuqaning sirlari'),KeyboardButton('Семинары')],
            [KeyboardButton('⚙️Настройка'),KeyboardButton('Консультация')],
            [KeyboardButton('🆘Помощь')],
        ], resize_keyboard=True)
    

def seminars_menu_keyboard(update):
    lang = check_user_lang(update)
    if lang == 'uz_latin':
        return ReplyKeyboardMarkup([
            [KeyboardButton('"Hayotga qayt" seminari'),    KeyboardButton('"Hayot bilan raqs" seminari')],
            [KeyboardButton('"Shishadagi qiz" seminari'),  KeyboardButton('"Turmushdagi xatolar" seminari')],
            [KeyboardButton('🔙 Orqaga')],
        ], resize_keyboard=True)
    elif lang == 'ru':
        return ReplyKeyboardMarkup([
            [KeyboardButton('Семинар "Hayotga qayt"'),    KeyboardButton('Семинар "Hayot bilan raqs"')],
            [KeyboardButton('Семинар "Shishadagi qiz"'),  KeyboardButton('Семинар "Turmushdagi xatolar"')],
            [KeyboardButton('🔙 Назад')]
        ], resize_keyboard=True)


def market_menu_keyboard(update):
    lang = check_user_lang(update)
    if lang == 'uz_latin':
        return ReplyKeyboardMarkup([
            [KeyboardButton('"O`zim" tarifi'),  KeyboardButton('"Kurator" tarifi')],
            [KeyboardButton('🔙 Orqaga'),       KeyboardButton('"VIP" tarifi')],
        ], resize_keyboard=True)
    elif lang == 'ru':
        return ReplyKeyboardMarkup([
            [KeyboardButton('Тариф "O`zim"'),  KeyboardButton('Тариф "Куратор"')],
            [KeyboardButton('🔙 Назад'),       KeyboardButton('Тариф "VIP"')],
        ], resize_keyboard=True)


def all_sale_keyboard(update):
    lang = check_user_lang(update)
    if lang == 'uz_latin':
        return ReplyKeyboardMarkup([
            [KeyboardButton('Xaridni boshlash')],
            [KeyboardButton('🔙 Orqaga')],
        ], resize_keyboard=True)
    elif lang == 'ru':
        return ReplyKeyboardMarkup([
            [KeyboardButton('Начать покупки')],
            [KeyboardButton('🔙 Назад')],
        ], resize_keyboard=True)


def check_keyboard(update):
    lang = check_user_lang(update)
    if lang == 'ru':
        keyboard = [
            [InlineKeyboardButton(text=str('Подпишитесь на канал'), url='https://t.me/admgroup_work')],
            [InlineKeyboardButton('✅ Я подписался!', callback_data='check_channel')]
            ]
    elif lang == 'uz_latin':
        keyboard = [
            [InlineKeyboardButton(text=str('Kanalga obuna bo`lish'), url='https://t.me/admgroup_work')],
            [InlineKeyboardButton('✅Obuna bo`ldim!', callback_data='check_channel')]
            ]

    return InlineKeyboardMarkup(keyboard)


def is_admin(update,context):
    user_id = update.effective_user.id
    print('=====================')
    user = context.bot.get_chat_member(channel_id,user_id)
    if user['status'] in ['administrator', 'creator']:
           return True
    else:
        return False


def test_cheking(update: Update, context: CallbackContext):
    user_sub = is_subscribed(update,context)
    lang = check_user_lang(update)
    if not user_sub:
        try:
            if lang == 'uz_latin':
                text_n = '❌ Siz kanalga obuna bo`lmagansiz!'
            elif lang == 'ru':
                text_n = '❌ Вы не подписаны на канал!'
            update.effective_message.edit_text(text=text_n, reply_markup=check_keyboard(update))
        except:
            if lang == 'uz_latin':
                text_n = '❌ Obuna bo`ling avval'
            elif lang == 'ru':
                text_n = '❌ Подпишись первым'
            update.effective_message.edit_text(text=text_n, reply_markup=check_keyboard(update))
    else:
        return hello(update,context)


def hello_lang(update):
    lang = check_user_lang(update)
    text = ''
    text2 = ''
    if lang == 'uz_latin':
        text = 'Ajoyib!'
        text2 = 'Kerakli bo`limni tanlang'
    elif lang == 'ru':
        text = 'Классно!'
        text2 = 'Выберите нужный раздел' 
    return text, text2


def hello(update, context):
    try:
        admin = is_admin(update,context)
        text, text2 = hello_lang(update)
        if admin:
            update.effective_message.edit_text(text)
            context.bot.send_message(chat_id = update.effective_chat.id, text=text2,reply_markup=menu_keyboard_admin(update))
            return MENU_STATE
        else:
            update.effective_message.edit_text(text)
            context.bot.send_message(chat_id = update.effective_chat.id, text=text2,reply_markup=menu_keyboard(update))
            return MENU_STATE
    except:
        if admin:
            context.bot.send_message(chat_id = update.effective_chat.id, text=text2,reply_markup=menu_keyboard_admin(update))
            return MENU_STATE
        else:
            context.bot.send_message(chat_id = update.effective_chat.id, text=text2,reply_markup=menu_keyboard(update))
            return MENU_STATE


def create_user(update,full_name_):
    dt = datetime.now()
    user = users.objects.create(
        full_name=full_name_,
        user_id=update.effective_user.id,
        user_lang = '',
        date_time = dt.strftime(f"%Y-%m-%d %H:%M:%S"))


def user_upgrade(update, lang):
    print('*****************')
    user = users.objects.filter(user_id=update.effective_user.id).update(user_lang = lang)
    print('*****************')


def check_user_lang(update):
    user_list = users.objects.filter(user_id=update.effective_user.id)
    user_lang = False
    for i in user_list:
        user_lang = i.user_lang
    return user_lang
    

def check_user(update):
    user_list = users.objects.filter(user_id=update.effective_user.id)
    user = ''
    for i in user_list:
        user = i.user_id
    if user:
        return True
    return False


def send_hello(update: Update, context: CallbackContext):
    lang = check_user_lang(update)
    print(lang)
    text = ''
    if lang == 'uz_latin':
        text = f"Assalomu alaykum {update.effective_user.first_name}\n Hilola Yussupova muallifidagi kurs va seminarlar haqida ma'lumot beruvchi botga xush kelibsiz!\nBotdan to`liq foydalanish uchun @admgroup_work kanaliga obuna bo`ling"
    elif lang == 'ru':
        text = f'Здравствуйте {update.effective_user.first_name}\nДобро пожаловать в информационный бот для курсов и семинаров Хилолы Юсуповой!!\nЧтобы полноценно использовать бота, подпишитесь на канал @admgroup_work' 
    else:
        return False
    print('*************')
    print(text)
    return text


def start_handler(update: Update, context: CallbackContext):
    if update.effective_user.first_name != None and update.effective_user.last_name!= None:
        fullname = f'{update.effective_user.first_name} {update.effective_user.last_name}'
        context.chat_data.update({
            'first_name': update.effective_user.first_name})
        context.chat_data.update({
            'last_name': update.effective_user.last_name})
    else:
        context.chat_data.update({
            'first_name': update.effective_user.first_name})
        context.chat_data.update({
            'last_name': ' '})
        fullname = update.effective_user.full_name
    new_flag = check_user(update)
    print(new_flag)
    if not new_flag:
        create_user(update, fullname)
    lang = check_user_lang(update)
    if not lang:
        print('Diyor')
        update.message.reply_text(
            'Tilni tanlang!\nВыберите язык!', reply_markup=main_lang_menu_keyboard())
    else:
        user_sub = is_subscribed(update,context)
        if not user_sub:
            hello_text = send_hello(update,context)
            print(hello_text)
            update.effective_message.delete()
            context.bot.send_message(chat_id = update.effective_user.id,text=hello_text,reply_markup=check_keyboard(update))
            # update.effective_message.edit_text(text="hello_text").edit_reply_markup(reply_markup=check_keyboard())
        else:
            return hello(update,context)


def mashuqaning_sirlari(update: Update, context: CallbackContext):
    text = market_handler_text(update)
    update.message.reply_text(
        text=text, reply_markup=market_menu_keyboard(update))
    return MARKET_MENU


def seminars_list(update: Update, context: CallbackContext):
    text = seminars_text(update)
    update.message.reply_text(
        text=text, reply_markup=seminars_menu_keyboard(update))
    return SEMINARS_MENU


def consultation(update: Update, context: CallbackContext):
    text = consultation_text(update)
    context.chat_data.update({
        'price': 'Erkin mavzu',
        'theme': 'Konsultatsiya'
    })
    update.message.reply_text(text=text, parse_mode=ParseMode.HTML, reply_markup=all_sale_keyboard(update))
    return ALL_SALE_CONS


def market_back(update: Update, context: CallbackContext):
    return hello(update, context)


def market_back_equ(update: Update, context: CallbackContext):
    return mashuqaning_sirlari(update, context)


def seminar_back_equ(update: Update, context: CallbackContext):
    return seminars_list(update, context)


def price_1(update: Update, context: CallbackContext):
    s_text = update.message.text
    
    if s_text =='Тариф "O`zim"' or s_text=='"O`zim" tarifi':
        text = price_1_handler_text(update)
        s_text = '"O`zim" tarifi'
    elif s_text =='Тариф "Куратор"' or s_text=='"Kurator" tarifi':
        text = price_2_handler_text(update)
        s_text = '"Kurator" tarifi'
    elif s_text =='Тариф "VIP"' or s_text=='"VIP" tarifi':
        text = price_3_handler_text(update)
        s_text = '"VIP" tarifi'
    context.chat_data.update({
        'price': s_text,
        'theme': 'Mashuqaning sirlari'
    })
    update.message.reply_text(
        text=text, parse_mode=ParseMode.HTML, reply_markup=all_sale_keyboard(update))
    return ALL_SALE


def seminars_handler(update: Update, context: CallbackContext):
    s_text = update.message.text
    
    if s_text =='"Turmushdagi xatolar" seminari' or s_text=='Семинар "Turmushdagi xatolar"':
        text = seminar_1_handler_text(update)
        s_text = '"Turmushdagi xatolar" seminari'
    elif s_text =='"Shishadagi qiz" seminari' or s_text=='Семинар "Shishadagi qiz"':
        text = seminar_2_handler_text(update)
        s_text = '"Shishadagi qiz" seminari'
    elif s_text =='"Hayot bilan raqs" seminari' or s_text=='Семинар "Hayot bilan raqs"':
        text = seminar_3_handler_text(update)
        s_text = '"Hayot bilan raqs" seminari'
    elif s_text =='"Hayotga qayt" seminari' or s_text=='Семинар "Hayotga qayt"':
        text = seminar_4_handler_text(update)
        s_text = '"Hayotga qayt" seminari'
    context.chat_data.update({
        'price': s_text,
        'theme': 'Seminar'
    })
    update.message.reply_text(text=text, parse_mode=ParseMode.HTML, reply_markup=all_sale_keyboard(update))
    return ALL_SALE_SEM


def market_handler_text(update):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = 'O`zingizga qulay tarifni tanlang!'
    elif lang == 'ru':
        text = 'Выбирайте удобный для вас тариф!'
    return text


def seminars_text(update):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = 'Qaysi seminarda qatnashamiz?!'
    elif lang == 'ru':
        text = 'Какой семинар мы возьмем?!'
    return text


def consultation_text(update):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = "Konsultatsiya online bo'lib o'tadi.\n1 soat davomida siz istagan mavzuyingizda suhbat bo'lib, barcha  savollaringizga javob olasiz❤️\n\nNarxi: 150$\nTo'lovdan keyin konsultatsiya kuni va soatini belgilaymiz."
    elif lang == 'ru':
        text = 'Консультация будет проходить онлайн.\nВ течение 1 часа будет разговор на любую интересующую вас тему, и вы получите ответы на все интересующие вас вопросы\n\nЦена: $150\nПосле оплаты мы назначим день и время консультации.'
    return text


def price_1_handler_text(update):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = '<b>"O`ZIM" ta`rifi\n\n✨ 4 ta modul:</b>\n1. Fiziologiya\n2. Psixologiya\n3. Seksologiya\n4. Energetika\n\n✨ <b>8ta video va audio darslar</b> (4ta modulga asoslangan holda).\n\n✨ <b>Chat</b> (Guruh uchun chatda Hilola savollarga javob bermaydi).\n\n<b>Narxi: 690 000 so`m</b>'
    elif lang == 'ru':
        text = '<b>Тариф «O`ZIM»\n\n✨ 4 модуля:</b>\n1. Физиология\n2. Психология\n3. Сексология\n4. Энергетика\n\n✨ <b>8 видео и аудио уроков</b> (на основе 4 модулей).\n\n✨ <b>Чат</b> (Хилола не отвечает на вопросы в групповом чате).\n\n<b>Цена: 690 000 сум</b>'
    return text


def price_2_handler_text(update):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
         text = '<b>"KURATOR BILAN" ta`rifi\n\n✨ 4 ta modul:</b>\n1. Fiziologiya\n2. Psixologiya\n3. Seksologiya\n4. Energetika\n\n✨ <b>8ta video va audio darslar</b> (4ta modulga asoslangan holda).\n\n✨ <b>Chat</b> (Guruh uchun chatda Hilola savollarga javob bermaydi).\n\n<b>✨Ekspertlardan video darslar\n\n✨Kurator-psixolog bilan alohida guruh chati\n\nESLATMA!</b> <i>"Kurator bilan" ta`rifining  "O`zim" tarifidan farqi shundaki, har bir o`quvchiga biriktirilgan kuratorlar darslarni tekshirib boradi va ekspertlardan video darslar berib boriladi.</i>\n\n<b>Narxi: 1 290 000 so`m</b>'
    elif lang == 'ru':
        text = '<b>Тариф «KURATOR BILAN»\n\n✨ 4 модуля:</b>\n1. Физиология\n2. Психология\n3. Сексология\n4. Энергия\n\n✨ <b>8 видео и аудиоуроков</b> (на основе 4 модулей).\n\n✨ <b>Чат</b> (Хилола не отвечает на вопросы в групповом чате).\n\n<b>✨Видеоуроки от экспертов\n\n✨Отдельный групповой чат с куратором-психологом\n\nВНИМАНИЕ!</b> <i>Разница между определениями «KURATOR BILAN» и «O`ZIM» в том, что каждый o Кураторы, прикрепленные к студенту, проверяют уроки и проводят видео уроки от экспертов</i>\n\n<b>Цена: 1 290 000 сум</b>'
    return text


def seminar_1_handler_text(update):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = '<b>"TURMUSHDAGI XATOLAR" seminari</b>\n\n✨Seminarning video va audio formati.\n✨Qo`shimcha audio formatdagi dars.\n✨Workbook\n<b>Narxi: 300 000 so`m</b>'
    elif lang == 'ru':
        text = '<b>Семинар "TURMUSHDAGI XATOLAR"</b>\n\nВидео и аудио формат семинара.\n✨Урок в дополнительном аудиоформате.\n✨Рабочая тетрадь\n<b>Цена: 300 000 сум</b>'
    return text


def seminar_2_handler_text(update):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = '<b>"SHISHADAGI QIZ" seminari</b>\n\n✨Seminarning video va audio formati.\n✨Workbook\n<b>Narxi: 100 000 so`m</b>'
    elif lang == 'ru':
        text = '<b>Семинар "SHISHADAGI QIZ"</b>\n\nВидео и аудио формат семинара.\n✨Рабочая тетрадь\n<b>Цена: 100 000 сум</b>'
    return text


def seminar_3_handler_text(update):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = '<b>"HAYOT BILAN RAQS" seminari</b>\n\n✨Seminarning video va audio formati.\n✨Workbook\n<b>Narxi: 100 000 so`m</b>'
    elif lang == 'ru':
        text = '<b>Семинар "HAYOT BILAN RAQS"</b>\n\nВидео и аудио формат семинара.\n✨Рабочая тетрадь\n<b>Цена: 100 000 сум</b>'
    return text


def seminar_4_handler_text(update):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = '<b>"HAYOTGA QAYT" seminari</b>\n\n✨Seminarning video va audio formati.\n✨Workbook\n<b>Narxi: 200 000 so`m</b>'
    elif lang == 'ru':
        text = '<b>Семинар "HAYOTGA QAYT"</b>\n\nВидео и аудио формат семинара.\n✨Рабочая тетрадь\n<b>Цена: 200 000 сум</b>'
    return text


def price_3_handler_text(update):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = '<b>"VIP" ta`rifi\n\n✨ 4 ta modul:</b>\n1. Fiziologiya\n2. Psixologiya\n3. Seksologiya\n4. Energetika\n\n✨ <b>8ta video va audio darslar</b> (4ta modulga asoslangan holda).\n\n✨ <b>Chat</b> (Guruh uchun chatda Hilola savollarga javob bermaydi).\n\n<b>✨Ekspertlardan video darslar\n\n✨Kurator-psixolog bilan alohida guruh chati\n\n✨Hilola Yussupova bilan 4ta offline uchrashuv:\n</b>\n1. Seminar\n2. Mix terapiya\n3. Art terapiya\n4. Sound healing\n\n<b>ESLATMA!</b> <i>"Vip" ta`rifining "Kurator bilan" tarifidan farqi shundaki, Hilola Yussupova bilan 4 ta offline uchrashuv bo`lib o`tadi.</i>\n\n<b>Narxi: 5 490 000 so`m</b>'
    elif lang == 'ru':
        text = '<b>Тариф «VIP»\n\n✨ 4 модуля:</b>\n1. Физиология\n2. Психология\n3. Сексология\n4. Энергия\n\n✨ <b>8 видео- и аудиоуроков</b> (на основе 4 модулей).\n\n✨ <b>Чат</b> (Хилола не отвечает на вопросы в групповом чате).\n\n<b>✨Видеоуроки от экспертов\n\n✨Отдельный групповой чат с куратором-психологом\n\n✨4 офлайн-встречи с Хилолой Юсуповой:\n</b>\n1. Семинар\n2. Комбинированная терапия\n3. Арт-терапия\n4. Исцеление звуком\n\n<b>ВНИМАНИЕ!</b> <i>Отличие определения "VIP" от тарифа "KURATOR BILAN" в том, что будет 4 офлайн-встречи с Хилолой Юсуповой.</i>\n\n<b>Цена: 5 490 000 сум</b>'
    return text


def market_handler(update: Update, context: CallbackContext):
    text = market_handler_text(update)
    update.message.reply_text(
        text=text, reply_markup=market_menu_keyboard(update))


def ru_lang_edit(update: Update, context: CallbackContext):
    edit_lang = user_upgrade(update,'ru')
    return start_handler(update,context)


def uz_latin_lang_edit(update: Update, context: CallbackContext):
    edit_lang = user_upgrade(update,'uz_latin')
    return start_handler(update,context)


def menu_handler(update: Update, context: CallbackContext):
    admin = is_admin(update,context)
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
            text = 'Sizga kerakli bo`limni tanlang'
    elif lang =='ru':
            text = 'Выберите нужный вам раздел'
    if admin:
        update.message.reply_text(
            text=text, reply_markup=menu_keyboard_admin(update))
    else:
        update.message.reply_text(
            text=text, reply_markup=menu_keyboard(update))
    return MENU_STATE


def phone_resend_handler(update: Update, context: CallbackContext):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = 'Iltimos telefon raqamingizni +998********* ko`rinishida kiriting yoki pastdagi tugmani bosing'
    elif lang =='ru':
        text = 'Пожалуйста, введите свой номер телефона как +998********* или нажмите кнопку ниже'
    update.message.reply_text(text=text, reply_markup=phone_keyboard(update))


def phone_keyboard(update):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
            text = '📲 Telefon raqam yuborish'
    elif lang =='ru':
            text = '📲 Отправить номер телефона'
    return ReplyKeyboardMarkup(
        [[KeyboardButton(text=text, request_contact=True)]], resize_keyboard=True, one_time_keyboard=True)


def new_sale_handler(update: Update, context: CallbackContext):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
            text = 'Ismingizni kiriting'
    elif lang =='ru':
            text = 'Введите ваше имя'
    update.message.reply_text(text=text, reply_markup=ReplyKeyboardRemove())
    return FIRST_NAME_STATE


def first_name_handler(update: Update, context: CallbackContext):
    context.chat_data.update({
        'first_name': update.message.text,
    })
    print(context.chat_data)
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = 'Ajoyib!\nAna endi familiyangizni kiriting!'
    elif lang =='ru':
        text = 'Классно!\nТеперь введите свою фамилию!'
    update.message.reply_text(text=text)
    return LAST_NAME_STATE


def last_name_resend_handler(update: Update, context: CallbackContext):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = 'Familiyangizni kiriting!'
    elif lang =='ru':
        text = 'Введите свою фамилию!'
    update.message.reply_text(text=text)


def user_age_resend_handler(update: Update, context: CallbackContext):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = 'Iltimos yoshingizni son ko`rinishida kiriting)\nMisol uchun: 20\n16 yoshdan boshlab qatnashish mumkin'
    elif lang =='ru':
        text = 'Пожалуйста, введите свой возраст в виде числа)\nНапример: 20\nУчастие возможно с 16 лет'
    update.message.reply_text(text=text)


def address_resend_handler(update: Update, context: CallbackContext):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = 'Iltimos yashash joyingizni to`liq kiriting!'
    elif lang =='ru':
        text = 'Пожалуйста, введите свой полный адрес!'
    update.message.reply_text(text=text)


def last_name_handler(update: Update, context: CallbackContext):
    context.chat_data.update({
        'last_name': update.message.text,
    })
    print(context.chat_data)
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = 'Ajoyib! Yoshingizni son ko`rinishida kiriting)\nMisol uchun: 20'
    elif lang =='ru':
        text = 'Классно! Введите свой возраст в виде числа)\nНапример: 20'
    update.message.reply_text(text=text)
    return AGE_STATE


def age_handler(update: Update, context: CallbackContext):
    context.chat_data.update({
        'user_age': update.message.text,
    })
    print(context.chat_data)
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = 'Yashash joyingizni to`liq kiriting'
    elif lang =='ru':
        text = 'Введите свой полный адрес'
    update.message.reply_text(text=text)
    return ADDRESS_STATE


def address_handler(update: Update, context: CallbackContext):
    context.chat_data.update({
        'address': update.message.text,
    })
    print(context.chat_data)
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = 'Telefon raqamingizni kiriting yoki pastdagi tugmani bosing'
    elif lang =='ru':
        text = 'Введите свой номер телефона или нажмите кнопку ниже'
    update.message.reply_text(text=text, reply_markup=phone_keyboard(update))

    return PHONE_STATE


def phone_handler(update: Update, context: CallbackContext):
    context.chat_data.update({
        'phone_number': update.message.text,
    })
    cd = context.chat_data

    return new_user(update,context)
    

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
        'phone_number': f'+{phone_number}',
    })
    print(context.chat_data)
    
    return new_user(update,context)


def new_user(update,context):
    cd = context.chat_data
    dt = datetime.now()
    s_first_name = cd['first_name'][0:255]
    s_last_name = cd['last_name'][0:255]
    s_user_age = cd['user_age'][0:255]
    s_address = cd['address'][0:255]
    s_price = cd['price'][0:255]
    s_theme = cd['theme'][0:255]
    s_phone_number = cd['phone_number'][0:63]
    s_date_time = dt.strftime(f"%Y-%m-%d %H:%M:%S")
    fullname = f'{s_first_name} {s_last_name}'
    if s_theme == 'Mashuqaning sirlari':
        appeal = Appeal.objects.create(
            first_name = s_first_name,
            last_name = s_last_name,
            user_age=s_user_age,
            address=s_address,
            phone_number=s_phone_number,
            date_time = s_date_time,
            price = s_price,
            user_id=update.effective_user.id
        )   
    elif s_theme == 'Seminar':
        seminar = Seminars.objects.create(
            first_name = s_first_name,
            last_name = s_last_name,
            user_age=s_user_age,
            address=s_address,
            phone_number=s_phone_number,
            date_time = s_date_time,
            seminar = s_price,
            user_id=update.effective_user.id
        ) 
    elif s_theme == 'Konsultatsiya':
        seminar = Consultation.objects.create(
            first_name = s_first_name,
            last_name = s_last_name,
            user_age=s_user_age,
            address=s_address,
            phone_number=s_phone_number,
            date_time = s_date_time,
            user_id=update.effective_user.id
        ) 




    return done_mess(update,context,fullname, s_user_age,s_phone_number, s_address, s_price, s_date_time,s_theme)


def done_mess(update,context,fullname, s_user_age,s_phone_number, s_address, s_price, s_date_time, s_theme):
    user_lang = check_user_lang(update)
    if user_lang == 'uz_latin':
        update.message.reply_text(
        'Murojaatingiz qabul qilindi. Tez orada aloqaga chiqamiz')
        user_lang = 'O`zbekcha'
    elif user_lang == 'ru':
        user_lang = 'Ruscha'
        update.message.reply_text('Ваш запрос принят. Мы свяжемся с вами в ближайшее время')
    print(context.chat_data)
    context.bot.send_message(chat_id = group_id, text=f'<b>🛎 Yangi ishtirokchi 🛎</b>\n<b>Mavzu:</b> {s_theme}\n<b>To`liq ismi:</b> {fullname}\n<b>Yoshi:</b> {s_user_age}\n<b>Telefon raqami:</b> {s_phone_number}\n<b>Manzili:</b> {s_address},\n<b>Muloqat tili:</b> {user_lang},\n<b>Username:</b> {update.effective_user.name},\n<b>Yo`nalish:</b> {s_price},\n<b>Murojaat vaqti:</b> {s_date_time}',parse_mode=ParseMode.HTML)
    
    return menu_handler(update, context)


def appeal_handler(update: Update, context: CallbackContext):
    dt = datetime.now()
    cd = context.chat_data
    appeal = Appeal.objects.create(
        first_name=cd['first_name'][0:255],
        last_name=cd['last_name'][0:255],
        kupon=cd['new_kupon'][0:255],
        kupon_sale=cd['new_kupon_sale'][0:255],
        phone_number=cd['phone_number'][0:63],
        date_time = dt.strftime(f"%Y-%m-%d %H:%M:%S"),
        user_id=update.effective_user.id
    )
    fullname = f'{cd["first_name"][0:255]} {cd["last_name"][0:255]}'
    phone = cd['phone_number'][0:63]
    phone = cd['phone_number'][0:63]
    new_kupon = cd['new_kupon'][0:63]
    new_kupon_sale = cd['new_kupon_sale'][0:63]
    dtime = dt.strftime(f"%Y-%m-%d %H:%M:%S")

    # context.bot.forward_message( )
    context.bot.send_message(chat_id = group_id, text=f'<b>🔔 Chegirma kuponi olindi ✔️</b>\n\n<b>👤 Xaridor:</b> {fullname}\n<b>📲 Telefon raqami:</b> {phone}\n<b>🔑 Chegirma kuponi:</b> {new_kupon}\n<b>💰 Chegirma foizi:</b> {new_kupon_sale}%\n<b>⏱Chegirma olingan vaqt:</b> {dtime}',parse_mode=ParseMode.HTML)

    update.message.reply_text(
        'Yoqimli haridlar:)')
    return menu_handler(update, context)


def send_file(update: Update, context: CallbackContext, db_type):
    appeals = ''
    if db_type == 'course_users':
        appeals = Appeal.objects.all()
        workbook = xlsxwriter.Workbook(f'Barcha_xaridorlar_kurs_boyicha.xlsx')
    elif db_type == 'seminar_users':
        appeals = Seminars.objects.all()
        workbook = xlsxwriter.Workbook(f'Barcha_xaridorlar_seminar_boyicha.xlsx')
    elif db_type == 'consultation_users':
        appeals = Consultation.objects.all()
        workbook = xlsxwriter.Workbook(f'Barcha_xaridorlar_konsultatsiya_boyicha.xlsx')
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': 1})
    wrap = workbook.add_format({'text_wrap': True})
    worksheet.set_column(1, 5, 25,wrap)
    worksheet.write('A1', 'Xaridor', bold)
    worksheet.write('B1', 'Ismi', bold)
    worksheet.write('C1', 'Familiyasi', bold)
    worksheet.write('D1', 'Telefon raqami', bold)
    worksheet.write('E1', 'Yoshi', bold)
    if db_type == 'course_users':
        worksheet.write('F1', 'Tarifi', bold)
    elif db_type == 'seminar_users':
        worksheet.write('F1', 'Mavzu', bold)
    elif db_type == 'consultation_users':
        worksheet.write('F1', 'Yo`nalish', bold)
    worksheet.write('G1', 'Manzili', bold)
    worksheet.write('H1', 'Murojaat vaqti', bold)
    worksheet.write('I1', 'User ID', bold)
    row = 1
    col = 0
    for appeal in appeals:
        worksheet.write_string(row, col, f'{row}')
        worksheet.write_string(row, col+1, appeal.first_name)
        worksheet.write_string(row, col+2, appeal.last_name)
        worksheet.write_string(row, col+3, appeal.phone_number)
        worksheet.write_string(row, col+4, appeal.user_age)
        if db_type == 'course_users':
            worksheet.write_string(row, col+5, appeal.price)
        elif db_type == 'seminar_users':
            worksheet.write_string(row, col+5, appeal.seminar)
        elif db_type == 'consultation_users':
            worksheet.write_string(row, col+5, 'Konsultatsiya')
        worksheet.write_string(row, col+6, appeal.address)
        worksheet.write_string(row, col+7, appeal.date_time)
        worksheet.write_string(row, col+8, str(appeal.user_id))
        row += 1
    worksheet.write(row, 0, 'Umumiy xaridorlar soni', bold)
    worksheet.write(row, 2, f'{row-1}', bold)
    workbook.close()
    if db_type == 'course_users':
        context.bot.send_document(chat_id = group_id, document=open('Barcha_xaridorlar_kurs_boyicha.xlsx', 'rb'))
        os.remove('Barcha_xaridorlar_kurs_boyicha.xlsx')
    elif db_type == 'seminar_users':
        context.bot.send_document(chat_id = group_id, document=open('Barcha_xaridorlar_seminar_boyicha.xlsx', 'rb'))
        os.remove('Barcha_xaridorlar_seminar_boyicha.xlsx')
    elif db_type == 'consultation_users':
        context.bot.send_document(chat_id = group_id, document=open('Barcha_xaridorlar_konsultatsiya_boyicha.xlsx', 'rb'))
        os.remove('Barcha_xaridorlar_konsultatsiya_boyicha.xlsx')


def send_notification(update, context, anons_text):
    all_users = users.objects.all()
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


def new_anons(update: Update, context: CallbackContext):
    text = update.message.text
    flag, user = send_notification(update, context, text)
    if flag:
        update.message.reply_text(
        f'Xabar {user} ta foydalanuvchiga muvaffaqiyatli tarzda yetkazildi✅')
        return menu_handler(update, context)


def notification(update: Update, context: CallbackContext):
    lang = check_user_lang(update)
    text = ''
    if lang == 'uz_latin':
        text = 'Xabar matnini kiriting.\n<b>ParseMode:</b><i> HTML</i>'
    elif lang =='ru':
        text = 'Введите текст сообщения.\n<b>ParseMode:</b><i> HTML</i>'
    admin = is_admin(update,context)
    if admin:
        update.message.reply_text(f'{text}',parse_mode=ParseMode.HTML)
        return ANONS
    else:
        return menu_handler(update, context)


def stop_handler(update: Update, context: CallbackContext):
    update.message.reply_text('Hayr!', reply_markup=ReplyKeyboardRemove())

def remove_user(update,context):
    m = context.bot.kick_chat_member(
        chat_id=channel_id, 
        user_id='1261601625',
        # timeout=int(time.time() + 5)
        )
    update.message.reply_text('<b>TUGADIII</b>',parse_mode=ParseMode.HTML)

def group(update: Update, context: CallbackContext):
    arg = update.message.text
    if arg == '/course_users':
        send_file(update,context, 'course_users')
    elif arg == '/seminar_users':
        send_file(update,context, 'seminar_users')
    elif arg == '/consultation_users':
        send_file(update,context, 'consultation_users')
    elif arg == '/remove_user':
        return remove_user(update,context)
    elif arg == '/users':
        all_users = users.objects.all()
        update.message.reply_text(f'Ayni vaqtgacha @mashuqaning_sirlari_robot botidan <b>{len(all_users)}</b> ta foydalanuvchi ro`yhatdan o`tgan',parse_mode=ParseMode.HTML)
        
    # is_reply = update.message.reply_to_message is not None
    # if is_reply:
    #     sent_dt = update.message.reply_to_message.text[-19:]
    #     print('==================')
    #     all_text = update.message.reply_to_message.text.split('\n')
    #     phone_num = all_text[3][-13:]
    #     print(phone_num)
    #     print('==================')
    #     appeals = Appeal.objects.order_by('id').filter(date_time=sent_dt).filter(phone_number=phone_num)[::]
    #     appeal = ''
    #     user_id = ''
    #     full_name = ''
    #     dtime = ''
    #     for i in appeals:
    #         appeal = i.appeal
    #         user_id = i.user_id
    #         full_name = f'{i.first_name} {i.last_name}'
    #         dtime = i.date_time
    #     context.bot.send_message(chat_id = user_id, text=f"Assalomu alaykum, hurmatli <b>{full_name}</b> \nSizni <b>{dtime}</b> dagi murojaatingizga asosan, <b>{arg}</b>",parse_mode=ParseMode.HTML)

    # return dispatcher.add_handler(MessageHandler(Filters.text('/stat'),send_file))
def release_member(context):
    user_id = context.job.context['user_id']
    chat_id = context.job.context['chat_id']
    context.bot.kick_chat_member(chat_id, user_id)
    context.bot.send_message(chat_id, f"User {user_id} has been automatically released due to inactivity.")

def new_member(update, context):
    join_date = datetime.datetime.fromtimestamp(update.message.date)
    release_date = join_date + datetime.timedelta(seconds=5)
    current_date = datetime.datetime.now()

    if current_date >= release_date:
        context.bot.kick_chat_member(update.message.chat_id, update.message.from_user.id)
        context.bot.send_message(update.message.chat_id, f"User {update.message.from_user.id} has been automatically released due to inactivity.")
    else:
        job = context.job_queue.run_once(release_member(context), release_date - current_date, context={'user_id': update.message.from_user.id, 'chat_id': update.message.chat_id})
        context.chat_data['job'] = job

dispatcher.add_handler(MessageHandler(Filters.group, group))
dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))
dispatcher.add_handler(ConversationHandler(
    
    entry_points=[
        CallbackQueryHandler(ru_lang_edit, pattern='rus'),
        CallbackQueryHandler(uz_latin_lang_edit, pattern='uz_latin'),
        CallbackQueryHandler(test_cheking, pattern='check_channel'),
        MessageHandler(Filters.private, start_handler)],
        

    states={
        

        MENU_STATE: [
            CallbackQueryHandler(ru_lang_edit, pattern='rus'),
            CallbackQueryHandler(uz_latin_lang_edit, pattern='uz_latin'),
            CallbackQueryHandler(use_bot, pattern='use_bot'),
            MessageHandler(Filters.regex((r'^Mashuqaning sirlari$')),
                           mashuqaning_sirlari),
            MessageHandler(Filters.regex((r'^Seminarlar$|^Семинары$')),
                           seminars_list),
            MessageHandler(Filters.regex((r'^⚙️Sozlash$|^⚙️Настройка$')),
                           setting),
            MessageHandler(Filters.regex((r'^🆘Yordam$|^🆘Помощь$')),
                           help_me),
            MessageHandler(Filters.regex((r'^Konsultatsiya|^Консультация$')),
                           consultation),
            MessageHandler(Filters.regex(
                r'^Obunachilarga xabar yuborish$|^Отправляйте сообщения подписчикам$'), notification),
            MessageHandler(Filters.all, menu_handler)
        ],
       

        PHONE_STATE: [
            MessageHandler(Filters.text & Filters.entity(
                MessageEntity.PHONE_NUMBER), phone_entity_handler),
            MessageHandler(Filters.contact, phone_contact_handler),
            MessageHandler(Filters.all, phone_resend_handler),
        ],


        MARKET_MENU: [
            MessageHandler(Filters.regex((r'^"O`zim" tarifi$|^Тариф "O`zim"$|^"Kurator" tarifi$|^Тариф "Куратор"$|^Тариф "VIP"$|^"VIP" tarifi$')),
                           price_1),
            MessageHandler(Filters.regex((r'^🔙 Orqaga$|^🔙 Назад$')),
                           market_back),
            MessageHandler(Filters.all, market_handler)
            
        ],


        SEMINARS_MENU: [
            MessageHandler(Filters.regex((r'^"Hayotga qayt" seminari$|^Семинар "Hayotga qayt"$|^"Turmushdagi xatolar" seminari$|^Семинар "Turmushdagi xatolar"$|^Семинар "Shishadagi qiz"$|^"Shishadagi qiz" seminari$|^Семинар "Hayot bilan raqs"$|^"Hayot bilan raqs" seminari$')),
                           seminars_handler),
            MessageHandler(Filters.regex((r'^🔙 Orqaga$|^🔙 Назад$')),
                           market_back),
            MessageHandler(Filters.all, market_handler)
            
        ],
        

        ALL_SALE: [
            MessageHandler(Filters.regex((r'^Начать покупки$|^Xaridni boshlash$')),
                           new_sale_handler),
            MessageHandler(Filters.regex((r'^🔙 Orqaga$|^🔙 Назад$')),
                           market_back_equ),
            MessageHandler(Filters.all, market_handler)
            
        ],


        ALL_SALE_SEM: [
            MessageHandler(Filters.regex((r'^Начать покупки$|^Xaridni boshlash$')),
                           new_sale_handler),
            MessageHandler(Filters.regex((r'^🔙 Orqaga$|^🔙 Назад$')),
                           seminar_back_equ),
            MessageHandler(Filters.all, market_handler)  
        ],


        ALL_SALE_CONS: [
            MessageHandler(Filters.regex((r'^Начать покупки$|^Xaridni boshlash$')),
                           new_sale_handler),
            MessageHandler(Filters.regex((r'^🔙 Orqaga$|^🔙 Назад$')),
                           market_back),
            MessageHandler(Filters.all, market_handler)  
        ],


        FIRST_NAME_STATE: [
            MessageHandler(Filters.text, first_name_handler),
            MessageHandler(Filters.all, new_sale_handler),
        ],


        LAST_NAME_STATE: [
            MessageHandler(Filters.text, last_name_handler),
            MessageHandler(Filters.all, last_name_resend_handler),
        ],


        AGE_STATE: [
            MessageHandler(Filters.regex(r'^(1[6-9]|[2-9]\d)$'), age_handler),
            MessageHandler(Filters.all, user_age_resend_handler),
        ],


        ADDRESS_STATE: [
            MessageHandler(Filters.text, address_handler),
            MessageHandler(Filters.all, address_resend_handler),
        ],


        PHONE_STATE: [
            MessageHandler(Filters.text & Filters.entity(
                MessageEntity.PHONE_NUMBER), phone_entity_handler),
            MessageHandler(Filters.contact, phone_contact_handler),
            MessageHandler(Filters.all, phone_resend_handler),
        ],


        ADDRESS_STATE: [
            MessageHandler(Filters.text, address_handler),
            MessageHandler(Filters.all, address_resend_handler),
        ],


        ANONS: [
            MessageHandler(Filters.text , new_anons),
            MessageHandler(Filters.all, new_anons_resend_handler)
        ],
    },

    fallbacks=['stop', stop_handler],

))

updater.start_polling(timeout=600)
updater.idle()
