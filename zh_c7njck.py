import dash
import os
from dash.exceptions import PreventUpdate
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

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
        value=kum_fogy['Energy_consumption'].max(),
        marks=None,
        tooltip={"placement": "bottom", "always_visible": True}),
        html.Div(id='country-list'),
    html.P(),
    html.H2('5. Feladat: Többváltozós legördülő lista'),
    html.Div(className='dd-2',children=[dcc.Dropdown(
        id='multi_dd',
        placeholder='Válasszon egy vagy több országot',
        options=[{'label': country,'value': country} for country in emission_data['Country'].unique()],
        className='dropdown-2',
        multi=True,
        style={'color':'black'},
        )],style={'width':'700px','margin':'0 auto'}),
    dcc.Graph(id='multi-energy-chart', figure=go.Figure()),
    html.P(),
    html.H2('6. Feladat: Évek szerinti CO2 kibocsájtás'),
    html.P(),
    dbc.Row([
        dbc.Col(dcc.Slider(
        id='year-slider',
        min=emission_data['Year'].unique().min(),
        max=emission_data['Year'].unique().max(),
        step=1,
        marks={str(year): str(year) for year in emission_data['Year'].unique()},
        value=emission_data['Year'].unique().min())),
    dbc.Col(html.Div([
        html.Label("Osztályközök száma:"),
        dcc.Input(id='bins-input', type='number', value=10, min=1, step=5)
    ], style={'display': 'inline-block', 'padding-left': '20px'}))]),
    html.P(),
    dcc.Graph(id='co2-histogram'),
    html.P(),
    html.H2('7. Feladat: Energia típusok tematikus térképen'),
    html.P(),
    dcc.Dropdown(
        id='energy-type-dd',
        options=[{'label': energy, 'value': energy} for energy in emission_data['Energy_type'].unique()],
        value=emission_data['Energy_type'].unique()[0],
        clearable=False
    ),
    dcc.Graph(id='choropleth-map', style={'height': '70vh'})

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
    Input('energy-slider', 'value')
)
def update_country_list(min_consumption):
    filtered_countries = kum_fogy[kum_fogy['Energy_consumption'] >= min_consumption]
    if filtered_countries.empty:
        return html.P("Nincs olyan ország, amelynek a kumulált energiafogyasztása meghaladja az adott értéket.")
    return html.Ul([html.Li(country) for country in filtered_countries['Country']])

@app.callback(
    Output('multi-energy-chart', 'figure'),
    Input('multi_dd', 'value'))

def update_charts(selected_countries):
    if not selected_countries:
        empty_fig = go.Figure()
        empty_fig.update_layout(title="Válassz országot a diagram megjelenítéséhez",template='plotly_dark')
        return empty_fig
    fig = go.Figure()
    for country in selected_countries:
        country_data = emission_data[emission_data['Country'] == country]
        fig.add_trace(go.Scatter(
            x=country_data['Year'],
            y=country_data['Energy_consumption'],
            mode='lines+markers',
            name=country
        ))

    fig.update_layout(
        title="Kiválasztott országok energiafogyasztása",

        template='plotly_dark'
    )

    return fig


@app.callback(
    Output('co2-histogram', 'figure'),
    [Input('year-slider', 'value'), Input('bins-input', 'value')]
)
def update_histogram(selected_year, num_bins):
    filtered_df = emission_data[emission_data['Year'] == selected_year]
    grouped_df = filtered_df.groupby('Country', as_index=False).agg({'CO2_emission': 'mean'})

    fig = go.Figure(
        data=go.Histogram(
            x=grouped_df['CO2_emission'],
            nbinsx=num_bins,
            marker=dict(color='#143e9e')
        )
    )

    fig.update_layout(
        title=f"CO₂ Kibocsátás {selected_year}-ban",
        title_font=dict(size=45, color='#143e9e'),
        xaxis_title="CO₂ Kibocsátás",
        yaxis_title="Országok száma",
        paper_bgcolor="#a7beda",
        plot_bgcolor="black",
        xaxis=dict(title_font=dict(size=24,color='#143e9e'),tickfont=dict(color='#143e9e')),
        yaxis = dict(automargin=True, autorange=True,title_font=dict(size=24,color='#143e9e'),tickfont=dict(color='#143e9e'))
    )

    return fig


@app.callback(
    Output('choropleth-map', 'figure'),
    Input('energy-type-dd', 'value')
)
def update_map(selected_energy_type):
    filtered_df = emission_data[emission_data['Energy_type'] == selected_energy_type]

    fig = px.choropleth(
        filtered_df,
        locations="Country",
        locationmode="country names",
        color="Energy_consumption",
        hover_name="Country",
        animation_frame="Year",
        color_continuous_scale="Viridis",
        title=f"{selected_energy_type} Fogyasztás Évek Szerint"
    )

    fig.update_layout(
        geo=dict(showframe=False, showcoastlines=True),
        coloraxis_colorbar=dict(title="Fogyasztás"),
        title_font=dict(size=20, color="black")
    )

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)