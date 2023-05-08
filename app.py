from flask import Flask, render_template, request,redirect,session
from mysql.connector import connect
from model import *
from flask_bcrypt import Bcrypt
import matplotlib.pyplot as plt
import io
import base64

app=Flask(__name__)
app.secret_key='hghfgfchhfhfh'
bcrypt = Bcrypt(app)

con=connect(host='localhost',port=3306,database='textanalysis',user='root')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def Login():
    return render_template('Login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/Signup_validation',methods=["POST","GET"])
def Signup_validation():
    if request.method=="POST":
        name=request.form['name']
        cur=con.cursor()
        cur.execute('select * from users where name=%s',(name,))
        x=cur.fetchone()
        if x==None:
            pass1=request.form['pass1']
            pass2=request.form['pass2']
            if pass1 == pass2:
                cur=con.cursor()
                password=bcrypt.generate_password_hash(pass1)
                cur.execute("insert into users values(%s,%s)",(name,password))
                con.commit()
                return redirect('/login')
            else:
                return "Please Check ur Password,Password should Match!..."
        else:
            return redirect('/login')
    else:
        return redirect('/signup')

@app.route('/login_validate',methods=["POST","GET"])
def login_validate():
    if request.method=="POST":
        name=request.form['name']
        session['name']=name
        cur=con.cursor()
        cur.execute("select * from users where name=%s",(name,))
        x=cur.fetchone()
        if x!=None and name==x[0]:
            return redirect('/')
        else:
            return redirect('/signup')
    else:
        return redirect('/login')
    

@app.route("/classify", methods=["POST"])
def classify():
    # Get the text from the form
    if session.get('name'):
        text = request.form["text"]
        
        # Preprocess the text
        text = [text]
        text = vectorizer.transform(text)
        
        # Classify the sentiment
        sentiment = model.predict(text)[0]
        
        # Convert the sentiment to a string
        if sentiment == "negative":
            cur=con.cursor()
            cur.execute("select * from negreview")
            neg=cur.fetchone()
            if neg==None:
                val=str(1)
                cur=con.cursor()
                cur.execute("insert into negreview values(%s)",(val,))
                con.commit()
            else:
                neg=neg[0]
                neg1=int(neg)
                neg1+=1
                neg1=str(neg1)
                cur.execute("update negreview set value=%s where value=%s",(neg1,neg))
                con.commit()
            result = "negative"
        elif sentiment == "positive":
            cur=con.cursor()
            cur.execute("select * from posreview")
            pos=cur.fetchone()
            if pos==None:
                val=1
                cur=con.cursor()
                cur.execute("insert into posreview values(%s)",(val,))
                con.commit()
            else:
                pos=pos[0]
                pos1=int(pos)
                pos1+=1
                pos1=str(pos1)
                cur.execute("update posreview set value=%s where value=%s",(pos1,pos))
                con.commit()
            result = "positive"
        else:
            result = "neutral"
        
        # Render the result page
        return render_template("result.html", result=result)
    else:
        return redirect('/login')

@app.route('/analysis')
def analysis():
    cur=con.cursor()
    cur.execute("select * from negreview")
    neg=cur.fetchone()
    cur.execute("select * from posreview")
    pos=cur.fetchone()
    if neg==None and pos==None:
        res="There are no reviews recorded yet to visualize the analysis."
        return render_template("noreviews.html",res=res)    
    else:
        if neg==None:
            n=0
            p=int(pos[0])
        elif pos==None:
            n=int(neg[0])
            p=0
        else:
            n=int(neg[0])
            p=int(pos[0])
        plt.figure(figsize=(6, 4))
        plt.bar(['Positive', 'Negative'], [p, n],width=0.3,color=['green', 'red'])
        plt.xlabel('Sentiment')
        plt.ylabel('Number of Reviews')
        plt.title('Sentiment Analysis Results')
        
        # convert the plot to a string buffer and encode as base64
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        # pass the image string to the template for display
        return render_template('sentiment_results.html', image=image)

        
        
    
@app.route('/logout')
def logout():
    session['name']=None
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)




