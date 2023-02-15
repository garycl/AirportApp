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

# Data
path = 'https://raw.githubusercontent.com/garycl/AirportData/master'
df_airports = pd.read_parquet(f'https://raw.githubusercontent.com/garycl/AirportApp/master/data/NPIAS_Airports.parquet')
df_airports = df_airports[df_airports['SvcLvl_FY23']=='P'].sort_values(by='LocID')
airport_options = [
    {"label": str(df_airports.loc[df_airports.LocID==airport,'LocID'].values[0]), "value": str(airport)}
    for airport in df_airports['LocID']
]

# Read data
def create_layout(n_clicks, start_year, end_year, origin, time):

    def get_data(df, time, airport):
        if time=='Quarter':
            group_var = ['Origin', 'Dest']
        else:
            group_var = ['Origin', 'Dest']
        tdf = df[(df.Origin==airport) | (df.Dest==airport)].copy()
        index_= tdf[tdf.Dest==airport].index
        tdf.loc[tdf.index.isin(index_),'Dest'] = tdf.loc[tdf.index.isin(index_),'Origin']
        tdf.loc[tdf.index.isin(index_),'Origin'] = airport
        return tdf

    def create_data(start_year, end_year, origin, time):
        start_year = int(start_year)
        end_year = int(end_year)
        min_year = min(start_year, end_year)
        max_year = max(start_year, end_year)
        data  = pd.DataFrame()
        for year in range(min_year, max_year+1):
            df = pd.read_parquet(f'{path}/data/db1b_mkt/dbmkt_{year}.parquet')
            df = df.rename(columns={'Passengers':'PAX'})
            df['Period'] = df['Year'].astype(str) + 'Q' + df['Quarter'].astype(str)
            for i in origin:
                if i=='HXD':
                    i='HHH'
                tdf = get_data(df, time, i)
                data = pd.concat([data, tdf], ignore_index=True)
        data = data[['Origin','Dest', 'PAX']]
        data = data.groupby(['Origin','Dest']).sum().reset_index()
        data = data.sort_values(by='PAX', ascending=False).reset_index(drop=True)
        data = data[data.index<=24]
        data['Ranking'] = data.index.values + 1
        data = data[['Ranking', 'Origin', 'Dest', 'PAX']]
        return data

    if n_clicks is None:
        return dash.no_update
    else:
        try:
            table=create_data(
                start_year,
                end_year, 
                origin,
                time
            )
            if time=='Quarter':
                group_var = [
                    {"name": "Ranking", "id":"Ranking"},
                    {"name": "Airport", "id": "Origin"},
                    {"name": "Top O&D", "id": "Dest"},
                ]
            else:
                group_var = [
                    {"name": "Ranking", "id":"Ranking"},
                    {"name": "Airport", "id": "Origin"},
                    {"name": "Top O&D", "id": "Dest"},
                ]

            table=dash_table.DataTable(
                    columns= group_var +[
                        {"name": "PAX", "id": "PAX", "type":'numeric', "format":Format().group(True)},
                    ],
                    data=table.to_dict('records'),
                    fixed_rows={'headers': True},
                    style_table={'height': 400},  # defaults to 500
                    style_cell={
                        'fontSize':16, 
                        'font-family':'Calibri', 
                        'textAlign':'center',
                    },
                    style_header={
                        'fontWeight': 'bold', 
                    },
                    export_format="csv"
                )
            return  table
        except:
            return html.Div('One of the parameters is not selected.', style={'size':12})