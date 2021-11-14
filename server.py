
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""


#author: Wei He Dongbing


import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@34.74.246.148/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.74.246.148/proj1part2"
#
DATABASEURI = "postgresql://wh2509:8944@34.74.246.148/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#

#engine.execute("""CREATE TABLE IF NOT EXISTS test (
#  id serial,
#  name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


#DONT NOT CHANGE THIS
@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  #print(request.args)


  #
  # example of a database query
  #
  """
  cursor = g.conn.execute("SELECT name FROM Patient")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()
  """

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  """
  context = dict(data = names)
  """

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  ###return render_template("index.html", **context)
  return render_template("index.html")

@app.route('/prescription')
def prescription():

  return render_template("prescription.html")

@app.route('/patient')
def patient():

  return render_template("patient.html")

@app.route('/finddoctor')
def finddoctor():

  return render_template("finddoctor.html")

@app.route('/findhospitalmed')
def findhospitalmed():

  return render_template("findhospitalmed.html")


# Example of adding new patient data to the database
# cannot implement error!
@app.route('/add_patient', methods=['POST'])
def add_patient():
  error = ''
  pid = request.form['pid']
  name = request.form['name']
  age = request.form ['age']
  gender = request.form['gender']
  zip = request.form['zip']

  # check if the input is invalid
  if not pid:
    error = 'Please enter a valid patient id.  '
  if not name:
    error = error + 'Please enter your name.  '
  if not age :
    error = error+'Please enter a valid age.  '
  if gender != 'male' and gender != 'female' and gender != 'other':
    error = error+'Please select your gender.  '
  if not zip:
    error = error+'Please enter zip code.  '
  if error != '':
    return render_template("patient.html", error=error)

  # if input is not blank, change the type to match input
  pid=int(pid)
  age=int(age)
  zip=int(zip)

  # check if pid has been assigned
  exist = g.conn.execute('SELECT * FROM patient WHERE pid=%s', pid)
  if exist:
    error = 'Patient id already existed. Please check your pid.'

  if error == '':
    g.conn.execute('INSERT INTO patient(pid,name,age,gender,zip) VALUES (%s, %s, %s, %s, %s) ', pid,name,age,gender,zip)
    return redirect('/patient')
  else:
    return render_template("patient.html",error=error)


#function search for the patient's prescription
@app.route('/search_prescription', methods=['POST'])
def search_prescription():
  error=None
  pid = int(request.form['pid'])

  cursor = g.conn.execute("SELECT * FROM prescription_belongto_issue WHERE pid=%s", pid)
  prescription = []
  #additional=[]
  for result in cursor:
    prescription.append(result)
  cursor.close()
  context = dict(data=prescription)
  #check if any result in database
  if not prescription:
    error = 'No record is found'
    return render_template("prescription.html", error=error)
  else:
    return render_template("prescription.html", **context)



#function search for the patient's doctor
@app.route('/search_doctor', methods=['POST'])
def search_doctor():
  error=None
  pid = request.form['pid']
  case_id = request.form['case_id']
  if not pid:
    error = 'Please enter your patient ID.'
    return render_template("finddoctor.html", error=error)
  if not case_id:
    error = 'Please enter your case number.'
    return render_template("finddoctor.html", error=error)

  pid=int(pid)
  case_id=int(case_id)

  cursor = g.conn.execute("SELECT * FROM doctor_worksin d, hospital h where d.hid = h.hid and d.qid = (SELECT qid FROM prescription_belongto_issue WHERE pid=%s and case_id=%s)", pid,case_id)
  doctor = []
  #additional=[]
  for result in cursor:
    doctor.append(result)
  cursor.close()
  context = dict(data=doctor)
  #check if any result in database
  if not doctor:
    error = 'No record is found'
    return render_template("finddoctor.html", error=error)
  else:
    return render_template("finddoctor.html", **context)


