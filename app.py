from flask import Flask, render_template
from flask_nav import Nav
from flask_nav.elements import Navbar, View

app = Flask(__name__)
nav = Nav(app)

nav.register_element('navbar', Navbar('navi', View('Index', 'index'), View('Organisation', 'org'),
                                      View('Serien', 'series')))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/org')
def org():
    return render_template('org.html')


@app.route('/series')
def series():
    return render_template('series.html')


if __name__ == '__main__':
    app.run(debug=True)
