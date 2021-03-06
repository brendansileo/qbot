from flask import Flask, Markup, redirect, request, render_template
import requests
from qbot_actions import QbotActions

app = Flask(__name__)

qa = QbotActions()
bestof = '1'
gamescore = [0,0]
format = 'viewerbattles'

@app.route('/')
def dashboard():
	if format == 'viewerbattles':
		return render_template('dashboard.html')

@app.route('/discord')
def discord():
	return redirect('https://discord.gg/KWdrhEjf')

@app.route('/dashlist')
def dash_list():
	player_list = qa.get_list()
	if len(player_list) == 0:
		return 'The list is empty!'
	response = '<b>On Stream - '+getScore()+'</b> <br>'
	response += player_list[0]+'<button class="admincontrols" onclick="dropButton(\''+player_list[0]+'\')">X</button><br>'
	response += '<b>Up Next:</b><br>'
	for name in player_list[1:]:
		response += name+'<button class="admincontrols" onclick="dropButton(\''+name+'\')">X</button><br>'
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
	if 'data' not in data.json():
		return 'Old Auth'
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
	        response = 'Your Record: '+str(data[name]['wins'])+'W-'+str(data[name]['losses'])+'L'	
	else:
		response = 'Your Record: 0W-0L'
	return response

@app.route('/getScore')
def getScore():
	return 'Bo'+bestof+': '+str(gamescore[0])+'-'+str(gamescore[1])

@app.route('/slobsScore')
def slobsScore():
	response = '<html><head><script>setTimeout(function(){window.location.reload(1);}, 1000);</script></head>'
	response += '<body>Bo'+bestof+': '+str(gamescore[0])+'-'+str(gamescore[1])+'</body></html>'
	return response

@app.route('/sitewin', methods=['POST'])
def sitewin():
	global gamescore
	token = request.form['token']
        name = qa.get_name(token)
        if name != 'its_mino_':
		return 'Auth fail'
	gamescore[0] += 1
	if gamescore[0] >= int(int(bestof)/2) + 1:
		gamescore = [0,0]
		loss()
		if len(player_list) > 1:
			next()
	return ''		

@app.route('/siteloss', methods=['POST'])
def siteloss():
	global gamescore
	token = request.form['token']
        name = qa.get_name(token)
        if name != 'its_mino_':
                return 'Auth fail'
	gamescore[1] += 1
	if gamescore[1] >= int(int(bestof)/2) + 1:
		gamescore = [0,0]
		win()
		if len(player_list) > 1:
			next()
	return ''

@app.route('/resetScore', methods=['POST'])
def resetScore():
	global gamescore
	token = request.form['token']
	name = qa.get_name(token)
        if name != 'its_mino_':
		return 'Auth fail'
	else:
		gamescore = [0,0]
		return ''

@app.route('/siteformat', methods=['POST'])
def siteformat():
	global gamescore
        global bestof
	token = request.form['token']
        name = qa.get_name(token)
        if name != 'its_mino_':
                return 'Auth fail'
        else:
		gamescore = [0,0]
		bestof = request.form['format']
	return ''

@app.route('/list')
def list():
	player_list = qa.get_list()
	response = 'On Stream: '
	response += (player_list[0]+' ('+qa.get_pronouns(player_list[0])+')' if len(player_list) > 0 else 'None') + '         '
	response += 'Up Next: '
	response += ', '.join(player_list[1:]) if len(player_list) > 1 else 'None'
	return response

@app.route('/slobslist')
def slobslist():
	player_list = qa.get_list()
	response = '<html><head><script>setTimeout(function(){window.location.reload(1);}, 1000);</script></head>'
	response += '<body><div style="margin-right: 0px"><b>On Stream:<b> '
	response += (player_list[0]+' ('+qa.get_pronouns(player_list[0])+')' if len(player_list) > 0 else 'None') + '</div>'
	response += '<div><b>Versus:<b> '
	if len(player_list) > 1:
		response += player_list[1]+' ('+qa.get_pronouns(player_list[1])+')' 
	else:
		response += 'None'
	response += '</div></body></html>'
	return response

