import dash
import os
from dash.exceptions import PreventUpdate
from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
import numpy as np

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.VAPOR, dbc.icons.FONT_AWESOME])

current_dir = os.path.dirname(os.path.abspath(__file__))
emission_data = pd.read_csv(os.path.join(current_dir, 'co2_merge_scaled.csv'),index_col=0)
kum_fogy = emission_data.groupby('Country')['Energy_consumption'].sum().reset_index()
aggr_kib = emission_data.groupby(['Country', 'Year'], as_index=False)['CO2_emission'].sum()
markdown_cim="# CO2 Kibocsájtás - Szabó Norbert "
markdown1= """
Szabó Norbert  
C7NJCK  
justtaylorsemail@gmail.com  
"""
markdown2= """
+ Elemzés és formázás  
+ Daily overdose on caffeine  
+ 2_co2_kibocsajtas.csv a fájlom  
+ Ehhez kapcsoltam a regions.xlsx-t, ami országokhoz tartozó régió nevek miatt volt fontos

*folytatás a következő lapon*
"""
markdown3= """
+ Tábla kapcsolat: Országokhoz régiókat rendeltem
+ Üres értékek: Régiók alapján az átlaggal feltöltöttem
+ Kiugró értékek: Z-score alapján kiszűrtem őket
+ Standardscaler használatával skáláztam az outlier-ek kivonása az adathalmazt
+ A skálázatlan adathalmaz is elérhető, ezzel is megtekinthető az eredmény: 'co2_merge.csv'
"""
markdown4= """
+ Átfogó stílusnak választottam a "dbc.themes.VAPOR, dbc.icons.FONT_AWESOME"
+ Próbáltam a fehér, fekete és kék színeket alkalmazni
+ Lineáris regresszió esetén nem lehet polinomiális fokot állítani
+ Visszajelzést küldd a felhasználónak ha a polinomiális fokot 1 alattira szeretné állítani
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
        style={'color':'blue','backgroundColor':'black'},
        )],style={'width':'700px','margin':'0 auto'}),

    dash_table.DataTable(
        id='netto_energiamerleg_dt',
        data=[],
        columns=[{"name": "Year", "id": "Year"},{'name':'Net_energy_balance','id':'Net_energy_balance'}],
        fixed_rows={'headers': True},
        style_table={'height': '400px','width':'700px','margin':'0 auto','color':'black', 'background-color':'black'},
        style_data={
        'color': 'white',
        'backgroundColor': 'black'},
        style_header={
        'backgroundColor': 'black',
        'color': 'white',
        'fontWeight': 'bold','whiteSpace': 'normal'
        },
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
        style={'color':'blue','backgroundColor':'black'},
        )],style={'width':'700px','margin':'0 auto'}),
    html.Div(id='multi-energy-chart'),
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
        dcc.Input(id='bins-input', type='number', value=1, min=1, step=5,style={'color':'white','backgroundColor':'black'})
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
        style={'color':'blue','backgroundColor':'black'},
        clearable=False
    ),
    dcc.Graph(id='choropleth-map', style={'height': '70vh'}),
    html.P(),
    html.H2('8. Feladat: Regressziós modell'),
    html.P(),
    dbc.Row([
    dbc.Col(dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in aggr_kib['Country'].unique()],
                placeholder="Válassz egy országot",
                style={'color': 'blue', 'backgroundColor': 'black'}
            )),
    dbc.Col(dcc.Dropdown(
                id='model-dropdown',
                options=[
                    {'label': 'Lineáris', 'value': 'linear'},
                    {'label': 'Polinomiális', 'value': 'polynomial'}
                ],
                placeholder="Válassz modellt",
                style={'color': 'blue', 'backgroundColor': 'black'}
            )),
    dbc.Col(dcc.Input(
                id='input-degree',
                type='number',
                placeholder="Polinom fok",
                min=1,
                value=1,
                style={'color':'white','backgroundColor':'black'}

            )),
    dbc.Col(dbc.Alert(id='degree-warning', color='danger', is_open=False))
    ]),
    dcc.Graph(id='output-graph'),
    html.P(),
    html.H2('9. Feladat: Formázások'),
    html.P(),
    dcc.Markdown(markdown4)
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
    Output('multi-energy-chart', 'children'),
    Input('multi_dd', 'value')  
)
def update_charts(selected_countries):
    if not selected_countries:
        return [html.Div("Válassz országot a diagram megjelenítéséhez", style={'color': 'white'})]

    charts = []

    for country in selected_countries:
        country_data = emission_data[emission_data['Country'] == country]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=country_data['Year'],
            y=country_data['Energy_consumption'],
            mode='lines+markers',
            name=country
        ))

        fig.update_layout(
            title=f"{country} energiafogyasztása",
            title_font=dict(size=20, color='white'),
            yaxis_title="Energiafogyasztás",
            template='plotly_dark'
        )

        charts.append(dcc.Graph(figure=fig))

    return charts


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
            marker=dict(color='blue')
        )
    )

    fig.update_layout(
        template='plotly_dark',
        title=f"CO₂ Kibocsátás {selected_year}-ban",
        title_font=dict(size=45, color='white'),
        xaxis_title="CO₂ Kibocsátás",
        yaxis_title="Országok száma",
        xaxis=dict(title_font=dict(size=24,color='white'),tickfont=dict(color='white')),
        yaxis = dict(automargin=True, autorange=True,title_font=dict(size=24,color='white'),tickfont=dict(color='white'))
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
        title_font=dict(size=35, color="white"),
        paper_bgcolor='black',
        plot_bgcolor='black',
        font_color='white'
    )

    return fig

@app.callback(
    Output('input-degree', 'disabled'),
    [Input('model-dropdown', 'value')]
)
def toggle_polynomial_degree_input(regression_type):

    return regression_type != 'polynomial'
@app.callback(
    Output('degree-warning', 'is_open'),
    Output('degree-warning', 'children'),
    Input('input-degree', 'value'),
     Input('model-dropdown', 'value')
)
def validate_polynomial_degree(poly_degree, regression_type):
    if regression_type == 'polynomial' and (poly_degree is None or poly_degree < 1):
        return True, "A polinom foknak legalább 1-nek kell lennie!"
    return False, ""
@app.callback(
    Output('output-graph', 'figure'),
    Input('country-dropdown', 'value'),
     Input('model-dropdown', 'value'),
     Input('input-degree', 'value')
)
def update_graph(selected_country, regression_type, poly_degree):

    fig = px.scatter(title='Válassz országot és regressziós típust a diagramhoz',template='plotly_dark')

    if not selected_country or not regression_type:

        return fig

    filtered_df = aggr_kib[aggr_kib['Country'] == selected_country]

    X = filtered_df['Year'].values.reshape(-1, 1)
    y = filtered_df['CO2_emission'].values

    if regression_type == 'polynomial':
        poly = PolynomialFeatures(degree=poly_degree)
        X_poly = poly.fit_transform(X)

        model = LinearRegression()
        model.fit(X_poly, y)

        X_pred = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
        X_pred_poly = poly.transform(X_pred)
        y_pred = model.predict(X_pred_poly)

        fig = px.scatter(filtered_df, x='Year', y='CO2_emission', title=f'{selected_country} CO2 kibocsátás (Polinomiális)', template='plotly_dark')
        fig.add_scatter(x=X_pred.flatten(), y=y_pred, mode='lines', name='Regresszió', line=dict(color='blue'))

    elif regression_type == 'linear':

        model = LinearRegression()
        model.fit(X, y)


        y_pred = model.predict(X)

        fig = px.scatter(filtered_df, x='Year', y='CO2_emission', title=f'{selected_country} CO2 kibocsátás (Lineáris)', template='plotly_dark')
        fig.add_scatter(x=X.flatten(), y=y_pred, mode='lines', name='Regresszió', line=dict(color='blue'))

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)