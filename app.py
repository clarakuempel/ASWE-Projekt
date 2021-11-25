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
    """
    Assign each new user a session_id. Session id is used to save user preferences.
    """
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
    """
    Connect user input with Watson Assistant. Handles usecase intent identification,
    loading and passing data to watson. And output back to the user.
    """
    user_input = request.json.get("input", None)
    print(f"Got user input: {user_input}")

    user_context = session.get("context", None)

    database = Database.get_instance()
    user_preferences = default_user_prefs.copy()
    user_preferences.update(database.load_prefs(session["id"]))
    print(user_preferences["username"])
    if user_context is not None:
        user_context["skills"]["main skill"]["user_defined"].update(
            {"username": user_preferences["username"]}
        )
    else:
        user_context = {"skills": {
            "main skill": {
                "user_defined": {
                    "username": user_preferences["username"]
                }
            }
        }}

    watson_res = assistant.message_stateless(
        assistant_id=os.environ.get("WATSON_ASSISTANT_ID"),
        input={
            'message_type': 'text',
            'text': user_input
        },
        context=user_context
    ).get_result()

    first_intent = get_first_intent(watson_res)
    tts_output = []
    tts = get_watson_tts(watson_res)
    tts_output.append(tts)

    user_defined, current_intent_var = get_context_variables(watson_res)

    usecase_data = {}
    if first_intent == "Good_Morning":
        usecase_data = welcome.load_data(session["id"])

    elif first_intent in ["Habit_Reading", "Habit_Meditating", "Habit_Sleeping"]:
        usecase_data = habit.load_data(session["id"])

    elif first_intent == "Sports":
        usecase_data = coach.load_data()

    elif first_intent == "holiday_finder":
        usecase_data = holiday.load_data()

    if first_intent is not None:
        watson_res["context"]["skills"]["main skill"]["user_defined"].update(usecase_data)
        if usecase_data:
            watson_res = assistant.message_stateless(
                assistant_id=os.environ.get("WATSON_ASSISTANT_ID"),
                context=watson_res["context"]
            ).get_result()
            tts = get_watson_tts(watson_res)
            tts_output.append(tts)

    session["context"] = watson_res.get("context", None)
    return jsonify(tts=" ".join(tts_output), watson=watson_res, intent=first_intent, user_defined=user_defined)


def get_first_intent(watson_response):
    """
    Parse watson response to get the first intent. first = highest identification confidence
    :param watson_response:  Watson response object
    :return: First intent as string
    """
    try:
        return watson_response["output"]["intents"][0]["intent"]
    except (KeyError, IndexError):
        return None


def get_watson_tts(watson_response):
    """
    Parse watson response to get TTS output
    :param watson_response: Watson response object
    :return: TTS output
    """
    tts = ""
    try:
        tts = " ".join([entry["text"] for entry in watson_response["output"]["generic"]])
    except (KeyError, IndexError):
        pass
    return tts


def get_context_variables(watson_response):
    """
    Parse the watson response to get context variables
    :param watson_response: Watson response object
    :return: user_defined, current_context
    """
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


@app.route("/api/preferences", methods=['GET'])
def get_user_preferences():
    """
    Get user preferences and gym selection
    """
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
    """
    Set user preferences
    """
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


@app.route("/debug-chat")
def test_chat():
    """
    Simple watson chat to debug usecase dialogs
    """
    return send_from_directory(app.static_folder, 'debug-chat.html')


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