#function search for the doctor by their type
@app.route('/search_doctor_type', methods=['POST'])
def search_doctor_type():
  error=None
  type = request.form['type']
  if not type:
    error = 'Please enter the type of doctor your are looking for.'
    return render_template("finddoctor.html", error=error)
  cursor = g.conn.execute("SELECT * FROM doctor_worksin d, hospital h  where d.hid=h.hid and d.type=%s", type)
  doctor = []
  #additional=[]
  for result in cursor:
    doctor.append(result)
  cursor.close()
  context = dict(data2=doctor)
  #check if any result in database
  if not doctor:
    error = 'No record is found'
    return render_template("finddoctor.html", error=error)
  else:
    return render_template("finddoctor.html", **context)



#function search for the nearest avalible hospital for medication purchasing
#with enough such medicine
@app.route('/search_near_med' , methods=['POST'])
def search_near_med():
  error = None
  drug_name = request.form['drug_name']
  amount = request.form['amount']
  zip = request.form['zip']
  if not drug_name:
    error = 'Please enter the medicine name you are looking for.'
    return render_template("findhospitalmed.html", error=error)
  if not amount:
    error = 'Please enter the amount of medicine you are looking for.'
    return render_template("findhospitalmed.html", error=error)
  if not zip:
    error = 'Please enter your zip code.'
    return render_template("findhospitalmed.html", error=error)

  cursor = g.conn.execute("SELECT h.hos_name,h.zip FROM medicine m, sell_in s ,hospital h  where m.med_name=%s and m.ndc=s.ndc and s.quantity>=%s and h.hid=s.hid ORDER BY ABS(%s-h.zip) ", drug_name,amount,zip)
  hospitalmed = []
  # additional=[]
  for result in cursor:
    hospitalmed.append(result)
  cursor.close()
  context = dict(data=hospitalmed)
  # check if any result in database
  if not hospitalmed:
    error = 'No record is found'
    return render_template("findhospitalmed.html", error=error)
  else:
    return render_template("findhospitalmed.html", **context)



#function to allow doctors to search for medicine by NDC and drug name
@app.route('/doctor_search_medicine', methods=['POST'])
def search_doctor_type():
  error=None
  ndc = request.form['ndc']
  drug_name = request.form['drug_name']
  if not drug_name:
    error = 'Please enter the medicine name you are looking for.'
    return render_template("doctorfindmed.html", error=error)
  if not ndc:
    error = 'Please enter the ndc of medicine you are looking for.'
    return render_template("doctorfindmed.html", error=error)

  cursor = g.conn.execute(
    "SELECT m.med_name,m.ndc, h.hos_name FROM medicine m, hospital h, sell_in s where m.med_name=%s and m.ndc=s.ndc and s.hid = h.hid",
    drug_name, ndc)
  ndcmed = []
  # additional=[]
  for result in cursor:
    ndcmed.append(result)
  cursor.close()
  context = dict(data=ndcmed)
  # check if any result in database
  if not ndcmed:
    error = 'No record is found'
    return render_template("doctorfindmed.html", error=error)
  else:
    return render_template("doctorfindmed.html", **context)


#function to allow doctors to search for medicine by NDC and drug name
@app.route('/doctor_search_patients', methods=['POST'])
def search_doctor_type():
  error=None
  pid = request.form['pid']
  if not pid:
    error = 'Please enter the perscription ID you are looking for.'
    return render_template("doctorfindpatient.html", error=error)

  cursor = g.conn.execute(
    "SELECT p.name,p.pid FROM patient p, doctor s, prescription_belongto_issue i where p.name=%s and p.pid=i.pid and i.qid = s.qid",
    pid)
  ndcmed = []
  # additional=[]
  for result in cursor:
    ndcmed.append(result)
  cursor.close()
  context = dict(data=ndcmed)
  # check if any result in database
  if not ndcmed:
    error = 'No record is found'
    return render_template("doctorfindmed.html", error=error)
  else:
    return render_template("doctorfindmed.html", **context)





#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")

"""
# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
  return redirect('/')
"""

#dont know the meaning of this
"""
@app.route('/login')
def login():
    abort(401)
    this_is_never_executed()
"""

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
