from shaderflow.scene import ShaderScene

scene = ShaderScene(backend="headless")
scene.main(output="/tmp/video.mp4", time=30)
