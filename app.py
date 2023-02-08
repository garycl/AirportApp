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

# App
app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.FLATLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
app.title="DB1B Data"
server = app.server

# Data
path = 'https://raw.githubusercontent.com/garycl/AirportApp/master'
df_airports = pd.read_parquet(f'{path}/data/NIPAS_Airports.parquet')
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

app.layout = html.Div(
    # Layout
    dbc.Col([
        html.P('Select Year Range', style={'textAlign': 'center'}),
        dcc.RangeSlider(
            id='year_slider',
            min=1993,
            max=2022,
            value=[1993, 2022],
            marks={int(i):str(i) for i in range(1993,2022+1,1)},
        ),
        html.Br(),
        html.P('Select Airports', style={'textAlign': 'center'}),
        dcc.Dropdown(
            id='origin_dropdown',
            value=[],
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
            labelStyle={'display': 'inline-block'}
        ),
        html.Button('Submit', id='button'),
        html.Div([
            html.Br(),
            html.Div(id="table-1")
        ]),
    ]),
    id="mainContainer",
    style={"display": "flex", "flex-direction": "column"},

)

variables = [
    'PAX','FaredPAX',
    'MktFare', 'MktMilesFlown', 
    'PWMktFare', 'PWMktMilesFlown', 
    'FareYield', 'PWFareYield',
    'AvgFare'
]

def get_yields(data):
    df = data.copy()
    df['FareYield'] = df['MktFare'].values / df['MktMilesFlown'].values
    df['PWFareYield']= df['PWMktFare'].values / df['PWMktMilesFlown'].values
    df['AvgFare'] = df['MktFare'].values / df['FaredPAX'].values
    return df

def get_data(df, time, airport):
    if time=='Quarter':
        group_var = ['Origin','Period']
    else:
        group_var = ['Origin','Year']
    tdf = df[(df.Origin==airport) | (df.Dest==airport)].copy()
    tdf['Origin']=airport
    tdf = tdf[group_var + variables]
    tdf = tdf.groupby(group_var).sum().reset_index()
    tdf = get_yields(tdf)
    tdf = tdf[group_var + variables]
    return tdf

def create_data(year_range, origin, time):
    min = year_range[0]
    max = year_range[1]
    data  = pd.DataFrame()
    for year in range(min, max+1):
        df = pd.read_parquet(f'{path}/data/dbmkt_{year}.parquet')
        df = df.rename(columns={'Passengers':'PAX'})
        df['Period'] = df['Year'].astype(str) + 'Q' + df['Quarter'].astype(str)
        df.loc[df.Origin=='HHH', 'Origin']='HXD'
        df.loc[df.Dest=='HHH', 'Dest']='HXD'
        df = df[
            (df.Origin.isin(origin)) | 
            (df.Dest.isin(origin))
        ]
        for i in origin:
            tdf = get_data(df, time, i)
            data = pd.concat([data, tdf], ignore_index=True)
    return data


# Table 1 callback
@app.callback(
    #Output('graph-1', 'figure'),
    Output('table-1', 'children'),
    [
        Input('button', 'n_clicks'),
        State('year_slider', 'value'),
        State('origin_dropdown', 'value'),
        State('time_radio', 'value'),
    ]
)

# ------------------------------------------------------------------------------
# Define table
# ------------------------------------------------------------------------------
def update_table(n_clicks, year_slider, origin, time):
    if n_clicks is None:
        return dash.no_update
    else:
        table=create_data(
            year_slider, 
            origin,
            time
        )
        if time=='Quarter':
            group_var = [
                {"name": "Airport", "id": "Origin"},
                {"name": "Period", "id": "Period"},
            ]
            table = table.sort_values(by=['Origin','Period'])
        else:
            group_var = [
                {"name": "Airport", "id": "Origin"},
                {"name": "Year", "id": "Year"},
            ]
            table = table.sort_values(by=['Origin','Year'])

        table=dash_table.DataTable(
                columns= group_var +[
                    {"name": "PAX", "id": "PAX", "type":'numeric', "format":Format().group(True)},
                    {"name": "FaredPAX", "id": "FaredPAX", "type":'numeric', "format":Format().group(True)},
                    {"name": "MktFare", "id": "MktFare", "type":'numeric', "format":FormatTemplate.money(2)},
                    {"name": "MktMilesFlown", "id": "MktMilesFlown", "type":'numeric', "format":Format().group(True)},
                    {"name": "PWMktFare", "id": "PWMktFare", "type":'numeric', "format":FormatTemplate.money(2)},
                    {"name": "PWMktMilesFlown", "id": "PWMktMilesFlown", "type":'numeric', "format":Format().group(True)},
                    {"name": "FareYield", "id": "FareYield", "type":'numeric', "format":FormatTemplate.money(4)},
                    {"name": "PWFareYield", "id": "PWFareYield", "type":'numeric', "format":FormatTemplate.money(4)},
                    {"name": "AvgFare", "id": "AvgFare", "type":'numeric', "format":FormatTemplate.money(2)},
                ],
                data=table.to_dict('records'),
                fixed_rows={'headers': True},
                style_table={'height': 400},  # defaults to 500
                style_cell={
                    'fontSize':16, 
                    'font-family':'Calibri', 
                    'textAlign':'right',
                },
                style_header={
                    'fontWeight': 'bold', 
                },
                export_format="csv"
            )
        return  table

if __name__ == '__main__':
    app.run_server(debug=True)
