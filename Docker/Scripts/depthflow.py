from DepthFlow import DepthScene
from DepthFlow.Webui import DepthGradio

if (WEBUI := True):
    DepthGradio().launch()
else:
    scene = DepthScene()
    scene.main(output="/tmp/video.mp4", time=30)
