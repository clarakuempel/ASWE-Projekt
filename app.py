from dotenv import load_dotenv
from flask import Flask
from flask.helpers import send_from_directory

import service.service

app = Flask(__name__, static_folder='./frontend')


@app.route("/")
def default():
    """
    returns default html page
    """
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == "__main__":
    # app.run(debug=True, host='0.0.0.0', port=9090, threaded=True)
    # Testing the APIs this way for now
    load_dotenv()

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
    print(service.service.get_news_stories()["entries"][0]["title"])
    # print(service.service.get_bestselling_books())
