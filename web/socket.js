//HTML OBJ
let light = document.getElementById("dirLight");

//INSERT HERE YOUR MACHINE'S IPv4 ADDRESS
let oscPort = new osc.WebSocketPort({
  url: "wss://192.168.1.208:3000",
});

oscPort.on("message", function (msg) {
  switch (msg.address) {
    case "/RGB":
      console.log("message", msg);
      colorOnMsg(msg.args);
      break;

    default:
      break;
  }
});

oscPort.open();

//NOT NEEDED
/* oscPort.socket.onmessage = function (e) {
  console.log('message', e);
  header.innerHTML = 'lel';
};
 */

function rgbToHex(r, g, b) {
  let res = "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
  console.log(res);
  return res;
}

function colorOnMsg(rgb) {
  let hexC = rgbToHex(rgb[0], rgb[1], rgb[2]);
  console.log("hex", hexC);
  light.setAttribute("light", "color", hexC + ";");
}
