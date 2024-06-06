from ShaderFlow.Scene import ShaderScene


class Default(ShaderScene):
    ...

scene = Default()
scene.main(output="/tmp/video.mp4")
