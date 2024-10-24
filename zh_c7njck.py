import dash
import os
from dash.exceptions import PreventUpdate
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import pandas as pd

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.VAPOR, dbc.icons.FONT_AWESOME])

current_dir = os.path.dirname(os.path.abspath(__file__))
emission_data = pd.read_csv(os.path.join(current_dir, 'co2_merge.csv'),index_col=0)
markdown_cim="# CO2 Kibocsájtás - Szabó Norbert "
markdown1= """
Szabó Norbert  
C7NJCK  
justtaylorsemail@gmail.com  
"""
markdown2= """
Elemzés és formázás  
Daily overdose on coffeine  
2_co2_kibocsajtas.csv a fájlom  
"""
markdown3= """
+ Tábla kapcsolat: Országokhoz régiókat rendeltem
+ Üres értékek: Régiók alapján az átlaggal feltöltöttem
+ Kiugró értékek: Z-score alapján kiszűrtem őket
"""
app.layout = html.Div([
    dcc.Markdown(markdown_cim),
    dbc.Tabs([
        html.P(),
        dbc.Tab([dcc.Markdown(markdown1)],label="Saját adatok"),
        html.P(),
        dbc.Tab([dcc.Markdown(markdown2)],label="Projekt adatai"),
        dbc.Tab([dcc.Markdown(markdown3)],label="ETL"),
    ]),
    html.P(),
    
    html.Div(className='dd-1',children=[dcc.Dropdown(
        id='netto_energiamerleg_dd',
        placeholder='Válasszon egy országot',
        options=[{'label': country,'value': country} for country in emission_data['Country'].unique()],
        className='dropdown-1',
        style={'background-color':'#783758', 'color':'black'},
        )],style={'width':'700px','margin':'0 auto'}),

    dash_table.DataTable(
        id='netto_energiamerleg_dt',
        data=[],
        columns=[{"name": "Year", "id": "Year"},{'name':'Net_energy_balance','id':'Net_energy_balance'}],
        style_header={'whiteSpace': 'normal'},
        fixed_rows={'headers': True},
        style_table={'height': '400px','width':'700px','margin':'0 auto','color':'black'},
        virtualization=True,
    )
        ])


@app.callback(
    Output('netto_energiamerleg_dt', 'data'),
    Input('netto_energiamerleg_dd', 'value')
)
def update_table(selected_country):
    if not selected_country:
        return []
    if selected_country not in emission_data['Country'].values:
        raise PreventUpdate
    filtered_df = emission_data[emission_data['Country'] == selected_country]
    grouped_df = filtered_df.groupby('Year').agg({
        'Net_energy_balance': 'sum'}).reset_index()
    return grouped_df.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)