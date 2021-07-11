from qbot_db import QbotDB
import requests

class QbotActions:
	db = None

	def __init__(self):
		self.db = QbotDB()

	def get_pronouns(self, name):
		data = self.db.read()
		try:
			return data[name]['pronouns']
		except Exception as e:
			print(e)
			return ''

	def get_name(self, token):
		data = requests.get('https://api.twitch.tv/helix/users', headers={'Client-Id': 'i2k8ufiwoixna3fcmdrt71ij386luw', 'Authorization': 'Bearer '+token})
        	return data.json()['data'][0]['display_name']
