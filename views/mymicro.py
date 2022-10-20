from ast import Param
from email import message
from queue import Empty
from re import T
from views.module import module_blueprint
from views.mylogin import login_blueprint
from myapp import *
from datetime import datetime, date, timedelta

import openpyxl
import json
import pandas as pd
import numpy as np
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, send_file,  Blueprint, abort


mymicro_blueprint = Blueprint('mymicro', __name__)
application = Flask(__name__)
application.config['MAIL_SERVER'] = 'smtp.office365.com'
application.config['MAIL_PORT'] = 587
application.config['MAIL_USERNAME'] = 'info@secforsys.com'
application.config['MAIL_PASSWORD'] = 'Nakata!99'
application.config['MAIL_USE_TLS'] = True
application.config['MAIL_USE_SSL'] = False
application.config['DOMAIN'] = 'http://10.38.38.5:5000'
mail = Mail(application)
application.config["SESSION_TYPE"] = "filesystem"
application.config["SESSION_PERMANENT"] = False

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = 'login'



"""
    micro gorev yazılımı yapılacaklar
    TODO: güvenlik konuları ekle
        ! login gerekli 
        ! role kontrol 
        ! kod üzerinde temizleme yap
        ! log json redis e yaz 
"""
# TODO: login zorunlu ekle


# ?# Kulanıcı listeleme
@mymicro_blueprint.route('/kullanici', methods=["GET", "POST"])
def kullanici():
    role = session.get('role')
    company_id = session.get('company_id')
    db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101",
                                 database="MicroGorev", auth_plugin='mysql_native_password')
    mycursor = db.cursor()
    mycursor.callproc("kullanici_get", [company_id])
    for result in mycursor.stored_results():
                result = (result.fetchall())
    mycursor.close()
    return render_template("kullanici.html", data=result, kekle='kekle', user=current_user, role=role)

# TODO: login zorunlu ekle
# ?# Kulanıcı Ekleme 1
@mymicro_blueprint.route('/kekle', methods=["GET", "POST"])
def kekle():
    role = session.get('role')
    company_id = session.get('company_id')
    db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101",
                                 database="MicroGorev", auth_plugin='mysql_native_password')
    mycursor = db.cursor()
    mycursor.callproc("kullanici_get", [company_id])
    for result in mycursor.stored_results():
                result = (result.fetchall())
    mycursor.close()
    dsn_tns = cx_Oracle.makedsn('10.9.141.15', '1521', service_name='MYASOFT') 
    oraconn = cx_Oracle.connect(user=r'MYASOFT', password='2019285473637', dsn=dsn_tns)
    data1 = []
    oracursor = oraconn.cursor()
    oracursor.execute("select LOKASYONNO, ACIKLAMA from MYASOFT_006.TBL_LOKASYONLAR")
    for row in oracursor.fetchall():
        data1.append(row)
    oracursor.close()
    oraconn.close()
    return render_template("kullanici.html", data=result, lokasyon= data1, kekle='kekle', user=current_user, role=role)

@mymicro_blueprint.route('/k1ekle', methods=["POST", "GET"])
#@login_required
def k1ekle():
    role = session.get('role')
    company_id = session.get('company_id')

    if request.method == 'POST':
        form = request.form
        firstname = form.get('firstname')
        lastname = form.get('lastname')
        e_mail = form.get('email')
        password = pbkdf2_sha256.hash(form.get('password'))
        phone = form.get('phone')
        firin_id = form.get('firin_id')
        dsn_tns = cx_Oracle.makedsn('10.9.141.15', '1521', service_name='MYASOFT') 
        oraconn = cx_Oracle.connect(user=r'MYASOFT', password='2019285473637', dsn=dsn_tns)
        oracursor = oraconn.cursor()
        sorgu1 = ("select  LOK.ACIKLAMA from MYASOFT_006.TBL_LOKASYONLAR LOK where LOK.LOKASYONNO = :firin_id")
        oracursor.execute(sorgu1, [firin_id])
        mem1 = oracursor.fetchone()
        member = mem1[0]    
        db = mysql.connector.connect(user="vipera", password="Nakata!99", host="10.9.141.101", database="MicroGorev", auth_plugin='mysql_native_password')
        mycursor = db.cursor()
        role1 = ".usrNormal"
        sql = """INSERT INTO user (user_id, company_id, firstname, lastname, e_mail, password, phone, firin_id, member, role) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""" 
        val =  (None, company_id, firstname, lastname, e_mail, password, phone, firin_id, member, role1)
        try:    
            mycursor.execute(sql, val)
            db.commit()
        except mysql.connector.Error as error :
                db.rollback() #rollback if any exception occured
                print("Kayıt Başarısız into Overview table {}".format(error))
                print ("Error code:", error.errno)        # error number
                print ("Error code:", error.args)       # error number
                print ("SQLSTATE value:", error.sqlstate) # SQLSTATE value
                print ("Error message:", error.msg)       # error message
                print ("Error:", error)              # errno, sqlstate, msg values
                s = str(error)
                print ("Error:", s)               # errno, sqlstate, msg values
        mycursor.close()
        db.close()   
    return redirect('/kekle')
