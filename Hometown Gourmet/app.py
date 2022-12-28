import os
import re
import ibm_db
from flask import Flask, session, render_template, request, redirect, send_from_directory, url_for


app = Flask(__name__)

app.secret_key = 'a'
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=b70af05b-76e4-4bca-a1f5-23dbb4c6a74e.c1ogj3sd0tgtu0lqde00.databases.appdomain.cloud;PORT=32716;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA (5).crt;UID=wln74818;PWD=2VOjd0gekddLy1tu", '', '')
print("connected")

# static file path
@app.route("/static/<path:path>")
def static_dir(path):
    return send_from_directory("static", path)
@app.route('/')
def home123():
    return render_template('home.html')
@app.route('/cart')
def cart():
    return render_template('index1.html')
@app.route('/pay')
def pay():
    return render_template('pay.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        USERNAME = request.form['username']
        PASSWORD = request.form['password']
        sql = "SELECT * FROM USER1 WHERE USERNAME=? AND PASSWORD=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, USERNAME)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            session["USERNAME"] = account["USERNAME"]
            session['USERID'] = account['USERID']
            msg = 'Logged in successfully !'
            return redirect(url_for('products'))
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        USERNAME = request.form["username"]
        PASSWORD = request.form["password"]
        EMAIL = request.form["email"]
        sql = "SELECT* FROM USER1 WHERE USERNAME= ? AND PASSWORD=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, USERNAME)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', EMAIL):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', USERNAME):
            msg = 'Username must contain only characters and numbers !'
        elif not USERNAME or not PASSWORD or not EMAIL:
            msg = 'Please fill out the form !'
        else:
            sql2 = "SELECT count(*) FROM USER"
            stmt2 = ibm_db.prepare(conn, sql2)
            ibm_db.execute(stmt2)
            length = ibm_db.fetch_assoc(stmt2)
            print(length)
            sql = "INSERT INTO  USER1 VALUES(?,?,?,?)"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, USERNAME)
            ibm_db.bind_param(stmt, 2, EMAIL)
            ibm_db.bind_param(stmt, 3, PASSWORD)
            ibm_db.bind_param(stmt, 4, length['1']+1)
            ibm_db.execute(stmt)
            msg = 'Successfully registered!'
            return render_template('login.html', msg=msg)

    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        # session.clear()
        USERNAME = request.form.get("username")
        PASSWORD = request.form.get("password")
        sql = "SELECT* FROM USER1 WHERE USERNAME=? AND PASSWORD=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, USERNAME)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        result = ibm_db.fetch_assoc(stmt)
        print(result)
        if result:
            session['Loggedin']=True
            session["USERID"]=result['USERID']
            Userid=result['USERNAME']
            session['USERNAME']=result['USERNAME']
            msg="logged in successfully !"
            return redirect(url_for('home'))
        else:
            msg="Incorrect username/password!" 
            return render_template('admin_login.html', msg=msg)
    return render_template('admin_login.html')  

# Admin signup
@app.route("/admin-signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # session.clear()
        USERNAME = request.form.get("username")
        EMAIL = request.form.get("email")
        PASSWORD = request.form.get("password")
        # password = request.form.get("password")
        sql ="SELECT * FROM USER1 WHERE USERNAME=? AND PASSWORD=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, USERNAME)
        ibm_db.bind_param(stmt, 2, PASSWORD)
        ibm_db.execute(stmt)
        data = ibm_db.fetch_assoc(stmt)
        if data:
            return render_template("admin-signup.html", message="Username already exists!")
        else:
            sql2 = "SELECT count(*) FROM USER1"
            stmt2 = ibm_db.prepare(conn, sql2)
            ibm_db.execute(stmt2)
            length = ibm_db.fetch_assoc(stmt2)
            print(length)
            sql = "INSERT INTO USER1 VALUES(?,?,?,?)"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt, 1, USERNAME)
            ibm_db.bind_param(stmt, 2, EMAIL)
            ibm_db.bind_param(stmt, 3, PASSWORD)
            ibm_db.bind_param(stmt, 4, length['1']+1)
            ibm_db.execute(stmt)
            print("Successful Signup")
            return redirect(url_for("admin_login"))
    return render_template("admin-signup.html")


