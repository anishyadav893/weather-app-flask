import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'someencryptedkey'

db = SQLAlchemy(app)

class City(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(50), nullable = False)

def get_weather(city):
	url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=imperial&appid=6d6c5d24d0c5c75d17cb90ad8525b285'
	r = requests.get(url).json()
	return r

@app.route('/')
def index():
	cities = City.query.all()
	weather_data = []

	url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=6d6c5d24d0c5c75d17cb90ad8525b285'
	for city in cities:
		r = get_weather(city.name)

		weather = {
			'city': city.name,
			'temperature': r['main']['temp'],
			'description': r['weather'][0]['description'],
			'icon': r['weather'][0]['icon']
		}
		weather_data.append(weather)

	return render_template('weather.html', weather_data = weather_data)

@app.route('/', methods=['POST'])
def post():
	new_city = request.form.get('city')
	if new_city:
		error = ''
		city_exists = City.query.filter_by(name=new_city).first()
		if not city_exists:
			if_city_valid = get_weather(new_city)
			if if_city_valid['cod'] == 200:
				city_obj = City(name = new_city)
				db.session.add(city_obj)
				db.session.commit()
			else:
				error = 'Invalid city name!'
		else:
			error = 'City already in the database'
	if error:
		flash(error, 'error')
	else:
		flash('City successfully added')

	return redirect(url_for('index'))

@app.route('/delete/<name>')
def delete(name):
	city = City.query.filter_by(name=name).first()
	db.session.delete(city)
	db.session.commit()
	flash(f'Successfully deleted { city.name }', 'success')
	return redirect(url_for('index'))