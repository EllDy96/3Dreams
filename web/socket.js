let header = document.getElementById("msg");

//INSERT HERE YOUR MACHINE'S IPv4 ADDRESS
let oscPort = new osc.WebSocketPort({
  url: "wss://192.168.1.187:3000",
});

oscPort.on("message", function (msg) {
  // header.innerHTML = msg.args[0];
  console.log("message", msg);
});

oscPort.open();

//NOT NEEDED
/* oscPort.socket.onmessage = function (e) {
  console.log('message', e);
  header.innerHTML = 'lel';
};
 */
