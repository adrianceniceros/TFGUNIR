"""****************************************************************************************************
* Functions that define the connection of the database
* Version: 0
* Date: 18/11/2019
****************************************************************************************************"""
import configparser
from mysql.connector import connect as mySQLConnect
from mysql.connector import Error as mySqlException

"""****************************************************************************************************
* Description: method to create a conexion to a MySQL database 
* INPUT: -
* OUTPUT: a conexion object to the database
****************************************************************************************************"""
def dbConnectMySQL(user=None,pwd=None):
	try:
		config = configparser.SafeConfigParser()
		config.read('config.ini')
		server = str(config.get('MySQLDatabase','Server'))
		db = str(config.get('MySQLDatabase','Database'))
		if(user is None or pwd is None):
			user = str(config.get('MySQLDatabase','User'))
			pwd = str(config.get('MySQLDatabase','Password'))

		return mySQLConnect(host = server, database = db, user = user, password = pwd)
	except mySQLException as e:
		raise e

