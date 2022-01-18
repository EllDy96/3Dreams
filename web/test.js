//TESTING
let velocity = 0.01;

let sfera = document.getElementById('sfera');
let start, previousTimeStamp;
let previousSecond = 0;
let direction = 1;

function render(timestamp) {
  if (start === undefined) {
    start = timestamp;
  }
  const elapsed = timestamp - start;
  let second = Math.trunc(elapsed - (Math.trunc(elapsed) % 1000)) / 1000;

  /* let nextX = sfera.object3D.position.x + velocity;
  sfera.setAttribute(
    'animation',
    `property: position; to: ${nextX} 1.319 3.663`
  );
  sfera.object3D.position.x = nextX; */
  /* console.log(sfera.children);  */

  if (sfera.object3D.position.x < -2 || sfera.object3D.position.x > 2)
    velocity *= -1;

  if (second !== previousSecond) {
    // Stop the animation after 2 seconds
    console.log('back animation');
    previousTimeStamp = timestamp;
    direction *= -1;
    sfera.setAttribute(
      'animation',
      `property: position; to: ${direction * 1.661} 1.319 3.663`
    );
  }

  previousSecond = second;
  window.requestAnimationFrame(render);
}

/* sfera.setAttribute('animation', `property: position; to: -1.661 1.319 3.663`); */

setInterval(() => {
  let nextX = sfera.object3D.position.x + velocity;
  sfera.setAttribute(
    'animation',
    `property: position; to: ${nextX} 1.319 3.663`
  );
  sfera.object3D.position.x = nextX;

  if (sfera.object3D.position.x < -2 || sfera.object3D.position.x > 2)
    velocity *= -1;
});

/* window.requestAnimationFrame(render); */
