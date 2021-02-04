# Linebot keyword table
# 2021/02/02
# Author: 蘇彥庭
import json
import pandas as pd
from sqlalchemy import create_engine

# read private configures json
secretFile = json.load(open('secretFile.json', 'r', encoding='utf-8'))

# read linebot keyword table
keywordTable = pd.read_json('linebot_keyword.json', orient='index')
keywordTable = keywordTable.explode('keyword')
keywordTable['method'] = keywordTable.index
keywordTable = keywordTable[['method', 'keyword', 'msg']]

# import data to mysql
dbHost = secretFile['host']
dbUser = secretFile['user']
dbPassword = secretFile['password']
dbPort = secretFile['port']
dbName = secretFile['dbName']
engine = create_engine('mysql+mysqlconnector://' + dbUser + ':' + dbPassword + '@' +
                       dbHost + ':' + dbPort + '/' + dbName)
conn = engine.connect()
keywordTable.to_sql('keyword', conn, index=False, if_exists='replace')
conn.close()
engine.dispose()
