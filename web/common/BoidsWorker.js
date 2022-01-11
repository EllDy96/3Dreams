import BoidsController from './BoidsController.js'

/**
 * @module BoidsWorker 
 * BoidsWorker is the wrapper for BoidsController to make it work inside a WebWorker context
 * The responsibility of this class is to create a new BoidsController instance with 
 * the received data and run the requested iterations in this isolated context.
 */
class BoidsWorker {
  constructor() {
    this.boidsController = undefined;
  }

  /**
   * Initializes the boids controller
   * @param {Object} data 
   */
  initializeBoidsController(data) {
    this.boidsController = BoidsController.deserialize(data);
  }
  
  /**
   * Iterates the BoidsController with the provided parameters
   * @param {Number} start 
   * @param {Number} end 
   * @param {Object} config 
   */
  iterateBoidsController(start, end, config) {
    this.boidsController.aligmentWeight = config.aligmentWeight;
    this.boidsController.cohesionWeight = config.cohesionWeight;
    this.boidsController.separationWeight = config.separationWeight;
    this.boidsController.maxEntitySpeed = config.maxEntitySpeed;
  
    this.boidsController.iterate(start, end);
    const data = this.boidsController.serializeBoidsData(start, end);
    postMessage({action: 'iterateCompleted', data})
  }
  
  /**
   * Updates the internal data of the BoidsController. When other BoidsWorkers have
   * new data, it is send to other workers in order to keep all workers in sync.
   * @param {Object} data 
   */
  updateBoidsData(data) {
    this.boidsController.applyBoidsData(data);
  }

  /**
   * Message handler for the worker
   */
  onMessage(e) {
    if(e.data.action == 'initialData') {
      this.initializeBoidsController(e.data.data)
    } else if(e.data.action == 'iterate') {
      this.iterateBoidsController(e.data.start, e.data.end, e.data.config);
    } else if(e.data.action = 'updateBoidsData') {
      this.updateBoidsData(e.data.data)
    }
  }
}

// create instance
const worker = new BoidsWorker();
onmessage = worker.onMessage.bind(worker);
