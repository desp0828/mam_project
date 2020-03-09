import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pyodbc

app = dash.Dash()
server = app.server


server = 'server_name/ip'
username = 'your_username'
database = 'database_name/ip'
password = 'your_password'
driver= '{ODBC Driver 17 for SQL Server}'
conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = conn.cursor()
#connect to database
cursor.execute('SELECT DISTINCT ISIN FROM mam ORDER BY ISIN')
#get all ISINs and used for shown in dropdown
row = cursor.fetchall()
ISINs=[]
for item in row:
    tmp=item
    ISINs.append(tmp[0])

head=html.H1(children='Hello Dash')

indicators=html.Div(children='''
        This is Dash running on Azure App Service without a Docker container.
    ''')
#web layout
app.layout = html.Div([
    html.Div([
        head,
        indicators,
        html.Label('ISIN'),
        html.Div([
            dcc.Dropdown(
                id='dropdown1',
                options=[{'label': i, 'value': i} for i in ISINs]
            ),
        ]),
    ]),
    html.Div([
         dcc.Graph(id='timeseries')
    ])
])

#callback function, will run after each click on the dropdown
@app.callback(
    dash.dependencies.Output('timeseries', 'figure'),
    [dash.dependencies.Input('dropdown1','value')]
)
#read date and INR of corresponding ISIN, save them in x and y array.
def update_timeseries(value_isin):
    cursor.execute('SELECT Date,INR FROM mam WHERE ISIN = ?',value_isin)
    row = cursor.fetchall()
    date=[]
    inr=[]
    for item in row:
        date.append(item[0])
        inr.append(item[1])

    trace = go.Bar(
            x=date,
            y=inr
        )

    layout = go.Layout(margin=dict(l=20, r=20, t=0, b=30))
    fig = go.Figure(data=[trace], layout=layout)
    return fig


if __name__ == '__main__':
    app.run_server(host='0.0.0.0',debug=True)#only set host to 0.0.0.0, it can receive all the requirements

