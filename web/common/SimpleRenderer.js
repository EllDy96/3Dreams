/**
 * @module SimpleRenderer
 * SimpleRenderer helps visualizing the entities in the BoidsController and controls the camera.
 */
export default class SimpleRenderer {
  constructor({ boidsController }) {
    this.boidsController = boidsController;
  }

  init() {
    let aframeBoids = n;
    this.render();
  }

  render() {
    const entities = this.boidsController.getFlockEntities();
    /* console.log(entities[1]); */
    entities.forEach((entity) => {
      const x = entity.x;
      const y = entity.y;
      const z = entity.z;
      const vx = entity.vx;
      const vy = entity.vy;
      const vz = entity.vz;
      let mesh = entity.mesh;
      if (!mesh) {
        mesh = document.createElement();
        mesh.localVelocity = { x: 0, y: 0, z: 0 };
        this.scene.add(mesh);
        entity.mesh = mesh;
      }

      // apply asymptotic smoothing
      mesh.position.x = 0.9 * mesh.position.x + 0.1 * x;
      mesh.position.y = 0.9 * mesh.position.y + 0.1 * y;
      mesh.position.z = 0.9 * mesh.position.z + 0.1 * z;
      mesh.localVelocity.x = 0.9 * mesh.localVelocity.x + 0.1 * vx;
      mesh.localVelocity.y = 0.9 * mesh.localVelocity.y + 0.1 * vy;
      mesh.localVelocity.z = 0.9 * mesh.localVelocity.z + 0.1 * vz;

      mesh.lookAt(
        mesh.position.x + mesh.localVelocity.x,
        mesh.position.y + mesh.localVelocity.y,
        mesh.position.z + mesh.localVelocity.z
      );
    });

    /* const obstacles = this.boidsController.getObstacleEntities();
        obstacles.forEach(entity => {
            const x = entity.x;
            const y = entity.y;
            const z = entity.z;
            let mesh = entity.mesh;
            if(!mesh) {
                mesh = new THREE.Mesh(this.obstacleGeometry, this.obstacleMaterial);
                this.scene.add(mesh);
                entity.mesh = mesh;
            }
            
            mesh.position.x = x;
            mesh.position.y = y;
            mesh.position.z = z;
        });

        if(this.lockOn && entities.length > 0) {
            this.updateCamera();
        }

        this.renderer.render(this.scene, this.camera); */
  }
}
