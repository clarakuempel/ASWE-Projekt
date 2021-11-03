import os
import uuid

from dotenv import load_dotenv
from flask import Flask, request, session, jsonify
from flask.helpers import send_from_directory
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import AssistantV2

import service
from database import Database
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


@app.route("/api/dialog", methods=['GET', 'POST'])
def get_dialog_response():
    req_data = request.json
    print(f"Got req data: {req_data}")

    if not req_data:
        return jsonify(tts="no input data")

    user_input = req_data.get("input")

    # if "watson" not in session:
    #     session["watson"] = assistant.create_session(assistant_id=os.environ.get("WATSON_ASSISTANT_ID")).get_result()[
    #         "session_id"]
    #
    # watson_res = assistant.message(
    #     assistant_id=os.environ.get("WATSON_ASSISTANT_ID"),
    #     session_id=session["watson"],
    #     input={
    #         'message_type': 'text',
    #         'text': user_input
    #     }
    # ).get_result()

    user_context = session.get("context", None)

    watson_res = assistant.message_stateless(
        assistant_id=os.environ.get("WATSON_ASSISTANT_ID"),
        input={
            'message_type': 'text',
            'text': user_input
        },
        context=user_context
    ).get_result()

    first_intent = watson_res["output"]["intents"][0]["intent"]
    print("123 " + first_intent)
    if first_intent == "welcome_news":
        watson_res["context"]["skills"]["main skill"]["user_defined"][
            "news_test"] = service.utility.get_new_stories()["tts"]

        watson_res = assistant.message_stateless(
            assistant_id=os.environ.get("WATSON_ASSISTANT_ID"),
            input={},
            context=watson_res["context"]
        ).get_result()

    session["context"] = watson_res["context"]

    return jsonify(tts=watson_res["output"]["generic"][0]["text"], watson=watson_res)


# first_intent = watson_res["output"]["intents"][0]["intent"]
# if first_intent == "General_Greetings":
#    return jsonify(tts="I am Ivy. What's your name?", context=watson_res["context"], watson=watson_res)
# else:
#    return jsonify(tts="I don't understand", context=watson_res["context"], watson=watson_res)


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


@app.route("/test_chat")
def test_chat():
    return send_from_directory(app.static_folder, 'watson_chat.html')


if __name__ == "__main__":
    # Load .env file with secrets and credentials
    load_dotenv()

    Database.get_instance().initialize()

    authenticator = IAMAuthenticator(os.environ.get("WATSON_ASSISTANT_API"))
    authenticator.set_disable_ssl_verification(True)
    assistant = AssistantV2(version='2021-06-14', authenticator=authenticator)

    assistant.set_service_url('https://api.eu-de.assistant.watson.cloud.ibm.com')
    assistant.set_disable_ssl_verification(True)

    app.run(debug=True, host='0.0.0.0', port=9090, threaded=True)
