import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dash_table.Format import Format, Group, Scheme
import dash.dash_table.FormatTemplate as FormatTemplate
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import pyarrow
import fastparquet
from tabs import tab1, tab2, tab3

# App
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.FLATLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
app.title="DB1B Data"
server = app.server

# Data
path = 'https://raw.githubusercontent.com/garycl/AirportData/master'
df_airports = pd.read_parquet(f'{path}/data/NPIAS_Airports.parquet')
df_airports = df_airports[df_airports['SvcLvl_FY23']=='P'].sort_values(by='LocID')
airport_options = [
    {"label": str(df_airports.loc[df_airports.LocID==airport,'LocID'].values[0]), "value": str(airport)}
    for airport in df_airports['LocID']
]

variables = [
    'PAX','FaredPAX',
    'MktFare', 'MktMilesFlown', 
    'PWMktFare', 'PWMktMilesFlown', 
    'FareYield', 'PWFareYield',
    'AvgFare'
]

# App set-up
app=dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.FLATLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}],
    suppress_callback_exceptions=True
)
app.title="Airpprt Data"
server=app.server

# Sidebar Style
SIDEBAR_STYLE={
    'position': 'fixed',
    'top': 0,
    'left': 0,
    'bottom': 0,
    'width': '20%',
    'padding': '20px 10px',
    'background-color': '#f8f9fa'
}

# Content Style
CONTENT_STYLE={
    'float':'left',
    'margin-left':'5%',
    'margin-right':'5%',
    'top': 0,
    'padding': '20px 10px'
}

tab_style = {
    'background-color': '#f8f9fa',
    'border-color':'#1b9e77',
    #'text-transform': 'uppercase',
    'font-size': '24px',
    'font-weight': 600,
    'align-items': 'center',
    'padding':'40px'
}

tab_selected_style = {
    'border-color':'#1b9e77',
    'color':'#1b9e77',
    #'text-transform': 'uppercase',
    'font-size': '24px',
    'font-weight': 2000,
    'align-items': 'center',
    'padding':'40px'
}

controls=dbc.Col([
    html.Br(),
    html.Br(),
    html.P('Select Start Year', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='start_year',
        value=None,
        options=[{"label":str(i),"value":str(i)} for i in range(1993,2023,1)]
    ),
    html.Br(),
    html.P('Select End Year', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='end_year',
        value=None,
        options=[{"label":str(i),"value":str(i)} for i in range(1993,2023,1)]
    ),
    html.Br(),
    html.P('Select Airports', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='origin_dropdown',
        value=None,
        multi=True,
        options=airport_options
    ),
    html.Br(),
    html.P('Frequency', style={'textAlign': 'center'}),
    dcc.RadioItems(
        id='time_radio',
        options = [dict(label = 'Quarter', value = 'Quarter'),
                 dict(label = 'Annual', value = 'Annual')],
        value='Quarter',
        style={'textAlign': 'center'},
    ),
    html.Button('Submit', id='button'),
]),

sidebar=html.Div(
    controls,
    style=SIDEBAR_STYLE
)
content=html.Div(
    [
        html.Br(),
        html.Div(id="table-1")
    ],
    style=CONTENT_STYLE
)

# Describe the layout/ UI of the app
app.layout=html.Div(
    [
        dcc.Tabs(
            id="tabs", 
            value='tab-1', 
            children=[
                dcc.Tab(label='Fare & Yields', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Origin & Destination', value='tab-2', style=tab_style, selected_style=tab_selected_style),
                dcc.Tab(label='Top O&D', value='tab-3', style=tab_style, selected_style=tab_selected_style),
            ]
        ),
        html.Div(id='tabs-content'),
        html.Div(
            dbc.Row([
                dbc.Col(sidebar, md=1), 
                dbc.Col(content, md=3)
            ])
        )

    ],
    style={'margin-left': '20%'}
)

@app.callback(
    Output('tabs-content', 'children'),
    [
        Input('tabs', 'value'),
        Input('button', 'n_clicks'),
        State('start_year', 'value'),
        State('end_year', 'value'),
        State('origin_dropdown', 'value'),
        State('time_radio', 'value'),
    ]
)
def render_content(tab, button, start_year, end_year, origin, time):
    if tab == 'tab-1':
        return tab1.create_layout(button, start_year, end_year, origin, time)
    elif tab=='tab-2':
        return tab2.create_layout(button, start_year, end_year, origin, time)
    elif tab=='tab-3':
        return tab3.create_layout(button, start_year, end_year, origin, time)

if __name__ == '__main__':
    app.run_server(debug=True)
