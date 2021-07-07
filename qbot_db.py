import json

class QbotDB:
	inuse = False

	def queue(self):
		while self.inuse:
			pass

	def new_user(self):
		return {'pronouns':'', 'wins': 0, 'losses': 0}

	def read(self):
		self.queue()
		self.inuse = True
		with open('db.json', 'r') as f:
			data = f.read()
		self.inuse = False
		return json.loads(data)

	def write(self, data):
		self.queue()
		self.inuse = True
		with open('db.json', 'w') as f:
			f.write(json.dumps(data))
		self.inuse = False