# ?# Kulanıcı Ekleme bitti 

# TODO: login zorunlu ekle
# ?# Kulanıcı Düzeltme baslangıc
@mymicro_blueprint.route('/kduz/<int:id>', methods=["GET", "POST"])
def kduz(id):
    role = session.get('role')
    company_id = session.get('company_id')
    db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101",
                                 database="MicroGorev", auth_plugin='mysql_native_password')
    mycursor = db.cursor()
    mycursor.callproc("kullanici_get", [company_id])
    for result in mycursor.stored_results():
                result = (result.fetchall())
    mycursor.close()
    db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101",
                                 database="MicroGorev", auth_plugin='mysql_native_password')
    mycursor = db.cursor()
    mycursor.callproc("tek_kullanici_getir", [id])
    for result1 in mycursor.stored_results():
                result1 = (result1.fetchall())
    mycursor.close()
    dsn_tns = cx_Oracle.makedsn('10.9.141.15', '1521', service_name='MYASOFT') 
    oraconn = cx_Oracle.connect(user=r'MYASOFT', password='2019285473637', dsn=dsn_tns)
    data2 = []
    oracursor = oraconn.cursor()
    oracursor.execute("select LOKASYONNO, ACIKLAMA from MYASOFT_006.TBL_LOKASYONLAR")
    for row in oracursor.fetchall():
        data2.append(row)
    oracursor.close()
    oraconn.close()
    return render_template("kullanici_duzelt.html", data=result, data1=result1, lokasyon=data2, user=current_user, role=role)

@mymicro_blueprint.route('/kdekle/<int:id>', methods=["POST", "GET"])
#@login_required
def kdekle(id):
    #company_id = session.get('company_id')
    role = session.get('role')
    if request.method == 'POST':
        form = request.form
        user_id = id
        firstname = form.get('firstname')
        lastname = form.get('lastname')
        e_mail = form.get('email')
        phone = form.get('phone')
        #member = form.get('member')
        firin_id = form.get('firin_id')
        dsn_tns = cx_Oracle.makedsn('10.9.141.15', '1521', service_name='MYASOFT') 
        oraconn = cx_Oracle.connect(user=r'MYASOFT', password='2019285473637', dsn=dsn_tns)
        oracursor = oraconn.cursor()
        sorgu1 = ("select  LOK.ACIKLAMA from MYASOFT_006.TBL_LOKASYONLAR LOK where LOK.LOKASYONNO = :firin_id")
        oracursor.execute(sorgu1, [firin_id])
        mem1 = oracursor.fetchone()
        oracursor.close()
        oraconn.close()
        member = mem1[0]    
        db = mysql.connector.connect(user="vipera", password="Nakata!99", host="10.9.141.101", database="MicroGorev", auth_plugin='mysql_native_password')
        mycursor = db.cursor()
        sql = """UPDATE user SET firstname = %s, lastname = %s, e_mail = %s, phone = %s, firin_id = %s, member = %s WHERE user_id = %s;"""
        val =  (firstname, lastname, e_mail,  phone, firin_id, member, user_id)
        try:    
            mycursor.execute(sql, val)
            db.commit()
        except mysql.connector.Error as error :
                db.rollback() #rollback if any exception occured
                print("Kayıt Başarısız into Overview table {}".format(error))
                print ("Error code:", error.errno)        # error number
                print ("Error code:", error.args)       # error number
                print ("SQLSTATE value:", error.sqlstate) # SQLSTATE value
                print ("Error message:", error.msg)       # error message
                print ("Error:", error)              # errno, sqlstate, msg values
                s = str(error)
                print ("Error:", s)               # errno, sqlstate, msg values
        mycursor.close()
        db.close()   
    return redirect('/kekle')
