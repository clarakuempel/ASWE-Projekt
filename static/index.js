window.onload = function () {
    setPreferences();
};

let setHour;
let setMin;

window.setInterval(function () {
    checkTime();
}, 50000);

function checkTime(time) {
    console.info("checking time..")
    var date = new Date()
    var hours = date.getHours();
    var mins = date.getMinutes();
    if (hours == setHour && mins == setMin) {
        console.info('match')
        triggerUsecase('Good Morning')
    }
}

var wsURI = {
    STT: 'wss://api.eu-de.speech-to-text.watson.cloud.ibm.com/instances/2bbdb10c-31b9-4df9-ac7f-bc364d79b14e/v1/recognize', //?access_token=' + access_token
    TTS: 'wss://api.eu-de.text-to-speech.watson.cloud.ibm.com/instances/87d423d8-6ddd-42c3-90a7-4711fca37587' ///v1/synthesize'
}

document.querySelector('#rec-button').addEventListener('click', function () {
    startRecord()
})

async function send(url) {
    const response = await fetch(url, {
        method: 'GET',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
    })
    return response.json()
}

async function sendPost(url, data) {
    const response = await fetch(url, {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
        body: JSON.stringify(data)
    })
    return response.json()
}

// text to speech
function speech(text) {
    send('/api/tts-token')
        .then(function (response) {
            return response.json();
        })
        .then(function (res) {
            const audio = TTS.synthesize({
                accessToken: res.token,
                url: res.url,
                text: text,
            });
            audio.onerror = function (err) {
                console.log('audio error: ', err);
            };
        });
}

async function startRecord() {
    var el = document.getElementById('rec-button'),
        elClone = el.cloneNode(true);
    el.parentNode.replaceChild(elClone, el);

    send('/api/stt-token').then((res) => {
        console.log('got token :: ', res)
        var stream = STT.recognizeMicrophone({
            accessToken: res.token,
            outputElement: "#m1_user",
            url: wsURI.STT
        })
        // stream.setEncoding('utf8')

        let input = ''

        stream.on('data', function (data) {
            try {
                console.log(data.results[0].alternatives[0].transcript);
                input = data.results[0].alternatives[0].transcript
            } catch (error) {

            }

        })
        stream.on('error', function (err) {
            console.log(err);
        })

        document.querySelector('#rec-button').addEventListener('click', () => {
            var el = document.getElementById('rec-button'),
                elClone = el.cloneNode(true);
            el.parentNode.replaceChild(elClone, el);
            stream.stop()
            console.log('stream stopped..', input)
            console.log(input.valueOf())
            data = {
                "input": input
            }
            sendPost('/api/dialog', data).then((res) => {
                document.getElementById('m2').innerHTML = res.tts
                speech(res.tts)
            })
            document.querySelector('#rec-button').addEventListener('click', function () {
                startRecord()
            })
        })
    })
}

//set pref
function setPreferences() {
    send('/api/preferences').then((res) => {
        document.getElementById("wakeup_time").value = res.wakeup_time
        document.getElementById("assistent_sex").value = res.assistant_sex
        document.getElementById('location_lat').value = res.location.lat
        document.getElementById('location_lon').value = res.location.lon
        document.getElementById('gemeindecode').value = res.location.ags
        document.getElementById("news_topic").value = res.news
        document.getElementById("gym").value = res.gym
    }).then(() => {
        updateWakeup(document.getElementById('wakeup_time').value)
    }).catch((err) => {
        console.error('Err in setPreferences :: ', err)
    })
}

function updateWakeup(time) {
    setHour = parseInt(time.substring(0, 2))
    setMin = parseInt(time.substring(3))
}

// send user pref to backend
function submitPreferences() {
    let data = {
        "wakeup_time": document.getElementById("wakeup_time").value,
        "assistent_sex": document.getElementById("assistent_sex").value,
        "location": {
            "lat": parseFloat(document.getElementById('location_lat').value),
            "lon": parseFloat(document.getElementById('location_lon').value),
            "ags": document.getElementById('gemeindecode').value,
        },
        "news": document.getElementById("news_topic").value,
        "gym": parseInt(document.getElementById("gym").value)
    }

    updateWakeup((document.getElementById("wakeup_time").value))

    sendPost('/api/preferences', data)
}


function triggerUsecase(trigger_text){
  let data = {
    input: trigger_text
  }
  sendPost('/api/dialog', data).then((res) => {
    console.log(res)
    document.getElementById('m1').innerHTML = res.tts
    speech(res.tts)
  })
}