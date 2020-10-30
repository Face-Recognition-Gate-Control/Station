var isStepsComplete = function() {
  var allCompleted = true;
  $(".step").each( function() {
      if (!($(this).hasClass("completed"))) {
        allCompleted = false;
        return false;
      }
    });
    return allCompleted;
};

$(document).on('keydown', function(e) {
  if((e.ctrlKey || e.metaKey) && (e.key == "p" || e.charCode == 16 || e.charCode == 112 || e.keyCode == 80) ){
      alert("Please use the Print PDF button below for a better rendering on the document");
      e.cancelBubble = true;
      e.preventDefault();

      e.stopImmediatePropagation();
  }  
});

setInterval(function() {
  var mainPath = "/static/images/gate_status.jpg";
  var thumbPath = "/static/images/scott_thumb.png";
  var allGood = isStepsComplete();
  if (allGood) {
    setMainDisplay(mainPath);
    setThumbnailDisplay(thumbPath);
  }
  else{
    //
  }
}, 750);


var setMainDisplay = function(imPath="") {
  var defaultSrc = "/static/images/test.png";
    // var defaultSrc = "{{ url_for('frame_streamer') }}"
  if (imPath == "") {
    document.getElementById('main_display').src  = defaultSrc;
  } else {
    document.getElementById('main_display').src  = imPath;
  }
};

var setThumbnailDisplay = function(imPath="") {
  var defaultSrc = "/static/images/thumbnail.png";
  if (imPath == "") {
    document.getElementById('thumbnail').src  = defaultSrc;
  } else {
    document.getElementById('thumbnail').src  = imPath;
  }
};

var resetSystem = function() {
  disableStep(1);
  disableStep(2);
  disableStep(3);
  setMainDisplay();
  setThumbnailDisplay();
  console.log("Person entered through the Gate.");
};

var disableStep = function(stepID) {
  var step = document.getElementById("step" + stepID);
  if(step.classList.contains("completed")) {
    step.classList.remove("completed");
  }
};

var enableStep = function(stepID) {
  var step = document.getElementById("step" + stepID);
  if (!(step.classList.contains("completed"))) {
    step.classList.add("completed");
  }
};

var S_INIT = 0;
var S_SCANNING = 1;
var S_SCANNING = 1;
var S_SCANNING = 1;
var S_SCANNING = 1;
var currente_state = S_INIT;

const STATES = {
    INIT: "init",
    SCANNING: "scanning",
    VALIDATING: "validating",
    ACCESS: "access",
    RESET: "reset",
};



const ws = new WebSocket("ws://localhost:8000/ws");


ws.onmessage = function(event) {

  if (event) {
    console.log(event);
  }




  // switch(system_state) {

  //   case STATES.INIT:
  //       enableStep(1)
  //       break;

  //   case STATES.SCANNING:
  //       enableStep(1)
  //       break;

  //   case STATES.VALIDATING:
  //       enableStep(2)
  //       break;

  //   case STATES.ACCESS:
  //       enableStep(3)
         // START SYSTEM TIMER FOR 10 seconds?
  //       break;

  //   case STATES.RESET:
  //       resetSystem();
  //       break;

  //   default:
       //BLABLA
  //   }
  //s.send(input.value)
};




$(document).ready(function() {
  console.log("Document ready");
});


