import dash
import os
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input
import pandas as pd

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])
current_dir = os.path.dirname(os.path.abspath(__file__))
emission_data = pd.read_csv(os.path.join(current_dir, '2_co2_kibocsajtas.csv'),index_col=0)

app.layout = html.Div([
    html.H1('Első feladat'),
    html.Pre(emission_data.head().to_string()),
    html.Pre(emission_data.dtypes.to_string())
])

if __name__ == '__main__':
    app.run_server(debug=True)