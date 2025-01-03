from flask import Flask, session, redirect, url_for, request, render_template, flash

from flask_mysqldb import MySQL
app = Flask(__name__)

from MySQLdb.cursors import DictCursor

from datetime import datetime

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_db'

app.secret_key = "yoursecretkey"
mysql = MySQL(app)

# OTHERS
@app.route("/")
def home():
    return redirect(url_for("show_login"))

@app.route("/login", methods=['GET', 'POST'])
def show_login():
    if 'username' in session:
        return redirect(url_for('viewDashboard'))
    
    if request.method == "POST":
        user_email = request.form['email']
        user_password = request.form['password']
        if user_email == 'janelaadmin@gmail.com' and user_password == '12345678':
            return render_template('admin/admin-dashboard.html')
        
        if not user_email:
            flash('Email is required', 'error')
            return render_template('login.html')
        elif not user_password:
            flash('Password is required', 'error')
            return render_template('login.html')
        elif len(user_password) < 6:
            flash("Pass must be more than 6 char", 'error')
            return render_template('login.html')
        else:
            try: 
                cursor = mysql.connection.cursor()
                cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (user_email, user_password))
                user = cursor.fetchone()
                cursor.close()
                if user: 
                    # print(user)
                    session['username'] = user[0]
                    print(session['username'])
                    return redirect(url_for('viewDashboard'))
                else: 
                    flash('Invalid Credentials', 'error')
                    return render_template('login.html')
            except Exception as e:
                flash(f"An error occured: {e}", 'error')
                return render_template('login.html')
    else:
        return render_template("login.html")


@app.route('/logout')
def logout():
    flash('Logout successful', 'success')
    session.pop('username', None)
    return redirect(url_for('show_login'))

# CUSTOMER 
@app.route("/dashboard") 
def viewDashboard():
    if 'username' in session:
        return render_template("dashboard.html")
    else:
        return redirect(url_for('show_login'))
    
@app.route('/manage-products')
def manageProducts():
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    return render_template('management-products.html', products = products)

@app.route('/add-product', methods=['GET', 'POST'])
def addProduct():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock = request.form['stock']
        category = request.form['category']
        status = request.form['status']
        
        try:
            cursor = mysql.connection.cursor(DictCursor)
            cursor.execute(
                "INSERT INTO products (user_id, name, description, price, stock, category, status) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)", 
                (session['username'], name, description, price, stock, category, status)
            )
            mysql.connection.commit()
            flash('Product added successfully', 'success')
            return redirect(url_for("manageProducts"))
        except Exception as e:
            print(e)
            mysql.connection.rollback()
            flash(f'Error: {e}', 'danger')
        finally:
            cursor.close()
    
    return render_template('add-product.html')

@app.route('/view-product/<id>', methods = ['GET'])
def viewProduct(id):
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT * FROM products WHERE product_id = %s", [id])
    product = cursor.fetchone()
    return render_template("view-product-details.html", product = product)


@app.route('/edit-product/<id>', methods = ['GET', 'POST'])
def editProduct(id):
    cursor = mysql.connection.cursor(DictCursor)
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        stock = request.form['stock']
        category = request.form['category']
        status = request.form['status']
        
        cursor.execute("UPDATE products SET name = %s, description = %s, price = %s, stock = %s, category = %s, status = %s WHERE product_id = %s", (name, description, price, stock,category, status, id))
        mysql.connection.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for("manageProducts"))
    cursor.execute("SELECT * FROM products WHERE product_id = %s", [id])
    product = cursor.fetchone()
    return render_template("edit-product.html", product = product)

@app.route('/delete-product/<id>', methods = ['GET', 'POST'])
def deleteProduct(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM products WHERE product_id = %s", [id])
    mysql.connection.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for("manageProducts"))


# ADMIN

@app.route("/admin-dashboard") 
def viewAdminDashboard():
        return render_template("admin/admin-dashboard.html")
    
@app.route('/add-customer', methods = ['GET','POST'])
def addCustomer():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone_number =  request.form['phone_number']
        address =  request.form['address']
        account_status =  request.form['account_status']
        registration_date = datetime.now()
        
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("INSERT INTO customers (full_name, email, phone_number, address, account_status, registration_date) VALUES(%s,%s,%s,%s,%s,%s)", (full_name, email, phone_number, address, account_status, registration_date))
        mysql.connection.commit()
        flash('User added successfully', 'success')
        return redirect(url_for("manageCustomers"))
    return render_template('admin/add-customer.html')

@app.route('/manage-customers')
def manageCustomers():
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT * FROM customers")
    customers = cursor.fetchall()
    return render_template('admin/manage-customers.html', customers = customers)

@app.route('/view-customer/<id>', methods = ['GET'])
def viewCustomer(id):
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s", [id])
    customer = cursor.fetchone()
    return render_template("admin/view-customer-details.html", customer = customer)

@app.route('/edit-customer/<id>', methods = ['GET', 'POST'])
def editCustomer(id):
    cursor = mysql.connection.cursor(DictCursor)
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone_number = request.form['phone_number']
        address = request.form['address']
        account_status = request.form['account_status']
        
        cursor.execute("UPDATE customers SET full_name = %s, email = %s, phone_number = %s, address = %s, account_status = %sWHERE customer_id = %s", (full_name, email, phone_number, address,account_status, id))
        mysql.connection.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for("manageCustomers"))
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s", [id])
    customer = cursor.fetchone()
    return render_template("admin/edit-customer.html", customer = customer)

@app.route('/delete-customer/<id>', methods = ['GET', 'POST'])
def deleteCustomer(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM customers WHERE customer_id = %s", [id])
    mysql.connection.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for("manageCustomers"))

if __name__ == "__main__":
    app.run(debug=True)