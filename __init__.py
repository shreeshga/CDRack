from flask import Flask


SQLALCHEMY_DATABASE_URI = 'mysql://nh7:guadaloupe616@nh7master.cft1jckkg165.ap-southeast-1.rds.amazonaws.com/nml'
SQLALCHEMY_ECHO = False
#UPLOAD_FOLDER = '/home/ubuntu/Python/FlaskWorks/cdRack/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__)
app.config.from_envvar('CDRACK_CONFIG_PATH')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


#import cdRack.models
import CDRack.views
