#from test.badsyntax_future3 import result
from Tix import Form
__author__ = "SAMI UL HUDA"
import sys
from flask import Flask, flash, redirect, render_template, request, session, abort, make_response
import cx_Oracle
import os
import hashlib
from passlib.hash import pbkdf2_sha256
import logging

con = cx_Oracle.connect('sami/sami123@localhost/gdb')  
app = Flask(__name__)


# MySQL configurations
# app.config['MYSQL_USER'] = 'skutagolla'    
# app.config['MYSQL_PASSWORD'] = 'password'
# app.config['MYSQL_DB'] = 'test'
# app.config['MYSQL_HOST'] = 'localhost'
#mysql = MySQL(app)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------  
@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('home.html')

#--------------------------------------------------------------------------------------------------------------------------------------------------------------------------          
@app.route('/login', methods=['GET', 'POST'])
def do_admin_login():
    if request.method == 'POST':
        try:
            email = request.form['username']
            password = request.form['password']
            
            print(type(email))
    
            #passphrase = pbkdf2_sha256.encrypt(password, rounds=200, salt_size=2)
            passphrase = hashlib.md5(password.encode('utf8')).hexdigest()
            print(passphrase)
            
            cur = con.cursor()
            cur.prepare('select * from employee where lower(email) = :email and passphrase = :passphrase')
            cur.execute(None, {'email': email.lower(), 'passphrase': passphrase})
            #cur.execute('select count(*) from employee')
            print (cur)
            for result in cur:
                session['logged_in'] = True
                session['employeeId'] = result[0]
                session['userName'] = result[7]
                isAdmin = False
                if result[9] == 1:
                    isAdmin = True
                session['is_admin'] = isAdmin
                #response = make_response('Authorized')
                #response.setHeader("Cache-Control", "no-cache, no-store, must-revalidate")
                #response.setHeader("Pragma", "no-cache");
                #print (result[0])
#             Print Some SQL Statement
#             user_data = cur.execute("SELECT EM.NAME, EM.GENDER, CT.ADDRESS, CT.CELL_PHONE,CT.LANDMARK,TR.DATE_T,TO_CHAR(TO_DATE(DATE_T,'dd/mm/yyyy'), 'DY') DAY,ST.SHIFT_IN,ST.SHIFT_OUT FROM TRANSPORT TR,  EMPLOYEE EM,  CONTACT CT,  SHIFT_TYPE STWHERE(1=1)AND TR.ID_EMPLOYEE = EM.IDAND EM.ID=CT.ID_EMPLOYEE AND TR.ID_SHIFT=ST.ID")
#             for i in user_data:
#                 print(i)
#             Print Some SQL Statement
            cur.close()
            
        except:
            print("Error in Authentication")
            flash('wrong password!')
        return redirect('/')
    else:
        return redirect('/')
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
@app.route("/logout")
def logout():
    session['logged_in'] = False
    session.clear()
    return redirect('/')

@app.route('/addUser', methods=['GET', 'POST'])
def addUser():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        if session['is_admin'] == True:
            if request.method == 'POST':
                isSaved = saveUser(request.form)
                if isSaved:
                    return home()
                else:
                   return render_template('addUser.html', managers = getMangersList(), errors='Error in Saving User') 
                    
            else:
                return render_template('addUser.html', managers = getMangersList(), errors={})
        else:
            return home()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/viewData', methods=['GET'])
def viewData():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('viewData.html', users = getUsers())
    
    
def getUsers():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        usersList = [];
        try: 
            cur = con.cursor()
            #cur.execute('select id,email, gender, is_regular, gateway, avail_cab, name from employee')
            cur.prepare('SELECT EM.NAME, EM.GATEWAY AS DEPT, EM.GENDER,  CT.ADDRESS,  CT.CELL_PHONE,  CT.LANDMARK,  TR.DATE_T, TO_CHAR(TO_DATE(DATE_T,\'dd/mm/yyyy\'), \'DY\') DAY,  ST.SHIFT_IN,  ST.SHIFT_OUT FROM TRANSPORT TR,  EMPLOYEE EM,   CONTACT CT,  SHIFT_TYPE ST WHERE(1            =1) AND TR.ID_EMPLOYEE = EM.ID AND EM.ID          =CT.ID_EMPLOYEE AND TR.ID_SHIFT    =ST.ID AND EM.ID = :employeeId')
            cur.execute(None, {'employeeId': session.get('employeeId')})
            
            for result in cur:
                record = {'name':result[0], 'gateway':result[1], 'gender': result[2], 'address': result[3], 'mobileNum': result[4], 'landmark': result[5], 'date': result[6], 'day': result[7], 'shiftIn': result[8], 'shiftOut': result[9]}
                #user = { 'id': result[0], 'email': result[1], 'gender': result[2], 'isRegular': result[3], 'gateway': result[4], 'avail_cab': result[5], 'name': result[6]}
                usersList.append(record)
        except:
            print("Error in getting users")
        finally:
            cur.close()
        return usersList;
    

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
@app.route('/contact')
def contact():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('contact.html')
    
def getMangersList():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        managerList = [];
        try: 
            cur = con.cursor()
            cur.execute('select id,name from employee where is_admin=1')
            
            for result in cur:
                dict = { 'id': result[0], 'name': result[1]}
                managerList.append(dict)
        except:
            print("Error in getting managers")
        finally:
            cur.close()
        return managerList;
    
def saveUser(form):
    isSaved = 0
    try: 
        password = form['password']
        passphrase = hashlib.md5(password.encode('utf8')).hexdigest()
        print(passphrase)
            
        cur = con.cursor()
        print(con.version)
        print(form['employeeType'], form['employeeId'])
        cur.prepare('insert into employee values(:employeeId, :email, :gender, :employeeType, :managerId, :gateway, :availCab, :name, :passphrase, :usertype)')
        cur.execute(None, {'email': form['email'].lower(), 'passphrase': passphrase, 'employeeId': form['employeeId'], 'gender': form['gender'], 'employeeType': form['employeeType'], 'managerId': form['managerId'], 'gateWay': form['gateWay'], 'availCab': form['transport'], 'name': form['employeeName'],'usertype': form['usertype']})
        
        #stmt ="INSERT INTO employee VALUES (5, 'samitry@rayan.com', 'M', 1, 500, 'DP', 1, 'Rayan', 'rayan123', 1)"
        #cur.execute(stmt)
        #cur.prepare('insert into manager values(1, :employeeId, :employeeType)')
        #cur.execute(None, {'employeeId': form['employeeId'], 'employeeType': form['employeeType']})
        
        con.commit()
        for result in cur:
            print(result)
        isSaved =  1
        cur.close()
        con.close()
    except Exception as e:
        print("Error in saving user", e)
        #e = sys.exc_info()[0]
        #print(e.message)
         
    finally:
        print("final")
    return isSaved
        
    
                
        
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=4000)

