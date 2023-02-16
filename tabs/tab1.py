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
df_airports = pd.read_parquet(f'{path}/NPIAS_Airports.parquet')
df_airports = df_airports[df_airports['SvcLvl_FY23']=='P'].sort_values(by='LocID')
airport_options = [
    {"label": str(df_airports.loc[df_airports.LocID==airport,'LocID'].values[0]), "value": str(airport)}
    for airport in df_airports['LocID']
]

# Read data
def create_layout(n_clicks, start_year, end_year, origin, time):

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

    def create_data(start_year, end_year, origin, time):
        start_year = int(start_year)
        end_year = int(end_year)
        min_year = min(start_year, end_year)
        max_year = max(start_year, end_year)
        data  = pd.DataFrame()
        for year in range(min_year, max_year+1):
            df = pd.read_parquet(f'{path}/db1b_mkt/dbmkt_{year}.parquet')
            df = df.rename(columns={'Passengers':'PAX'})
            for i in origin:
                tdf = get_data(df, time, i)
                data = pd.concat([data, tdf], ignore_index=True)
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
                    {"name": "Airport", "id": "Origin"},
                    {"name": "Period", "id": "Period"},
                ]
                table['Period']=table['Period'].astype(str)
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