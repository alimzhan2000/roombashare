class Seeker:
	# def init_vars():
	# 	self.name = ""
	# 	self.age = 0
	# 	self.homeland = ""
	# 	self.phone_num = ""
	# 	self.gender = ""
	# 	self.worker_or_student = ""
	# 	self.study_or_work_place = ""
	# 	self.sleeping_mode = ""
	# 	self.langs = ""
	# 	self.distr = ""
	# 	self.near_what = ""
	# 	self.price = ""
	# 	self.seeking_for = ""
	# 	self.interest = ""
	# 	self.chat_id = ""
	# 	self.photo_id = []
	# 	self.bad_habits = ""
	# 	self.telegram_username = ""
	# 	self.hata = False
	def __init__(self, profile=None):
		if profile is None:
			self.name = ""
			self.age = 0
			self.homeland = ""
			self.phone_num = ""
			self.gender = ""
			self.worker_or_student = ""
			self.study_or_work_place = ""
			self.sleeping_mode = ""
			self.langs = ""
			self.distr = ""
			self.near_what = ""
			self.price = ""
			self.seeking_for = ""
			self.interest = ""
			self.chat_id = ""
			self.photo_id = []
			self.bad_habits = ""
			self.telegram_username = ""
			self.hata = False
			self.food = False
			return
		self.name = profile[1]
		self.age = profile[2]
		self.homeland = profile[3]
		self.phone_num = profile[14]
		self.gender = profile[4]
		self.worker_or_student = profile[5]
		self.study_or_work_place = profile[6]
		self.sleeping_mode = profile[7]
		self.langs = profile[8]
		self.distr = profile[9]
		self.near_what = profile[10]
		self.price = profile[11]
		self.seeking_for = profile[12]
		self.interest = profile[13]
		self.chat_id = profile[16]
		self.photo_id = profile[17]
		self.bad_habits = profile[18]
		self.telegram_username = profile[19]
		self.hata = profile[20]
		self.food = profile[21]