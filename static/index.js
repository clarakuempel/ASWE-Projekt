const VOICES = [
    'en-US_AllisonV3Voice',
    'en-US_EmilyV3Voice',
    'en-US_HenryV3Voice',
    'en-US_KevinV3Voice',
    'en-US_LisaV3Voice',
    'en-US_MichaelV3Voice'
]

window.onload = function () {
    setVoices()
    setPreferences();
};

window.setInterval(function () {
    checkTime();
}, 50000);

document.querySelector('#rec-button').addEventListener('click', function () {
    startRecord()
})

let setHour;
let setMin;

function setVoices(){
    var min = 0,
    max = 5,
    select = document.getElementById('assistent_sex');
    for (var i = min; i<=max; i++){
        var voice_pre = VOICES[i].split(['_'])
        var voice_name = voice_pre[1].split('V3')
        var opt = document.createElement('option');
        opt.value = VOICES[i];
        opt.innerHTML = voice_name[0];
        select.appendChild(opt);
    }
    return true
}

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
    fetch('/api/tts-token')
        .then(function (response) {
            return response.json();
        })
        .then(function (res) {
            let voice = document.getElementById('assistent_sex').value
            const audio = TTS.synthesize({
                accessToken: res.token,
                voice: voice,
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
            document.getElementById('m1_user').style.display = 'block'
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
            sendToBackend(data, 'm2')
            document.querySelector('#rec-button').addEventListener('click', function () {
                startRecord()
            })
        })
    })
}

function sendToBackend(data, targetId){
    sendPost('/api/dialog', data).then((res) => {
        if(targetId == 'm2'){
            document.getElementById('m1').style.display = 'none'
        }
        let target = document.getElementById(targetId)
        console.log(res)
        target.style.display = 'block'
        target.innerHTML = res.tts
        speech(res.tts)
        console.log(res.extra.image)
        if(res.extra.link != undefined && res.extra.image != undefined && res.extra.image != 'https://openweathermap.org/img/wn/03n@2x.png'
        && res.tts != "I didn't get your meaning." && res.tts != "I didn't understand. You can try rephrasing."
        && res.tts != "Can you reword your statement? I'm not understanding."
        && (
            res.user_defined.current_intent == "2:mediation_yes"
            || res.user_defined.current_intent == "3:workout"
        )
         && (res.tts).toLowerCase().includes('video')
        ){
            let target_extra1 = document.getElementById('m2_extra1')
            target_extra1.style.display = 'block'
            target_extra1.src = res.extra.image
            target_extra1.href = res.extra.link
            let target_extra2 = document.getElementById('m2_extra2')
            target_extra2.style.display = 'block'
            target_extra2.innerHTML = res.extra.link
            target_extra2.href = res.extra.link
        } else {
            document.getElementById('m2_extra1').style.display = 'none'
            document.getElementById('m2_extra2').style.display = 'none'
        }
    })
}

function test(triggertext){
    let data = {
        input: triggertext
    }
    sendToBackend(data, 'm2')
}


function triggerUsecase(trigger_text){
    let data = {
      input: trigger_text
    }
    document.getElementById('m2').style.display = 'none'
    document.getElementById('m1_user').style.display = 'none'
    sendToBackend(data, 'm1')
  }

//set pref
function setPreferences() {
    send('/api/preferences').then((res) => {
        document.getElementById("wakeup_time").value = res.preferences.wakeup_time
        document.getElementById("assistent_sex").value = res.preferences.assistant_sex
        document.getElementById('location_lat').value = res.preferences.location.lat
        document.getElementById('location_lon').value = res.preferences.location.lon
        document.getElementById('gemeindecode').value = res.preferences.location.ags
        document.getElementById("news_topic").value = res.preferences.news
        document.getElementById("username").value = res.preferences.username
        setGyms(res.gyms, res.preferences.gym)
    }).then(() => {
        updateWakeup(document.getElementById('wakeup_time').value)
    }).catch((err) => {
        console.error('Err in setPreferences :: ', err)
    })
}

function setGyms(gyms, thisone){
    console.log(gyms[0].id)
    select = document.getElementById("gym");
    for (let i = 0; i < gyms.length; i++){
        var opt = document.createElement('option');
        opt.value = gyms[i].id;
        opt.innerHTML = gyms[i].name;
        select.appendChild(opt);
    }
    document.getElementById('gym').value=thisone
}

function updateWakeup(time) {
    setHour = parseInt(time.substring(0, 2))
    setMin = parseInt(time.substring(3))
}

// send user pref to backend
function submitPreferences() {
    let data = {
        "wakeup_time": document.getElementById("wakeup_time").value,
        "assistant_sex": document.getElementById("assistent_sex").value,
        "location": {
            "lat": parseFloat(document.getElementById('location_lat').value),
            "lon": parseFloat(document.getElementById('location_lon').value),
            "ags": document.getElementById('gemeindecode').value,
        },
        "news": document.getElementById("news_topic").value,
        "gym": parseInt(document.getElementById("gym").value),
        "username": document.getElementById("username").value
    }

    updateWakeup((document.getElementById("wakeup_time").value))

    sendPost('/api/preferences', data)
}