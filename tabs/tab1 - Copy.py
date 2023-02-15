import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import pandas as pd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, dash_table
from dash.dash_table.Format import Format, Group, Scheme
import dash.dash_table.FormatTemplate as FormatTemplate
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

# Data
path = 'https://raw.githubusercontent.com/garycl/AirportApp/master'
df_airports = pd.read_parquet(f'{path}/data/NIPAS_Airports.parquet')
df_airports = df_airports[df_airports['SvcLvl_FY23']=='P'].sort_values(by='LocID')
airport_options = [
    {"label": str(df_airports.loc[df_airports.LocID==airport,'LocID'].values[0]), "value": str(airport)}
    for airport in df_airports['LocID']
]

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

# Period
period_dict = {
    'Year':range(1993,2023),
    'Quarter':pd.period_range(
        start='1993Q1',
        end='2022Q3',
        freq='Q'
    )
}

Options = list(period_dict.keys())
nestedOptions = period_dict[Options[0]]

controls=dbc.Col([
    html.Br(),
    html.Br(),
    html.P('Frequency', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='period-1',
        options=[{'label': k, 'value': k} for k in period_dict.keys()],
        value='Year',
        style={'textAlign': 'center'},
    ),
    html.Br(),
    html.P('Select Start Period', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='p_start-1',
        value=nestedOptions,
    ),
    html.Br(),
    html.P('Select End Period', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='p_end-1',
        value=nestedOptions,
    ),
    html.Br(),
    html.P('Select Airports', style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='origin-1',
        value=None,
        multi=True,
        options=airport_options
    ),
    html.Br(),
    html.Button('Submit', id='button-1'),
])

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

tab_1_layout = html.Div(
    dbc.Row([
            dbc.Col(sidebar, md=1), 
            dbc.Col(content, md=3)
    ])
)