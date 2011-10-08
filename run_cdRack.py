#from SELWeb import app
from urllib import urlopen
import os
activate_this = '/Users/shreeshga/Work/Python/env/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

os.environ['CDRACK_CONFIG_PATH']="/Users/shreeshga/Work/NH7/FlaskWorks/CDRack/CDRack.cfg"
#from CDRack import app
#from SELWeb import app
from CDRack import app
#app.run(host='0.0.0.0')
app.run(host='127.0.0.1')

