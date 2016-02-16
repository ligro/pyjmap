import sys
import os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pyjmap
pyjmap.app.run(debug=True)

