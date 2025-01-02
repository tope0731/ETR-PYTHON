from flask import Flask, session, redirect, url_for, request, render_template, flash

from flask_mysqldb import MySQL
app = Flask(__name__)

from MySQLdb.cursors import DictCursor

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'flask_db'

app.secret_key = "yoursecretkey"
mysql = MySQL(app)
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
            return render_template('admin.html')
        
        if not user_email:
            flash('Email is required', 'error')
            return render_template('index.html')
        elif not user_password:
            flash('Password is required', 'error')
            return render_template('index.html')
        elif len(user_password) < 6:
            flash("Pass must be more than 6 char", 'error')
            return render_template('index.html')
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
                    return render_template('index.html')
            except Exception as e:
                flash(f"An error occured: {e}", 'error')
                return render_template('index.html')
    else:
        return render_template("index.html")


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
    
@app.route('/manage-users')
def manageUsers():
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    return render_template('manage-users.html', users = users)

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

@app.route('/add-user', methods = ['GET','POST'])
def addUser():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = 12345678
        cursor = mysql.connection.cursor(DictCursor)
        cursor.execute("INSERT INTO users (email, name, password) VALUES(%s,%s,%s)", (email, name, password))
        mysql.connection.commit()
        flash('User added successfully', 'success')
        return redirect(url_for("manageUsers"))
    return render_template('add-user.html')

@app.route('/view/<id>', methods = ['GET'])
def view(id):
    cursor = mysql.connection.cursor(DictCursor)
    cursor.execute("SELECT * FROM users WHERE id = %s", [id])
    user = cursor.fetchone()
    return render_template("view-details.html", user = user)

@app.route('/edit/<id>', methods = ['GET', 'POST'])
def edit(id):
    cursor = mysql.connection.cursor(DictCursor)
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        
        cursor.execute("UPDATE users SET email = %s, name = %s WHERE id = %s", (email, name, id))
        mysql.connection.commit()
        flash('User updated successfully', 'success')
        return redirect(url_for("manageUsers"))
    cursor.execute("SELECT * FROM users WHERE id = %s", [id])
    user = cursor.fetchone()
    return render_template("edit-user.html", user = user)
    

@app.route('/delete/<id>', methods = ['GET', 'POST'])
def delete(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", [id])
    mysql.connection.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for("manageUsers"))

# @app.route("/product/<category>/<product_id>")
# def show_product(category, product_id):
#     return f"c: {category}, p: {product_id}"

if __name__ == "__main__":
    app.run(debug=True)