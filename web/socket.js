//HTML OBJ
let light = document.getElementsByClassName("primaryLight");
let secondarylight = document.getElementsByClassName("secondaryLight");
let scene = document.getElementById("scene");

//INSERT HERE YOUR MACHINE'S IPv4 ADDRESS
let oscPort = new osc.WebSocketPort({
  url: "wss://192.168.1.208:3000",
});

oscPort.on("message", function (msg) {
  console.log("message", msg);
  switch (msg.address) {
    case "/RGB":
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
  return res;
}

function componentToHex(c) {
  var hex = c.toString(16);
  return hex.length == 1 ? "0" + hex : hex;
}

function colorOnMsg(rgb) {
  let hexC = rgbToHex(rgb[0], rgb[1], rgb[2]);
  let compHex = getComplementaryColor(hexC);
  console.log("hex", hexC);
  console.log("complementary", compHex);
  for (let i = 0; i < light.length; i++) {
    light[i].setAttribute("animation", {
      property: "light.color",
      to: hexC,
      dur: 500,
      easing: "linear",
    });
  }
  for (let j = 0; j < secondarylight.length; j++) {
    secondarylight[j].setAttribute("animation", {
      property: "light.color",
      to: compHex,
      dur: 500,
      easing: "linear",
    });
    scene.setAttribute("animation", {
      property: "fog.color",
      to: hexC,
      dur: 500,
      easing: "linear",
    });
  }
  //light.setAttribute('light', 'color', hexC);
}

const getComplementaryColor = (color = "") => {
  const colorPart = color.slice(1);
  const ind = parseInt(colorPart, 16);
  let iter = ((1 << (4 * colorPart.length)) - 1 - ind).toString(16);
  while (iter.length < colorPart.length) {
    iter = "0" + iter;
  }
  return "#" + iter;
};
