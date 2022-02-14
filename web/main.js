import BoidsController from '../common/BoidsController.js';
import SimpleRenderer from '../common/SimpleRenderer.js';
import ControlHelper from '../common/ControlHelper.js';
import BoidsWorkerPlanner from '../common/BoidsWorkerPlanner.js';
import initSocket from './socket.js';

class Application {
  constructor() {
    this.flockEntityCount = 500;
    this.obstacleEntityCount = 50;
    this.simpleRenderer = undefined;
    this.boidsController = undefined;
    this.controlHelper = undefined;

    this.workerPlanner = undefined;

    this.iterateRequested = false;
  }

  init() {
    // create a boids controller with the given boundary [2000, 600, 2000]
    // subdivide the world in to 10*10*10 cubes by passing subDivisionCount as 10
    // this will reduce the time spent for finding nearby entities
    this.boidsController = new BoidsController(2000, 600, 2000, 10);
    initSocket(this.boidsController);

    // create renderer and pass boidsController to render entities
    this.simpleRenderer = new SimpleRenderer({
      boidsController: this.boidsController,
      flockEntityCount: this.flockEntityCount,
      obstacleEntityCount: this.obstacleEntityCount,
    });
    this.simpleRenderer.init();

    // create worker planner to run the simulation in WebWorker thread.
    // keep the default worker count as 4
    this.workerPlanner = new BoidsWorkerPlanner(
      this.boidsController,
      this.onWorkerUpdate.bind(this)
    );
    this.workerPlanner.init();

    // create control helper for example controls
    this.controlHelper = new ControlHelper(
      this.boidsController,
      this.simpleRenderer,
      this.workerPlanner
    );
    this.controlHelper.init();

    // add initial entities for an interesting view
    this.controlHelper.addBoids(this.flockEntityCount);
    this.controlHelper.addObstacles(this.obstacleEntityCount);

    // request the first animation frame
    /* window.requestAnimationFrame(this.render.bind(this)); */
    setInterval(() => {
      /* console.log('test'); */
      // call statBegin() to measure time that is spend in BoidsController
      this.controlHelper.statBegin();

      // if the iterate is not requested, make a new iteration reques
      if (!this.iterateRequested) {
        this.workerPlanner.requestIterate();
        this.iterateRequested = true;
      }

      // update screen by rendering
      this.simpleRenderer.render();
    });
  }

  /* render() {
    window.requestAnimationFrame(this.render.bind(this));

    // call statBegin() to measure time that is spend in BoidsController
    this.controlHelper.statBegin();

    // if the iterate is not requested, make a new iteration reques
    if (!this.iterateRequested) {
      this.workerPlanner.requestIterate();
      this.iterateRequested = true;
    }

    // update screen by rendering
    this.simpleRenderer.render();
  } */

  onWorkerUpdate() {
    // call statEnd() to finalize measuring time
    this.controlHelper.statEnd();
    this.iterateRequested = false;
  }
}

// create the application when the document is ready
/* document.querySelector('a-scene').addEventListener('loaded', function () {
  document.addEventListener('DOMContentLoaded', new Application().init());
}); */
document.addEventListener('DOMContentLoaded', new Application().init());
