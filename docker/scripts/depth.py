from depthflow.scene import DepthScene
from depthflow.webui import DepthGradio

if (WEBUI := True):
    DepthGradio().launch()
else:
    scene = DepthScene()
    scene.main(output="/tmp/video.mp4", time=30)
