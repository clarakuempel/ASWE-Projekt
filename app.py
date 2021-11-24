import json
import os
import uuid

import urllib3
from dotenv import load_dotenv
from flask import Flask, request, session, jsonify
from flask.helpers import send_from_directory
from ibm_cloud_sdk_core import IAMTokenManager
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import AssistantV2

from database.database import Database
from usecase import habit, welcome, holiday, coach

app = Flask(__name__, static_folder='./static')
app.secret_key = "DEV_fe5dce3c7b5a0a3339342"

with open(os.path.join(os.path.dirname(__file__), './database/default_user_prefs.json')) as f:
    default_user_prefs: dict = json.load(f)


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
    user_input = request.json.get("input", None)
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

    # Intent is not needed anymore, this is old and will be probably removed
    first_intent = get_first_intent(watson_res)

    tts_output = []

    # Get the TTS text because the current node requires no external data
    tts = get_watson_tts(watson_res)
    # tts_output is an List that collects all Watson Chat responses since we do two requests (initial and data response)
    tts_output.append(tts)

    # Get context variables dict and the current_intent variable
    user_defined, current_intent_var = get_context_variables(watson_res)

    if first_intent == "Good_Morning":
        usecase_data = welcome.load_data()
        print(usecase_data)

        watson_res["context"]["skills"]["main skill"]["user_defined"].update(usecase_data)

        watson_res = assistant.message_stateless(
            assistant_id=os.environ.get("WATSON_ASSISTANT_ID"),
            context=watson_res["context"]
        ).get_result()

        tts = get_watson_tts(watson_res)
        tts_output.append(tts)

    elif first_intent in ["Habit_Reading", "Habit_Meditating", "Habit_Sleeping"]:
        usecase_data = habit.load_data()

        watson_res["context"]["skills"]["main skill"]["user_defined"].update(usecase_data)

        watson_res = assistant.message_stateless(
            assistant_id=os.environ.get("WATSON_ASSISTANT_ID"),
            context=watson_res["context"]
        ).get_result()

        tts = get_watson_tts(watson_res)
        tts_output.append(tts)
    elif first_intent == "Sports":
        usecase_data = coach.load_data()

        watson_res["context"]["skills"]["main skill"]["user_defined"].update(usecase_data)

        watson_res = assistant.message_stateless(
            assistant_id=os.environ.get("WATSON_ASSISTANT_ID"),
            context=watson_res["context"]
        ).get_result()

        tts = get_watson_tts(watson_res)
        tts_output.append(tts)

    elif first_intent == "holiday_finder":
        usecase_data = holiday.load_data()

        watson_res["context"]["skills"]["main skill"]["user_defined"].update(usecase_data)

        watson_res = assistant.message_stateless(
            assistant_id=os.environ.get("WATSON_ASSISTANT_ID"),
            context=watson_res["context"]
        ).get_result()

        tts = get_watson_tts(watson_res)
        tts_output.append(tts)

    # Save the last known context to user cookie so we have it in the next user request (contains username etc.)
    session["context"] = watson_res.get("context", None)

    # watson, intent, and user_defined are debugging values will be removed
    # Later we pass only tts output and display data (e.g. links, images, etc)
    print(tts_output)
    return jsonify(tts=" ".join(tts_output), watson=watson_res, intent=first_intent, user_defined=user_defined)


def get_first_intent(watson_response):
    try:
        return watson_response["output"]["intents"][0]["intent"]
    except (KeyError, IndexError):
        return None


def get_watson_tts(watson_response):
    tts = ""
    try:
        tts = " ".join([entry["text"] for entry in watson_response["output"]["generic"]])
    except (KeyError, IndexError):
        pass
    return tts


def get_context_variables(watson_response):
    try:
        user_defined = watson_response["context"]["skills"]["main skill"]["user_defined"]
    except (KeyError, IndexError):
        user_defined = {}
        watson_response["context"]["skills"]["main skill"]["user_defined"] = {}
    if user_defined:
        try:
            current_context = user_defined["current_intent"]
        except (KeyError, IndexError):
            current_context = None
    else:
        current_context = None
    return user_defined, current_context


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
    user_preferences = default_user_prefs.copy()
    user_preferences.update(
        database.load_prefs(session["id"]))
    with open(os.path.join(os.path.dirname(__file__), 'database/gym_selection.json'), encoding='utf-8') as gym_f:
        gyms = json.load(gym_f)
    gym_selection = [{"id": gym["id"], "name": gym["studioName"]} for gym in gyms]
    return jsonify(preferences=user_preferences, gyms=gym_selection)


@app.route("/api/preferences", methods=['POST'])
def set_user_preferences():
    user_preferences: dict = request.json
    unnecessary_keys = [key for key in user_preferences.keys() if key not in default_user_prefs.keys()]
    for key in unnecessary_keys:
        del user_preferences[key]

    if "location" in user_preferences.keys():
        unnecessary_keys = [key for key in user_preferences["location"].keys()
                            if key not in default_user_prefs["location"].keys()]
        for key in unnecessary_keys:
            del user_preferences["location"][key]

    database = Database.get_instance()
    database.store_prefs(session["id"], user_preferences)
    return "", 201


@app.route("/test")
def test():
    db = Database.get_instance()
    prefs = db.load_prefs(session["id"])
    print(habit.load_data())
    print(welcome.load_data())
    print(holiday.load_data())
    print(coach.load_data())
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
