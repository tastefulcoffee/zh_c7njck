import dash
import os
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import pandas as pd

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
current_dir = os.path.dirname(os.path.abspath(__file__))
emission_data = pd.read_csv(os.path.join(current_dir, '2_co2_kibocsajtas.csv'),index_col=0)
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
app.layout = html.Div([
    dcc.Markdown(markdown_cim),
    dbc.Tabs([
        dbc.Tab([dcc.Markdown(markdown1)],label="Saját adatok"),
        dbc.Tab([dcc.Markdown(markdown2)],label="Projekt adatai")

    ])
])

if __name__ == '__main__':
    app.run_server(debug=True)