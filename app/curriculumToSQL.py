# Arrange Tibame CEB102 Curriculum to MySQL
# 2021/02/01
# Author: 蘇彥庭
import json
import pandas as pd
from sqlalchemy import create_engine

print('Status: Start Program!')

# read private configures json
secretFile = json.load(open('secretFile.json', 'r', encoding='utf-8'))

print('Status: Read and clean raw curriculum.')

# generate sheet name (months)
sheetNameList = [str((11000+i)/100) for i in range(2, 6)]

# for each sheets
# sheetName = sheetNameList[0]
outputDf = pd.DataFrame()
for sheetName in sheetNameList:

    # read excel sheet contents
    classInfo = pd.read_excel(open('第42期(CEB102)課表 .xlsx', 'rb'), sheet_name=sheetName, usecols='A:H', nrows=21)

    # normal form the curriculum
    # up to 5 weeks per month, every 4 rows represent a week curriculum
    iOutputDf = pd.DataFrame()
    for i in range(5):
        iClassInfo = classInfo.iloc[(i * 4 + 1):(i * 4 + 4), :]
        iClassInfo.columns = ['period'] + classInfo.iloc[(i * 4), 1:].to_list()
        iClassInfo = iClassInfo.melt(id_vars='period', var_name='date', value_name='className')
        iClassInfo = iClassInfo.dropna()
        iClassInfo.className = iClassInfo.className.str.replace('\n', '-').str.strip()
        iOutputDf = pd.concat([iOutputDf, iClassInfo])

    # remove vacation event
    iOutputDf = iOutputDf[~iOutputDf.className.str.contains('假|結訓')]

    # add date columns
    sheetYear = int(sheetName.split(".")[0]) + 1911
    sheetMonth = int(sheetName.split(".")[1])
    iOutputDf = iOutputDf.assign(dates=pd.to_datetime((sheetYear*10000 + sheetMonth*100 +
                                                       iOutputDf.date.astype(int)), format='%Y%m%d'))
    iOutputDf = iOutputDf[['dates', 'period', 'className']]

    # save output
    outputDf = pd.concat([outputDf, iOutputDf])

print('Status: Generate classroom journal principal table.')

# person in charge of teaching log
# student name list
studentNameList = secretFile['studentNameList']
# principal start site in studentNameList
iStudent = 1
# date list
dateList = pd.unique(outputDf['dates'])

principalDf = pd.DataFrame()
for i in range(len(dateList)):

    # check whether there have classes in this date
    iPrincipalDf = outputDf[(outputDf['dates'] == dateList[i]) & (~outputDf['className'].str.contains('專題|輔導'))]
    # if have class, assign the student to be principal
    if len(iPrincipalDf) > 0:

        iPrincipalDf = iPrincipalDf.assign(principal=studentNameList[iStudent])
        iPrincipalDf = iPrincipalDf[['dates', 'period', 'principal']]
        principalDf = pd.concat([principalDf, iPrincipalDf])

        # next student
        iStudent += 1
        # handle out of range
        if iStudent == len(studentNameList):
            iStudent = 0

print('Status: Join class info table and classroom journal principal table.')

# principalDf left join to outputDf with dates column
outputDf = outputDf.merge(principalDf, on=['dates', 'period'], how='left')

# # check data
# outputDf.to_csv('check_data.csv')

print('Status: Import output data to MySQL.')

# import data to mysql
dbHost = secretFile['host']
dbUser = secretFile['user']
dbPassword = secretFile['password']
dbPort = secretFile['port']
dbName = secretFile['dbName']
engine = create_engine('mysql+mysqlconnector://' + dbUser + ':' + dbPassword + '@' +
                       dbHost + ':' + dbPort + '/' + dbName)
conn = engine.connect()
outputDf.to_sql('curriculum', conn, index=False, if_exists='replace')
conn.close()
engine.dispose()

print('Finish!')
