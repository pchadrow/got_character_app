import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

df = pd.read_csv('Game_of_Thrones_Script_Corrected.csv')

#gives list of all seasons to be used as buttons
available_seasons = {'All': None,
                    'Season 1': 'Season 1',
                    'Season 2': 'Season 2',
                    'Season 3': 'Season 3',
                    'Season 4': 'Season 4',
                    'Season 5': 'Season 5',
                    'Season 6': 'Season 6',
                    'Season 7': 'Season 7',
                    'Season 8': 'Season 8'}

app.layout = html.Div([
   html.Div([
    
    dcc.Dropdown(
    id='season_select',
    options=[{'label': k, 'value': k} for k in available_seasons.keys()],
    value='All'
    ),
    ]), 
    
    dcc.Graph(id='season_plot')
])

@app.callback(
    Output('season_plot', 'figure'),
    [Input('season_select', 'value')])
def update_graph(season):
    if not season == 'All':
        dfs = df[df['Season'] == season]
        dfcount = dfs.Character.value_counts().reset_index(name="count").query("count > 5")[:25]
        fig = px.bar(dfcount,
            x = 'index',
            y = 'count',
            title = f'Top 25 Speaking Characters in {season}')
        fig.update_xaxes(title='Character')
        fig.update_yaxes(title='Number of Lines')
        
        return fig
        
    else:
        dfcount = df.Character.value_counts().reset_index(name="count").query("count > 5")[:25]
            
        fig = px.bar(dfcount,
            x = 'index',
            y = 'count',
            title = 'Top 25 Speaking Character Overall')
        fig.update_xaxes(title='Character')
        fig.update_yaxes(title='Number of Lines')
    
        return fig


if __name__ == '__main__':
    app.run_server(debug=False)