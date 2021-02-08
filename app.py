from flask import Flask, render_template, request
import crawler

app = Flask(__name__)

@app.route('/', methods = ['POST', 'GET'])
def index():
	results = {}

	if request.method == 'POST':
		searchTerm = request.form['search']
		results = crawler.getCountdown(searchTerm)
		return render_template('index.html', results=results)
	else:
		return render_template('index.html')
