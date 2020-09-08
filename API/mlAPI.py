"""****************************************************************************************************
* REST API to make predictions over email analisys
* Version: 1.0
* Date: 30/06/2020
****************************************************************************************************"""

from flask import Flask, request, abort
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import connections as cn
import emailClassification
from emailClassification import AnalyzedMail
import emailClassification
import json
import re
import os


app = Flask(__name__)
api = Api(app, prefix="/v1")
auth = HTTPBasicAuth()



@auth.verify_password
def verify(username, password):
	"""
	Basic authentication implementation, verify user and password.

	Args:
		username(str): user name
		password(str): user password

	Returns:
		True if user and password are right
	Raises:
		mySqlException: an error occured accessing the database.
	"""
	verified = False
	if not (username and password):
		return verified
	else:
		conexion = None
		try:
			conexion = cn.dbConnectMySQL()
			mycursor = conexion.cursor()
			mycursor.execute("SELECT password FROM users WHERE username =" + "\'" + username + "\'")
			_password = mycursor.fetchone()

			mycursor.close()

			verified = (not (_password is None) and check_password_hash( _password[0],password))

		except cn.mySqlException as e:
			raise e
		finally:
			try:
				if conexion is not None:
					conexion.close()
			except cn.mySqlException as eCon:
				raise eCon
		return verified


class ping(Resource):
	#Authentication
	@auth.login_required

	def get(self):
		pass


class userManagement(Resource):
	"""
	User add API function

	Args:
		POST user: user name
		POST pwd: user password
		POST email: user email
		POST role: user role

	Returns:
		message that wants to raise

	Raises:
		mySqlException: an error occured accessing the database.
	"""
	#Authentication
	@auth.login_required

	def post(self):
		#Read post parameters
		user  = request.form['user']
		pwd = request.form['pwd']
		email = request.form['email']
		role = request.form.get('role')

		#Validate email
		if (not re.match('^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$',email.lower())):
			abort(400)

		#Validate role
		if (role) and (role not in ('admin', 'expert' , 'user')):
			abort(400)

		#Create the connection
		con = None
		try:
			conexion = cn.dbConnectMySQL()
			mycursor = conexion.cursor()

			#Validate admin permisions for the user
			mycursor.execute("SELECT Role FROM users WHERE username=" + "\'" + auth.username() + "\'")
			userRole = mycursor.fetchone()
			if userRole[0]== 'admin':

				#Check if the username exists in the database
				mycursor.execute("SELECT username from users WHERE username=" + "\'" + user + "\'")
				_userWithSameName = mycursor.fetchone()

				if (not _userWithSameName):

					#Create the user in the database
					if (role):
						mycursor.execute("INSERT INTO users (username, password, email, role) VALUES ("+"\'"+user+"\',"+"\'"+generate_password_hash(pwd)+"\',"+"\'"+email+"\',"+"\'"+role+"\')")
					else:
						mycursor.execute("INSERT INTO users (username, password, email) VALUES ("+"\'"+user+"\',"+"\'"+generate_password_hash(pwd)+"\',"+"\'"+email+"\')")
					conexion.commit()

					#Return response
					app.logger.info(f'User {user} added to the database')
					return {'message': 'User added to the database'}

				else:
					abort(400,"There is already an username with this name in the database")
			else:
				abort(401)
			mycursor.close()

		except cn.mySqlException as e:
			try:
				if not (con is None):
					con.rollback()
				app.logger.exception('mySQL Exception', e)
				abort(500)
			except cn.mySqlException as eRoll:
				app.logger.exception('mySQL Exception', e)
				abort(500)
		finally:
			try:
				if not (con is None):
					con.close()
			except mySqlException as eCon:
				app.logger.exception('Unable to close connection to the database', e2)



