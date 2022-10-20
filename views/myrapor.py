from views.module import *
from myapp import *
from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, send_file,  Blueprint, abort
from email import message
import pandas as pd
import numpy as np
import csv
from datetime import datetime, timedelta
import time
from io import BytesIO
#import zipfile
import shutil
import os
#import argparse

myrapor_blueprint = Blueprint('myrapor', __name__)
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




@myrapor_blueprint.route('/txtrapor', methods=["GET", "POST"])
def txtrapor():
    role = session.get('role')
    dsn_tns = cx_Oracle.makedsn('10.9.141.15', '1521', service_name='MYASOFT') 
    oraconn = cx_Oracle.connect(user=r'MYASOFT', password='2019285473637', dsn=dsn_tns)
    oracursor = oraconn.cursor()    
    member = []
    sorgu1 = ("select  LOK.LOKASYONNO, LOK.ACIKLAMA from MYASOFT_006.TBL_LOKASYONLAR LOK WHERE DURUM = 1  ORDER BY LOK.ACIKLAMA ")
    oracursor.execute(sorgu1)
    for row in oracursor.fetchall():
        member.append(row)
    return render_template("txtrapor.html", role=role, firin = member)


@myrapor_blueprint.route('/txtraporsend1', methods=["GET", "POST"])
def txtraporsend1():
    df = pd.DataFrame()
    df1 = pd.DataFrame()
    dfz = pd.DataFrame()
    date = open('tarih.txt').read().split()
    zrap= ('./temp/' + 'zrap' + '.csv' )
    file = open(zrap, "w")
    writer = csv.writer(file, quoting=csv.QUOTE_ALL)
    writer.writerows([[ 'Firinid', 'ddate', 'Aratotal', 'indirim', 'total']])
    number = open('firin.txt').read().split()
    #os.remove("./temp/*")
    #directory_name = 'temp/'
    #os.remove(directory_name)
    role = session.get('role')
    form = request.form
    #basdate = form.get('basdate')
    #basdate = datetime.strptime(basdate, '%Y-%m-%d').strftime('%m-%d-%Y')
    #bitdate = form.get('bitdate')
    #bitdate = datetime.strptime(bitdate, '%Y-%m-%d').strftime('%m-%d-%Y')
    data = request.form.getlist('selectedfirin')
    dsn_tns = cx_Oracle.makedsn('10.9.141.15', '1521', service_name='MYASOFT') 
    oraconn = cx_Oracle.connect(user=r'MYASOFT', password='2019285473637', dsn=dsn_tns)
    oracursor = oraconn.cursor()    
    member = []
    sorgu1 = ("select  LOK.LOKASYONNO, LOK.ACIKLAMA from MYASOFT_006.TBL_LOKASYONLAR LOK WHERE DURUM = 1  ORDER BY LOK.ACIKLAMA ")
    oracursor.execute(sorgu1)
    for row in oracursor.fetchall():
        member.append(row)
    indirimxt= ('./temp/' + 'indirimxt' + '.csv' )
    #number = open('firin.txt').read().split()
    #date = open('tarih.txt').read().split()
    file = open(indirimxt, "w")
    writer = csv.writer(file, quoting=csv.QUOTE_ALL)
    writer.writerows([[ 'Firinid', 'ddate', 'Aratotal', 'indirim', 'total']])

    if  request.method == 'POST':
        first = form.get('basdate')
        first = datetime.strptime(first, '%Y-%m-%d').strftime('%m/%d/%Y')
        last = form.get('bitdate')
        last = datetime.strptime(last, '%Y-%m-%d').strftime('%m/%d/%Y')
        first = datetime.strptime(first, '%m/%d/%Y')

        last = datetime.strptime(last, '%m/%d/%Y')
        list_of_dates = [ first + timedelta(i) for i in range((last - first).days + 1) ]
        print(list_of_dates)

        for date in list_of_dates[1:-1]:
            bdate = date.strftime("%m/%d/%Y")
            tarih = date.strftime("%m/%d/%Y")
            print(tarih)

            number = request.form.getlist('selectedfirin')
            print(number)
            sparm = {}  
            sparm['bdate'] = bdate
            for data in number:
                Firinid = data
                print(Firinid, bdate)
                sparm['Firinid'] = Firinid 
                # Oracle sorgu
                sorgu = """
                SELECT TL.STORE_NO, 
                TL.STOCK_BARCODE, 
                TL.STOCK_CODE, TL.AMOUNT, 
                TL.LINE_TOTAL_VALUE, TL.LINE_TOTAL_VAT, 
                TL.LINE_TOTL_DISCOUNT
                FROM MYASOFT_006.TBL_TRANSACTION_LINES TL 
                WHERE TL.STORE_NO =:Firinid AND TL.TRANSACTION_TYPE = 0 AND Line_Total_Vat > 0
                AND TL.TRANSACTION_DATE = TO_DATE(:bdate, 'mm/dd/yyyy')
                """
                #np db ye çevirip hucre hucre veri yakalamak için
                date = datetime.strptime(bdate, "%m/%d/%Y")
                fdate = datetime.strftime(date, "%d-%m-%Y")
                ddate = datetime.strftime(date, "%d/%m/%Y")
                df_ora = pd.read_sql(sorgu, con=oraconn, params=sparm)
                txtyaz =np.array(df_ora) 
                #xml icin
                df = df_ora.set_index('STORE_NO')
                Aratotal = (df.LINE_TOTAL_VALUE.sum())
                print("aratotal", Aratotal)
                indirim = (df.LINE_TOTL_DISCOUNT.sum())
                print("indirim", indirim)   
                total = (Aratotal - indirim)
                print("total", total)
                Dokumant= ('./temp/' + 'Transaction' + '-' + (str(Firinid)) + '-' + (str(fdate)) + '.txt' )
                Dokumanx= ('./temp/' + 'Transaction' + '-' + (str(Firinid)) + '-' + (str(fdate)) + '.xml' )
                indirimx= ('./temp/' + 'indirim' + '-' + (str(Firinid)) + '-' + (str(fdate)) + '.txt' )
                indirimxt= ('./temp/' + 'indirimxt' + '.csv' )
                file = open(Dokumanx, "w")
                writer = csv.writer(file, quoting=csv.QUOTE_ALL)
                writer.writerows([[ '<ID>90300000001068</ID>'],[ '<NUM>', Firinid ,'</NUM>'],[ '<DATE_START>', ddate ,'</DATE_START>'],[ '<LOCAL_TOTAL>', total ,'</LOCAL_TOTAL>']])
                file.close()
                file = open(indirimx, "w")
                writer = csv.writer(file, quoting=csv.QUOTE_ALL)
                writer.writerows([[ '<NUM>', Firinid ,'</NUM>'],[ '<DATE_START>', ddate ,'</DATE_START>'],[ '<Ara Total>', Aratotal ,'</Ara Total>'],[ '<İndirim>', indirim ,'</İndirim>'],[ '<LOCAL_TOTAL>', total ,'</LOCAL_TOTAL>']])
                file.close()
                file = open(indirimxt, "a")
                writer = csv.writer(file, quoting=csv.QUOTE_ALL)
                writer.writerows([[ Firinid, ddate, int(Aratotal), int(indirim), int(total)]])
                file = open(Dokumant, "w")
                #txt icin
                hdtid = 90300000463048
                i = 0
                zk = 0
                for i in range(len(txtyaz)):
                    id = '1030' + '[' + str(Firinid) + ']'
                    id1 = '2089' +'[' + '1030' + '[' + str(Firinid) + ']' +';' + '1' +']'
                    kid = '1001' +'[' + '1' + ']'
                    file = open(Dokumant, "a")
                    hdtid = (hdtid + 1)
                    zk = (zk +1)
                    writer = csv.writer(file, quoting=csv.QUOTE_ALL)
                    writer.writerows([[ '1', hdtid, id, id1, '', ddate, kid, zk ,'0','0','','','','', txtyaz[i][4], txtyaz[i][5], txtyaz[i][6], '0', '', '', '', '', '', '', '', '' ],
                    [ 2,  '', '', '', '', '', '', '', txtyaz[i][3], '', '', '', '', '', txtyaz[i][4], '', txtyaz[i][5], txtyaz[i][6], 0,  '', '', '', '', '', '', txtyaz[i][1], txtyaz[i][2],
                    '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],
                    [ 3,  '', '', '', '',1 , '', 0, txtyaz[i][4], '', '', '', '', '', '', '', '', '', '', '', '', '', '', '']])
                    file.close()
                # xml Replace için
                with open(Dokumanx, 'r') as file :
                    filedata = file.read()
                    filedata = filedata.replace(',', '')
                    filedata = filedata.replace('"', '')
                    filedata = filedata.replace('.', ',')
                    # xml Replace edilen write için
                    with open(Dokumanx, 'w') as file:
                        file.write(filedata)
                    # txt Replace için
                    with open(Dokumant, 'r') as file :
                        filedata = file.read()
                        filedata = filedata.replace(',', ';')
                        filedata = filedata.replace('"', '')
                        filedata = filedata.replace('.', ',')
                    # txt Replace edilen write için
                    with open(Dokumant, 'w') as file:
                        file.write(filedata)
                    # csv Replace için
                    with open(indirimxt, 'r') as file :
                        filedata = file.read()
                        filedata = filedata.replace(',', ';')
                        filedata = filedata.replace('"', '')
                        #filedata = filedata.replace('.', ',')
                    # txt Replace edilen write için
                    with open(indirimxt, 'w') as file:
                        file.write(filedata)
    zip_name = 'txtdosya'
    directory_name = 'temp'
    shutil.make_archive(zip_name, 'zip', directory_name)
    email = session.get('e_mail')
    email_info = Message('Satıs Raporu', sender=application.config['MAIL_USERNAME'], recipients=[email])
    email_info.body = 'Raporunuz ektedir: ' 
    email_info.html = '<p>Raporunuz ektedir </p>'
    with application.open_resource("../txtdosya.zip") as fp:
        email_info.attach("/txtdosya.zip", "text/csv", fp.read())
    mail.send(email_info)
    message = (email) + " " + "e-mail adresine Satıs Raporu için mail gönderilmiştir."
    flash(message)
    sparm = {}
    oracursor.close()
    oraconn.close()
    return render_template("txtrapor.html", role=role, firin = member)

@myrapor_blueprint.route('/xlssend', methods=["GET", "POST"])
def xlssend():
    dsn_tns = cx_Oracle.makedsn('10.9.141.15', '1521', service_name='MYASOFT') 
    oraconn = cx_Oracle.connect(user=r'MYASOFT', password='2019285473637', dsn=dsn_tns)
    oracursor = oraconn.cursor()    
    member = []
    sparm = {} 
    df = pd.DataFrame()
    df1 = pd.DataFrame()
    dfz = pd.DataFrame()
    form = request.form
    number = request.form.getlist('selectedfirin')
    role = session.get('role')
    #data = request.form.getlist('selectedfirin')
    sorgu1 = ("select  LOK.LOKASYONNO, LOK.ACIKLAMA from MYASOFT_006.TBL_LOKASYONLAR LOK WHERE DURUM = 1  ORDER BY LOK.ACIKLAMA ")
    oracursor.execute(sorgu1)
    for row in oracursor.fetchall():
        member.append(row)
    #sparm['bdate'] = bdate
    for data in number:
        sparm['Firinid'] = data 
        first = form.get('basdate')
        first = datetime.strptime(first, '%Y-%m-%d').strftime('%m/%d/%Y')
        last = form.get('bitdate')
        last = datetime.strptime(last, '%Y-%m-%d').strftime('%m/%d/%Y')
        first = datetime.strptime(first, '%m/%d/%Y')
        first = (first - timedelta(days=1))
        last = datetime.strptime(last, '%m/%d/%Y')
        last = (last + timedelta(days=1))
        list_of_dates = [ first + timedelta(i) for i in range((last - first).days + 1) ]
        print(list_of_dates)
        for date in list_of_dates[1:-1]:
            bitdate = (date + timedelta(days=1))
            bdate = date.strftime("%m/%d/%Y")
            bitdate = bitdate.strftime("%m/%d/%Y")
            print(bdate)
            print(bitdate)
            sparm['basdate'] = bdate
            sparm['bitdate'] = bitdate
            #sparm['Firinid'] = number 
            sorgu = """ select ZR.ID, ZR.STORE_NO, ZR.POS_NO, ZR.ZNO, ZR.TARIH, ZR.ZTEXT, ZR.DIPTOPLAM 
                                FROM  MYASOFT_006.TBL_Z_REPORTS ZR  
                                WHERE  ZR.STORE_NO = :Firinid
                                and ZR.TARIH >= to_date(:basdate,'mm/dd/yyyy HH24:MI:SS') 
                                and ZR.TARIH <= to_date(:bitdate,'mm/dd/yyyy HH24:MI:SS')
                                order by ZR.POS_NO
                                """
            df = df.append(pd.read_sql(sorgu, con=oraconn, params=sparm ))
            df.to_excel('Z_Raporları.xlsx', sheet_name='new_sheet_name')
        for date in list_of_dates[1:-1]:
            bitdate = (date + timedelta(days=1))
            bdate = date.strftime("%m/%d/%Y")
            bitdate = bitdate.strftime("%m/%d/%Y")
            print(bdate)
            print(bitdate)
            sparm['basdate'] = bdate
            sparm['bitdate'] = bitdate  
            sorgu2 = """ select ZR.STORE_NO, ZR.POS_NO, ZR.TARIH, sum(ZR.DIPTOPLAM) as toplam
                        FROM MYASOFT_006.TBL_Z_REPORTS ZR  
                        WHERE ZR.STORE_NO = :Firinid
                        and ZR.TARIH >= to_date(:basdate, 'mm/dd/yyyy HH24:MI:SS') 
                        and ZR.TARIH <= to_date(:bitdate, 'mm/dd/yyyy HH24:MI:SS')
                        GROUP BY ZR.STORE_NO , ZR.POS_NO , ZR.TARIH 
                        order by ZR.POS_NO """
            dfz = dfz.append(pd.read_sql(sorgu2, con=oraconn, params=sparm))
            dfz.to_excel('Toplam_Z_Rapor.xlsx', sheet_name='new_sheet_name')

    zip_name = 'txtdosya'
    directory_name = 'temp'
    shutil.make_archive(zip_name, 'zip', directory_name)
    email = session.get('e_mail')
    email_info = Message('Firinlar Z Raporu', sender=application.config['MAIL_USERNAME'], recipients=[email])
    email_info.body = 'Raporunuz ektedir: ' 
    email_info.html = '<p>Raporunuz ektedir </p>'
    with application.open_resource("../Z_Raporları.xlsx") as fp:
        email_info.attach("/Z_Raporları.xlsx", "text/csv", fp.read())
    with application.open_resource("../Toplam_Z_Rapor.xlsx") as fp:
        email_info.attach("/Toplam_Z_Rapor.xlsx", "text/csv", fp.read())        
    mail.send(email_info)
    message = (email) + " " + "e-mail adresine Satıs Raporu için mail gönderilmiştir."
    flash(message)
    #sparm = {}
    oracursor.close()
    oraconn.close()
    return render_template("xlsrapor.html", role=role, firin = member)
        