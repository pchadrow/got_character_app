import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from wordcloud import WordCloud
from PIL import Image
from io import BytesIO
import numpy as np

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

df = pd.read_csv('Game_of_Thrones_Script_Corrected.csv')
cloud_mask = np.array(Image.open('mask.png'))

#gives list of all seasons to be used as buttons
available_seasons = {'All Seasons': None,
                    'Season 1': 'Season 1',
                    'Season 2': 'Season 2',
                    'Season 3': 'Season 3',
                    'Season 4': 'Season 4',
                    'Season 5': 'Season 5',
                    'Season 6': 'Season 6',
                    'Season 7': 'Season 7',
                    'Season 8': 'Season 8'}

app.layout = html.Div([
   html.Div(
       style ={'padding': "20px 10px 25px 4px"},
       children = [
            html.P('Season Select'),
            html.Div(style={"margin-left": "6px"}, children=dcc.Dropdown(
                id='season_select',
                options=[{'label': k, 'value': k} for k in available_seasons.keys()],
                value='All Seasons'
                )),
       #creates callback list providing options depending on previous selection    
       html.Div(
           style={'margin': '10px 0px'},
           children=[
           html.P(children='Episode Select', style={'margin-left': '3px'}),
               dcc.RadioItems(id='episode_select',
                     labelStyle={'display': 'inline-block'})]),
    ]), 
    
    dcc.Graph(id='season_plot'),
    
    html.Div(
        style={'padding': '20px 10px 25px 4px'},
        children =[
            html.P('Top (x) Character Selector'),
            html.Div(style={'margin-left': '6px'}, children=dcc.Slider(
                id = 'top_selection',
                min = 5,
                max = 25,
                marks={
                    5: '5',
                    10: '10',
                    15: '15',
                    20: '20',
                    25: '25'
                    },
                value = 10))]),
        
            html.Div([
        
            dcc.Graph(id='count_plot')
    ]),

    html.Div([
        html.Div(
            style ={'padding': "20px 10px 25px 4px"},
            children = [
            html.P('Character Word Cloud Select'),
            html.Div(style={"margin-left": "6px"}, children=dcc.Dropdown(
                id='character_select',
                value = 'None'
                ))]
        ),
        html.Div([
            html.Img(id='word_cloud')
        ])
    ])
    
])

#refreshes app every time season_select is changed to provide new options to episode select
@app.callback(
    Output('episode_select', 'options'),
    [Input('season_select', 'value')])
def set_episode_options(season):
    dfs = df[df['Season'] == season]
    eps = list(dfs['Episode'].unique())
    selection = [{'label': i, 'value': i} for i in eps]
    selection.append({'label': 'All Episodes', 'value': None})
    return selection

#sets default value for episode selection
@app.callback(
    Output('episode_select', 'value'),
    [Input('episode_select', 'options')])
def set_episode_value(avail_options):
    return avail_options[-1]['value']

#refreshes graph after every selection change
@app.callback(
    Output('season_plot', 'figure'),
    [Input('season_select', 'value'),
     Input('episode_select', 'value'),
     Input('top_selection', 'value')])
def update_graph(season, episode, top):
    if not season == 'All Seasons':
        dfs = df[df['Season'] == season]
        if episode:
            dfe = dfs[dfs['Episode'] == episode]
            dfcount = dfe.Character.loc[df['Character'] != 'man'].value_counts().reset_index(name='count').query('count > 5')[:top]
            fig = px.bar(dfcount,
                x = 'index',
                y = 'count',
                title = f'Top {top} Speaking Characters in {season} {episode}')
            fig.update_xaxes(title = 'Character')
            fig.update_yaxes(title = 'Number of Lines')
            return fig
        
        else:
            dfcount = dfs.Character.loc[df['Character'] != 'man'].value_counts().reset_index(name="count").query("count > 5")[:top]
            fig = px.bar(dfcount,
                x = 'index',
                y = 'count',
                title = f'Top {top} Speaking Characters in {season}')
            fig.update_xaxes(title='Character')
            fig.update_yaxes(title='Number of Lines')
        
            return fig
        
    else:
        dfcount = df.Character.value_counts().reset_index(name="count").query("count > 5")[:top]
            
        fig = px.bar(dfcount,
            x = 'index',
            y = 'count',
            title = f'Top {top} Speaking Characters Overall')
        fig.update_xaxes(title='Character')
        fig.update_yaxes(title='Number of Lines')
    
        return fig

