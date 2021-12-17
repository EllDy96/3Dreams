let scene = document.querySelector('a-scene');

console.log(scene);

let env = document.createElement('a-entity');
env.setAttribute('environment', 'preset: volcano');

scene.appendChild(env);
