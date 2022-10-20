#!/usr/bin/env python3

import email
import imp
from views.module import *
from myapp import *

from passlib.hash import sha256_crypt
from logging.config import dictConfig
from requests import get

application = Flask(__name__)
application.config['MAIL_SERVER'] = 'smtp.office365.com'
application.config['MAIL_PORT'] = 587
application.config['MAIL_USERNAME'] = 'info@secforsys.com'
application.config['MAIL_PASSWORD'] = 'Nakata!99'
application.config['MAIL_USE_TLS'] = True
application.config['MAIL_USE_SSL'] = False
application.config['DOMAIN'] = 'http://10.38.38.57:5000'
mail = Mail(application)
application.config["SESSION_TYPE"] = "filesystem"
application.config["SESSION_PERMANENT"] = False
#TODO : deneme



# ? logging 
"""LOGGING_CONFIG = {
    'version': 1,
    'loggers': {
        '': {  # root logger
            'level': 'NOTSET',
            'handlers': ['debug_console_handler', 'info_rotating_file_handler', 'error_file_handler', 'critical_mail_handler'],
        },
        'my.package': { 
            'level': 'WARNING',
            'propagate': False,
            'handlers': ['info_rotating_file_handler', 'error_file_handler' ],
        },
    },
    'handlers': {
        'debug_console_handler': {
            'level': 'DEBUG',
            'formatter': 'info',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'info_rotating_file_handler': {
            'level': 'INFO',
            'formatter': 'info',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': './Log/info.log',
            'mode': 'a',
            'maxBytes': 1048576,
            'backupCount': 10
        },
        'error_file_handler': {
            'level': 'WARNING',
            'formatter': 'error',
            'class': 'logging.FileHandler',
            'filename': './Log/error.log',
            'mode': 'a',
        },
        'critical_mail_handler': {
            'level': 'CRITICAL',
            'formatter': 'error',
            'class': 'logging.handlers.SMTPHandler',
            'mailhost' : 'localhost',
            'fromaddr': 'monitoring@domain.com',
            'toaddrs': ['dev@domain.com', 'qa@domain.com'],
            'subject': 'Critical error with application name'
        }
    },
    'formatters': {
        'info': {
            'format': '%(asctime)s-%(levelname)s-%(name)s::%(module)s|%(lineno)s:: %(message)s'
        },
        'error': {
            'format': '%(asctime)s-%(levelname)s-%(name)s-%(process)d::%(module)s|%(lineno)s:: %(message)s'
        },
    },

}

dictConfig(LOGGING_CONFIG)"""

"""dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '%(asctime)s [%(levelname)s] [%(funcName)s():%(lineno)s] [PID:%(process)d TID:%(thread)d] %(name)s: %(message)s'
            }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})"""


login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'login'

#Session(application)

today = datetime.date.today()

login_blueprint = Blueprint('login', __name__)


db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101", database="MicroGorev", auth_plugin='mysql_native_password')
cursor = db.cursor()
token = ""



# ? ###########################################################
# ? Login
# ? Kullanıcı Giriş Decorator'ı


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için lütfen giriş yapın.", "danger")
            return redirect('/login')
    return decorated_function


@login_blueprint.route('/index', methods=["GET", "POST"])
@login_required
def index():
    role = session.get('role')
    #message = "Sisteme Hoş geldiniz"
    #flash(message)
    firinadi = session.get('firin_adi')
    return render_template("index.html", role=role, firinadi=firinadi)


@login_blueprint.route('/', methods=["GET", "POST"])
@login_blueprint.route('/login', methods=["GET", "POST"])
def login():
    return render_template("login.html", user=current_user)


