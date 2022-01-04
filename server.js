const express = require('express');
const https = require('https');
const path = require('path');
const fs = require('fs');

const WebSocket = require('ws');
const osc = require('osc');

let getIPAddresses = function () {
  const os = require('os'),
    interfaces = os.networkInterfaces(),
    ipAddresses = [];

  for (let deviceName in interfaces) {
    let addresses = interfaces[deviceName];
    for (let i = 0; i < addresses.length; i++) {
      let addressInfo = addresses[i];
      if (addressInfo.family === 'IPv4' && !addressInfo.internal) {
        ipAddresses.push(addressInfo.address);
      }
    }
  }

  return ipAddresses;
};

// Bind to a UDP socket to listen for incoming OSC events.
let udpPort = new osc.UDPPort({
  localAddress: '0.0.0.0',
  localPort: 57121,
});

udpPort.on('ready', function () {
  let ipAddresses = getIPAddresses();
  console.log('Listening for OSC over UDP.');
  ipAddresses.forEach(function (address) {
    console.log(' Host:', address + ', Port:', udpPort.options.localPort);
  });
});

udpPort.open();

//Setting up https web server
const app = express();

let appResources = __dirname + '/web';
app.use('/', express.static(appResources));

const sslServer = https.createServer(
  {
    key: fs.readFileSync(path.join(__dirname, 'cert', 'key.pem')),
    cert: fs.readFileSync(path.join(__dirname, 'cert', 'cert.pem')),
  },
  app
);

//INSERT HERE YOUR MACHINE'S IPv4 ADDRESS
sslServer.listen(3000, 'here --> 192.x.x.x', () => {
  console.log('secure server on port 3000');
});

let wss = new WebSocket.Server({
  server: sslServer,
});

wss.on('connection', function (socket) {
  console.log('A Web Socket connection has been established!');
  let socketPort = new osc.WebSocketPort({
    socket: socket,
  });

  let relay = new osc.Relay(udpPort, socketPort, {
    raw: true,
  });
});