@app.callback(
    Output('count_plot', 'figure'),
    [Input('season_select', 'value'),
     Input('episode_select', 'value'),
     Input('top_selection', 'value')])
def update_word_count(season, episode, top):
    if not season == 'All Seasons':
        dfs = df[df['Season'] == season]
        if episode:
            dfe = dfs[dfs['Episode'] == episode]
            dfcount = dfe.groupby('Character').sum().sort_values('word_count', ascending = False).reset_index()[:top]
            fig = px.bar(dfcount,
            x = 'Character',
            y = 'word_count',
            title = f'Top {top} Speaking Characters in {season} {episode} by Total Number of Words')
            fig.update_xaxes(title = 'Character')
            fig.update_yaxes(title = 'Total Number of Words Spoken')
            return fig   
        
        else:
            dfcount = dfs.groupby('Character').sum().sort_values('word_count', ascending = False).reset_index()[:top]
            fig = px.bar(dfcount,
            x = 'Character',
            y = 'word_count',
            title = f'Top {top} Speaking Characters in {season} by Total Number of Words')
            fig.update_xaxes(title='Character')
            fig.update_yaxes(title='Total Number of Words Spoken')
        
            return fig
        
    else:
        dfcount = df.groupby('Character').sum().sort_values('word_count', ascending = False).reset_index()[:top]
            
        fig = px.bar(dfcount,
            x = 'Character',
            y = 'word_count',
            title = f'Top {top} Speaking Characters Overall by Number of Words Spoken')
        fig.update_xaxes(title='Character')
        fig.update_yaxes(title='Total Number of Words Spoken')
    
        return fig


# creates list of available characters to select for a word cloud based upon previous selections
@app.callback(
    Output('character_select', 'options'),
    [Input('season_select', 'value'),
     Input('episode_select', 'value'),
     Input('top_selection', 'value')])
def set_character_options(season, episode, top):
    if not season == 'All Seasons':
        dfs = df[df['Season'] == season]
        if episode:
            dfe = dfs[dfs['Episode'] == episode]
            dfcount = dfe.groupby('Character').sum().sort_values('word_count', ascending = False).reset_index()[:top+5]
            names = list(dfcount['Character'])
            selection = [{'label' : i, 'value': i} for i in names]
            selection.append({'label': 'None', 'value': None})
            return selection
        else:
            dfcount = dfs.groupby('Character').sum().sort_values('word_count', ascending = False).reset_index()[:top+5]
            names = list(dfcount['Character'])
            selection = [{'label' : i, 'value': i} for i in names]
            selection.append({'label': 'None', 'value': None})
            return selection
    
    else:
        dfcount = df.groupby('Character').sum().sort_values('word_count', ascending = False).reset_index()[:top+5]
        names = list(dfcount['Character'])
        selection = [{'label' : i, 'value': i} for i in names]
        selection.append({'label': 'None', 'value': None})
        return selection
    
    
@app.callback(
    Output('word_cloud', 'src'),
    [Input('season_select', 'value'),
     Input('episode_select', 'value'),
     Input('character_select', 'value')])
def create_word_cloud(season, episode, character):
    wc = WordCloud(background_color='white' ,collocations = False,
                mask = cloud_mask, contour_width=1, height = 150, width = 300)
    if not season == 'All Seasons':
        dfs = df[df['Season'] == season]
        if episode:
            dfe = dfs[dfs['Episode'] == episode]
            dfc = dfe[dfe['Character'] == character]
            text = ' '.join(dfc['Sentence'])
            wc.generate(text)
            img = wc.to_image()
            byte = BytesIO()
            img.save(byte, format='PNG')
            return 'data:image/png;base64,{}'.format(base64.b64encode(byte.getvalue()).decode())
        
        else:
            dfc = dfs[dfs['Character'] == character]
            text = ' '.join(dfc['Sentence'])
            wc.generate(text)
            img = wc.to_image()
            byte = BytesIO()
            img.save(byte, format='PNG')
            return 'data:image/png;base64,{}'.format(base64.b64encode(byte.getvalue()).decode())
            return None
    
    else:
        dfc = df[df['Character'] == character]
        text = ' '.join(dfc['Sentence'])
        wc.generate(text)
        img = wc.to_image()
        byte = BytesIO()
        img.save(byte, format='PNG')
        return 'data:image/png;base64,{}'.format(base64.b64encode(byte.getvalue()).decode())

if __name__ == '__main__':
    app.run_server(debug=False)