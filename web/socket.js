export default function initSocket(boidsController, simpleRenderer) {
  //HTML OBJ
  let light = document.getElementsByClassName('primaryLight');
  let secondarylight = document.getElementsByClassName('secondaryLight');
  let sky = document.getElementById('sky');
  let scene = document.getElementById('scene');
  let colorAnimation = document.getElementsByClassName('colorAnimation');
  let obstacles = boidsController.getObstacleEntities();

  //INSERT HERE YOUR MACHINE'S IPv4 ADDRESS
  let oscPort = new osc.WebSocketPort({
    url: 'wss://192.168.1.208:3000',
  });

  oscPort.on('message', function (msg) {
    switch (msg.address) {
      case '/RGB':
        colorOnMsg(msg.args);
        break;
      case '/INST_ENERGY':
        //console.log('message', msg);
        lightIntensity(msg.args);
        simpleRenderer.breathe(msg.args[0]);
      case '/COHESION':
        //console.log('COHESION', msg.args);
        changeCohesion(msg.args);
        break;
      case '/ALIGNMENT':
        //console.log('ALIGNMENT', msg.args);
        changeAlignment(msg.args);
        break;
      case '/SEPARATION':
        //console.log('SEPARATION', msg.args);
        changeSeparation(msg.args);
        break;
      case '/SPEED':
        //console.log('SPEED', msg.args);
        changeMaxSpeed(msg.args);
        break;
      case '/VALENCE':
        //console.log('VALENCE', msg.args);

        break;
      case '/AROUSAL':
        //console.log('AROUSAL', msg.args);
        if (msg.args < 0) {
          increaseSadness(msg.args);
        } else {
          decreaseSadness(msg.args);
        }
        break;
      default:
        break;
    }
  });

  oscPort.open();

  //NOT NEEDED
  /* oscPort.socket.onmessage = function (e) {
  console.log("message", e);
  header.innerHTML = "lel";
};
 */

  function decreaseSadness(arousal) {
    scene.setAttribute('animation__arousal', {
      property: 'fog.density',
      to: 0.013,
      dur: 500,
      easing: 'linear',
    });

    light[0].setAttribute('animation__arousal', {
      property: 'light.intensity',
      to: 0.5,
      dur: 1500,
      easing: 'linear',
    });

    light[1].setAttribute('animation__arousal', {
      property: 'light.intensity',
      to: 2.5,
      dur: 1500,
      easing: 'linear',
    });
  }

  function increaseSadness(arousal) {
    scene.setAttribute('animation__arousal', {
      property: 'fog.density',
      to: 0.05 - arousal / 7,
      dur: 1500,
      easing: 'linear',
    });

    light[0].setAttribute('animation__arousal', {
      property: 'light.intensity',
      to: 2.5 - arousal / 4,
      dur: 1500,
      easing: 'linear',
    });

    light[1].setAttribute('animation__arousal', {
      property: 'light.intensity',
      to: 0,
      dur: 1500,
      easing: 'linear',
    });
  }

  function changeAlignment(args) {
    boidsController.setAligmentWeight(args[0]);
  }

  function changeSeparation(args) {
    boidsController.setSeparationWeight(args[0]);
  }

  function changeCohesion(args) {
    boidsController.setCohesionWeight(args[0]);
  }

  function changeMaxSpeed(args) {
    boidsController.setMaxSpeed(args[0]);
  }

  function lightIntensity(args) {
    let min_value = 0.02;
    let max_value = 0.21;
    let value = args[0];
    let max_intensity = 3;
    let min_intensity = 0.1;
    let intensity =
      ((value - min_value) * (max_intensity - min_intensity)) /
        (max_value - min_value) +
      min_intensity;
    for (let j = 0; j < secondarylight.length; j++) {
      secondarylight[j].setAttribute('animation__light', {
        property: 'light.intensity',
        to: intensity,
        dur: 300,
        easing: 'linear',
      });

      // secondarylight[j].object3D.el.getAttribute('light').intensity = intensity;
    }
  }

  function rgbToHex(r, g, b) {
    let res = '#' + componentToHex(r) + componentToHex(g) + componentToHex(b);
    return res;
  }

  function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? '0' + hex : hex;
  }

  function hexToRgbA(hex) {
    var c;
    if (/^#([A-Fa-f0-9]{3}){1,2}$/.test(hex)) {
      c = hex.substring(1).split('');
      if (c.length == 3) {
        c = [c[0], c[0], c[1], c[1], c[2], c[2]];
      }
      c = '0x' + c.join('');
      return (
        'rgba(' + [(c >> 16) & 255, (c >> 8) & 255, c & 255].join(',') + ',1)'
      );
    }
    throw new Error('Bad Hex');
  }

  function colorOnMsg(rgb) {
    let hexC = rgbToHex(rgb[0], rgb[1], rgb[2]);
    let compHex = getComplementaryColor(hexC);
    // let rgba = hexToRgbA(hexC);
    let compRgba = hexToRgbA(compHex);

    /* console.log("hex", hexC); */
    /* console.log('complementary', compRgba); */

    scene.setAttribute('animation', {
      property: 'fog.color',
      to: hexC,
      dur: 1500,
      easing: 'linear',
    });

    for (let i = 0; i < light.length; i++) {
      /* light[i].object3D.el.getAttribute("light").color = hexC; */

      light[i].setAttribute('animation', {
        property: 'light.color',
        to: hexC,
        dur: 1500,
        easing: 'linear',
      });
    }
    for (let j = 0; j < secondarylight.length; j++) {
      /* secondarylight[j].object3D.el.getAttribute("light").color = compHex; */
      secondarylight[j].setAttribute('animation', {
        property: 'light.color',
        to: compHex,
        dur: 1500,
        easing: 'linear',
      });
    }
  }

  const getComplementaryColor = (color = '') => {
    const colorPart = color.slice(1);
    const ind = parseInt(colorPart, 16);
    let iter = ((1 << (4 * colorPart.length)) - 1 - ind).toString(16);
    while (iter.length < colorPart.length) {
      iter = '0' + iter;
    }
    return '#' + iter;
  };

  /* setInterval(() => {
  console.log(secondarylight[0].getAttribute("light").color);
  console.log(secondarylight[0].getAttribute("light").intensity);
}); */
}
