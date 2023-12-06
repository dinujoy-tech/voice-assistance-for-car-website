const openModalButton = document.getElementById("open-modal");
const modal = document.getElementById("modal");
const closeModalButton = document.getElementById("close-modal");
const typingSpeed = 100;
const typingContainer = document.getElementById("modal-content");
var transcript="";
window.SpeechRecognition = window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
recognition.interimResults = true;

async function speakText(text) {
  var synth = window.speechSynthesis;
  var utterance = new SpeechSynthesisUtterance(text);
  synth.speak(utterance);
  return true;
  }
function typeText(index,textToType) {
  modal.style.display = "block";
 
  if (index < textToType.length) {
      typingContainer.innerHTML += textToType.charAt(index);
      setTimeout(function () {
          typeText(index + 1,textToType);
      }, typingSpeed);

  }
  else{
      recognition.start();
      }
}

openModalButton.addEventListener("click", () => {
    
  connect_todialogflow("Hello")
  
});


window.addEventListener("click", (event) => {
    if (event.target === modal) {
        modal.style.display = "none";
    }
});
openModalButton.addEventListener("click", () => {
    
    
});

 recognition.addEventListener('result', e => {
      transcript = Array.from(e.results)
         .map(result => result[0])
         .map(result => result.transcript)
         .join('')

     console.log(transcript);
 });

 recognition.addEventListener('end', async e => {
      connect_todialogflow(transcript);
   
 });
async function connect_todialogflow(request) {
    console.log(request);
    transcript="";
    var url = '/dialog';
    var data = {
        text: request
    };
    var headers = {
        'Content-Type': 'application/json'
    };

    return fetch(url, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        var contentType = response.headers.get('content-type');
        if (contentType.includes('application/json')) {
          // Handle JSON response
          return response.json()
              .then(data => {
                  console.log(data);
                  if(data.intent_name == "Welcome Intent"|| data.intent_name == "Default Fallback Intent" || data.intent_name=="brand_selection"){
                    console.log(data.fullfilment_text);
                    speakText(data.fullfilment_text);
                    typingContainer.innerHTML = "";
                    typeText(0,data.fullfilment_text);
                  }
                
              });
          } else if (contentType.includes('text/html')) {
                  // Handle HTML response
                  console.log("html");
                  return response.text()
                      .then(html => {
                          // Assuming you want to display the HTML content in a div with ID 'response-container'
                        modal.style.display = "none";
                      document.getElementById('main').innerHTML = html;
                        b_effect();
                        // recognition.start();
                      });
              }
          })
    .catch(error => {
        console.error('Error:', error);
        throw error; // Propagate the error
    });
  
}

async function b_effect() {
  const images = document.querySelectorAll('.images');

  function addBorderEffect(image) {
    image.classList.add('border-effect', 'active');
  }

  function removeBorderEffect(image) {
    image.classList.remove('active');
  }

  function applyEffectWithDelay(image, delay) {
    return new Promise((resolve) => {
      setTimeout(() => {
        addBorderEffect(image);
        resolve();
      }, delay);
    });
  }

  function resetEffectWithDelay(image,delay) {
    return new Promise((resolve) => {
      setTimeout(() => {
          removeBorderEffect(image);
        resolve();
      }, delay);
    });
  }

  for (let i = 0; i < images.length; i++) {
     await speakText(images[i].alt);
    await applyEffectWithDelay(images[i],0);
    
    await resetEffectWithDelay(images[i],3000);
  }
  
  recognition.start();
}
