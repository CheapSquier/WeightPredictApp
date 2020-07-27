import numpy as np
import pandas as pd
import datetime as dt
import streamlit as st
#import mysql.connector
#from mysql.connector import errorcode
#from darts import TimeSeries
#from darts.models import AutoARIMA
#from darts.models import NaiveDrift
# Change to multi-model where if <30 days, use naive_drift, naive_mean, or RegressionModel
#   If > 30 days, allow to choose AutoARIMA or others
#import <some kind of sql library

global glMODEL, glSqlCursor, glWeightDB
#glMODEL = NaiveDrift()
glSqlCursor = None
glWeightDB = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    passwd="adminadmin",
    database="date_weight_pairs"
)
todaysEXPTDate = dt.date(2020, 7, 30)

todaysDate = dt.date.today()

#These 2 imply hardcoding the server and database.
#Make those constants for now, maybe provide a user param later
#Maybe a DB object that stores server address, DB name, etc
def sqlStoreWeight(currentDate, weight):
    sqlCursor = glWeightDB.cursor(buffered=True)
    sql = "INSERT INTO dateWeightTable VALUES (%s, %s)"
    val = (currentDate, weight)
    sqlCursor.execute(sql, val)
    glWeightDB.commit()
    # With sendToSQLDB we got a return status. Will .commit() give that?
        #insertTableStr = "INSERT INTO " + self.TableName + " VALUES(" + str(listOfValues)[1:-1] + ");"
        #success = self.sendToSQLDB(insertTableStr, "Insert into SQL table")
        #return success
    return
#@st.cache
def sqlGetWeightsDF():
    sqlCursor = glWeightDB.cursor(buffered=True)
    sqlCursor.execute("SELECT * FROM dateWeightTable")
    sqlDF = pd.DataFrame(sqlCursor.fetchall())
    return sqlDF

#@st.cache
def trainTheModel(training_data):
    glMODEL.fit(training_data)
    print("Training...")
    return

#@st.cache
def predict_next(days=3):
    next3days = glMODEL.predict(days)
    print("Predicting...")
    return next3days.pd_dataframe()

st.write("""
# Weight Prediction App
No magic here, just looking for trends and cycles in an individual's body weight.
The app will allow no more than one weight value per day.
""")

st.write("""
*Today's Date:*
""", todaysDate.strftime('%m-%d-%Y'))

st.selectbox("Who's weight are we working with?",('Wade', 'Larry', 'Mo', 'Curly'),0)

weight = st.number_input("Today's weight:", min_value=50, max_value=750, format="%d")
st.write("Echoing weight: ", weight)

sqlStoreWeight(weight)
#weightsDF = pd.DataFrame({'date':['7-17-2020','7-18-2020','7-19-2020','7-20-2020','7-21-2020','7-22-2020'],
#                          'weight':[170.8, 170.4, 170.8, 170.6, 170.6, 745]})
weightsDF = sqlGetWeightsDF() # Would passing todaysEXPTDate here be helpful?

series = TimeSeries.from_dataframe(weightsDF, 'date', 'weight')

train, val = series.split_after(pd.Timestamp(todaysEXPTDate))

trainTheModel(train)

next3daysDF = predict_next(3)
print(next3daysDF[0])

totalPlotDF = weightsDF + next3daysDF
st.line_chart(weightsDF.weight)
st.write("*Tomorrows weight expected to be: *", next3daysDF[0][0])


