from dotenv import load_dotenv
from flask import Flask

from service import service

app = Flask(__name__)


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    # Testing the APIs this way for now
    load_dotenv()

    print(service.get_rapla())
    STUTTGART_LAT = 48.783333
    STUTTGART_LON = 9.183333
    print(service.get_weather_forecast(STUTTGART_LAT, STUTTGART_LON))
    print(service.get_air_pollution(STUTTGART_LAT, STUTTGART_LON))
    print(service.get_sunrise_sunset(STUTTGART_LAT, STUTTGART_LON))
    print(service.get_wikipedia_extract("Stuttgart"))
    MCFIT_STUTTGART_MITTE = 1731421430
    print(service.get_gym_utilization(MCFIT_STUTTGART_MITTE))
    STUTTGART_AGS = "08111"
    print(service.get_covid_stats(STUTTGART_AGS))
