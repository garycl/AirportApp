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

    def get_poo(data):
        df = data.copy()
        df['%POO'] = (
            (df['RoundTripPAX'].values * 2 + df['OneWayPAX'].values) / df['PAX'].values
        )
        df['%POD'] = 1 - df['%POO'].values
        return df

    def get_data(mdf, tdf, time, airport):
        if time=='Quarter':
            group_var = ['Year','Quarter']
        else:
            group_var = ['Year']
        if airport=='HXD':
            airport='HHH'
        mkt = mdf[(mdf.Origin==airport)|(mdf.Dest==airport)].copy()
        mkt = mkt.groupby(group_var).sum().reset_index()
        mkt['Origin']=airport
        mkt = mkt[['Origin'] + group_var + ['PAX']]

        tix = tdf[tdf.Origin==airport].copy()
        tix = tix.groupby(group_var).sum().reset_index()
        tix['Origin']=airport
        tix = tix[['Origin'] + group_var + ['RoundTripPAX', 'OneWayPAX']]
    
        new_group_var = ['Origin'] + group_var
        merged = pd.merge(mkt, tix, on=new_group_var)
        if time=='Quarter':
            merged['Period'] = merged['Year'].astype(str) + 'Q' + merged['Quarter'].astype(str)
            merged.drop(columns=['Year','Quarter'], inplace=True)

        return merged

    def create_data(start_year, end_year, origin, time):
        start_year = int(start_year)
        end_year = int(end_year)
        min_year = min(start_year, end_year)
        max_year = max(start_year, end_year)
        data  = pd.DataFrame()
        for year in range(min_year, max_year+1):
            mkt = pd.read_parquet(f'{path}/data/db1b_mkt/dbmkt_{year}.parquet')
            mkt = mkt.rename(columns={'Passengers':'PAX'})
            tix = pd.read_parquet(f'{path}/data/db1b_tix/dbtix_{year}.parquet')
            for i in origin:
                tdf = get_data(mkt, tix, time, i)
                tdf = get_poo(tdf)
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
                        {"name": "RoundTripPAX", "id": "RoundTripPAX", "type":'numeric', "format":Format().group(True)},
                        {"name": "OneWayPAX", "id": "OneWayPAX", "type":'numeric', "format":Format().group(True)},
                        {"name": "%POO", "id": "%POO", "type":'numeric', "format":FormatTemplate.percentage(2)},
                        {"name": "%POD", "id": "%POD", "type":'numeric', "format":FormatTemplate.percentage(2)},
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