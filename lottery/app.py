#web frame
from flask import Flask, render_template
from random import randint
app = Flask(__name__)
hero = ['刘备','关羽','张飞','诸葛亮','赵云','马超','黄月英','孙权',
'甘宁','吕蒙','黄盖','周瑜','大乔','陆逊','曹操','司马懿',
'夏侯惇','张辽','许褚','郭嘉','甄姬','华佗','吕布','貂蝉',
'孙尚香','黄忠','魏延','夏侯渊','曹仁','小乔','周泰','张角',
'于吉','典韦','荀彧','庞统','卧龙诸葛','太史慈','庞德',]
@app.route('/index')
def index():
    return render_template('index.html', hero = hero)

@app.route('/lottery')
def lottery():
    n = len(hero)
    i = randint(0, n - 1)
    return render_template('index.html', hero = hero, h = hero[i])

app.run(debug = True)


