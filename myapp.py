#!/usr/bin/env python3
# ! Import the modules
from views.module import *
from views.mylogin import login_blueprint
from views.module import module_blueprint
from views.mymicro import mymicro_blueprint
from views.myrapor import myrapor_blueprint

application = Flask(__name__)
application.secret_key= "Vipera"
application.static_folder = 'static'
application.register_blueprint(login_blueprint)
application.register_blueprint(module_blueprint)
application.register_blueprint(mymicro_blueprint)
application.register_blueprint(myrapor_blueprint)
application.config['threaded'] = True


# ? Enter your database connection details below
application.config['MYSQL_HOST'] = '10.38.38.58'
application.config['MYSQL_USER'] = 'root'
application.config['MYSQL_PASSWORD'] = 'Nakata!99'
application.config['MYSQL_DB'] = 'MicroGorev'

mysql = MySQL(application)

# ? Enter your Mail send connection details below
application.config['DOMAIN'] = 'http://10.38.38.50:5000'
application.config['MAIL_SERVER']='smtp.office365.com'
application.config['MAIL_PORT'] = 587
application.config['MAIL_USERNAME'] = 'info@secforsys.com'
application.config['MAIL_PASSWORD'] = 'Nakata!99'
application.config['MAIL_USE_TLS'] = True
application.config['MAIL_USE_SSL'] = False
mail = Mail(application)

# ? Enter your Apps connection details below
application.config['RECAPTCHA_USE_SSL']= False
application.config['RECAPTCHA_PUBLIC_KEY']='enter_your_public_key'
application.config['RECAPTCHA_PRIVATE_KEY']='enter_your_private_key'
application.config['RECAPTCHA_OPTIONS']= {'theme':'white'}


