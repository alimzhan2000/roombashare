#-*-coding: utf-8-*-

import telebot
import time
import urllib
from telebot import types
from database import SQL
from users import Seeker
import photos

token = "1012075393:AAFXyQtFOdrH7mPxeV2QmSX2otYfrEi-aRA" #testbot
bot = telebot.TeleBot(token)
db = SQL()
allvars = {}

class Settings:
	def __init__(self):
		self.mode = 0
		self.cur_profile = 0
		self.change_st = 0
		self.last_mess_id = 0
		self.seeker = Seeker()
		self.profiles = ""
		self.seeker_st = False
		self.seeker_search_st = False
		self.search_profile = False
		self.feedback_st = False		
def add_new_user(chat_id):
	global allvars
	if chat_id in allvars.keys():
		return 
	a = Settings()
	allvars[chat_id] = a
def default_vars(chat_id):
	global allvars
	allvars[chat_id] = Settings()

@bot.message_handler(commands = ['start'])
def start(message):
	add_new_user(message.chat.id)
	default_vars(message.chat.id)
	keyboard = types.ReplyKeyboardMarkup(True, False)
	keyboard.row('Создать объявление\n и начать поиск', 'Быстрый поиск')
	keyboard.row('Мои объявления', 'Обратная связь')
	bot.send_message(message.chat.id, 'Привет👋 \n\nМеня зовут Roomba - бот для подбора тебе идеальных соседей для совместной аренды жилья🏠, а также поиска людей для подселения👪\n\n Для начала нашей работы выбери что ты хочешь сделать: \n▶ Создать объявление \n▶ Совершить быстрый поиск \n▶ Изменить или просмотреть свое объявление, \n▶ Оставить свою обратную связь по моей работе, это поможет мне стать лучше', reply_markup=keyboard)

@bot.message_handler(commands = ['menu'])
def main_menu(message):
	default_vars(message.chat.id)
	keyboard = types.ReplyKeyboardMarkup(True, False)
	keyboard.row('Создать объявление\n и начать поиск', 'Просмотреть объявления')
	keyboard.row('Мои объявления', 'Обратная связь')
	bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard)

def profile_info(profile):
	if profile[20] == True:
		text = '*Ищет людей для подселения в свою квартиру*\n*Расположение квартиры:* ' + profile[9] + ' район\n\n'
	else:
		text = ''
	if profile[2] > 1000:
		age = str(int(profile[2]/100)) + '-' + str(profile[2]%100)
	else:
		age = str(profile[2])
	age += ' лет'
	if profile[5] == 'student':
		work = '*Студент.* Учится в '
	else:
		work = '*Работник.* Работает в сфере '
	place = ""
	if profile[8] == 'Казахский':
		place = 'Говорит на казахском'
	elif profile[8] == 'Русский':
		place = 'Говорит на русском'
	else:
		place = 'Говорит и на казахском, и на русском'
	text += '*Имя:* '+ profile[1] + '\n' + '*Возраст:* ' + str(age) + '\n' + \
			'*Родом с* '+ profile[3] + '\n' + '*Пол:* ' + profile[4] + '\n' + work + \
			profile[6] + '\n' + '*Режим работы:* '+ profile[7] + '\n' + place + '\n' + \
			'*Вредные привычки: *' + profile[18] + '\n' + '*О себе:* ' + profile[13]
	if profile[19] is not None:
		text += '\n@'+profile[19]
	return text

