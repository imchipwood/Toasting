from flask import Flask, flash, redirect, render_template, request, session, abort, url_for

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('login.html')


@app.route("/thermal_profile/<name>")
def thermal_profile(name):
    return "Thermal Profile Page - welcome {}".format(name)


@app.route("/configuration")
def configuration():
    return render_template("configuration.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['nm']
        return redirect(url_for('thermal_profile', name=user))
    else:
        user = request.args.get('nm')
        return redirect(url_for('thermal_profile', name=user))


# @app.route('/admin')
# def hello_admin():
#    return 'Hello Admin'
#
#
# @app.route('/guest/<guest>')
# def hello_guest(guest):
#    return 'Hello %s as Guest' % guest
#
#
# @app.route('/user/<name>')
# def hello_user(name):
#    if name =='admin':
#       return redirect(url_for('hello_admin'))
#    else:
#       return redirect(url_for('hello_guest',guest = name))


if __name__ == "__main__":
    app.run(debug=True)
