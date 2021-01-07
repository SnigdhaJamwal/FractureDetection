from flask import Flask, render_template, request, url_for, redirect, flash, session
from passlib.hash import sha256_crypt
from validate_email import validate_email
from dbConnect import connection
from datetime import datetime
import gc
import os,io
from werkzeug.utils import secure_filename
from verifyImageUpload import is_greyscale
from pingVisionAPI import is_xray
from PIL import Image
from datetime import datetime
from SVM_testing import testSVM
from combinedFinalResult import outputNetwork

app = Flask(__name__)

# To create session it is required to create a secret key for server to communicate with browser securely
app.secret_key = os.urandom(24)

admin = 1
user = 2

user_dir = dict()


def session_check():
    # To check user is in session
    # Alternate approach to @login.required decorator
    if 'email' in session:
        return True
    else:
        return False

app.jinja_env.globals.update(session_check=session_check) # Required to enable calling this function from front-end jinja2


@app.route('/', methods = ['GET'])
def home():
    if request.args:
        section = request.args['section']
        return render_template('HomePage.html',section='')
    else:
        return render_template('HomePage.html')


@app.route('/contact-us')
def contactUs():
    return redirect(url_for('home', section='#contact'))

@app.route('/signup', methods = ['POST','GET'])
def signup():
    if request.method == 'POST':
        name = request.form['sign-up-name']
        email_id = request.form['sign-up-email']
        pswd = sha256_crypt.hash(str(request.form['sign-up-password']))
        now = datetime.now()
        if not validate_email(email_id,verify=True):
        #if False:
            flash('Email address does not exist!')
            return redirect(url_for('home'))

        c, conn = connection()
        c.execute("SELECT * FROM users WHERE email=%s;",tuple([email_id]))
        x = c.fetchall()
        if len(x) > 0:
            #modal_show = '<div class="modal fade show" id="login" tabindex="-1" role="dialog" aria-labelledby="loginLabel" style="display: block; padding-right: 17px;" aria-modal="true">'
            #right_panel_active = 'right-panel-active'
            flash('You already have an account!')
            return redirect(url_for('home'))
            #return render_template('home.html', modal_show = modal_show, right_panel_active = right_panel_active, \
            #    signupEmailFeedback = 'is-invalid', signupEmailError="That username is already taken, please choose another")
        else:
            c.execute("INSERT INTO users (name, email, password, date_created, user_rank) VALUES (%s, %s, %s, %s, %s)",(name,email_id, pswd, datetime.now(), user))
            conn.commit()

            c.execute("SELECT * FROM users WHERE email=%s;",tuple([email_id]))
            togetuid = c.fetchall()

            c.close()
            conn.close()
            gc.collect()

            session['logged_in'] = True
            session['email'] = email_id
            session['name'] = name
            session['uid'] = togetuid[0][0]

            flash("Thanks for registering!")
            
            return redirect(url_for('uploadImage'))
    else:
        return redirect(url_for('home'))

@app.route('/login', methods = ['POST','GET'])
def login():
    if request.method == 'POST':
        email_id = request.form['sign-in-email']

        c, conn = connection()
        c.execute("SELECT * FROM users WHERE email=%s;",tuple([email_id]))
        x = c.fetchall()

        c.close()
        conn.close()
        gc.collect()

        if len(x) == 0:
            flash('Invalid username!')
            return redirect(url_for('home'))
        else:
            if sha256_crypt.verify(request.form['sign-in-password'], x[0][3]):

                session['logged_in'] = True
                session['email'] = email_id
                session['name'] = x[0][1]
                session['uid'] = x[0][0]

                flash('Welcome, '+session['name']+'! You are now logged in!')
                return redirect('/upload-image')

            else:

                flash('Login failed!')
                return redirect(url_for('home'))
            
    else:
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    if session_check:
        session.clear()
        flash('You\'re now logged out!')
    else:
        flash('You\'re already logged out!')
    return redirect(url_for('home'))

@app.route('/checksession')
def check_session():
    if session_check:
        return 'You\'re logged in as '+session['name']+'!'
    else:
        return 'You\'re not logged in!'

@app.route('/show-users')
def show_users():
    c, conn = connection()

    c.execute('SELECT name, email FROM users;')
    x = c.fetchall()
    for each in x:
        flash(str(each[0])+'&nbsp;&nbsp; - &nbsp;&nbsp;'+str(each[1]))
    return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(e):
    return 'Oops! Couldn\'t find that web page!'

@app.errorhandler(500)
def internal_server_error(e):
    return 'Sorry, something\'s up (actually, down) with our server! Try again later.'

@app.errorhandler(405)
def method_not_allowed(e):
    return 'Your methods are ugly. Stop messing with our website!'

@app.route('/test', methods = ['POST','GET'])
def test_home():
    if request.method == 'POST':
        email_id = request.form['email']
        smtp_server_validity = ''
        email_validity = ''
        if validate_email(email_id, check_mx = True):
            smtp_server_validity += 'SMTP Server Exists!'
            flash(smtp_server_validity)
        if validate_email(email_id,verify=True):
            email_validity += 'Congratulations! Email address exists!'
            flash(email_validity)
        else:
            email_validity += 'Pooh! That email address does not exist.'
            flash(email_validity)
        return redirect(url_for('home'))
        #return render_template('home.html', email_id = ("Email id: "+email_id), smtp_server_validity = smtp_server_validity, email_validity = email_validity)
    return render_template('home.html')