# ?# Kulanıcı Düzeltme bitti
   
# TODO: login zorunlu ekle
# ?# Kulanıcı Silme
@mymicro_blueprint.route('/ksil/<int:id>', methods =["GET", "POST"])
#@login_required
def ksil(id):
    if not id or id != 0:
        entry = (id)
        print(entry)
        db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101",
                                 database="MicroGorev", auth_plugin='mysql_native_password')
        mycursor = db.cursor()
        sql = "DELETE FROM user WHERE user_id = '%s' " % (entry)
        try:
            #print (sql)    
            mycursor.execute(sql)
            db.commit()
        except mysql.connector.Error as error :
                db.rollback() #rollback if any exception occured
                print("Kayıt Başarısız into Overview table {}".format(error))
                print ("Error code:", error.errno)        # error number
                print ("Error code:", error.args)       # error number
                print ("SQLSTATE value:", error.sqlstate) # SQLSTATE value
                print ("Error message:", error.msg)       # error message
                print ("Error:", error)              # errno, sqlstate, msg values
                s = str(error)
                print ("Error:", s)               # errno, sqlstate, msg values
    mycursor.close()
    db.close() 
    return redirect('/kullanici')

# ?# KulIskarta giris basladı 
@mymicro_blueprint.route('/iskarta', methods=["GET", "POST"])
def iskarta():
    role = session.get('role')
    firinadi = session.get('firin_adi')
    firin_id = session.get('firin_id')
    dsn_tns = cx_Oracle.makedsn('10.9.141.15', '1521', service_name='MYASOFT') 
    conn = cx_Oracle.connect(user=r'MYASOFT', password='2019285473637', dsn=dsn_tns)
    urun = []
    tdate = str(date.today())
    cursor = conn.cursor()
    cursor.execute(""" select KOD, ACIKLAMA from MYASOFT_006.TBL_URUNLER where STATU = 1 and USTURUNKTRL <> 3 """)
    for row in cursor.fetchall():
        urun.append(row)
    conn.close()
    db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101",
                                 database="MicroGorev", auth_plugin='mysql_native_password')
    mycursor = db.cursor()
    mycursor.callproc("iskartagetir", [firin_id, tdate]);
    for result in mycursor.stored_results():
                list = (result.fetchall())
    mycursor.close()

    return render_template("iskarta.html", role=role, urun=urun, list=list, firinadi=firinadi, date=tdate)   

@mymicro_blueprint.route('/iskartagetir', methods=["GET", "POST"])
def iskartagetir():
    role = session.get('role')
    #! incele bos olunca icin kontrol koy
    if request.method == 'POST' and "tdate" in request.form:
        form = request.form
        date = form.get('tdate')
        firinadi = session.get('firin_adi')
        firin_id = session.get('firin_id')
        dsn_tns = cx_Oracle.makedsn('10.9.141.15', '1521', service_name='MYASOFT') 
        conn = cx_Oracle.connect(user=r'MYASOFT', password='2019285473637', dsn=dsn_tns)
        urun = []
        #date = datetime.datetime.now()
        cursor = conn.cursor()
        cursor.execute("select ACIKLAMA from MYASOFT_006.TBL_URUNLER")
        for row in cursor.fetchall():
            urun.append(row[0])
        conn.close()
        db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101",
                                    database="MicroGorev", auth_plugin='mysql_native_password')
        mycursor = db.cursor()
        mycursor.callproc("iskartagetir", [firin_id, date]);
        for result in mycursor.stored_results():
                    list = (result.fetchall())
        mycursor.close()
        return render_template("iskarta.html", role=role, urun=urun, list=list, firinadi=firinadi, date=date)   
    return redirect("/iskarta") 

