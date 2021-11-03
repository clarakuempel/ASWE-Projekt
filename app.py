import json
import os
import uuid

from dotenv import load_dotenv
from flask import Flask, request, session, jsonify
from flask.helpers import send_from_directory
from ibm_cloud_sdk_core import IAMTokenManager

from database import Database
from usecase import welcome

app = Flask(__name__, static_folder='./static')
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
    user_input = request.form.get("input", "Hi")
    print(f"Got user input: {user_input}")
    # TODO Message Watson service and get response
    res = json.loads("""{
    "output": {
        "intents": [
            {
                "intent": "General_Greetings",
                "confidence": 0.9273388385772705
            }
        ]
    }
}""")
    first_intent = res["output"]["intents"][0]["intent"]
    if first_intent == "General_Greetings":
        return jsonify(tts="I am Ivy. What's your name?")
    else:
        return jsonify(tts="I don't understand")


@app.route("/api/habits", methods=['GET'])
def get_user_habits():
    # Get habits for user, idk what format
    user_habits = []
    return jsonify(user_habits)


@app.route("/api/habits", methods=['POST'])
def set_user_habits():
    print(f"Set habits for user {session.get('id', None)}")
    user_habits = []
    return jsonify(user_habits)


@app.route("/api/preferences", methods=['GET'])
def get_user_preferences():
    database = Database.get_instance()
    user_preferences = database.load_prefs(session["id"])
    if user_preferences is None:
        user_preferences = {
            "location": {
                "ags": "08111",
                "lat": 48.783333,
                "lon": 9.183333,
            },
            "news": 1,
        }
    return jsonify(user_preferences)


@app.route("/api/preferences", methods=['POST'])
def set_user_preferences():
    # Get form fields, default values: Stuttgart + All news
    lat = request.form.get("location_lat", 48.783333)
    lon = request.form.get("location_lon", 9.183333)
    ags = request.form.get("location_ags", "08111")
    news_pref = request.form.get("news_pref", 1)
    database = Database.get_instance()
    user_preferences = {
        "location": {
            "ags": ags,
            "lat": lat,
            "lon": lon,
        },
        "news": news_pref,
    }
    database.store_prefs(session["id"], user_preferences)
    return jsonify(prefs=user_preferences)


@app.route("/test")
def test():
    text = welcome.get_welcome_text()
    db = Database.get_instance()
    prefs = db.load_prefs(session["id"])
    return jsonify(output=text, preferences=prefs, session_id=session["id"])


@app.route("/api/tts-token", methods=["GET"])
def get_tts_token():
    """
    Get Token for TTS
    """
    iam_token_manager = IAMTokenManager(apikey=os.environ.get("TTS_APIKEY"))
    iam_token_manager.set_disable_ssl_verification(True)
    token = iam_token_manager.get_token()
    res = {"token": token, "url": os.environ.get("TTS_URL")}
    return jsonify(res)


@app.route("/api/stt-token", methods=["GET"])
def get_stt_token():
    """
    Get Token for STT
    """
    iam_token_manager = IAMTokenManager(apikey=os.environ.get("STT_APIKEY"))
    iam_token_manager.set_disable_ssl_verification(True)
    token = iam_token_manager.get_token()
    res = {"token": token, "url": os.environ.get("STT_URL")}
    return jsonify(res)


if __name__ == "__main__":
    # Load .env file with secrets and credentials
    load_dotenv()

    Database.get_instance().initialize()

    app.run(debug=True, host='0.0.0.0', port=9090, threaded=True)
