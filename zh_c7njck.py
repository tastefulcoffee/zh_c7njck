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
kum_fogy = emission_data.groupby('Country')['Energy_consumption'].sum().reset_index()
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
    html.P(),
    dcc.Markdown(markdown_cim),
    html.H2('2. Feladat: Saját-és projekt adatok felírása'),
    dbc.Tabs([
        html.P(),
        dbc.Tab([dcc.Markdown(markdown1)],label="Saját adatok"),
        html.P(),
        dbc.Tab([dcc.Markdown(markdown2)],label="Projekt adatai"),
        dbc.Tab([dcc.Markdown(markdown3)],label="ETL"),
    ]),
    html.P(),
    html.H2('3. Feladat: Legördülő menü és nettó energiamérleg'),
    html.Div(className='dd-1',children=[dcc.Dropdown(
        id='netto_energiamerleg_dd',
        placeholder='Válasszon egy országot',
        options=[{'label': country,'value': country} for country in emission_data['Country'].unique()],
        className='dropdown-1',
        style={'color':'black'},
        )],style={'width':'700px','margin':'0 auto'}),

    dash_table.DataTable(
        id='netto_energiamerleg_dt',
        data=[],
        columns=[{"name": "Year", "id": "Year"},{'name':'Net_energy_balance','id':'Net_energy_balance'}],
        style_header={'whiteSpace': 'normal'},
        fixed_rows={'headers': True},
        style_table={'height': '400px','width':'700px','margin':'0 auto','color':'black'},
        virtualization=True,
    ),
    html.P(),
    html.H2('4. Feladat: Csúszka és kumulált energia fogyasztás'),
    dcc.Slider(
        id='energy-slider',
        min=0,
        max=kum_fogy['Energy_consumption'].max(),
        step=50,
        value=200,
        marks=None,
        tooltip={"placement": "bottom", "always_visible": True}),
        html.Div(id='country-list')
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


@app.callback(
    Output('country-list', 'children'),
    [Input('energy-slider', 'value')]
)
def update_country_list(min_consumption):
    filtered_countries = kum_fogy[kum_fogy['Energy_consumption'] >= min_consumption]
    if filtered_countries.empty:
        return html.P("Nincs olyan ország, amelynek a kumulált energiafogyasztása meghaladja az adott értéket.")
    return html.Ul([html.Li(country) for country in filtered_countries['Country']])

if __name__ == '__main__':
    app.run_server(debug=True)