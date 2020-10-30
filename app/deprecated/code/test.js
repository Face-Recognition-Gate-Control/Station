// // var ws = new WebSocket("ws://localhost:8000/ws");

// // ws.onmessage = function(event) {
// //     var messages = document.getElementById('messages')
// //     var message = document.createElement('li')
// //     var content = document.createTextNode(event.data)
// //     message.appendChild(content)
// //     messages.appendChild(message)
// // };
// // function sendMessage(event) {
// //     var input = document.getElementById("messageText")
// //     ws.send(input.value)
// //     input.value = ''
// //     event.preventDefault()
// // }

// var trigger = false;

// setInterval(function() {
//   var mainPath = "/static/images/gate_status.jpg";
//   var thumbPath = "/static/images/scott_thumb.png";

//   if(trigger) {
//     setMainDisplay(mainPath);
//   }
//   else {
//     setMainDisplay(thumbPath);
//   }
//   trigger = !trigger;
 
// }, 750);

// var setMainDisplay = function(imPath) {
//     document.getElementById('thumbnail').src  = imPath;
// };
  
  
// $(document).ready(function() {
//     // pass
//     console.log("FRONT-END INITIALIZED.");
// });