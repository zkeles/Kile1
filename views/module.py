# - *- coding: utf- 8 - *-

# ? Import the modules
import os
import sys
import re
from typing import Dict
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, send_file,  Blueprint
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
#from passlib.hash import sha256_crypt
from functools import wraps
from flask_session import Session
from flask_web_log import Log
from flask_login import LoginManager, login_required, login_user, logout_user, current_user 
#from flask_session import session
import mysql.connector
from mysql.connector import errorcode
import requests
import redis
import json
import argparse
import pandas as pd
from flask_mysqldb import MySQL
#from mailmerge import MailMerge
from flask_mail import Mail, Message
import MySQLdb.cursors 
import re, uuid, hashlib, datetime, os
from passlib.hash import pbkdf2_sha256
import cx_Oracle








module_blueprint = Blueprint('module', __name__)
data = list()
firmadata = list()

cx_Oracle.init_oracle_client(lib_dir="/Users/vipera/Downloads/instantclient_19_8")
dsn_tns = cx_Oracle.makedsn('10.9.141.15', '1521', service_name='MYASOFT') 
oraconn = cx_Oracle.connect(user=r'MYASOFT', password='2019285473637', dsn=dsn_tns)








