AFRAME.registerComponent('box', {
  schema: {
    width: { type: 'number', default: 1 },
    height: { type: 'number', default: 1 },
    depth: { type: 'number', default: 1 },
    color: { type: 'color', default: '#AAA' },
    position: { type: 'vec3', defalut: { x: 0, y: 0, z: 0 } },
  },

  init: function () {
    var data = this.data;
    var el = this.el;
    this.geometry = new THREE.BoxBufferGeometry(
      data.width,
      data.height,
      data.depth
    );
    this.material = new THREE.MeshStandardMaterial({ color: data.color });
    this.mesh = new THREE.Mesh(this.geometry, this.material);
    el.setObject3D('mesh', this.mesh);
  },

  /**
   * Update the mesh in response to property updates.
   */
  update: function (oldData) {
    var data = this.data;
    var el = this.el;

    // If `oldData` is empty, then this means we're in the initialization process.
    // No need to update.
    if (Object.keys(oldData).length === 0) {
      return;
    }
    console.log(data.position);
  },
});
