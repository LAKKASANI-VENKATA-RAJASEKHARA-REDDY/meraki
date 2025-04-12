from flask import Flask, render_template, redirect, url_for, session, flash, request
import mysql.connector
from flask_mail import Mail, Message
import random,os
import google.generativeai as genai
import time

def create_db_connection():
    return mysql.connector.connect(
        host="crossover.proxy.rlwy.net",
        user="root",
        password="nYMLabGfqklOHiHhthPsSmZGZwgsMukU",
        database="railway",
        port=48105
    )


app = Flask(__name__)
app.secret_key="Sekhar@26"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'lvrajasekharareddy.2007@gmail.com'  
app.config['MAIL_PASSWORD'] = 'pavf zpvp lhzb gndm'  

mail = Mail(app)

@app.route('/')
def home():
  #session.clear()
  if 'status' not in session:
    return render_template('home_page.html', display="no")
  else:
    return render_template('home_page.html')

@app.route('/home')
def home_page():
   return render_template('home_page.html')

@app.route('/register', methods=["POST"])
def register():
  return render_template('registration_page.html')

@app.route('/registeration', methods=['POST','GET'])
def reg():
  session['email'] = request.form.get('email')
  session['name'] = request.form.get('name')
  '''name = request.form.get('name')'''
  email = request.form.get('email')
  session['usn'] = request.form.get('usn')
  session['position'] = request.form.get('position')
  session['branch'] = request.form.get('branch')
  session['password'] = request.form.get('password')
  conn = create_db_connection()
  cursor = conn.cursor(dictionary=True)
  cursor.execute("SELECT * FROM members WHERE email = %s",(session['email'],))
  result = cursor.fetchone()
  if result:
     print("email: ",session['email'])
     return render_template('registration_page.html', error_message = "User already exists ! Try Again")
  else:
      otp = random.randint(100000, 999999)
      session['otp'] = otp
      #session['email'] = email
      msg = Message("Your otp", sender=app.config['MAIL_USERNAME'], recipients=[email])
      msg.body = f"Your otp is: {otp}"
      mail.send(msg)
      return render_template('verify.html')
  
  #return render_template('verify.html')

