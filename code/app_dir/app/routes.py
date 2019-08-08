from app import application, classes
from flask import render_template


@application.route('/index')
@application.route('/')
def index():
    return "<h1> COME ON AND SLAM</h1><p> And welcome to the Jam </p>"


@application.route('/front_page')
def front_page():
    return render_template('front_page.html',
                           img_path='/static/intro_2.jpg')


application.run(host='0.0.0.0', port=8080)
