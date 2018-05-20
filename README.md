To install, drop the .py files into your Maya startup scripts directory.  

By default, your scripts directory should be:

Mac:
```
/Users/USER_NAME/Library/Preferences/Autodesk/MAYA_VERSION/scripts/
```

Windows:
```
C:\Users\USER_NAME\Documents\maya\MAYA_VERSION\scripts\
```

After restarting Maya, you can use the scripts' functions in your own scripts and shelf buttons.

To load the script automatically, create a new script named userSetup.py in the same location and add the line:
```
from mayatoolbox import *
```

An example userSetup.py script is provided, but it's generally better to edit your existing one than replace it.

