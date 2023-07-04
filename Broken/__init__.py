from Broken.Base import *
from Broken.Smart import *

# Close Pyinstaller splash screen
try:
    import pyi_splash
    pyi_splash.close()
except:
    pass