@app.route('/add/<name>')
def add(name):
	player_list = qa.get_list()
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
			response = '@'+name+' you will be up in '+str(i-1)+' matches!'
		qa.write_list(player_list)
	return response

@app.route('/siteadd', methods=['POST'])
def siteadd():
	player_list = qa.get_list()
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
		qa.write_list(player_list)
        return response	

@app.route('/clear')
def clear():
	qa.write_list([])
	return 'The list has been cleared'

@app.route('/siteclear', methods=['POST'])
def siteclear():
	token = request.form['token']
        name = qa.get_name(token)
        if name != 'its_mino_':
                return 'Auth failed'
        else:
		qa.write_list([])
		return 'The list has been cleared'

@app.route('/drop/<name>')
def drop(name):
	player_list = qa.get_list()
	try:
		player_list.remove(name)
		response = 'Removed @'+name+' from the list'
	except:
		response = '@'+name+' is not in the list!'
	qa.write_list(player_list)
	return response

@app.route('/sitedrop', methods=['POST'])
def sitedrop():
	player_list = qa.get_list()
	token = request.form['token']
	name = qa.get_name(token)
	try:
                player_list.remove(name)
                response = 'Removed @'+name+' from the list'
		qa.write_list(player_list)
        except:
                response = '@'+name+' is not in the list!'
        return response

@app.route('/buttondrop', methods=['POST'])
def buttondrop():
	token = request.form['token']
        name = qa.get_name(token)
        if name != 'its_mino_':
                return 'Auth failed'
        else:
		name = request.form['name']
		player_list = qa.get_list()
		token = request.form['token']
		name = qa.get_name(token)
		try:
			player_list.remove(name)
			response = 'Removed @'+name+' from the list'
			qa.write_list(player_list)
		except:
			response = '@'+name+' is not in the list!'
	return response

@app.route('/next')
def next():
	player_list = qa.get_list()
	last = player_list.pop(0)
	response = 'Thanks for playing @'+last+'!'
	if len(player_list) > 0:
		 response += ' @'+player_list[0]+' is up next!'
	qa.write_list(player_list)
	return response

@app.route('/sitenext', methods=['POST'])
def sitenext():
	player_list = qa.get_list()
	token = request.form['token']
	name = qa.get_name(token)
	if name != 'its_mino_':
		return 'Auth failed'
	else:
		last = player_list.pop(0)
	        response = 'Thanks for playing @'+last+'!' 
	 	if len(player_list) > 0:                
			response += ' @'+player_list[0]+' is up next!'
		player_list.append(last)
		qa.write_list(player_list)
		return response

@app.route('/secondnext', methods=['POST'])
def secondnext():
	player_list = qa.get_list()
        token = request.form['token']
        name = qa.get_name(token)
        if name != 'its_mino_':
                return 'Auth failed'
        else:
                last = player_list.pop(1)
                response = 'Thanks for playing @'+last+'!'
                if len(player_list) > 0:
                        response += ' @'+player_list[0]+' is up next!'
		player_list.append(last)
		qa.write_list(player_list)
                return response

@app.route('/win')
def win():
	player_list = qa.get_list()
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
	player_list = qa.get_list()
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
	if choice.strip() == '':
		return 'Please include your pronoun choice in the command (ex: !pronouns they/them)'
	data = qa.db.read(
	if name not in data:
		data[name] = qa.db.new_user()
	data[name]['pronouns'] = choice
	qa.db.write(data)
	response = 'Thank you @'+name+' for setting your pronouns!'
	return response

@app.route('/sitepronouns', methods=['POST'])
def sitepronouns():
	token = request.form['token']
	pronouns = request.form['pronouns']
	name = name = qa.get_name(token)
	data = qa.db.read()
	if name not in data:
		data[name] = qa.db.new_user()
	data[name]['pronouns'] = pronouns
	qa.db.write(data)
	response = 'Thank you @'+name+' for setting your pronouns!'
	return response

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, ssl_context='adhoc')
