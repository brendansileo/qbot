from qbot_db import QbotDB

class QbotActions:
	db = None

	def __init__(self):
		self.db = QbotDB()

	def get_pronouns(self, name):
		data = self.db.read()
		try:
			print(data[name]['pronouns'])
			return data[name]['pronouns']
		except Exception as e:
			print(e)
			return ''
