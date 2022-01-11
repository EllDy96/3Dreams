/**
 * @module SimpleRenderer
 * SimpleRenderer helps visualizing the entities in the BoidsController and controls the camera.
 */
export default class SimpleRenderer {
  constructor({ boidsController, scene }) {
    this.boidsController = boidsController;
    this.scene = scene;
    this.isDragging = false;
    this.mouseX = 0;
    this.mouseY = 0;
    this.degX = 45;
    this.degY = 60;
    const b = this.boidsController.getBoundary();
    this.cameraMax = Math.max(b[0], b[1], b[2]);
    this.cameraRadius = (this.cameraMax * 2) / 3;
    this.lockOn = false;
  }

  init() {
    let sceneObj = document.getElementById('scene');

    this.camera = sceneObj.camera;
    /* this.camera = new THREE.PerspectiveCamera(
      70,
      window.innerWidth / window.innerHeight,
      0.01,
      100000
    );
    this.camera.position.z = 0; */

    this.scene = sceneObj.object3D;

    this.entityGeometry = new THREE.BoxGeometry(5, 5, 15);
    this.obstacleGeometry = new THREE.SphereGeometry(50, 15, 15);
    this.entityMaterial = new THREE.MeshNormalMaterial();
    this.obstacleMaterial = new THREE.MeshNormalMaterial();

    this.createGridVisual(this.boidsController.subDivisionCount);

    // create boundary
    const b = this.boidsController.getBoundary();
    const geometry = new THREE.BoxGeometry(b[0], b[1], b[2]);
    const wireframe = new THREE.EdgesGeometry(geometry);
    const line = new THREE.LineSegments(wireframe);
    line.material.color = new THREE.Color(0x000000);
    line.material.transparent = false;
    line.position.x = b[0] / 2;
    line.position.y = b[1] / 2;
    line.position.z = b[2] / 2;
    this.scene.add(line);

    this.renderer = sceneObj.renderer;
    /* this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(this.renderer.domElement); */

    this.render();
  }

  createGridVisual(subdivisionCount) {
    this.gridVisual = new THREE.Group();
    const b = this.boidsController.getBoundary();
    const maxLen = Math.max(b[0], b[1], b[2]);
    const len = maxLen / subdivisionCount;
    for (let x = 0; x < subdivisionCount; x++) {
      for (let y = 0; y < subdivisionCount; y++) {
        for (let z = 0; z < subdivisionCount; z++) {
          if (
            (x + 0.5) * len > b[0] ||
            (y + 0.5) * len > b[1] ||
            (z + 0.5) * len > b[2]
          ) {
            continue;
          }

          // create boundary wireframe
          const geometry = new THREE.BoxGeometry(len, len, len);
          const wireframe = new THREE.EdgesGeometry(geometry);
          const line = new THREE.LineSegments(wireframe);
          //line.material.depthTest = false;
          line.material.color = new THREE.Color(0x999999);
          line.material.transparent = false;
          line.position.x = len / 2 + x * len;
          line.position.y = len / 2 + y * len;
          line.position.z = len / 2 + z * len;
          //this.scene.add(line);
          this.gridVisual.add(line);
        }
      }
    }

    this.scene.add(this.gridVisual);
    this.gridVisual.visible = false;
  }

  touchStart(e) {
    const t = e.changedTouches[0];
    this.mouseX = t.pageX;
    this.mouseY = t.pageY;
    this.isDragging = true;
  }

  touchEnd(e) {
    this.isDragging = false;
  }

  onMouseDown(e) {
    this.isDragging = true;
    this.mouseX = e.offsetX;
    this.mouseY = e.offsetY;
  }

  onMouseUp(e) {
    this.isDragging = false;
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

    const obstacles = this.boidsController.getObstacleEntities();
    obstacles.forEach((entity) => {
      const x = entity.x;
      const y = entity.y;
      const z = entity.z;
      let mesh = entity.mesh;
      if (!mesh) {
        mesh = new THREE.Mesh(this.obstacleGeometry, this.obstacleMaterial);
        this.scene.add(mesh);
        entity.mesh = mesh;
      }

      mesh.position.x = x;
      mesh.position.y = y;
      mesh.position.z = z;
    });

    this.renderer.render(this.scene, this.camera);
  }
}