@login_blueprint.route('/submit', methods=['POST'])
def login_submit():
    #logging.basicConfig(filename='api.log',level=logging.DEBUG)
    db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101",
                                 database="MicroGorev", auth_plugin='mysql_native_password')
    cursor = db.cursor()
    _email = request.form['email']
    _password = request.form['password']
    if _email and _password and request.method == 'POST':
        sorgu = "SELECT * FROM MicroGorev.user WHERE e_mail = %s"
        val = (_email,)
        cursor.execute(sorgu, val)
        row = cursor.fetchall()
        if row:
            if pbkdf2_sha256.verify(_password, row[0][5]):
                session['company_id'] = row[0][1]
                session['e_mail'] = row[0][4]
                session["logged_in"] = True
                session['firin_id'] = row[0][8]
                session['firin_adi'] = row[0][9]
                session['role'] = row[0][10]

                clientip = get('https://api.ipify.org').text
                application.logger.info('%s  logged in successfully', clientip +" "+ _email)
                return redirect('/index')
            else:
                flash('Invalid password!')
                clientip = get('https://api.ipify.org').text
                application.logger.info('failed to log in', clientip +" "+ _email)
                #abort(401)
                return render_template("login.html")
        else:
            message = 'Invalid email/password!'
            flash(message)
            clientip = get('https://api.ipify.org').text
            application.logger.info('%s failed to log in', clientip +" "+ _email)
            return redirect('/login')
    cursor.close()
    db.close()




@login_blueprint.route("/logout")
@login_required
def logout():
    # logout_user()
    _email = session['e_mail']
    clientip = get('https://api.ipify.org').text
    application.logger.info('%s Logout', clientip +" "+ _email)
    session.clear()
    return redirect('/login')

###########################################################
# ? Register 1 new kayıt


@login_blueprint.route('/reg', methods=["GET", "POST"])
def newaccount():
    msg = ''
    if request.method == 'POST' and 'email' in request.form:
        email = request.form['email']
        cursor = db.cursor()
        cursor.execute(
            'SELECT * FROM MicroGorev.register WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            msg = 'An account with this email exists!'
            cursor.close()
            db.close()
        else:
            token = str(uuid.uuid4())
            sql = """INSERT INTO MicroGorev.register (id, email, token) VALUES (%s, %s, %s);"""
            val = (None, email, token)
            cursor.execute(sql, val)
            # cursor.commit()
            # Change your_email@gmail.com
            email_info = Message(
                'Sisteme kayıt', sender=application.config['MAIL_USERNAME'], recipients=[email])
            # Generate reset password link
            reset_link = application.config['DOMAIN'] + \
                url_for('login.register', email=email, code=str(token))
            # change the email body below
            email_info.body = 'Lufen sisteme kayıt için linke tıklayın ' + \
                str(reset_link)
            email_info.html = '<p>Lütfen uygulamaya kayıt için lütfen aşağıdaki bağlantıya tıklayın: <a href="' + \
                str(reset_link) + '">' + str(reset_link) + '</a></p>'
            mail.send(email_info)
            msg = 'Sisteme kayıt için mil gönderilmistir!'
    return redirect("/login")

# ? Register 2 kontrol


@login_blueprint.route('/<string:email>/<string:code>', methods=['GET', 'POST'])
def register(email, code):
    token = code
    db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101",
                                 database="MicroGorev", auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute(
        'SELECT * FROM  MicroGorev.register WHERE email = %s AND token = %s', (email, token,))
    account = cursor.fetchone()
    # If account exists
    if account:
        cursor.close()
        db.close()
        return render_template('firma.html')
    else:
        return render_template('login.html')

# ? Register 3 Kayıt


@login_blueprint.route('/register', methods=['GET', 'POST'])
def kayit():
    if request.method == 'POST':
        db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101",
                                     database="MicroGorev", auth_plugin='mysql_native_password')
        cursor = db.cursor()
        form = request.form
        company_name = form['firmaadi']
        company_short_name = form['fadi']
        country = form['country']
        city = form['city']
        is_active = 1
        date_license = today + datetime.timedelta(days=15)
        is_recurring = 15
        cursor = db.cursor()
        sql = "Insert into MicroGorev.company (company_id, company_name, company_short_name, country, city, is_active, date_license,  is_recurring, date_added) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (None, company_name, company_short_name,
                             country, city, is_active, date_license, is_recurring, today))
        db.commit()
        # print(cursor.lastrowid)
        company_id = cursor.lastrowid
        firstname = form['adi']
        lastname = form['soyadi']
        e_mail = form['email']
        password = pbkdf2_sha256.hash(form.get('password'))
        phone = form['phone']
        token = ""
        member = "member"
        is_active = 1
        sql = "Insert into MicroGorev.user (user_id, company_id, firstname, lastname, e_mail, password, phone, token,  member) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (None, company_id, firstname, lastname,
                       e_mail, password, phone, token,  member))
        db.commit()
        email = [e_mail]
        cursor.execute(
            "update MicroGorev.register set token = null where email = %s", (email))
        db.commit()

        # print(cursor.lastrowid)
        # cursor.close()
        db.close()
        #flash("Başarıyla Kayıt Oldunuz...", "success")
        cursor.close()
        db.close()
        return redirect("/login")
    else:
        return redirect("/reg")


