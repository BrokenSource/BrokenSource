from shaderflow.scene import ShaderScene


class Default(ShaderScene):
    ...

scene = Default(backend="headless")
scene.main(output="/tmp/video.mp4", time=30)