@mymicro_blueprint.route('/iskartaekle', methods=["GET", "POST"])     
def iskartaekle(): 
    role = session.get('role')   
    company_id = session.get('company_id')
    if request.method == 'POST':
        firin_id = session.get('firin_id')
        firin_adi = session.get('firin_adi')
        form = request.form
        date = form.get('date')
        adet = form.get('adet')
        urun = form.get('urun')
        db = mysql.connector.connect(user="vipera", password="Nakata!99", host="10.9.141.101", database="MicroGorev", auth_plugin='mysql_native_password')
        mycursor = db.cursor()
        sql = """INSERT INTO iskarta (id, company_id, firin_id, date, adet, urun) VALUES (%s, %s, %s, %s, %s, %s);""" 
        val =  (None, company_id, firin_id, date, adet, urun)
        try:    
            mycursor.execute(sql, val)
            db.commit()
        except mysql.connector.Error as error :
                db.rollback() #rollback if any exception occured
                print("Kayıt Başarısız into Overview table {}".format(error))
                print ("Error code:", error.errno)        # error number
                print ("Error code:", error.args)       # error number
                print ("SQLSTATE value:", error.sqlstate) # SQLSTATE value
                print ("Error message:", error.msg)       # error message
                print ("Error:", error)              # errno, sqlstate, msg values
                s = str(error)
                print ("Error:", s)               # errno, sqlstate, msg values
        mycursor.close()
        db.close()
        db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101",
                                    database="MicroGorev", auth_plugin='mysql_native_password')
        mycursor = db.cursor()
        mycursor.callproc("iskartagetir", [firin_id, date]);
        for result in mycursor.stored_results():
                    list = (result.fetchall())
        mycursor.close() 
    return redirect('/iskarta')
    #return render_template("iskarta.html", urun=data, role=role, list=list, firinadi=firin_adi, date=date) 
# ?# KulIskarta giris bitti

# TODO: login zorunlu ekle
# ?# Kulanıcı Password Resetleme yeni ekran ve dizayn yap
@mymicro_blueprint.route('/passreset/<int:id>', methods=['GET', 'POST'])

@mymicro_blueprint.route('/firinrapor', methods=['GET', 'POST'])
def firinrapor():
    role = session.get('role')
    dsn_tns = cx_Oracle.makedsn('10.9.141.15', '1521', service_name='MYASOFT') 
    oraconn = cx_Oracle.connect(user=r'MYASOFT', password='2019285473637', dsn=dsn_tns)
    oracursor = oraconn.cursor()    
    member = []
    sorgu1 = ("select  LOK.LOKASYONNO, LOK.ACIKLAMA from MYASOFT_006.TBL_LOKASYONLAR LOK WHERE DURUM = 1  ORDER BY LOK.ACIKLAMA")
    oracursor.execute(sorgu1)
    for row in oracursor.fetchall():
        member.append(row)
    return render_template("firinrapor.html", role=role, firin = member)

