window.onload = function() {
  setPreferences();
};


var wsURI = {
  STT: 'wss://api.eu-de.speech-to-text.watson.cloud.ibm.com/instances/2bbdb10c-31b9-4df9-ac7f-bc364d79b14e/v1/recognize', //?access_token=' + access_token
  TTS: 'wss://api.eu-de.text-to-speech.watson.cloud.ibm.com/instances/87d423d8-6ddd-42c3-90a7-4711fca37587' ///v1/synthesize'
}

document.querySelector('#rec-button').addEventListener('click', function(){
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

// text to speech
function speech(text){
  fetch('/api/tts-token')
  .then(function(response) {
    return response.json();
  })
  .then(function(res) {
    const audio = TTS.synthesize({
      accessToken: res.token,
      url: res.url,
      text: text,
    });
    audio.onerror = function(err) {
      console.log('audio error: ', err);
    };
  });
}

async function startRecord(){
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

      stream.on('data', function(data) {
        console.log(data)
        try {
          console.log(data.results[0].alternatives[0].transcript);
          input = data.results[0].alternatives[0].transcript
        } catch (error) {
          
        }
        
      })
      stream.on('error', function(err) {
        console.log(err);
      })

      document.querySelector('#rec-button').addEventListener('click', () => {
        var el = document.getElementById('rec-button'),
        elClone = el.cloneNode(true);
        el.parentNode.replaceChild(elClone, el);
        stream.stop()
        console.log('stream stopped..', input)
        console.log(input.valueOf())
        if(input.length === 0){console.log("SDSDS")}
        send('/api/dialog', input).then((res) => {
          res = 'Test test'
          // speech(res)
          document.getElementById('m2').innerHTML = res
        })
        document.querySelector('#rec-button').addEventListener('click', function(){
          startRecord()
        })
      })
  })
}

//set pref
function setPreferences(){
  send('/api/preferences').then((res) => {
    document.getElementById("wakeup_time").value = res.wakeup_time
    document.getElementById("assistent_sex").value = res.assistant_sex
    document.getElementById('location_lat').value = res.location.lat
    document.getElementById('location_lon').value = res.location.lon
    document.getElementById('gemeindecode').value = res.location.ags
    document.getElementById("news_topic").value = res.news
    document.getElementById("gym").value = res.gym
  })
}

// send user pref to backend
function submitPreferences(){
  let data = {
    "weckzeit": document.getElementById("wakeup_time").value,
    "assistent_sex": document.getElementById("assistent_sex").value,
    "location": {
      "lat": parseFloat(document.getElementById('location_lat').value),
      "lon": parseFloat(document.getElementById('location_lon').value),
      "ags": document.getElementById('gemeindecode').value,
    },
    "news": document.getElementById("news_topic").value,
    "gym": parseInt(document.getElementById("gym").value)
  }
  console.log(data)

  send('/api/preferences', data)

  async function send(url, data) {
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
}

function triggerUsecase(trigger_text){
  send('/api/dialog', trigger_text).then((res) => {
    document.getElementById('m1').innerHTML = res
  })
}