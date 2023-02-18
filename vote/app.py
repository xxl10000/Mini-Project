from flask import Flask, render_template,request

app = Flask(__name__)

data = [
    {'id':0, 'name': 'Spring Festival', 'num': 0},
    {'id':1, 'name': 'Dragon Boat Festival', 'num': 0},
    {'id':2, 'name': 'Mid-Autumn Festival', 'num': 0}
]

@app.route('/index')
def index():
    return render_template('index.html', data = data)

@app.route('/vote')
def vote():
    id = request.args.get('id')
    data[int(id)]['num'] += 1
    return render_template('index.html', data = data)
app.run(debug= True)