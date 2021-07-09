from flask import Flask, Markup, redirect, request, render_template
import requests
from qbot_actions import QbotActions

app = Flask(__name__)

qa = QbotActions()
player_list = []

@app.route('/')
def dashboard():
	return render_template('dashboard.html')

@app.route('/discord')
def discord():
	return redirect('https://discord.gg/2eqKB828GA')

@app.route('/dashlist')
def dash_list():
	if len(player_list) == 0:
		return 'The list is empty!'
	response = '<b>On Stream:</b> <br>'
	response += player_list[0]+'<br>'
	response += '<b>Up Next:</b><br>'
	response += '<br>'.join(player_list[1:]) if len(player_list) > 1 else 'None'
	return Markup(response)

@app.route('/auth')
def auth():
	return render_template('auth.html')

@app.route('/authtoken', methods=['POST'])
def authtoken():
	with open('client_secret', 'r') as f:
		secret = f.read().strip()
	code = request.form['code']
	data = requests.post('https://id.twitch.tv/oauth2/token?client_id=i2k8ufiwoixna3fcmdrt71ij386luw&client_secret='+secret+'&code='+code+'&grant_type=authorization_code&redirect_uri=https://itsmino.tk/auth')
	return data.json()['access_token']	

@app.route('/verify', methods=['POST'])
def verify():
	token = request.form['token']
	name = request.form['name']
	if len(token) == 0 or len(name) == 0: 
		return token+':'+name
	data = requests.get('https://api.twitch.tv/helix/users', headers={'Client-Id': 'i2k8ufiwoixna3fcmdrt71ij386luw', 'Authorization': 'Bearer '+token})
	if name == data.json()['data'][0]['display_name']:
		return 'True'
	else:
		return str(data)

@app.route('/getRecord', methods=['POST'])
def getRecord():
	token = request.form['token']
	name = qa.get_name(token)
	data = qa.db.read()
	if name in data:
	        response = str(data[name]['wins'])+'W-'+str(data[name]['losses'])+'L'	
	else:
		response = '0W-0L'
	return response

@app.route('/list')
def list():
	response = 'On Stream: '
	response += (player_list[0]+' ('+qa.get_pronouns(player_list[0])+')' if len(player_list) > 0 else 'None') + '         '
	response += 'Up Next: '
	response += ', '.join(player_list[1:2]) if len(player_list) > 1 else 'None'
	return response

@app.route('/slobslist')
def slobslist():
	response = '<html><head><script>setTimeout(function(){window.location.reload(1);}, 1000);</script></head>'
	response += '<body><div style="margin-right: 0px"><b>On Stream:<b> '
	response += (player_list[0]+' ('+qa.get_pronouns(player_list[0])+')' if len(player_list) > 0 else 'None') + '</div>'
	response += '<div><b>Up Next:<b> '
	response += ', '.join(player_list[1:2]) if len(player_list) > 1 else 'None'
	response += '</div></body></html>'
	return response

@app.route('/add/<name>')
def add(name):
	if name in player_list:
		response = '@'+name+' you are already in the list!'
	else:
		player_list.append(name)
		i = player_list.index(name)
		if i == 0:
			response = '@'+name+' you are up!'
		elif i == 1:
			response = '@'+name+' you are up next!'
		else:
			response = '@'+name+' you will be up in '+str(i)+' matches!'
	return response

@app.route('/siteadd', methods=['POST'])
def siteadd():
	token = request.form['token']
	name = qa.get_name(token)
	if name in player_list:
                response = '@'+name+' you are already in the list!'
        else:
                player_list.append(name)
                i = player_list.index(name)
                if i == 0:
                        response = '@'+name+' you are up!'
                elif i == 1:
                        response = '@'+name+' you are up next!'
                else:
                        response = '@'+name+' you will be up in '+str(i)+' matches!'
        return response	

@app.route('/clear')
def clear():
	while len(player_list) > 0:
		player_list.pop()
	return 'The list has been cleared'

@app.route('/siteclear', methods=['POST'])
def siteclear():
	token = request.form['token']
        name = qa.get_name(token)
        if name != 'its_mino_':
                return 'Auth failed'
        else:
		while len(player_list) > 0:
			player_list.pop()	
		return 'The list has been cleared'

@app.route('/drop/<name>')
def drop(name):
	try:
		player_list.remove(name)
		response = 'Removed @'+name+' from the list'
	except:
		response = '@'+name+' is not in the list!'
	return response

@app.route('/sitedrop', methods=['POST'])
def sitedrop():
	token = request.form['token']
	name = qa.get_name(token)
	try:
                player_list.remove(name)
                response = 'Removed @'+name+' from the list'
        except:
                response = '@'+name+' is not in the list!'
        return response

@app.route('/next')
def next():
	last = player_list.pop(0)
	response = 'Thanks for playing @'+last+'!'
	if len(player_list) > 0:
		 response += ' @'+player_list[0]+' is up next!'
	return response

@app.route('/sitenext', methods=['POST'])
def sitenext():
	token = request.form['token']
	name = qa.get_name(token)
	if name != 'its_mino_':
		return 'Auth failed'
	else:
		last = player_list.pop(0)
	        response = 'Thanks for playing @'+last+'!' 
	 	if len(player_list) > 0:                
			response += ' @'+player_list[0]+' is up next!'
	        return response

@app.route('/win')
def win():
	last = player_list[0]
	data = qa.db.read()
	if last not in data:
		data[last] = qa.db.new_user()
	data[last]['wins'] += 1
	qa.db.write(data)
	response = 'Nice one @'+last+'!'
	return response

@app.route('/loss')
def loss():
	last = player_list[0]
	data = qa.db.read()
	if last not in data:
		data[last] = qa.db.new_user()
	data[last]['losses'] += 1
	qa.db.write(data)
	response = 'Try again!'
	return response

@app.route('/record/<name>')
def record(name):
	data = qa.db.read()
	if name not in data:
		response = 'You aren\'t in the database!'
	else:
		response = 'Your record is '+str(data[name]['wins'])+' wins and '+str(data[name]['losses'])+' losses'

	return response

@app.route('/pronouns/<name>/<choice>')
def pronouns(name, choice):
	data = qa.db.read()
	if name not in data:
		data[name] = qa.db.new_user()
	data[name]['pronouns'] = choice
	qa.db.write(data)
	response = 'Thank you @'+name+' for setting your pronouns!'
	return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, ssl_context='adhoc')