@bot.message_handler(func=lambda message:message.text is not None and len(message.text) > 6 and message.text[:7] == '/advert')
def adverts(message):
	if message.text[7] == '1':
		profile_id = message.text[8:]
		profile = db.get_profile_by_id(profile_id)
		cap = profile_info(profile)
		photo_id = db.get_profile_photo(profile[0])
		keyboard = types.InlineKeyboardMarkup()
		button = types.InlineKeyboardButton('Изменить объявление', callback_data = 'change_profile')
		keyboard.add(button)
		button = types.InlineKeyboardButton('Удалить объявление', callback_data = 'delete_profile')
		keyboard.add(button)
		if photo_id == '0':
			bot.send_message(message.chat.id, cap, reply_markup = keyboard, parse_mode = 'Markdown')
		else: 
			photo = photos.download_photo(photo_id)
			bot.send_photo(message.chat.id, photo, caption = cap, reply_markup=keyboard, parse_mode = 'Markdown')
	elif message.text[7] == '2':
		flat_id = message.text[8:]
		flat = db.get_flat_by_id(flat_id)
		keyboard = types.InlineKeyboardMarkup()
		cap = '*Расположение квартиры:* '+ flat[1] + ' район, ' + flat[2] + '\n' + \
		 '*Цена аренды:* '+ str(flat[3]) + '\n' + '*Количество комнат:* ' + str(flat[4]) + '\n' + \
		 '*Количество спальных мест:* ' + str(flat[5]) + '\n' + '*Стоимость аренды на одного человека:*' + str(flat[6]) + \
		 '\n' + '*Описание:* '+ flat[7] + '\n' + '*Номер телефона:* ' + flat[8]
		photo_id = db.get_flat_photo_file_id(flat[0])
		if photo_id == '0':
			bot.send_message(message.chat.id, cap, parse_mode = 'Markdown')
		else: 
			photo = photos.download_photo(photo_id)
			bot.send_photo(message.chat.id, photo, caption = cap, parse_mode = 'Markdown')

@bot.message_handler(func=lambda message:message.text is not None and len(message.text) > 6 and message.text[:7] == '/delete')
def delete_ads(message):
	if message.text[7] == '2':
		flat_id = message.text[8:]
		db.offerer_delete(flat_id)
		bot.send_message(message.chat.id, 'Твое объявление удалено. Но ты всегда можешь создать новое!')

