from flask import Flask, request
from utils.response import response_template

app = Flask(__name__)


@app.route("/", methods=['GET'])
def home():
    return response_template(request, 'index.html')


@app.route('/register', methods=["GET", "POST"])
def register():
    return response_template(request, "register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    return response_template(request, "login.html")


@app.route('/logout', methods=["GET", "POST"])
def logout():
    return response_template(request, "login.html")


# Forgot Password
@app.route('/forgot-password', methods=["GET"])
def forgot_password():
    return response_template(request, 'forgot-password.html')


# 404 Page
@app.route('/404', methods=["GET"])
def error_page():
    return response_template(request, "404.html")


# Blank Page
@app.route('/blank', methods=["GET"])
def blank():
    return response_template(request, 'blank.html')


# Buttons Page
@app.route('/buttons', methods=["GET"])
def buttons():
    return response_template(request, "buttons.html")


# Cards Page
@app.route('/cards', methods=["GET"])
def cards():
    return response_template(request, 'cards.html')


# Charts Page
@app.route('/charts', methods=["GET"])
def charts():
    return response_template(request, "charts.html")


# Tables Page
@app.route('/tables', methods=["GET"])
def tables():
    return response_template(request, "tables.html")


# Utilities-animation
@app.route('/utilities-animation', methods=["GET"])
def utilities_animation():
    return response_template(request, "utilities-animation.html")


# Utilities-border
@app.route('/utilities-border', methods=["GET"])
def utilities_border():
    return response_template(request, "utilities-border.html")


# Utilities-color
@app.route('/utilities-color', methods=["GET"])
def utilities_color():
    return response_template(request, "utilities-color.html")


# utilities-other
@app.route('/utilities-other', methods=["GET"])
def utilities_other():
    return response_template(request, "utilities-other.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)