class emailAnalyze(Resource):
        """Class to analyze email with API.

        Args:
            POST texto: full EML text to analyze.

        Returns:
            analyzed_email json.

        Raises:
            mySqlException: an error occured accessing the database.
        """
        #Authentication
        @auth.login_required

        def post(self):
                #Read post parameters
                content = request.form['texto']

                try:
                    conexion = cn.dbConnectMySQL()
                    mycursor = conexion.cursor()

                    analyzed_email = AnalyzedMail(content, 0) #mode 0 EML with headers required 

                    texto = analyzed_email.getText()
                    texto = texto.replace("'","")
                    texto = texto.replace('\"','')
                    varfrom = analyzed_email.getFrom()
                    to = analyzed_email.getTo()
                    subject = analyzed_email.getSubject()
                    user = auth.username()

                    query1 = "INSERT INTO email (username, mainText, sender, receiver, subject) VALUES ('" + user + "','" + texto + "','" + str(varfrom[1]) + "','" + str(to[1]) + "','" + subject + "')"
                    mycursor.execute(query1)
                    query2 = "SELECT max(id_email) from email"
                    mycursor.execute(query2)
                    idemail = mycursor.fetchone()
                    query3 = "INSERT INTO predictions (username, id_email, is_phishing, department, score) VALUES ('" + user + "'," + str(idemail[0])  +  "," + str(analyzed_email.getPhish())  + ",'" + analyzed_email.getDpto() +"'," + str(analyzed_email.getProb()) + ")"

                    mycursor.execute(query3)
                    conexion.commit()

                    y = json.dumps(vars(analyzed_email))

                    return({'analyzed_mail':vars(analyzed_email)})
                except cn.mySqlException as e:
                        raise e
                finally:
                        try:
                                if conexion is not None:
                                        conexion.close()
                        except cn.mySqlException as eCon:
                                raise eCon


class emailAnalyzeTxt(Resource):
    """Class to analyze text with API.

    Args:
        POST texto: text to analyze.

    Returns:
        text to raise

    Raises:
        mySqlException: an error occured accessing the database.
    """
    #Authentication
    @auth.login_required

    def post(self):
        #Read post parameters
        texto  = request.form['texto']

        try:
            conexion = cn.dbConnectMySQL()
            mycursor = conexion.cursor()
            analyzed_email = AnalyzedMail(texto, 1) # mode 1 only text

            texto = texto.replace("'","")
            texto = texto.replace('\"','')
            mycursor.execute("INSERT INTO email (username, mainText) VALUES ('" + auth.username() + "','" + texto + "')")
            mycursor.execute("SELECT max(id_email) from email")
            idemail = mycursor.fetchone()
            query3 = "INSERT INTO predictions (username, id_email, is_phishing, department, score) VALUES ('" + auth.username() + "'," + str(idemail[0]) +", '0','" + analyzed_email.getDpto()  + "'," + str(analyzed_email.getProb()) + ")"

            mycursor.execute(query3)
            conexion.commit()

            return("<b>Text analyzed:</b> " + texto +  " </br><b>Department:</b> " + analyzed_email.getDpto() + "</br> <b>Probability: </b>" +  str(analyzed_email.getProb())) 
        except cn.mySqlException as e:
            raise e
        finally:
            try:
                if conexion is not None:
                    conexion.close()
            except cn.mySqlException as eCon:
                raise eCon



