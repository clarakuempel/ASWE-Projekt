from flask import Flask
from flask.helpers import send_from_directory

app = Flask(__name__, static_folder='./frontend')

@app.route("/")
def default():
    """
    returns default html page
    """
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9090, threaded=True)