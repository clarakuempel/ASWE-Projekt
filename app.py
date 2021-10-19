import uuid

from dotenv import load_dotenv
from flask import Flask
from flask import session, jsonify
from flask.helpers import send_from_directory

from usecase import welcome

app = Flask(__name__, static_folder='./frontend')
app.secret_key = "DEV_fe5dce3c7b5a0a3339342"


@app.before_request
def assign_user_id():
    if "id" not in session:
        session.permanent = True
        session["id"] = uuid.uuid4().hex


@app.route("/")
def default():
    """
    returns default html page
    """
    return send_from_directory(app.static_folder, 'index.html')


@app.route("/api/dialog")
def get_dialog_response():
    return "dialog response"


@app.route("/api/habits", methods=['GET'])
def get_user_habits():
    print(f"Get habits for user {session.get('id', None)}")
    # Get habits for user, idk what format
    user_habits = [
        {
            "name": "Running",
            "achieved": 1,
            "goal": 3
        },
        {
            "name": "test",
            "achieved": 1,
            "goal": 1
        }
    ]
    return jsonify(user_habits)


@app.route("/api/habits", methods=['POST'])
def set_user_habits():
    print(f"Set habits for user {session.get('id', None)}")
    return f"Set habits for user {session.get('id', None)}"


@app.route("/api/preferences", methods=['GET'])
def get_user_preferences():
    print(f"Get preferences for user {session.get('id', None)}")
    # Get preferences for user or default values if new user
    user_preferences = {
        "location": {
            "city": "Stuttgart",
            "lat": 48.783333,
            "lon": 9.183333,
        },
        "gyms": [1731421430],
        "wakeup": "08:00"
    }
    return jsonify(user_preferences)


@app.route("/api/preferences", methods=['POST'])
def set_user_preferences():
    print(f"Set preferences for user {session.get('id', None)}")
    return f"Set preferences for user {session.get('id', None)}"


@app.route("/test")
def test():
    return welcome.get_welcome_text()


if __name__ == "__main__":
    load_dotenv()

    app.run(debug=True, host='0.0.0.0', port=9090, threaded=True)

    # print(service.get_rapla())

    # STUTTGART_LAT = 48.783333
    # STUTTGART_LON = 9.183333
    # print(service.get_weather_forecast(STUTTGART_LAT, STUTTGART_LON))
    # print(service.get_air_pollution(STUTTGART_LAT, STUTTGART_LON))
    # print(service.get_sunrise_sunset(STUTTGART_LAT, STUTTGART_LON))

    # print(service.get_wikipedia_extract("Stuttgart"))

    # MCFIT_STUTTGART_MITTE = 1731421430
    # print(service.get_gym_utilization(MCFIT_STUTTGART_MITTE))

    # STUTTGART_AGS = "08111"
    # print(service.get_covid_stats(STUTTGART_AGS))

    # print(service.get_youtube_search("Yoga Workout"))
    # print(service.service.get_news_stories()["entries"][0]["title"])
    # print(service.service.get_bestselling_books())
