from constants import readMySQLConfigDataFromS3

readMySQLConfFilesData = readMySQLConfigDataFromS3()
CONNECTION_NAME = readMySQLConfFilesData['connect_name']
HOST = readMySQLConfFilesData['host']
PORT = readMySQLConfFilesData['port']
USERNAME = readMySQLConfFilesData['username']
PASSWORD = readMySQLConfFilesData['password']