@mymicro_blueprint.route('/firinrapor1', methods=['GET', 'POST'])
def firinrapor1():
    role = session.get('role')
    df = pd.DataFrame()
    dsn_tns = cx_Oracle.makedsn('10.9.141.15', '1521', service_name='MYASOFT') 
    oraconn = cx_Oracle.connect(user=r'MYASOFT', password='2019285473637', dsn=dsn_tns)
    oracursor = oraconn.cursor()    
    member = []
    sorgu1 = ("select  LOK.LOKASYONNO, LOK.ACIKLAMA from MYASOFT_006.TBL_LOKASYONLAR LOK WHERE DURUM = 1  ORDER BY LOK.ACIKLAMA")
    oracursor.execute(sorgu1)
    for row in oracursor.fetchall():
        member.append(row)
    satis = []
    sparm = {}
    if  request.method == 'POST':
        if 'web' in request.form:
            print('oldu')
            form = request.form
            basdate = form.get('basdate')
            basdate = datetime.strptime(basdate, '%Y-%m-%d').strftime('%m-%d-%Y')
            bitdate = form.get('bitdate')
            bitdate = datetime.strptime(bitdate, '%Y-%m-%d').strftime('%m-%d-%Y')
            data = request.form.getlist('selectedfirin')
            for row in data:
                Firinid = row
                sparm['Firinid'] = Firinid 
                sorgu = """
                SELECT         
                TP.STORE_NO, 
                TP.TRANSACTION_DATE,
                TP.POS_NO,
                MYASOFT_006.TBL_ODEMETIP.ACIKLAMA,
                sum(TP.PAYMENT_TOTAL)  as Satis
                FROM MYASOFT_006.TBL_TRANSACTION_PAYMENTS TP inner join MYASOFT_006.TBL_ODEMETIP on TP.PAYMENT_REF = MYASOFT_006.TBL_ODEMETIP.KOD
                WHERE 
                TP.STORE_NO =:Firinid
                and TP.TRANSACTION_DATE >= TO_DATE(:basdate, 'MM/DD/YYYY')
                
                and TP.TRANSACTION_DATE <= TO_DATE(:bitdate, 'MM/DD/YYYY')
                group by STORE_NO, TP.TRANSACTION_DATE, TP.POS_NO, PAYMENT_REF, MYASOFT_006.TBL_ODEMETIP.ACIKLAMA
                order by TP.TRANSACTION_DATE """
                oracursor.execute(sorgu, (Firinid, basdate, bitdate))
                for row1 in oracursor.fetchall():
                    satis.append(row1)
                    #print(satis)
        else:
            print('excel')
            df = pd.DataFrame()
            dsn_tns = cx_Oracle.makedsn('10.9.141.15', '1521', service_name='MYASOFT') 
            oraconn = cx_Oracle.connect(user=r'MYASOFT', password='2019285473637', dsn=dsn_tns)
            oracursor = oraconn.cursor()    
            role = session.get('role')
            sparm = {}
            if request.method == 'POST':
                form = request.form
                basdate = form.get('basdate')
                basdate = datetime.strptime(basdate, '%Y-%m-%d').strftime('%m-%d-%Y')
                bitdate = form.get('bitdate')
                bitdate = datetime.strptime(bitdate, '%Y-%m-%d').strftime('%m-%d-%Y')
                sparm['basdate'] = basdate
                sparm['bitdate'] = bitdate
                data = request.form.getlist('selectedfirin')
                for row in data:
                    Firinid = row
                    sparm['Firinid'] = Firinid 
                    sorgu = """
                    SELECT         
                    TP.STORE_NO, 
                    TP.TRANSACTION_DATE,
                    TP.POS_NO,
                    MYASOFT_006.TBL_ODEMETIP.ACIKLAMA,
                    sum(TP.PAYMENT_TOTAL)  as Satis
                    FROM MYASOFT_006.TBL_TRANSACTION_PAYMENTS TP inner join MYASOFT_006.TBL_ODEMETIP on TP.PAYMENT_REF = MYASOFT_006.TBL_ODEMETIP.KOD
                    WHERE 
                    TP.STORE_NO =:Firinid
                    and TP.TRANSACTION_DATE > TO_DATE(:basdate, 'MM/DD/YYYY')
                    and TP.TRANSACTION_DATE < TO_DATE(:bitdate, 'MM/DD/YYYY')
                    group by STORE_NO, TP.TRANSACTION_DATE, TP.POS_NO, PAYMENT_REF, MYASOFT_006.TBL_ODEMETIP.ACIKLAMA
                    order by TP.TRANSACTION_DATE """
                    df = df.append(pd.read_sql(sorgu, con=oraconn, params=sparm))
                    
                    print(df)
            df.to_excel('FirinSatis.xlsx', sheet_name='new_sheet_name')
            print ('Rapor Bitti')

            email = session.get('e_mail')
            email_info = Message('Satıs Raporu', sender=application.config['MAIL_USERNAME'], recipients=[email])
            email_info.body = 'Raporunuz ektedir: ' 
            email_info.html = '<p>Raporunuz ektedir </p>'
            with application.open_resource("../FirinSatis.xlsx") as fp:
                email_info.attach("/FirinSatis.xlsx", "text/csv", fp.read())
            mail.send(email_info)
            message = (email) + " " + "e-mail adresine Satıs Raporu için mail gönderilmiştir."
            flash(message)
    oracursor.close()
    oraconn.close()
    return render_template("firinrapor.html", role=role, firin = member, data = satis)

