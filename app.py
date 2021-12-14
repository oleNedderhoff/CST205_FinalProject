"""
Course: CST 205
Title: Average Score Calculator
Authors: Ole Nedderhoff, Paul Zamora, Reda Gerges, Victoria Cimino
Date: 12/13/21

Python file: by Ole (except classes)
HTML files: by Paul
CSS file and readme: by Victoria
"""


import requests, json
from flask import Flask, render_template, redirect
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired

api_key = str(40130162) #key given by api to access data
app = Flask(__name__, static_url_path='/static')
app.config['SECRET_KEY'] = 'sports'
bootstrap = Bootstrap(app)
sports = []
countries = []
teams1 = []
teams2 = []
sportChosen = ""
country1 = ""
country2 = ""
teamsFound1 = []
teamsFound2 = []
beenHere = False
teamlist = []
sportList = []

def getBeenHere():
    return beenHere

def setBeenHere(value):
    global beenHere
    beenHere = value

#function to access the api with a given url and turn it into a dictionary
def dataBaseAccess(url):
    r = requests.get(url)
    data = r.text
    return json.loads(data)

def store_teams(team1, team2):
    teamlist.clear()
    teamlist.append(team1)
    teamlist.append(team2)

def store_sport(sport, country1, country2):
    sportList.clear()
    sportList.append(sport)
    sportList.append(country1)
    sportList.append(country2)

# list of all sports
parse_json = dataBaseAccess('https://www.thesportsdb.com/api/v1/json/' + api_key + '/all_sports.php')
for i in range(0,len(parse_json['sports'])):
    sports.append(parse_json['sports'][i]['strSport'])

# list of all countries
parse_json = dataBaseAccess('https://www.thesportsdb.com/api/v1/json/' + api_key + '/all_countries.php')
for i in range(0,len(parse_json['countries'])):
    countries.append(parse_json['countries'][i]['name_en'])

# forms that are included in the templates
# mainly done by paul
class sportChoice(FlaskForm):
    sportChosen = SelectField('Sport', choices = sports, validators = [DataRequired()])
    country1 = SelectField('Country of 1st Team', choices = countries, validators = [DataRequired()])
    country2 = SelectField('Country of 2nd Team', choices = countries, validators = [DataRequired()])

class teamSearch(FlaskForm):
    team1 = StringField('Team 1',validators=[DataRequired()])
    team2 = StringField('Team 2',validators=[DataRequired()])

class teamslist(FlaskForm):
    team1input = SelectField('1st Team', choices = teams1, validators = [DataRequired()])
    team2input = SelectField('2nd Team', choices = teams2, validators = [DataRequired()])

class pickTeams(FlaskForm):
    team1input = SelectField('1st Team', choices = teamsFound1, validators = [DataRequired()])
    team2input = SelectField('2nd Team', choices = teamsFound2, validators = [DataRequired()])

# home page that lets you pick a sport and coutry or search any two teams
@app.route('/', methods = ('GET', 'POST'))
def index():
    form = sportChoice()
    form1 = teamSearch()
    if form.validate_on_submit():
        store_sport(form.sportChosen.data, form.country1.data, form.country2.data)
        teams1.clear()
        teams2.clear()
        return redirect('/sport')
    if form1.validate_on_submit():
        store_teams(form1.team1.data, form1.team2.data)
        return redirect('/teams')
    return render_template('index.html', form = form, form1 = form1)

# second page that offers all of the teams in the two countries chosen in the sport chosen
@app.route('/sport', methods = ('GET', 'POST'))
def sport():
    parse_json = dataBaseAccess('https://www.thesportsdb.com/api/v1/json/' + api_key + '/search_all_teams.php?s=' + sportList[0] + '&c=' + sportList[1])
    if parse_json['teams']:
        for i in range(0,len(parse_json['teams'])):
            teams1.append(parse_json['teams'][i]['strTeam'])
    parse_json = dataBaseAccess('https://www.thesportsdb.com/api/v1/json/' + api_key + '/search_all_teams.php?s=' + sportList[0] + '&c=' + sportList[2])
    if parse_json['teams']:
        for i in range(0,len(parse_json['teams'])):
            teams2.append(parse_json['teams'][i]['strTeam'])
    form = teamslist()
    if form.validate_on_submit():
        setBeenHere(True)
        store_teams(form.team1input.data, form.team2input.data)
        return redirect('/teams')
    return render_template('sport.html', form = form, sportChosen = sportList[0], c1 = sportList[1], c2 = sportList[2])

#third page, only opened up when multiple teams are found for a search. Teams out of a list can be chosen.
@app.route('/searchResults', methods = ('GET', 'POST'))
def searchResults():
    form = pickTeams()
    if form.validate_on_submit():
        setBeenHere(True)
        store_teams(form.team1input.data, form.team2input.data)
        return redirect('/teams')
    return render_template('searchResults.html', form = form)

