funcName = "moveSavechart_from_db_to_s3_function"
try:
	import MySQLdb
	import boto3
	import sys
	import pdb
except:
	print "ERR : %s : %s : %s" % (moduleName, "Could not import a module", e)

sys.path.insert(0,"/home/user/fyers_code/fyers_repositories/fy_datafeed_rest_django/fy_trade/fy_config/")

from fy_connections_defines import *
from fy_data_and_trade_defines import *
from fy_common_internal_functions import *


# To connect to the database
def connectDatabase():
	db = MySQLdb.connect("localhost","root","","fyers_trading_bridge")
	cursor = db.cursor()
	return db, cursor

# To put data taken from DB in s3
def putDataIns3(userData):
	# pdb.set_trace()
	s3cient = boto3.client("s3")

	for path, data in userData.items():
		# print("data is : %s"%(data))
		# print("path is : %s"%(path))
		if data == None:
			continue
		try:
			putResponse = s3cient.put_object(
				Body = data,
				Bucket = AWS_S3_BUCKET_NAME_USER_DATA_CHARTS,
				Key = path
			)
			if "ETag" in putResponse:
				if putResponse["ETag"] != '' or putResponse["ETag"] != None:
					if putResponse["ResponseMetadata"]["HTTPStatusCode"] == 200:
						pass
					else:
						return [ERROR_C_1, path, putResponse["ResponseMetadata"]["HTTPStatusCode"]]
				else:
					return [ERROR_C_1, path, "ETag: empty/None"]
			else:
				return [ERROR_C_1, path, "ETag: not found"]	
		except Exception, e:
			logEntryFunc(LOG_STATUS_ERROR_1, funcName, e)
			return [ERROR_C_1, funcName, "Unknown Error"]
		
		
# To take data from db and defining the path in s3 for each data
def insertIntos3():
	db, cursor = None, None
	try:
		db, cursor = connectDatabase()
	except Exception, e:
		logEntryFunc(LOG_STATUS_ERROR_1, funcName, "db fail", e)
	try:
		query = "SELECT * FROM save_chart_layout LIMIT 5"
		cursor.execute(query)
		result = cursor.fetchall()
	except:
		logEntryFunc(LOG_STATUS_ERROR_1, funcName, "Exception", e)
	# print(result)
	# pdb.set_trace()
	for data in result:
		userData = {
			"%s/%s/%s-%s-web.txt"%(AWS_S3_FOLDER_PATH_USER_DATA_CHARTS, data[0], data[0], AWS_S3_K_SAVECHART_FILE_VALUE)        : data[1],   # userTestData/fyID/fyID-9001-web.txt
			"%s/%s/%s-%s-template.txt"%(AWS_S3_FOLDER_PATH_USER_DATA_CHARTS, data[0], data[0], AWS_S3_K_SAVECHART_FILE_VALUE)   : data[2],   # userTestData/fyID/fyID-9001-template.txt
			"%s/%s/%s-%s-mob.txt"%(AWS_S3_FOLDER_PATH_USER_DATA_CHARTS, data[0], data[0], AWS_S3_K_SAVECHART_FILE_VALUE)        : data[3]    # userTestData/fyID/fyID-9001-mob.txt
		}
		# print("data[0] is: %s"%(data[0]))
		# print("data[1] is : %s"%(data[1])) 
		# print("type of data[1] is : %s"%(type(data[1]))) 
		# print("data[2] is : %s"%(data[2])) 
		# print("type of data[2] is : %s"%(type(data[2]))) 
		# print("data[3] is : %s"%(data[3])) 
		# print("type of data[3] is : %s"%(type(data[3]))) 
		# print("userData is %s"%(userData))
		putDataIns3(userData)

if __name__ == "__main__":
	insertIntos3()