class phishing(Resource):
	"""Class to get phishing URLs or add one.

	Args:
		POST texto: URL that shoud be considered phishing

	Returns:
		text to raise

	Raises:
		mySqlException: an error occured accessing the database.
	"""
    #Authentication
	@auth.login_required

	def post(self):
		#Read post parameters
		texto  = request.form['texto']

		try:
				conexion = cn.dbConnectMySQL()
				mycursor = conexion.cursor()

				mycursor.execute("SELECT Role FROM users WHERE username=" + "\'" + auth.username() + "\'")
				userRole = mycursor.fetchone()

				if userRole[0] not in ('admin', 'expert'):
					return("<p style='color:red'>User has not enough permisions to add URLs</p>")
				else :


					url = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2})).*', texto)
					if(len(url)==0):
					  return("<p style='color:red'>URL not detected</p>")
					elif(len(url)>1 ):
					  return("<p style='color:red'>More than 1 URL given, introduce URLs one by one</p>")
					else:
						mycursor.execute("INSERT INTO phishing (site_url, username) VALUES ('" + url[0] + "', '" + auth.username()  + "')")

						conexion.commit()

						return("<p style='color:green'>URL added to phishing database</p>")

		except cn.mySqlException as e:
				raise e
		finally:
				try:
						if conexion is not None:
								conexion.close()
				except cn.mySqlException as eCon:
						raise eCon


	def get(self):
		#Select the URLs considered phishing
		try:
			conexion = cn.dbConnectMySQL()
			mycursor = conexion.cursor()

			mycursor.execute("SELECT site_url, date_added from phishing WHERE date_added >= NOW() - INTERVAL 60 DAY")
			list = mycursor.fetchall()

			#Build a JSON with phishing info, datetime is not JSON serializable, parsed handly
			strlist = []
			stritem = [" "," "]
			for item in list:
				stritem[0] = item[0]
				stritem[1] = item[1].strftime("%d %m %Y, %H:%M:%S")
				strlist.append(stritem)
				stritem = [" "," "]
			return {'list':strlist}

		except cn.mySqlException as err:
			raise err
		finally:
			try:
				if conexion is not None:
				   conexion.close()
			except cn.mySqlException as eCon:
				raise eCon



class check(Resource):
	"""Class to check predictions as roght or wrong.

	Args:
		POST eval: right or wrong, as user has marked the prediction
		POST idpred: the id of the prediction that is beening rewiewed

	Returns:
		text to raise

	Raises:
		mySqlException: an error occured accessing the database.
	"""
	#Authentication
	@auth.login_required

	def post(self):
		try:
			conexion = cn.dbConnectMySQL()
			mycursor = conexion.cursor()
			mycursor.execute("SELECT Role FROM users WHERE username=" + "\'" + auth.username() + "\'")
			userRole = mycursor.fetchone()

			if userRole[0] not in ('admin', 'expert'):
				return("<p style='color:red'>User has not enough permisions to correct predictions</p>")
			else :
				#Read post parameters
				eval  = request.form['eval']
				idpred = request.form['idpred']

				query1 = "UPDATE predictions SET checked = '" +  str(eval) + "' WHERE id_prediction =  '"+ str(idpred) + "'"
				mycursor.execute(query1) 
				conexion.commit()
				return("Updated prediction")

		except cn.mySqlException as e:
			raise e
		finally:
			try:
				if conexion is not None:
					conexion.close()
			except cn.mySqlException as eCon:
				raise eCon

	def get(self):
		try:
			conexion = cn.dbConnectMySQL()
			mycursor = conexion.cursor()

			mycursor.execute("SELECT p.id_prediction, p.id_email, p.department, p.score, e.mainText FROM `predictions` AS p INNER JOIN `email` AS e USING (id_email) WHERE (p.checked is null) LIMIT 1")
			list = mycursor.fetchone()
			if (list == None):
				msg = ["No predictions unchecked left"]
				return  {'list': msg}
			return {'list':list}

		except cn.mySqlException as err:
			raise err
		finally:
			try:
				if conexion is not None:
				   conexion.close()
			except cn.mySqlException as eCon:
				raise eCon

"""****************************************************************************************************
* Methods definition
****************************************************************************************************"""
api.add_resource(userManagement,'/users')
api.add_resource(ping,'/ping')
api.add_resource(emailAnalyze,'/email')
api.add_resource(emailAnalyzeTxt,'/emailtxt')
api.add_resource(phishing,'/phishing')
api.add_resource(check,'/check')

if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)

