let audioCtx = new AudioContext();

if (audioCtx.state === 'suspended') audioCtx.resume();
audioCtx.resume();
audioCtx.play();