app.config['IMAGE_UPLOADS'] = "C://Users//Snigdha//Desktop//Comp Project//finalApp//static//img//uploads"
app.config['ALLOWED_IMAGE_EXTENSIONS']  = ['PNG','JPG','JPEG']

def allowed_image(filename):

    if "." not in filename:
        return False
    extension = filename.rsplit('.',1)[1]
    if extension.upper() in app.config['ALLOWED_IMAGE_EXTENSIONS']:
        return True
    else:
        return False


@app.route('/upload-image', methods = ["POST","GET"])
def uploadImage():
    if session_check():
        if request.method == "POST":

            uploadTime = datetime.now()
            if request.files:

                if not request.files['image']:
                    return redirect(request.url)
                    

                if not allowed_image(request.files['image'].filename):
                    flash("File type not allowed!")
                    return redirect(request.url)

                else:

                    image = request.files['image']
                    img = Image.open(request.files['image']).convert('RGB')                   

                    if is_greyscale(img):
                        filename = secure_filename(image.filename)
                        extension = filename.rsplit('.',1)[1]
                        filename = "image" + '.' + extension
                        foldername = str(uploadTime.strftime("%Y_%m_%d_%H_%M_%S_%f"))+"_"+str(session['uid'])
                        
                        os.mkdir(os.path.join(app.config['IMAGE_UPLOADS'],foldername))

                        image.stream.seek(0)
                        image.save(os.path.join(app.config['IMAGE_UPLOADS'],foldername,filename))
###########
                        if is_xray(os.path.join(app.config['IMAGE_UPLOADS'],foldername,filename)):

                            print(os.path.join(app.config['IMAGE_UPLOADS'],foldername))
                            output, prob = outputNetwork(os.path.join(app.config['IMAGE_UPLOADS'],foldername)+'/')
                            #color=""
                            prob = round(prob,4)
                            if prob>=0.8:
                                color="#8b0000"
                            elif prob>=0.6:
                                color="#c23a3a"
                            elif prob>=0.4:
                                color="#b18f33"
                            elif prob>=0.2:
                                color="#a9c23a"
                            else:
                                color="#77c23a"
                            session['outputColor']=color
                            session['inputImage'] = "../static/img/uploads" + '/' + foldername+'/' + filename

                            session['outputImage'] = "../static/img/uploads" + '/' + foldername+'/' + '0.png'

                            if output == 1:
                                session['output'] = True
                            else:
                                session['output'] = False
                            
                            session['fractureProbability'] = prob

                            return redirect(url_for('resultsPage'))
                            #return render_template("use-page.html", filename=filename, imagepath=os.path.join(app.config['IMAGE_UPLOADS'],filename))
                        else:
                            flash('Image must be an X-Ray Image!')
                            os.remove(os.path.join(app.config['IMAGE_UPLOADS'],foldername,filename))
                            os.rmdir(os.path.join(app.config['IMAGE_UPLOADS'],foldername))

                            return redirect(request.url)
#######
                    else:
                        flash('Image must be in grayscale.')
                        return redirect(request.url)

        return render_template("use-page.html")
    else:
        flash("You need to log in!")
        return redirect(url_for("home"))

def fetchUploadedImages(uid):
    root = app.config['IMAGE_UPLOADS']
    paths = list()

    # Find full paths of all images in uploads directory
    for root,direct,files in os.walk(root):
        for f in files:
            if f!='image.png':
                continue
            paths.append(os.path.join(root,f))
    
    uidpaths = list()

    # Iterate through all images paths to check for user id and image extension uploaded
    for path in paths:
        uidpath = int(path.rsplit("_",1)[1].split("\\",1)[0])   # Retrieve uid from folder name
        extension = path.rsplit(".",1)[1]                       # Find file extension - JPG/PNG/JPEG
        
        # Show only those images for the particular user
        if uid == uidpath:
            # Reduce image path to short relative to templates directory for url to front end
            finalPath = "../static" + path.split("static",1)[1] 

            # Avoid escape sequences
            finalPath = finalPath.replace("\\","/")
            uidpaths.append(finalPath)
    
    # Return only valid image URLs for current user session['uid']
    return uidpaths


@app.route('/previous-uploads')
def previousUploads():
    if session_check():

        return render_template('previousUploads.html', uploads = fetchUploadedImages(session['uid']))
    else:
        flash('You need to log in!')
        return redirect(url_for("home"))

@app.route('/results')
def  resultsPage():
    if session_check():
        if 'outputImage' in session:
            return render_template('results.html', inputImage=session['inputImage'], \
                outputImage=session['outputImage'], output = session['output'], fractureProbability = session['fractureProbability'], outputColor=session['outputColor'])
        else:
            return render_template('results.html')
    else:
        flash('You need to log in!')
        return redirect(url_for('home'))

@app.route('/feedback')
def feedbackPage():
    if session_check():
        return 'Feedback Page'
    else:
        flash('You need to log in!')
        return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)