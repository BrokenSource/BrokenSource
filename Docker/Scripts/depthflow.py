from DepthFlow.Scene import DepthScene
from DepthFlow.Server import DepthServer
from DepthFlow.Webui import DepthGradio

if (WEBUI := True):
    DepthGradio().launch()
elif (SERVER := False):
    DepthServer().launch()
else:
    scene = DepthScene()
    scene.main(output="/tmp/video.mp4", time=30)
