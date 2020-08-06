import numpy as np
import pandas as pd
import datetime as dt
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import pymysql
from darts import TimeSeries
from darts.models import AutoARIMA
from darts.models import NaiveDrift
# Change to multi-model where if <30 days, use naive_drift, naive_mean, or RegressionModel
#   If > 30 days, allow to choose AutoARIMA or others

global glModel, glWeightDB
glSqlCursor = None
sqlEngine       = create_engine('mysql+pymysql://root:adminadmin@127.0.0.1:3306/date_weight_pairs', echo=False)
try:
    glWeightDB    = sqlEngine.connect()
except:
    print("ERROR: Couldn't connect to database")
'''glWeightDB = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    passwd="adminadmin",
    database="date_weight_pairs"
)'''
#todaysDate = dt.date(2020, 9, 3) # Use this for debugging
todaysDate = dt.date.today()

''' Notes on using SQL Alchemy and the pandas .to_sql command:

    It seems to be common in pandas to just use a default index column. The pandas index is treated as the SQL key.
    So that's like saying we'll just juse a default, autoincrement PK. When designing SQL tables,
    that's not always the case. It's common to use a specific, unique value like transaction ID, username, etc.
    There's likely to be some significance to the PK so a simple AUTO_INCREMENT on the PK column isn't sufficient.
    If that's the case, where we're setting specific values for the PK, then we need to make sure pandas is treating
    the corresponding column as the index and not using an auto generated index column. Also, make sure that index=True
    when calling .to_sql

    This also brings up an interesting case with composite PKs. Say we have 3 columns in our PK. Only pandas > 1.0+ have
    multi-index capability (I think). Not sure how this would work. Might be interesting to try. If it doesn't work, then
    would have to manually create the SQL string and use SQL Alchemy's .execute command. That also leads to the question,
    "If I'm just going to use .execute, when not just use pymysql? Or the MySQL python connector?"
'''
def sqlStoreWeight(currentDateObj, weight):
    # Check if this date already exits in DB. If yes, switch to UPDATE (which also means don't use to_sql, since that would overwrite the whole table
    # If just using INSERT, this would be a PK error
    tempDateStr = currentDateObj.strftime('%Y-%m-%d')
    tempDF = pd.DataFrame({'date':tempDateStr, 'weight':weight}, index=[0]) # If only passing scalars, have to specify an index value
                                                                            # Index takes an array-like, so can't just use 'date'
                                                                            # Specifying the date value will result in that value
                                                                            # for both the index and the 'date' column. Easiest to
                                                                            # just give a dummy array value like [0]
    tempDF.set_index('date', inplace=True)

    try:
        #tempDF.to_sql('dateweighttable', glWeightDB,if_exists='append', index=True)
        if sqlCheckDateExists(currentDateObj):
            sqlStr = "UPDATE dateweighttable SET weight = {} WHERE date = \'{}\'".format(weight, currentDateObj.strftime('%Y-%m-%d'))
        else:
            sqlStr = "INSERT INTO dateweighttable (date, weight) VALUES (\'{}\', {})".format(currentDateObj.strftime('%Y-%m-%d'), weight) 
        glWeightDB.execute(sqlStr)
    except:
        print("ERROR: writing date and weight data to database")
        if ValueError:
            print("ERROR: ValueError writing date and weight data to database")
    return

#@st.cache
def sqlGetWeightsDF():
    sqlDF = pd.read_sql_table('dateweighttable', glWeightDB, columns=['date', 'weight'])
    return sqlDF

def sqlCheckDateExists(dateObj):
    sqlStr = "SELECT date FROM date_weight_pairs.dateweighttable WHERE date = \'{}\'".format(dateObj.strftime('%Y-%m-%d'))
    response = glWeightDB.execute(sqlStr)
    if response.rowcount == 0:
        return False
    else:
        return True

#@st.cache
def trainTheModel(training_data):
    glModel.fit(training_data)
    print("Training...")
    return

#@st.cache
def predict_next(days=3):
    next3days = glModel.predict(days)
    print("Predicting...")
    return next3days.pd_dataframe()

st.title("Weight Prediction App")
st.write("""
No magic here, just looking for trends and cycles in an individual's body weight.
The app will allow no more than one weight value per day.
""")

st.write("""
*Today's Date:*
""", todaysDate.strftime('%m-%d-%Y'))

st.selectbox("Who's weight are we working with?",('Wade', 'Larry', 'Mo', 'Curly'),0)

weight = st.number_input("Today's weight:", min_value=50.0, max_value=750.0, format="%4.1f", step=.1)
st.write("Echoing weight: ", weight)

sqlStoreWeight(todaysDate,weight)
#weightsDF = pd.DataFrame({'date':['7-17-2020','7-18-2020','7-19-2020','7-20-2020','7-21-2020','7-22-2020'],
#                          'weight':[170.8, 170.4, 170.8, 170.6, 170.6, 745]})
weightsDF = sqlGetWeightsDF() # Would passing todaysEXPTDate here be helpful?
if weightsDF.date.size > 30:  # Remember, size is rows*cols, so just get the size of a series or the index of the DF
    glModel = AutoARIMA()
else:
    glModel = NaiveDrift()

series = TimeSeries.from_dataframe(weightsDF, time_col='date', value_cols='weight')

train, val = series.split_after(pd.Timestamp(todaysDate - dt.timedelta(days=3)))

trainTheModel(train)

next3daysDF = predict_next(4)
print(next3daysDF[0])

plotYmax = weightsDF['weight'].max() + 0.5
plotYmin = weightsDF['weight'].min() - 0.5
weightMarker = go.scatter.Marker(symbol="circle", size=8, color='blue')
# Super simple chart, very minimal customization options
#st.line_chart(weightsDF.weight)
# Plotly Express is better, but can't currently add markers to the line
weightFig = px.line(weightsDF, x='date', y='weight', title="Past and Predicted Weights", range_y=[plotYmin, plotYmax])
weightFig.add_scatter(x=weightsDF['date'], y=weightsDF['weight'], mode='markers', marker=weightMarker, name="Actual")
weightFig.add_scatter(x=next3daysDF.index, y=next3daysDF[0], name="Predicted")
weightFig.update_layout(showlegend=True)
# So move on the full Plotly Graph Objects
st.plotly_chart(weightFig, use_container_width = False)
#outputStr = "*Based on data from the last {} days, omorrow's weight is expected to be: {}*".format(weightsDF.date.size, next3daysDF[0][3])
st.write("*Based on data from the last {} days, tomorrow's weight is expected to be: {:4.1f}*".format(weightsDF.date.size, next3daysDF[0][3]))


'''
TODO: Handle time when days are between 1-3 and 3-6 (need to adjust # days in validation trace)
TODO: Add multi-user support
TODO: Limit number of days on the graph (x-axis) to... 30? 45?
TODO: Store previous predictions in DB, plot them, and calculate an MSE or something similar
TODO: SQL errors should be handled and sent to the app so the user can report them
TODO: Pull default weight from SQL so the current 50 default doesn't show up in another browser or during refresh. 50 should only occur when no weight has ever been entered
'''
