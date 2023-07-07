# isort: skip
from Broken.Base import *
from Broken.Modules import *

# Close Pyinstaller splash screen
try:
    import pyi_splash
    pyi_splash.close()
except:
    pass
