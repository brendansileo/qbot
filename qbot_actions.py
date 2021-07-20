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
		with open('log', 'w+') as f:
			f.write(str(data.json()))
        	return data.json()['data'][0]['display_name']

	def get_list(self):
		with open('list.txt', 'r') as f:
			l = f.read()
		if l == '':
			return []
		return l.split(',')
	
	def write_list(self, player_list):
		with open('list.txt', 'w') as f:
			f.write(','.join(player_list))
