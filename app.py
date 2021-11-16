import os
import random
import uuid

import urllib3
from dotenv import load_dotenv
from flask import Flask, request, session, jsonify
from flask.helpers import send_from_directory
from ibm_cloud_sdk_core import IAMTokenManager
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import AssistantV2

from database import Database
from service import api, utility
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

        watson_res["context"]["skills"]["main skill"]["user_defined"].update(usecase_data)

        watson_res = assistant.message_stateless(
            assistant_id=os.environ.get("WATSON_ASSISTANT_ID"),
            context=watson_res["context"]
        ).get_result()

        tts = get_watson_tts(watson_res)
        tts_output.append(tts)

    if current_intent_var == "reading_no":
        # Get data required for this specific node:
        # -> user has not read yet
        # -> we need a book that watson can recommend
        book_data = api.get_bestselling_books().json()
        books = utility.parse_bestselling_books(book_data)

        # Set 'backend data' in context variable so watson can access it
        watson_res["context"]["skills"]["main skill"]["user_defined"][
            "book"] = f"'{books[0]['title'].title()}' by {books[0]['author']}"

        # Send the updated context (with the new data) to watson
        watson_res = assistant.message_stateless(
            assistant_id=os.environ.get("WATSON_ASSISTANT_ID"),
            context=watson_res["context"]
        ).get_result()

        # Get the final sentence (-> the book recommendation)
        tts = get_watson_tts(watson_res)
        tts_output.append(tts)

        # Delete the context variable if we dont need it anymore so it doesn't interfere with future requests
        del watson_res["context"]["skills"]["main skill"]["user_defined"]["book"]

        # Repeat above pattern for every node that requires data
    elif current_intent_var == "3:yes_sport":
        rapla_current_lecture = None
        rapla_next_lecture = None
        rapla_lectures = None
        rapla_data = api.get_rapla().json()
        events = utility.get_events(rapla_data)
        if "rapla_lectures" in events.keys():
            rapla_lectures = events["rapla_lectures"]
        if "rapla_current_lecture" in events.keys():
            rapla_current_lecture = events["rapla_current_lecture"]
        if "rapla_next_lecture" in events.keys():
            rapla_next_lecture = events["rapla_next_lecture"]

        watson_res["context"]["skills"]["main skill"]["user_defined"]["rapla_lectures"] = rapla_lectures
        watson_res["context"]["skills"]["main skill"]["user_defined"]["rapla_current_lecture"] = rapla_current_lecture
        watson_res["context"]["skills"]["main skill"]["user_defined"]["rapla_next_lecture"] = rapla_next_lecture

        # weather_data = api.get_weather_forecast(48.783333, 9.183333).json()
        # weather, icon = utility.get_current_weather(weather_data)
        # watson_res["context"]["skills"]["main skill"]["user_defined"]["weather"] = weather

        watson_res = assistant.message_stateless(
            assistant_id=os.environ.get("WATSON_ASSISTANT_ID"),
            context=watson_res["context"]
        ).get_result()

        tts = get_watson_tts(watson_res)
        tts_output.append(tts)

        del watson_res["context"]["skills"]["main skill"]["user_defined"]["rapla_lectures"]
        del watson_res["context"]["skills"]["main skill"]["user_defined"]["rapla_current_lecture"]
        del watson_res["context"]["skills"]["main skill"]["user_defined"]["rapla_next_lecture"]

    elif current_intent_var == "3:rapla_yes":
        weather_data = api.get_weather_forecast(48.783333, 9.183333).json()
        weather, icon = utility.get_current_weather(weather_data)
        watson_res["context"]["skills"]["main skill"]["user_defined"]["weather"] = weather

        gym_data = api.get_gym_utilization(1731421430).json()
        utilization = utility.parse_gym_utilization(gym_data)
        gym = {
            "auslastung": utilization,
            "name": "McFIT Stuttgart-Mitte"
        }
        watson_res["context"]["skills"]["main skill"]["user_defined"]["gym"] = gym

        yt_data = api.get_youtube_search("home workout pamela reif 20 min").json()
        yt = utility.parse_youtube_search(yt_data)
        r = random.randrange(0, 10)
        video = {
            "title": yt[r]["title"],
        }
        watson_res["context"]["skills"]["main skill"]["user_defined"]["video"] = video

        watson_res = assistant.message_stateless(
            assistant_id=os.environ.get("WATSON_ASSISTANT_ID"),
            context=watson_res["context"]
        ).get_result()

        tts = get_watson_tts(watson_res)
        tts_output.append(tts)

        del watson_res["context"]["skills"]["main skill"]["user_defined"]["weather"]

    # Save the last known context to user cookie so we have it in the next user request (contains username etc.)
    session["context"] = watson_res.get("context", None)

    # watson, intent, and user_defined are debugging values will be removed
    # Later we pass only tts output and display data (e.g. links, images, etc)
    return jsonify(tts=" ".join(tts_output), watson=watson_res, intent=first_intent, user_defined=user_defined)


def get_first_intent(watson_response):
    try:
        return watson_response["output"]["intents"][0]["intent"]
    except (KeyError, IndexError):
        return None


def get_watson_tts(watson_response):
    tts = None
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
