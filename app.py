import os
import uuid

import urllib3
from dotenv import load_dotenv
from flask import Flask, request, session, jsonify
from flask.helpers import send_from_directory
from ibm_cloud_sdk_core import IAMTokenManager
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import AssistantV2

from database import Database

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


@app.route("/api/dialog", methods=["POST"])
def get_dialog_response():
    user_input = request.json.get("input", "Hi")
    print(f"Got user input: {user_input}")

    user_context = session.get("context", None)

    watson_res = assistant.message_stateless(
        assistant_id=os.environ.get("WATSON_ASSISTANT_ID"),
        input={
            'message_type': 'text',
            'text': user_input
        },
        context=user_context
    ).get_result()

    try:
        first_intent = watson_res["output"]["intents"][0]["intent"]
        tts = watson_res["output"]["generic"][0]["text"]
    except (KeyError, IndexError):
        first_intent = None
        tts = "No intent identified"

    try:
        user_defined = watson_res["context"]["skills"]["main skill"]["user_defined"]
    except (KeyError, IndexError):
        user_defined = None

    if first_intent == "General_Greetings":
        pass
        # Send data to watson
        # set tts =  watson response text
    elif first_intent == "Weather":
        pass
        # Send data to watson
        # set tts =  watson response text

    session["context"] = watson_res.get("context", None)
    return jsonify(tts=tts, watson=watson_res, intent=first_intent, user_defined=user_defined)


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
    db = Database.get_instance()
    prefs = db.load_prefs(session["id"])
    return jsonify(preferences=prefs, session_id=session["id"])


@app.route("/chat")
def test_chat():
    return send_from_directory(app.static_folder, 'chat.html')


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

    urllib3.disable_warnings()

    Database.get_instance().initialize()

    authenticator = IAMAuthenticator(os.environ.get("WATSON_ASSISTANT_API"))
    authenticator.set_disable_ssl_verification(True)
    assistant = AssistantV2(version='2021-06-14', authenticator=authenticator)

    assistant.set_service_url('https://api.eu-de.assistant.watson.cloud.ibm.com')
    assistant.set_disable_ssl_verification(True)

    app.run(debug=True, host='0.0.0.0', port=9090, threaded=True)
