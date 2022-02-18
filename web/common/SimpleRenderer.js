/**
 * @module SimpleRenderer
 * SimpleRenderer helps visualizing the entities in the BoidsController and controls the camera.
 */
export default class SimpleRenderer {
  constructor({ boidsController, flockEntityCount, obstacleEntityCount }) {
    this.boidsController = boidsController;
    this.flockEntityCount = flockEntityCount;
    this.obstacleEntityCount = obstacleEntityCount;
    this.boids = [];
    this.obstacles = [];
    this.noses = [];
    //Obstacle angular velocities
    this.oscCounter = 0;
    this.obstaclesPeriods = [];
  }

  init() {
    /* BOIDS */
    let env = document.getElementById('boids');
    for (let i = 0; i < this.flockEntityCount; i++) {
      let boid = document.createElement('a-box');
      boid.setAttribute('depth', 15);
      boid.setAttribute('width', 5);
      boid.setAttribute('height', 5);
      boid.setAttribute('material', 'metalness: 1; color: white');
      this.boids.push(boid);
      env.appendChild(boid);

      let nose = document.createElement('a-entity');
      nose.setAttribute('id', `nose${i}`);
      boid.setAttribute('look-at', `#nose${i}`);
      this.noses.push(nose);
      env.appendChild(nose);
    }

    for (let i = 0; i < this.obstacleEntityCount; i++) {
      let obstacle = document.createElement('a-sphere');
      obstacle.setAttribute('radius', 40);
      obstacle.setAttribute('material', 'metalness: 1; color: white');
      this.obstacles.push(obstacle);
      env.appendChild(obstacle);

      //Periods generation
      let freq = 2;
      let period = 1 / freq;
      let Fs = 5000;
      let N = Math.floor(period * Fs);
      let phase = 2 * Math.PI * Math.random();
      let amp = 0.1 * Math.random();
      let osc = [];
      for (let i = 0; i < N; i++) {
        osc.push(amp * Math.cos((2 * Math.PI * freq * i) / Fs + phase));
      }

      this.obstaclesPeriods.push(osc);
    }
    this.render();
  }

  render() {
    const entities = this.boidsController.getFlockEntities();
    entities.forEach((entity, i) => {
      const x = entity.x;
      const y = entity.y;
      const z = entity.z;
      const vx = entity.vx;
      const vy = entity.vy;
      const vz = entity.vz;
      let mesh = entity.mesh;
      if (!mesh) {
        mesh = new THREE.Mesh(this.entityGeometry, this.entityMaterial);
        mesh.localVelocity = { x: 0, y: 0, z: 0 };
        entity.mesh = mesh;
      }

      // apply asymptotic smoothing
      mesh.position.x = 0.9 * mesh.position.x + 0.1 * x;
      mesh.position.y = 0.9 * mesh.position.y + 0.1 * y;
      mesh.position.z = 0.9 * mesh.position.z + 0.1 * z;
      mesh.localVelocity.x = 0.9 * mesh.localVelocity.x + 0.1 * vx;
      mesh.localVelocity.y = 0.9 * mesh.localVelocity.y + 0.1 * vy;
      mesh.localVelocity.z = 0.9 * mesh.localVelocity.z + 0.1 * vz;

      this.noses[i].object3D.position.x =
        mesh.position.x + mesh.localVelocity.x;
      this.noses[i].object3D.position.y =
        mesh.position.y + mesh.localVelocity.y;
      this.noses[i].object3D.position.z =
        mesh.position.z + mesh.localVelocity.z;

      this.boids[i].object3D.position.x = mesh.position.x;
      this.boids[i].object3D.position.y = mesh.position.y;
      this.boids[i].object3D.position.z = mesh.position.z;
    });

    const obstacles = this.boidsController.getObstacleEntities();
    obstacles.forEach((entity, i) => {
      const x = entity.x;
      const y = entity.y;
      const z = entity.z;
      let mesh = entity.mesh;
      if (!mesh) {
        mesh = new THREE.Mesh(this.obstacleGeometry, this.obstacleMaterial);
        entity.mesh = mesh;
      }

      mesh.position.x = x;
      mesh.position.y = y;
      mesh.position.z = z;

      //OBSTACLES
      this.obstacles[i].object3D.position.x = entity.x;
      this.obstacles[i].object3D.position.z = entity.z;

      //Oscillation on Y-dir
      this.obstacles[i].object3D.position.y =
        entity.y + this.obstaclesPeriods[i][this.oscCounter];
      entity.y = this.obstacles[i].object3D.position.y;
    });

    this.oscCounter++;
    if (this.oscCounter === this.obstaclesPeriods[0].length)
      this.oscCounter = 0;
  }
}