@app.route('/resend', methods=['POST','GET'])
def resend():
      email = session['email']
      otp = random.randint(100000, 999999)
      session['otp'] = otp
      #session['email'] = email
      msg = Message("Your otp", sender=app.config['MAIL_USERNAME'], recipients=[email])
      msg.body = f"Your otp is: {otp}"
      mail.send(msg)
      print(msg)
      print(otp)
      session['status'] = "ok"
      return render_template('verify.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    
    if request.method == 'POST':
        entered_otp = request.form.get('otp')
        stored_otp = session.get('otp')

        if entered_otp and stored_otp and entered_otp == str(stored_otp):
            name = session['name']
            email = session['email']
            usn = session['usn']
            branch = session['branch']
            position = session['position']
            password = session['password']
            conn = create_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("INSERT INTO members (name, email, USN, branch, position, password) VALUES(%s,%s,%s,%s,%s,%s)",(name, email, usn, branch, position, password))
            conn.commit()
            session['status'] = "ok"
            print("Successfully uploaded to session")
            return render_template('home_page.html')
        else:
            return 'Invalid otp. Try again!'

    return render_template('verify.html')
        
@app.route('/profile',methods=['POST','GET'])
def profile():
   if 'status' in session:
    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM members WHERE email = %s",(session['email'],))
    info = cursor.fetchone()
    name = info['name']
    position = info['position']
    branch = info['branch']
    usn = info['USN']
    return render_template('profile.html', name=name,branch=branch,position=position,usn=usn)
   else:
    return render_template('registration_page.html')
  
@app.route('/login')
def login():
   return render_template('logging_in.html')

@app.route('/logging_in', methods=['POST','GET'])
def logging_in():
   email = request.form.get('email')
   password = request.form.get('password')
   session['email'] = email
   conn = create_db_connection()
   cursor = conn.cursor(dictionary=True)
   cursor.execute("SELECT password FROM members WHERE email = %s", (email,))

   db_password = cursor.fetchone()
   if password == db_password['password']:
      session['otp'] = 000000
      session['status'] = "ok"
      
      return render_template('home_page.html')
   else:
      return "invalid credentials"

@app.route('/work', methods=['POST'])
def work():
  if 'status' in session:
    return render_template('work.html')
  else:
      return render_template('registration_page.html')

@app.route('/upwork', methods=['POST', 'GET'])
def upwork():
    if 'status' in session:
        name = session.get('name')
        title = request.form.get('title')
        description = request.form.get('description')
        pdf = request.files.get('pdf')

        if not pdf:
            return "No file uploaded. Please try again.", 400

        filename = pdf.filename
        pdf_path = os.path.join('static/uploads', filename)
        pdf.save(pdf_path)

        conn = create_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO works(name, title, description, pdf_path, filename) VALUES (%s, %s, %s, %s, %s)",
            (name, title, description, pdf_path, filename)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return render_template('home_page.html')

    else:
      return render_template('registration_page.html')


@app.route('/show_works')
def show_works():
  if 'status' in session:
    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM works ")
    works = cursor.fetchall()
    return render_template('display_work.html', works = works)
  else:
      return render_template('registration_page.html')

  

@app.route('/news', methods=['POST'])
def news():
  if 'status' in session:
    return render_template('news.html')
  else:
      return render_template('registration_page.html')


@app.route('/upnews', methods=['POST', 'GET'])
def upnews():
    if 'status' in session:
        name = session.get('name')
        news = request.form.get('news')

        conn = create_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO news(name, news) VALUES (%s,%s)",
            (name,news)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return render_template('home_page.html')

    else:
      return render_template('registration_page.html')

@app.route('/show_news')
def show_news():
  if 'status' in session:
    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM news ")
    news = cursor.fetchall()
    return render_template('display_news.html', news = news)
  else:
      return render_template('registration_page.html')


@app.route('/logout')
def logout():
   session.pop('status')
   return render_template('home_page.html', display = "no")

@app.route('/show_your_news')
def show_your_news():
  if 'status' in session:
    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM news WHERE name = %s", (session['name'],))
    your_news = cursor.fetchall()
    return render_template('your_news.html', your_news=your_news)
  else:
    return render_template('registration_page.html')


@app.route('/show_your_works')
def show_your_works():
   if 'status' in session:
      conn = create_db_connection()
      cursor = conn.cursor(dictionary=True)
      cursor.execute("SELECT * FROM works where name = %s",(session['name'],))
      your_works = cursor.fetchall()
      return render_template('your_works.html', your_works = your_works)
   else:
      return render_template('registration_page.html')

@app.route('/edit_profile', methods=['POST','GET'])
def display_edit():
   return render_template('edit_profile.html')

@app.route('/edit',methods=['POST','GET'])
def edit():
   name = request.form.get('name')
   usn = request.form.get('usn')
   branch = request.form.get('branch')
   position = request.form.get('position')
   conn = create_db_connection()
   cursor = conn.cursor(dictionary=True)
   cursor.execute("UPDATE members SET name = %s, USN = %s, branch = %s, position = %s WHERE email = %s", (name, usn, branch, position, session['email']))
   conn.commit()
   return render_template('home_page.html')

@app.route('/delete', methods=['POST'])
def delete():
    filename = request.form.get('filename')
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM works WHERE filename = %s", (filename,))
    conn.commit()
    cursor.close()
    conn.close()
    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM works where name = %s",(session['name'],))
    your_works = cursor.fetchall()
    return render_template('your_works.html', your_works = your_works)

@app.route('/delete_news', methods=['POST'])
def delete_news():
    news = request.form.get('news')
    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM news WHERE news = %s", (news,))
    conn.commit()
    cursor.close()
    conn.close()
    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM news where name = %s",(session['name'],))
    your_news = cursor.fetchall()
    return render_template('your_news.html', your_news = your_news)



if __name__ == "__main__":
  app.run(debug=True)