# ? Password resetleme forgotpassword

@login_blueprint.route('/forgot', methods=['GET', 'POST'])
def forgot():
    return render_template('forgotpassword.html')


@login_blueprint.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():
    db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101", database="MicroGorev", auth_plugin='mysql_native_password')
    cursor = db.cursor()
    msg = ''
    if request.method == 'POST' and 'email' in request.form:
        email = request.form['email']
        db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101", database="MicroGorev", auth_plugin='mysql_native_password')
        cursor = db.cursor()
        cursor.execute('SELECT * FROM MicroGorev.user WHERE e_mail = %s', (email,))
        account = cursor.fetchone()
        if account:
            # Generate unique ID
            token = str(uuid.uuid4())
            # Update the reset column in the accounts table to reflect the generated ID
            cursor.execute(
                'UPDATE MicroGorev.register SET token = %s WHERE email = %s', (token, email))
            # mysql.connection.commit()
            # Change your_email@gmail.com
            email_info = Message(
                'Password Reset', sender=application.config['MAIL_USERNAME'], recipients=[email])
            # Generate reset password link
            reset_link = application.config['DOMAIN'] + \
                url_for('login.resetpassword', email=email, token=token)
            # change the email body below
            email_info.body = 'Please click the following link to reset your password: ' + \
                str(reset_link)
            email_info.html = '<p>Please click the following link to reset your password: <a href="' + \
                str(reset_link) + '">' + str(reset_link) + '</a></p>'
            mail.send(email_info)
            msg = 'Reset password link has been sent to your email!'
        else:
            msg = 'An account with that email does not exist!'
    cursor.close()
    return render_template('login.html', msg=msg)


@login_blueprint.route('/reset/<string:email>/<string:token>', methods=['GET', 'POST'])
def resetpassword(email, token):
    db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101",
                                 database="MicroGorev", auth_plugin='mysql_native_password')
    cursor = db.cursor()                        
    cursor.execute(
        'SELECT * FROM  MicroGorev.register WHERE email = %s AND token = %s', (email, token,))
    account = cursor.fetchone()
    if account:
        # Check if the new password fields were submitted
        msg = 'Yeni Parolanızı belirledikden sonra Giriş Yapabilirsiniz'
        if request.method == 'POST' and 'npassword' in request.form:
            cpassword = request.form['npassword']
            # Password fields must match
            password = pbkdf2_sha256.hash(cpassword)
            # Update the user's password
            cursor.execute(
                        'UPDATE Login.user SET password = %s WHERE e_mail = %s', (password, email,))
            msg = 'Başarıyla Parolanız Yenilendi... Tekrar Giriş Yapabilirsiniz'
            return redirect('/login')
        else:
            msg = 'Yeni Parolanızı Oluşturabilirsiniz'
        return render_template('resetpassword.html', msg=msg, email=email, code=token)
cursor.close()