#final page that shows the average score and other stats of the two teams selected
@app.route('/teams')
def teams():
    played = False
    totalScore1 = 0
    totalScore2 = 0
    games = 0
    wins1 = 0
    wins2 = 0
    ties = 0
    team1 = teamlist[0]
    team2 = teamlist[1]
    average1 = 0
    average2 = 0
    badge1Url = 'https://www.ncenet.com/wp-content/uploads/2020/04/No-image-found.jpg'
    badge2Url = 'https://www.ncenet.com/wp-content/uploads/2020/04/No-image-found.jpg'
    website1Url = ""
    website2Url = ""
    multiple = False
    
    if getBeenHere() == False:
        parse_json = dataBaseAccess('https://www.thesportsdb.com/api/v1/json/' + api_key + '/searchteams.php?t=' + team1)
        if parse_json['teams']:
            if len(parse_json['teams']) > 1:
                multiple = True
                teamsFound1.clear()
                for i in range(0,len(parse_json['teams'])):
                    teamsFound1.append(parse_json['teams'][i]['strTeam'])
            else:
                teamsFound1.clear()
                teamsFound1.append(parse_json['teams'][0]['strTeam'])
        else:
            multiple = True
            teamsFound1.clear()
            teamsFound1.append('No Team found')

        parse_json = dataBaseAccess('https://www.thesportsdb.com/api/v1/json/' + api_key + '/searchteams.php?t=' + team2)
        if parse_json['teams']:
            if len(parse_json['teams']) > 1:
                multiple = True
                teamsFound2.clear()
                for i in range(0,len(parse_json['teams'])):
                    teamsFound2.append(parse_json['teams'][i]['strTeam'])
            else:
                teamsFound2.clear()
                teamsFound2.append(parse_json['teams'][0]['strTeam'])
        else:
            multiple = True
            teamsFound2.clear()
            teamsFound2.append('No Team found')
        if multiple:
            return redirect('/searchResults')

    parse_json = dataBaseAccess('https://www.thesportsdb.com/api/v1/json/' + api_key + '/searchevents.php?e=' + team1 + '_vs_' + team2)
    if parse_json['event']:
        for i in range(0,len(parse_json['event'])):
            if parse_json['event'][i]['intHomeScore']:
                played = True
                home = int(parse_json['event'][i]['intHomeScore'])
                away = int(parse_json['event'][i]['intAwayScore'])
                totalScore1 = totalScore1 + int(home or 0)
                totalScore2 = totalScore2 + int(away or 0)                
                games = games + 1
                if home > away:
                    wins1 = wins1 + 1
                if home < away:
                    wins2 = wins2 + 1
                if home == away:
                    ties = ties + 1
                
    parse_json = dataBaseAccess('https://www.thesportsdb.com/api/v1/json/' + api_key + '/searchevents.php?e=' + team2 + '_vs_' + team1)
    if parse_json['event']:
        for i in range(0,len(parse_json['event'])):
            if parse_json['event'][i]['intHomeScore']:
                played = True
                home = int(parse_json['event'][i]['intHomeScore'])                
                away = int(parse_json['event'][i]['intAwayScore'])                
                totalScore1 = totalScore1 + int(away or 0)
                totalScore2 = totalScore2 + int(home or 0)
                games = games + 1
                if home > away:
                    wins2 = wins2 + 1
                if home == away:
                        ties = ties + 1
                if home < away:
                    wins1 = wins1 + 1

    if played:
        average1 = round(totalScore1/games, 2)
        average2 = round(totalScore2/games, 2)

    parse_json = dataBaseAccess('https://www.thesportsdb.com/api/v1/json/' + api_key + '/searchteams.php?t=' + team1)
    if parse_json['teams']:
        if parse_json['teams'][0]['strTeamBadge']:
            badge1Url = parse_json['teams'][0]['strTeamBadge']
        if parse_json['teams'][0]['strWebsite']:
            website1Url = parse_json['teams'][0]['strWebsite']        

    parse_json = dataBaseAccess('https://www.thesportsdb.com/api/v1/json/' + api_key + '/searchteams.php?t=' + team2)
    if parse_json['teams']:
        if parse_json['teams'][0]['strTeamBadge']:
            badge2Url = parse_json['teams'][0]['strTeamBadge']
        if parse_json['teams'][0]['strWebsite']:
            website2Url = parse_json['teams'][0]['strWebsite']       

    setBeenHere(False)

    return render_template('teams.html', 
    team1 = team1, 
    team2 = team2, 
    avg1 = average1, 
    avg2 = average2, 
    games = games, 
    totalScore1 = totalScore1, 
    totalScore2 = totalScore2, 
    logo1 = badge1Url, 
    logo2 = badge2Url, 
    wins1 = wins1, 
    wins2 = wins2, 
    ties = ties, 
    website1url = website1Url, 
    website2url = website2Url)