@bot.callback_query_handler(func=lambda call:True)
def callback(call):
	global allvars
	add_new_user(call.message.chat.id)
	u = allvars[call.message.chat.id]
	if call.message:
		if call.data == 'profile_next' or call.data == 'profile_prev' or call.data == 'rematch_profiles':
			bot.delete_message(call.message.chat.id, call.message.message_id)
			if call.data == 'rematch_profiles':
				profile = db.get_profile(call.message.chat.id)
				seeker = Seeker(profile)
				u.profiles = db.get_profiles_by_filters(seeker)
			if call.data == 'profile_prev':
				u.cur_profile -= 2
			if u.profiles is None or u.cur_profile >= len(u.profiles) or u.cur_profile < 0:
				bot.send_message(call.message.chat.id, 'Упс. Похоже ты у нас первый клиент🙀!Подожди немного или попробуй через некоторое время')
				return
			profile = u.profiles[u.cur_profile]
			u.cur_profile += 1
			keyboard = types.InlineKeyboardMarkup()
			if u.cur_profile + 1 <= len(u.profiles) and u.cur_profile > 1:
				button1 = types.InlineKeyboardButton('Следующий >>', callback_data = 'profile_next')
				button2 = types.InlineKeyboardButton('<< Предыдущий', callback_data = 'profile_prev')
				keyboard.row(button2, button1)
			elif u.cur_profile > 1:
				button = types.InlineKeyboardButton('<< Предыдущий профиль', callback_data = 'profile_prev')
				keyboard.add(button)
			elif u.cur_profile + 1 <= len(u.profiles):
				button = types.InlineKeyboardButton('Следующий профиль >>', callback_data = 'profile_next')
				keyboard.add(button)
			cap = profile_info(profile)
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.send_message(call.message.chat.id, cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				photo = photos.download_photo(photo_id)
				bot.send_photo(call.message.chat.id, photo, caption = cap, reply_markup = keyboard, parse_mode = 'Markdown')
		elif call.data == 'delete_profile':
			db.seeker_delete(str(call.message.chat.id))
			bot.delete_message(call.message.chat.id, call.message.message_id)
			bot.send_message(call.message.chat.id, '*Объявление удалено.*', parse_mode = 'Markdown')
		elif call.data == 'change_profile':
			keyboard = types.InlineKeyboardMarkup()
			button1 = types.InlineKeyboardButton('Изменить Имя', callback_data = 'change_name')
			button2 = types.InlineKeyboardButton('Изменить Возраст', callback_data = 'change_age')
			button3 = types.InlineKeyboardButton('Изменить \nОткуда Родом', callback_data = 'change_homeland')
			button4 = types.InlineKeyboardButton('Изменить О себе', callback_data = 'change_desc')
			button5 = types.InlineKeyboardButton('🔙Назад в меню', callback_data='')
			keyboard.row(button1, button2)
			keyboard.row(button3, button4)
			keyboard.row(button5)
			bot.edit_message_reply_markup(chat_id = call.message.chat.id, message_id = call.message.message_id, reply_markup = keyboard)
		elif call.data == 'change_name':
			bot.send_message(call.message.chat.id, 'Хмм. Надеюсь ты в розыск не попал) Введи свое новое имя')
			u.change_st = 1
			u.last_mess_id = call.message.message_id
		elif call.data == 'change_age':
			bot.send_message(call.message.chat.id, 'У кого-то день рождение? Введи свой новый возраст\n(целое число)')
			u.change_st = 2
			u.last_mess_id = call.message.message_id
		elif call.data == 'change_homeland':
			bot.send_message(call.message.chat.id, 'Введи свое новое место откуда ты родом\n(регион, город)')
			u.change_st = 3
			u.last_mess_id = call.message.message_id
		elif call.data == 'change_desc':
			bot.send_message(call.message.chat.id, 'Появились новые интересы? Буду рад о них услышать')
			u.change_st = 4
			u.last_mess_id = call.message.message_id

@bot.message_handler(content_types = ['text'])
def name_insert_data(message):
	global allvars
	add_new_user(message.chat.id)
	u = allvars[message.chat.id]
	if message.text == 'Создать объявление\n и начать поиск':
		chat_id = str(message.chat.id)
		if db.seeker_check_chat_id(chat_id) == True:
			keyboard = types.InlineKeyboardMarkup()
			button = types.InlineKeyboardButton('Просмотреть профили людей', callback_data = 'rematch_profiles')
			keyboard.add(button)
			bot.send_message(message.chat.id, 'Привет мой старый друг! Так как у тебя уже есть активное объявление можешь сразу просмотреть профили. '
			'Если ты хочешь что-то изменить или удалить свое объявление, переходи в раздел *\'Мои объявления\'*'
			' в главном меню (/menu).', reply_markup = keyboard, parse_mode = 'Markdown')
			return
		keyboard = types.ReplyKeyboardMarkup(True, False)
		keyboard.row('🔙Назад в меню')
		bot.send_message(message.chat.id, 'Хээй🙌 Давай начнем наше знакомство и заодно заполним тебе анкету', reply_markup=keyboard)
		time.sleep(1)
		bot.send_message(message.chat.id, 'Для начала скажи свое имя')
		u.seeker_search_st = True
		u.mode = 1
	elif message.text == '🔙Назад в меню':
		default_vars(message.chat.id)
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Создать объявление\n и начать поиск', 'Быстрый поиск')
		keyboard.row('Мои объявления', 'Обратная связь')
		bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard)
	elif message.text == 'Быстрый поиск':
		u.search_profile = True
		u.mode = 1
		u.seeker = Seeker()
		bot.send_message(message.chat.id, 'Для более эффективного поиска указажи район города и желаемую стоимость аренды')
		time.sleep(1)
		keyboard = types.ReplyKeyboardMarkup(True, True)
		keyboard.row('Алматинский', 'Байконурский')
		keyboard.row('Есильский', 'Сарыаркинский')
		keyboard.row('🔙Назад в меню')
		bot.send_message(message.chat.id, 'Для начала укажи желаемый район', reply_markup = keyboard)
	elif message.text == 'Мои объявления':
		profile = db.get_profile(message.chat.id)
		if profile is None:
			bot.send_message(message.chat.id, 'У тебя нет активных объявлений')
			return
		text = '*Твои объявления*\n\n'
		if profile is not None:
			text += '*Поиск квартиры*\n'
			text += '📄Подробнее: /advert1' + str(profile[0]) + '\n\n'
		bot.send_message(message.chat.id, text, parse_mode = 'Markdown')
	elif message.text == 'Обратная связь' or u.feedback_st == True:
		if u.feedback_st == False:
			u.feedback_st = True
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Оставь свой отзыв или предложение, отправив мне сообщение!', reply_markup=keyboard)
		else:
			bot.send_message(259442131, str(message.text) + '\nот ' + str(message.from_user.last_name) + ' ' + str(message.from_user.first_name) + ' @' + str(message.from_user.username))
			default_vars(259442131)
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Создать объявление\n и начать поиск', 'Быстрый поиск')
			keyboard.row('Мои объявления', 'Обратная связь')
			bot.send_message(message.chat.id, 'Спасибо за оставленный отзыв!', reply_markup=keyboard)
	elif u.seeker_st == True or u.seeker_search_st == True:	
		if u.mode == 1:
			u.seeker.chat_id = message.chat.id
			u.seeker.name = message.text
			u.mode = 2
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Приятно познакомиться :) Теперь укажи свой возраст(извини если грубо - это нужно)', reply_markup = keyboard)
		elif u.mode == 2:
			age = message.text
			if not age.isdigit() or int(age) > 110 or int(age) < 14:
				bot.send_message(message.chat.id, 'Вводи целое число')
				return
			u.seeker.age = int(age)
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Так, с возрастом закончили. Кстати, хотел у тебя еще узнать, с какого ты города или региона приехал/а?', reply_markup=keyboard)
		elif u.mode == 3:
			u.seeker.homeland = message.text
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Мужcкой', 'Женский')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Вау, я тоже оттуда! Мы с тобой земляки😏 Теперь укажи свой пол', reply_markup = keyboard)
		elif u.mode == 4:
			if message.text == 'Мужской':
				u.seeker.gender = 'Мужской'
			elif message.text == 'Женский':
				u.seeker.gender = 'Женский'
			else:
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('Мужской', 'Женский')
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'Упс, что-то не вышло. Выбери еще раз. Только воспользуйся кнопочками внизу ("Мужской", "Женский")', reply_markup = keyboard)
				return
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Учусь', 'Работаю', 'Не учусь и не работаю')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Хотел у тебя еще спросить твой основной род деятельности. Ты пока учишься или уже работаешь? \nЕсли находишься в поиске самого себя - это тоже прекрасно! Можешь нажать кнопку одну из трех:', reply_markup = keyboard)
		elif u.mode == 5:
			keyboard = types.ReplyKeyboardMarkup(True, True)
			if message.text == 'Учусь':
				u.seeker.worker_or_student = 'student'
				keyboard.row('🔙Назад в меню')
				keyboard.row('Astana IT University', 'Университет "Астана"')
				keyboard.row('КАЗАТУ им. Сейфуллина', 'Назарбаев Университет')
				keyboard.row('Евразийский НУ', 'Университет КАЗГЮУ')
				keyboard.row('Медицинкий университет Астаны', 'Филиал МГУ в Казахстане')
				keyboard.row('Другое...')
				bot.send_message(message.chat.id, 'Ух ты. Люблю образованных людей🎓 В каком заведнии ты учишься?', reply_markup=keyboard)
			elif message.text == 'Работаю':
				u.seeker.worker_or_student = 'worker'
				keyboard.row('🔙Назад в меню')
				keyboard.row('Строительство', 'Торговля')
				keyboard.row('IT', 'Образование')
				keyboard.row('Госслужба', 'Финансы')
				keyboard.row('Предприниматель', 'Услуги')
				keyboard.row('Другое...')
				bot.send_message(message.chat.id, 'Ух ты. Люблю деловых людей! В какой сфере ты работаешь?', reply_markup=keyboard)
			elif message.text == 'Не учусь и не работаю':
				u.seeker.worker_or_student = 'neither'
				u.mode += 2
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('Казахский', 'Русский', 'Оба языка')
				keyboard.row('Назад в меню')
				bot.send_message(message.chat.id, 'На каких языках ты умеешь говорить?', reply_markup=keyboard)
			else:
				bot.send_message(message.chat.id, 'Хээй! Вводи пожалуйста с клавиатуры. Я просто по-другому не понимаю😓')
				return
			u.mode += 1
		elif u.mode == 6:
			status = u.seeker.worker_or_student
			if message.text == 'Другое...':
				if status == 'student':
					bot.send_message(message.chat.id, 'Напиши название своего места обучения')
				elif status == 'worker':
					bot.send_message(message.chat.id, 'Напиши сферу деятельности, в которой ты работаешь')
			else:
				u.seeker.study_or_work_place = message.text
				u.mode += 1
				keyboard = types.ReplyKeyboardMarkup(True, True)
				if status == 'student':
					keyboard.row('С утра до вечера')
					keyboard.row('С обеда до вечера','С утра до обеда')
					keyboard.row('🔙Назад в меню')
					bot.send_message(message.chat.id, 'Какой у тебя режим учебы или работы? В какое время ты занят/а?', reply_markup=keyboard)
				elif status == 'worker':
					keyboard.row('С утра до вечера', 'С утра до обеда')
					keyboard.row('Ночью', 'Вахтовые смены')
					keyboard.row('Через день/два', '🔙Назад в меню')
					bot.send_message(message.chat.id, 'Теперь мне нужно знать в какое время ты работаешь, чтобы и тебе и соседям было удобнее всего жить вместе', reply_markup=keyboard)
		elif u.mode == 7:
			u.seeker.sleeping_mode = message.text
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Казахский', 'Русский', 'Оба языка')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Так, половину пути мы с тобой уже прошли. Осталось еще немного. \n Укажи языки, на которых ты умеешь говорить:', reply_markup=keyboard)
		elif u.mode == 8:
			lang = message.text
			if lang == 'Казахский' or lang == 'Русский' or lang == 'Оба языка': 
				u.seeker.langs = message.text
				u.mode += 1
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('Курю/Не пью', 'Не курю/Пью')
				keyboard.row('Не курю/Не пью', 'Курю/Пью')
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'Надеюсь у тебя их нет, но все же мне нужно знать о твоих вредных привычках🚬', reply_markup=keyboard)
			else:
				bot.send_message(message.chat.id, 'Выбирай кнопочки пожалуйста) Я по-другому не понимаю😓')
				return
		elif u.mode == 9:
			u.seeker.bad_habits = message.text
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Людей', 'Жилье')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Самый главный вопрос! Ты ищещь людей к себе на подселение или ищешь жилье для совместной аренды?', reply_markup=keyboard)
		elif u.mode == 10:
			if message.text == 'Людей':
				u.seeker.hata = True
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('Алматинский', 'Байконурский')
				keyboard.row('Есильский', 'Сарыаркинский')
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'В каком районе находится твоя квартира/дом🏡?', reply_markup = keyboard)
			elif message.text == 'Жилье':
				u.seeker.hata = False
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('Алматинский', 'Байконурский')
				keyboard.row('Есильский', 'Сарыаркинский')
				keyboard.row('🔙Назад в меню')
				bot.send_message(message.chat.id, 'Укажи желаемый район города', reply_markup = keyboard)
			else:
				bot.send_message(message.chat.id, 'Неправильный ввод.\n(Да/Нет)')
				return
			u.mode += 1
		elif u.mode == 11:
			distr = message.text
			if distr == 'Алматинский' or distr == 'Байконурский' or distr == 'Есильский' or distr == 'Сарыаркинский':
				u.seeker.distr = message.text
				u.mode += 1
				if u.seeker.hata == True:
					u.mode += 2
					keyboard = types.ReplyKeyboardMarkup(True, True)
					keyboard.row('до 20.000 тенге', 'от 20.000 до 30.000 тенге')
					keyboard.row('от 30.000 до 40.000 тенге', 'от 40.000 до 50.000 тенге')
					keyboard.row('выше 50.000 тенге', '🔙Назад в меню')
					bot.send_message(message.chat.id, 'Вау, этой мою самый любимый район! Сколько ты хочешь брать арендную плату с одного человека?', reply_markup=keyboard)
				else:	
					bot.send_message(message.chat.id, 'Уточни возле какого здания тебе бы хотелось найти жилье(название \
					микрорайона, магазин🏪, бизнес-центр🏢, пересечение улиц, достопримечательность🏯)')
			else:
				bot.send_message(message.chat.id, 'Хээй. Выбирай с кнопочками. Я по-другому не понимаю :(')
		elif u.mode == 12:
			u.seeker.near_what = message.text
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('до 20.000 тенге', 'от 20.000 до 30.000 тенге')
			keyboard.row('от 30.000 до 40.000 тенге', 'от 40.000 до 50.000 тенге')
			keyboard.row('выше 50.000 тенге', '🔙Назад в меню')
			bot.send_message(message.chat.id, 'Желательная цена', reply_markup=keyboard)
		elif u.mode == 13:
			u.seeker.price = message.text
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('Отдельную комнату', 'Можно с кем-нибудь в комнате')
			keyboard.row('Оба варианта')
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Все, осталось еще три шага... Как тебе комфортнее жить: с кем-то или отдельно?', reply_markup=keyboard)
			u.mode += 1
		elif u.mode == 14:
			if u.seeker.hata == True:
				u.seeker.price = message.text
			else:
				u.seeker.seeking_for = message.text
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Теперь я хочу узнать по больше о твоих интересах🎤, хобби🏀, что любишь читать🎒, какие фильмы смотреть🎥. Люблю знакомиться с интересными личностями😊',reply_markup=keyboard)
		elif u.mode == 15:
			u.seeker.interest = message.text
			u.mode += 1
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Теперь введи свой номер телефона. P.S. Не переживай, я тебе не буду писать:)\n(следуй этому примеру: 8-ххх-ххх-хх-хх)', reply_markup=keyboard)
		elif u.mode == 16:
			num = message.text
			digits = 0
			correct = True
			for a in num:
				if a.isdigit():
					digits += 1
				elif a != '-':
					correct = False
			if digits != 11:
				correct = False
			if not correct:
				bot.send_message(message.chat.id, 'Вводи следуя этому примеру: 8-ххх-ххх-хх-хх')
				return
			u.seeker.phone_num = message.text
			keyboard = types.ReplyKeyboardMarkup(True, True)
			keyboard.row('🔙Назад в меню')
			bot.send_message(message.chat.id, 'Отправь своё селфи. Хочу увидеть тебя вживую. Только не стесняйся :з ', reply_markup=keyboard)
			u.mode += 1
		elif u.mode == 17:
			bot.send_message(message.chat.id, 'Загрузи фотографию')
	elif u.search_profile == True:
		if u.mode == 1:
			distr = message.text
			if distr == 'Алматинский' or distr == 'Байконурский' or distr == 'Есильский' or distr == 'Сарыаркинский':
				u.seeker.distr = message.text
				u.mode += 1
				keyboard = types.ReplyKeyboardMarkup(True, True)
				keyboard.row('до 20.000 тенге', 'от 20.000 до 30.000 тенге')
				keyboard.row('от 30.000 до 40.000 тенге', 'от 40.000 до 50.000 тенге')
				keyboard.row('выше 50.000 тенге', '🔙Назад в меню')
				bot.send_message(message.chat.id, 'Теперь укажи желаемую стоимость аренды.', reply_markup=keyboard)
			else:
				bot.send_message(message.chat.id, 'Извини, но тебе нужно выбирать с помощью кнопочек')
		elif u.mode == 2:
			u.seeker.price = message.text
			u.seeker.chat_id = message.chat.id
			u.seeker.hata = None
			u.profiles = db.get_profiles_by_filters(u.seeker)
			u.seeker = Seeker()
			u.search_profile = False
			u.mode = 0
			if u.profiles is None or u.cur_profile >= len(u.profiles) or u.cur_profile < 0:
				bot.send_message(message.chat.id, 'Так, видно ты у нас самый первый! Подожди немного, пока придут еще люди. С таким интересным человеком думаю все захотят жить)')
				return
			profile = u.profiles[u.cur_profile]
			u.cur_profile += 1
			keyboard = types.InlineKeyboardMarkup()
			if u.cur_profile + 1 <= len(u.profiles) and u.cur_profile > 1:
				button1 = types.InlineKeyboardButton('Следующий >>', callback_data = 'profile_next')
				button2 = types.InlineKeyboardButton('<< Предыдущий', callback_data = 'profile_prev')
				keyboard.row(button2, button1)
			elif u.cur_profile > 1:
				button = types.InlineKeyboardButton('<< Предыдущий профиль', callback_data = 'profile_prev')
				keyboard.add(button)
			elif u.cur_profile + 1 <= len(u.profiles):
				button = types.InlineKeyboardButton('Следующий профиль >>', callback_data = 'profile_next')
				keyboard.add(button)
			cap = profile_info(profile)
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.send_message(message.chat.id, cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				photo = photos.download_photo(photo_id)
				bot.send_photo(message.chat.id, photo, caption = cap, reply_markup = keyboard, parse_mode = 'Markdown')
	elif u.change_st > 0:
		if u.change_st == 1:
			name = message.text
			db.change_name(message.chat.id, name)
			bot.send_message(message.chat.id, 'Твое Имя успешно изменено!')
			profile = db.get_profile(message.chat.id)
			keyboard = types.InlineKeyboardMarkup()
			button1 = types.InlineKeyboardButton('Изменить Имя', callback_data = 'change_name')
			button2 = types.InlineKeyboardButton('Изменить Возраст', callback_data = 'change_age')
			button3 = types.InlineKeyboardButton('Изменить\nОткуда Родом', callback_data = 'change_homeland')
			button4 = types.InlineKeyboardButton('Изменить О себе', callback_data = 'change_desc')
			button5 = types.InlineKeyboardButton('🔙Назад в меню', callback_data='')
			keyboard.row(button1, button2)
			keyboard.row(button3, button4)
			keyboard.row(button5)
			cap = profile_info(profile)
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.edit_message_text(chat_id = message.chat.id, message_id = u.last_mess_id, text = cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				bot.edit_message_caption(chat_id = message.chat.id, message_id = u.last_mess_id, caption = cap, reply_markup = keyboard, parse_mode = 'Markdown')
			u.change_st = 0
		elif u.change_st == 2:
			age = message.text
			if not age.isdigit():
				bot.send_message(message.chat.id, 'Введи пожалуйста целое число!')
				return
			db.change_age(message.chat.id, age)
			bot.send_message(message.chat.id, 'Твой возраст успешно изменен!')
			profile = db.get_profile(message.chat.id)
			keyboard = types.InlineKeyboardMarkup()
			button1 = types.InlineKeyboardButton('Изменить Имя', callback_data = 'change_name')
			button2 = types.InlineKeyboardButton('Изменить Возраст', callback_data = 'change_age')
			button3 = types.InlineKeyboardButton('Изменить \nОткуда Родом', callback_data = 'change_homeland')
			button4 = types.InlineKeyboardButton('Изменить О себе', callback_data = 'change_desc')
			button5 = types.InlineKeyboardButton('🔙Назад в меню', callback_data='')
			keyboard.row(button1, button2)
			keyboard.row(button3, button4)
			keyboard.row(button5)
			cap = profile_info(profile)
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.edit_message_text(chat_id = message.chat.id, message_id = u.last_mess_id, text = cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				bot.edit_message_caption(chat_id = message.chat.id, message_id = u.last_mess_id, caption = cap, reply_markup=keyboard, parse_mode = 'Markdown')
			u.change_st = 0
		elif u.change_st == 3:
			homeland = message.text
			db.change_homeland(message.chat.id, homeland)
			bot.send_message(message.chat.id, 'Твое место откуда ты родом успешно изменено!')
			profile = db.get_profile(message.chat.id)
			keyboard = types.InlineKeyboardMarkup()
			button1 = types.InlineKeyboardButton('Изменить Имя', callback_data = 'change_name')
			button2 = types.InlineKeyboardButton('Изменить Возраст', callback_data = 'change_age')
			button3 = types.InlineKeyboardButton('Изменить\nОткуда Родом', callback_data = 'change_homeland')
			button4 = types.InlineKeyboardButton('Изменить О себе', callback_data = 'change_desc')
			button5 = types.InlineKeyboardButton('🔙Назад в меню', callback_data='')
			keyboard.row(button1, button2)
			keyboard.row(button3, button4)
			keyboard.row(button5)
			cap = profile_info(profile)
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.edit_message_text(chat_id = message.chat.id, message_id = u.last_mess_id, text = cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				bot.edit_message_caption(chat_id = message.chat.id, message_id = u.last_mess_id, caption = cap, reply_markup=keyboard, parse_mode = 'Markdown')
			u.change_st = 0
		elif u.change_st == 4:
			desc = message.text
			db.change_desc(message.chat.id, desc)
			bot.send_message(message.chat.id, 'Твое описание о себе успешно изменено!')
			profile = db.get_profile(message.chat.id)
			keyboard = types.InlineKeyboardMarkup()
			button1 = types.InlineKeyboardButton('Изменить Имя', callback_data = 'change_name')
			button2 = types.InlineKeyboardButton('Изменить Возраст', callback_data = 'change_age')
			button3 = types.InlineKeyboardButton('Изменить\nОткуда Родом', callback_data = 'change_homeland')
			button4 = types.InlineKeyboardButton('Изменить О себе', callback_data = 'change_desc')
			button5 = types.InlineKeyboardButton('🔙Назад в меню', callback_data='')
			keyboard.row(button1, button2)
			keyboard.row(button3, button4)
			keyboard.row(button5)
			cap = profile_info(profile)
			photo_id = db.get_profile_photo(profile[0])
			if photo_id == '0':
				bot.edit_message_text(chat_id = message.chat.id, message_id = u.last_mess_id, text = cap, reply_markup = keyboard, parse_mode = 'Markdown')
			else: 
				bot.edit_message_caption(chat_id = message.chat.id, message_id = u.last_mess_id, caption = cap, reply_markup=keyboard, parse_mode = 'Markdown')
			u.change_st = 0
	else:
		bot.send_message(message.chat.id, 'Чтобы выйти в главное меню выполни команду /menu')

@bot.message_handler(content_types = ['photo'])
def upload_photo(message):
	global allvars
	add_new_user(message.chat.id)
	u = allvars[message.chat.id]
	if (u.seeker_st == True or u.seeker_search_st == True) and u.mode == 17:
		u.seeker.photo_id.append(photos.document_handler(message, bot))
		if message.from_user.username is not None:
			u.seeker.telegram_username = message.from_user.username
		db.seeker_insert(u.seeker)
		bot.send_message(message.chat.id, 'Ура🎉 Мы с тобой это сделали. Твоя анкета успешно сформирована! Если я тебе понравился, расскажи про меня своим друзьям. Я очень люблю новые знакомства😊')
		bot.send_chat_action(message.chat.id, 'typing')
		time.sleep(2)
		profile = db.get_profile(message.chat.id)
		cap = profile_info(profile)
		photo_id = db.get_profile_photo(profile[0])
		if photo_id == '0':
			bot.send_message(message.chat.id, cap, parse_mode = 'Markdown')
		else: 
			photo = photos.download_photo(photo_id)
			bot.send_photo(message.chat.id, photo, caption = cap, parse_mode = 'Markdown')
		bot.send_chat_action(message.chat.id, 'typing')
		time.sleep(2)
		bot.send_message(message.chat.id, 'Если вдруг ты захочешь изменить анкету, можешь сделать это в разделе \'Мои объявления\' в главном меню /menu \n В следующий раз если захочешь увидеть объявление переходи на "Создать объявление и начать поиск" в разделе /menu')
		time.sleep(2)
		if u.seeker_st == True:
			bot.send_message(message.chat.id, '*Подбираю тебе жилье с идеальным для тебя соседями...*', parse_mode = "Markdown")
			bot.send_chat_action(message.chat.id, 'typing')
			time.sleep(5)
			seeker_st = False
			flat_matches = db.get_matches(seeker)
			seeker = Seeker()
			keyboard = types.InlineKeyboardMarkup()
			button = types.InlineKeyboardButton('Показать', callback_data = 'matches_out')
			keyboard.add(button)
			bot.send_message(message.chat.id, 'Квартиры найдены!', reply_markup = keyboard)
		elif u.seeker_search_st == True:
			bot.send_message(message.chat.id, '*Подбираю для тебя идеальных соседов по квартире...*', parse_mode = 'Markdown')
			bot.send_chat_action(message.chat.id, 'typing')
			time.sleep(5)
			u.seeker_search_st = False
			u.profiles = db.get_profiles_by_filters(u.seeker)
			u.seeker = Seeker()
			keyboard = types.InlineKeyboardMarkup()
			button = types.InlineKeyboardButton('Показать', callback_data = 'profile_next')
			keyboard.add(button)
			bot.send_message(message.chat.id, 'Люди найдены! Нажми на эту кнопочку', reply_markup = keyboard)
bot.polling(none_stop=True)