@mymicro_blueprint.route('/kontrolpaneli', methods=['GET', 'POST'])
def kontrolpaneli():
    Firin_id = session.get('firin_id')
    message = session.get('firin_adi')
    #flash(message)
    if Firin_id == 1:
        role = session.get('role')
        N_DAYS_AGO = 6
        today = datetime.now()    
        n_days_ago = today - timedelta(days=N_DAYS_AGO)
        today = str(date.today())
        tdate = datetime.strptime(today, '%Y-%m-%d').strftime('%m-%d-%Y')
        basdate = str(n_days_ago)
        basdate = datetime.strptime(basdate, '%Y-%m-%d %H:%M:%S.%f').strftime('%m-%d-%Y')
        satis = []
        gsatis = []
        dsatis = []
        dsn_tns = cx_Oracle.makedsn('10.9.141.15', '1521', service_name='MYASOFT') 
        oraconn = cx_Oracle.connect(user=r'MYASOFT', password='2019285473637', dsn=dsn_tns)
        oracursor = oraconn.cursor()  
        sorgu2 = """SELECT TP.TRANSACTION_DATE,
                sum(TP.PAYMENT_TOTAL)  as Satis
                FROM MYASOFT_006.TBL_TRANSACTION_PAYMENTS TP 
                WHERE 

                TP.TRANSACTION_DATE >= TO_DATE(:basdate, 'MM/DD/YYYY')
                and TP.TRANSACTION_DATE <= TO_DATE(:tdate, 'MM/DD/YYYY')
                group by TP.TRANSACTION_DATE
                order by TP.TRANSACTION_DATE"""
        oracursor.execute(sorgu2, [basdate, tdate])
        for row in oracursor.fetchall():
            dt = row[0].strftime("%d/%m/%Y")
            dsatis.append(dt)
            gsatis.append(row[1])
        sorgu="""SELECT 
                sum(TP.PAYMENT_TOTAL)  as Satis
                FROM MYASOFT_006.TBL_TRANSACTION_PAYMENTS TP 
                WHERE 
                TP.TRANSACTION_DATE = TO_DATE(:tdate, 'MM/DD/YYYY')"""
        oracursor.execute(sorgu, [tdate])
        sat1 = oracursor.fetchone()
        sorgu = """SELECT         
                    MYASOFT_006.TBL_ODEMETIP.ACIKLAMA As OdemeTipi, sum(TP.PAYMENT_TOTAL)  as Satis
                    FROM MYASOFT_006.TBL_TRANSACTION_PAYMENTS TP inner join MYASOFT_006.TBL_ODEMETIP on TP.PAYMENT_REF = MYASOFT_006.TBL_ODEMETIP.KOD
                    WHERE 
                    TP.TRANSACTION_DATE = TO_DATE(:tdate, 'MM/DD/YYYY')
                    group by  PAYMENT_REF, MYASOFT_006.TBL_ODEMETIP.ACIKLAMA 
                    order by Satis desc"""
        oracursor.execute(sorgu, [tdate])
        
        for row in oracursor.fetchall():
            satis.append(row)
    else:
        sparm = {}
        Firinid = session.get('firin_id')
        Firinadi = session.get('firin_adi')
        role = session.get('role')
        N_DAYS_AGO = 6
        today = datetime.now()    
        n_days_ago = today - timedelta(days=N_DAYS_AGO)
        today = str(date.today())
        tdate = datetime.strptime(today, '%Y-%m-%d').strftime('%m-%d-%Y')
        basdate = str(n_days_ago)
        basdate = datetime.strptime(basdate, '%Y-%m-%d %H:%M:%S.%f').strftime('%m-%d-%Y')
        satis = []
        gsatis = []
        dsatis = []
        dsn_tns = cx_Oracle.makedsn('10.9.141.15', '1521', service_name='MYASOFT') 
        oraconn = cx_Oracle.connect(user=r'MYASOFT', password='2019285473637', dsn=dsn_tns)
        oracursor = oraconn.cursor()
        sparm['Firinid'] = Firinid   
        sorgu2 = """SELECT TP.TRANSACTION_DATE,
                sum(TP.PAYMENT_TOTAL)  as Satis
                FROM MYASOFT_006.TBL_TRANSACTION_PAYMENTS TP 
                WHERE 
                TP.STORE_NO =:Firinid
                and TP.TRANSACTION_DATE >= TO_DATE(:basdate, 'MM/DD/YYYY')
                and TP.TRANSACTION_DATE <= TO_DATE(:tdate, 'MM/DD/YYYY')
                group by TP.TRANSACTION_DATE
                order by TP.TRANSACTION_DATE"""
        oracursor.execute(sorgu2, [Firinid, basdate, tdate])
        for row in oracursor.fetchall():
            dt = row[0].strftime("%d/%m/%Y")
            dsatis.append(dt)
            gsatis.append(row[1])
        sorgu="""SELECT 
                sum(TP.PAYMENT_TOTAL)  as Satis
                FROM MYASOFT_006.TBL_TRANSACTION_PAYMENTS TP 
                WHERE 
                TP.STORE_NO =:Firinid
                and TP.TRANSACTION_DATE = TO_DATE(:tdate, 'MM/DD/YYYY')"""
        oracursor.execute(sorgu, [Firinid, tdate])
        sat1 = oracursor.fetchone()
        sorgu = """SELECT         
                    MYASOFT_006.TBL_ODEMETIP.ACIKLAMA As OdemeTipi, sum(TP.PAYMENT_TOTAL)  as Satis
                    FROM MYASOFT_006.TBL_TRANSACTION_PAYMENTS TP inner join MYASOFT_006.TBL_ODEMETIP on TP.PAYMENT_REF = MYASOFT_006.TBL_ODEMETIP.KOD
                    WHERE 
                    TP.STORE_NO =:Firinid
                    and  TP.TRANSACTION_DATE = TO_DATE(:tdate, 'MM/DD/YYYY')
                    group by  PAYMENT_REF, MYASOFT_006.TBL_ODEMETIP.ACIKLAMA 
                    order by Satis desc"""
        oracursor.execute(sorgu, [Firinid, tdate])
        
        for row in oracursor.fetchall():
            satis.append(row)

    oracursor.close()
    oraconn.close()

    return render_template("kontrolpaneli.html", role=role, data=satis, toplam=sat1, gsatis=gsatis, labels=dsatis, message=message)
 