# Merchant home page to add new productss
@app.route("/home", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        image = request.files['image']
        PROID = request.form.get("proid")
        CATOGERY = request.form.get("category")
        SUB_CATOGERY = request.form.get("Sub-category")
        DESCRIPTION = request.form.get("description")
        PRICE_RANGE = request.form.get("price_range")
        COMMENTS = request.form.get("comments")
        current_user = session["USERNAME"]
        sql="SELECT * FROM USER1 WHERE USERID = " +str(session['USERID']) 
        stmt=ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        data=ibm_db.fetch_tuple(stmt)
        insert_sql ="INSERT INTO PRODUCTS VALUES (?,?,?,?,?,?,?,?)"
        stmt1 = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(stmt1, 1, data[3])
        ibm_db.bind_param(stmt1, 2, PROID)
        ibm_db.bind_param(stmt1, 3, data[0])
        ibm_db.bind_param(stmt1, 4, CATOGERY)
        ibm_db.bind_param(stmt1, 5, SUB_CATOGERY)
        ibm_db.bind_param(stmt1, 6, DESCRIPTION)
        ibm_db.bind_param(stmt1, 7, PRICE_RANGE)
        ibm_db.bind_param(stmt1, 8, COMMENTS)
        ibm_db.execute(stmt1)
        # sql = 'select max(prodid) as maxi from products'
        sql = 'SELECT * FROM PRODUCTS' 
        stmt2 = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt2)
        data = ibm_db.fetch_assoc(stmt2)
        filename = str(data['PROID'])
        image.save(os.path.join("static/images", filename))
        current_user = session["USERID"]
        sql = "SELECT * FROM PRODUCTS WHERE USERID=" +str(session['USERID'])
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.execute(stmt)
        data = ibm_db.fetch_assoc(stmt)
        rows = []
        while True:
            data = ibm_db.fetch_assoc(stmt)
            if not data:
                break
            else:
                data['PROID'] = str(data['PROID'])
                rows.append(data)
        return render_template("home1.html", rows=rows, message="Product added")

    current_user1 = session["USERID"]
    select_sql = "SELECT * FROM PRODUCTS WHERE USERID=" +str(session['USERID'])
    stmt = ibm_db.prepare(conn, select_sql)
    ibm_db.execute(stmt)
    data = ibm_db.fetch_assoc(stmt)
    rows = []
    while True:
        data = ibm_db.fetch_assoc(stmt)
        if not data:
            break
        else:
            data['PROID'] = str(data['PROID'])
            rows.append(data)
    return render_template("home1.html", rows=rows)

@app.route('/delete_product/<string:PROID>', methods = ['POST'])
def delete_product(PROID):
    current_user = session["USERID"]
    sql= "DELETE FROM PRODUCTS WHERE PROID=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, PROID)
    ibm_db.execute(stmt)
    # print('item deleted')
    return redirect(url_for('home'))

@app.route('/del_pro/<string:PROID>', methods = ['POST'])
def del_pro(PROID):
    current_user = session["USERID"]
    sql= "DELETE FROM TRANSACTION WHERE PROID=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, PROID)
    ibm_db.execute(stmt)
    print('item deleted')
    return redirect(url_for('trans'))

@app.route('/add_to_cart/<string:PROID>', methods = ['GET', 'POST'])
def add_to_cart(PROID):
    current_user = session["USERID"]
    sql="SELECT * FROM PRODUCTS WHERE PROID ="+PROID
    stmt=ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    data=ibm_db.fetch_tuple(stmt)
    print(data)
    print('done bro')
    # if request.method=='post':
    insert_sql ="INSERT INTO TRANSACTION VALUES (?,?,?,?,?)"
    stmt = ibm_db.prepare(conn, insert_sql)
    ibm_db.bind_param(stmt, 1, data[0])
    ibm_db.bind_param(stmt, 2, data[1])
    ibm_db.bind_param(stmt, 3, data[2])
    ibm_db.bind_param(stmt, 4, data[5])
    ibm_db.bind_param(stmt, 5, data[6])
    ibm_db.execute(stmt)
    return redirect(url_for('products'))
    # return render_template('trans.html')


@app.route('/products')
def products():
    select_sql = "SELECT * FROM products"
    stmt = ibm_db.prepare(conn, select_sql)
    ibm_db.execute(stmt)
    rows = []
    while True:
        data = ibm_db.fetch_assoc(stmt)
        if not data:
            break 
        else:

            data['PROID'] = str(data['PROID'])
            # if(data['PROID']==101):

            rows.append(data)
    print('rows: ', rows)
    return render_template('index.html',rows=rows)

@app.route('/trans')
def trans():
    select_sql = "SELECT * FROM TRANSACTION"
    stmt = ibm_db.prepare(conn, select_sql)
    ibm_db.execute(stmt)
    data=ibm_db.fetch_tuple(stmt)
    print(data)
    rows = []
    while data!= False:
        rows.append(data)
        data=ibm_db.fetch_tuple(stmt)
    print(rows)
    return render_template('trans.html', rows=rows)    


@app.route('/products/<string:PROID>')
def men():
    select_sql = "SELECT * FROM products WHERE catogery='<string:PROID>'"
    stmt = ibm_db.prepare(conn, select_sql)
    ibm_db.execute(stmt)
    rows = []
    while True:
        data = ibm_db.fetch_assoc(stmt)
        if not data:
            break 
        else:
            data['PROID'] = str(data['PROID'])
            rows.append(data)
    print('rows: ', rows)
    return render_template('index.html', rows=rows)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route("/logout")
def admin_logout():
    session.clear()
    return redirect("/login")
if __name__ == '__main__':
    app.run(debug=True)