def passreset(id):
    role = session.get('role')
    company_id = session.get('company_id')
    db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101",
                                 database="MicroGorev", auth_plugin='mysql_native_password')
    mycursor = db.cursor()
    mycursor.callproc("kullanici_get", [company_id])
    for result in mycursor.stored_results():
                result = (result.fetchall())
    mycursor.close()
    db = mysql.connector.connect(user="root", password="Nakata!99", host="10.9.141.101",
                                     database="MicroGorev", auth_plugin='mysql_native_password')
    cursor = db.cursor()
    cursor.execute(
        'SELECT * FROM MicroGorev.user WHERE user_id = %s', (id,))
    account = cursor.fetchone()
    # Generate unique ID
    token = str(uuid.uuid4())
    email = account[4]
    # Update the reset column in the accounts table to reflect the generated ID
    cursor.execute('UPDATE MicroGorev.register SET token = %s WHERE email = %s', (token, email))
        # mysql.connection.commit()
        # Change your_email@gmail.com
    email_info = Message('Password Reset', sender=application.config['MAIL_USERNAME'], recipients=[email])
        # Generate reset password link
    reset_link = application.config['DOMAIN'] + url_for('login.resetpassword', email=email, token=token)
        # change the email body below
    email_info.body = 'Please click the following link to reset your password: ' + str(reset_link)
    email_info.html = '<p>Please click the following link to reset your password: <a href="' + str(reset_link) + '">' + str(reset_link) + '</a></p>'
    mail.send(email_info)
    cursor.close()
    message = (email) + " " + "e-mail adresine parola sıfırlaması için mail gönderilmiştir."
    flash(message)
    return render_template("kullanici.html", data=result, kekle='kekle', user=current_user, role=role)
    #return redirect('/kullanici', msg=msg)

"""
@mymicro_blueprint.route('/passreset', methods=['GET', 'POST'])
def forgot():
    return render_template('forgotpassword.html')

""" 