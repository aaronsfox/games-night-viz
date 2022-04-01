# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Script to create Dash app for level 3 of #GamesNightViz
    
"""

# %% Import packages

import plotly.io as pio
pio.renderers.default = 'svg'
import plotly.graph_objs as go
from PIL import Image
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output

# %% Set-up

#Import data
songData = pd.read_csv('data\\songData.csv')

#Load map image
mapImg = Image.open('img\\oot_map.jpg')

#Load ocarina image
ocarinaSmallImg = Image.open('img\\ocarina_small.png')

#Load Link image
linkImg = Image.open('img\\linkPlaying.png')

#Set song point location size
songPointSize = 25

#Import N64 button images
buttonImageFiles = ['n64_A', 'n64_up', 'n64_left', 'n64_right', 'n64_down']
buttonImg = {}
for button in buttonImageFiles:
    buttonImg[button.split('_')[-1]] = Image.open('img\\'+button+'.png')
    
#Map buttons to plotting values
buttonPlotVal = {'A': 100, 'down': 200, 'right': 400, 'left': 500, 'up': 700}

#Set list for note names
noteList = ['note1', 'note2', 'note3', 'note4', 'note5', 'note6', 'note7', 'note8']

#Set note image size
notePointSize = 100

#Load treble clef image
clefImg = Image.open('img\\treble_clef.png')

#Set axis ranges for calculations
musicRangeX = [0.5, 850]
musicRangeY = [-100,800]

#Calculate ratio of Link image height to map
linkToMap_heightRatio = mapImg.size[1] / linkImg.size[1]

#Calculate ratio Link image width
linkImg_ratioWidth = linkImg.size[0] * linkToMap_heightRatio

#Calculate width proportion that Link image should take up
linkImg_widthProp = linkImg_ratioWidth / (linkImg_ratioWidth + mapImg.size[0])

#Calcualte width proportion that map image should take up
mapImg_widthProp = 1 - linkImg_widthProp 

#Calculate map figure height to widthratio
mapFig_heightToWidth = mapImg.size[1] / (mapImg.size[0] + linkImg_ratioWidth)

#Calculate relative height and width we want map figure to cover
mapFigRelWidth = 78
mapFigRelHeight = mapFigRelWidth / mapFig_heightToWidth

# %% Create static map figure

##### TODO: consider extra hover points over link image

#Create blank figure
mapFig = go.Figure()

#Update figure layout
mapFig.update_layout(
    #Sizing
    autosize = True,
    #Figure boundaries
    margin = dict(l = 0,
                  r = 0,
                  t = 0,
                  b = 0),
    #Axis limits
    xaxis_range = [(linkImg.size[0] * (mapImg.size[1] / linkImg.size[1]) * -1), mapImg.size[0]],
    yaxis_range = [0,mapImg.size[1]],
    #Figure & background colour
    paper_bgcolor = 'rgba(255, 255, 255, 0)',
    plot_bgcolor = 'rgba(255, 255, 255, 0)',
    #Turn off legend
    showlegend = False,
    #Hover label font
    hoverlabel = dict(bgcolor = "white",
                      font_size = 14, font_family = 'Arial')
    )

#Add Link image
mapFig.add_layout_image(
    dict(
        source = linkImg,
        xref = 'paper', yref = 'paper',
        x = 0, y = 0,
        sizex = linkImg_widthProp-0.01, sizey = 1,
        xanchor = 'left', yanchor = 'bottom',
        layer = 'above'
    )
)

#Add map image
mapFig.add_layout_image(
    dict(
        source = mapImg,
        xref = 'paper', yref = 'paper', 
        x = linkImg_widthProp, y = 0,
        sizex = mapImg_widthProp, sizey = 1,
        xanchor = 'left', yanchor = 'bottom',
        layer = 'below'       
        )
    )

# #Add map border
# mapFig.add_trace(
#     go.Scatter(
#         x = [1-mapImg_widthProp, 1, 1, 1-mapImg_widthProp, 1-mapImg_widthProp],
#         y = [0, 0, 1, 1, 0],
#         line = dict(color = '#000000', width = 3),
#         mode = 'lines', hoverinfo = 'skip'
#         )
#     )

#Set invisible axes
mapFig.update_xaxes(visible = False, showgrid = False, fixedrange = True)
mapFig.update_yaxes(visible = False, showgrid = False, fixedrange = True)

#Add scatter of song location points
mapFig.add_trace(
    go.Scatter(
        x = songData['learntWhere_X'], y = songData['learntWhere_Y'],
        marker = dict(
            color = 'white', size = songPointSize,
            line = dict(color = '#373f87', width = 2)
                      ),
        mode = 'markers', name = '',
        hovertext = songData['song'].to_list(),
        customdata = songData['learntWhere'].to_list(),
        text = songData['songType'].to_list(),
        hovertemplate = '<b>Song:</b> %{hovertext}<br><b>Location:</b> %{customdata}<br><b>Type:</b> %{text}'
        )
    )

#Add ocarina images on points
for songInd in range(len(songData)):
    mapFig.add_layout_image(
        dict(
            source = ocarinaSmallImg,
            xref = 'paper', yref = 'paper',
            x = linkImg_widthProp + (1-linkImg_widthProp)*(songData['learntWhere_X'][songInd] / mapImg.size[0]),
            y = songData['learntWhere_Y'][songInd] / mapImg.size[1],
            sizex = 0.023, sizey = 0.023,
            xanchor = 'center', yanchor = 'middle',
            layer = 'above'
        )
    )

# %% Create app


####Layout not really working 
#### Review here: https://dash.plotly.com/interactive-graphing
#### May need to create figures in a different way?

#### Layout working better
#### Size scaling of images on graph is poor
#### Need to calculate or create size relative to axes coordinates

#Create the app
app = dash.Dash()

#Create app layout
app.layout = html.Div([
    
    #Create div for header and text section
    html.Div([
        
        #Create heading
        html.H1('The Legend of Zelda: Ocarina of Time'),        
        
        #Create introductory text
        html.P("There are many items that offer power ups and increase Link's abilities in Ocarina of Time. During the game — Link receives the Fairy Ocarina and later the Ocarina of Time, on which he can play a series of songs that are learnt throughout the game."),
        
        html.P("These songs are learnt at various locations across Hyrule, with each holding it's own unique power. This page allows you to explore the various songs Link learns across Hyrule, and the unique powers of each. Hover over the ocarina symbols to discover where each song is learnt and its general power type. Use the dropdown box to select specific songs to learn how each is played and more details on the power up the song provides."),
        
        ]), #end of header and intro text div
    
    #Create div for static map figure
    html.Div([
        
        #Add the figure via dcc graph
        dcc.Graph(figure = mapFig, responsive = True,
                  style = {'width': '78vw', 'height': '65vh', 'margin': '0em'},
                  config = {'displayModeBar': False})
        ],
        #Set the style for width
        #Width to height ratio determined via earlier calculations
        style = {'width': '78vw', 'float': 'left', 'display': 'inline-block'}        
        
        ), #end of static map div
    
    #Create div for dropdown box
    html.Div([
        
        #Add level 2 heading
        html.H2('Select Song:'),
        
        #Add the dropdown box
        dcc.Dropdown(id = 'songDropDown',
                     options = [{'label': songName, 'value': songName} for songName in songData['song']],
                     value = "Zelda's Lullaby")
        ],        
        #Set the style for width
        style = {'width': '20vw', 'float': 'center', 'display': 'inline-block'}
                
        ), #end of dropdown box div
    
    #Create div for song graph
    html.Div([
        
        #Add level 2 heading
        html.H2('How to Play:'),
        
        #Add the song graph
        dcc.Graph(id = 'songGraph', responsive = True,
                  style = {'width': '20vw', 'height': '15vh', 'margin': '0em'},
                  config = {'displayModeBar': False}),
        ],       
        #Set the style
        style = {'width': '20vw', 'float': 'center', 'display': 'inline-block'}
        
        ),
    
    #Create div for song type
    html.Div([
        
        #Add level 2 heading
        html.H2('Song Type:'),
        
        #Add the song type
        html.Div(id = 'songTypeText')
        
        ],       
        #Set the style for width
        style = {'width': '20vw', 'float': 'center', 'display': 'inline-block'}
        
        ),
    
    #Create div for song power
    html.Div([
        
        #Add level 2 heading
        html.H2('Song Power:'),
        
        #Add the song power
        html.Div(id = 'songPowerText')
        
        ],       
        #Set the style for width
        style = {'width': '20vw', 'float': 'center', 'display': 'inline-block'}
        
        ),
    
    
    ]) #end of overall parent

#Create the app callback for figure
@app.callback(Output(component_id = 'songGraph', component_property = 'figure'),
              Output(component_id = 'songTypeText', component_property = 'children'),
              Output(component_id = 'songPowerText', component_property = 'children'),
              [Input(component_id = 'songDropDown', component_property = 'value')])

#Define function to update song graph, song type text and song power
def graph_update(songDropDownValue):
    
    #Set song
    songName = songDropDownValue
    songInd = songData.index[songData['song'] == songName].tolist()[0]

    #Get notes in list form
    songNotes = songData[noteList].iloc[songInd].dropna().tolist()
    
    #Get the song type
    songType = songData['songType'].iloc[songInd]
    
    #Get the song type
    songPower = songData['power'].iloc[songInd]

    #Create blank figure
    fig = go.Figure()

    #Update figure layout
    fig.update_layout(
        #Sizing
        autosize = True,
        # width = musicFigWidth,
        # height = musicFigHeight,
        #Figure boundaries
        margin = dict(l = 10,
                      r = 10,
                      t = 10,
                      b = 10),
        #Axis limits
        xaxis_range = musicRangeX, yaxis_range = musicRangeY,
        #No legend
        showlegend = False,
        #Figure & background colour
        paper_bgcolor = 'rgba(255, 255, 255, 0)',
        plot_bgcolor = 'rgba(255, 255, 255, 0)')

    #Add lines for music bars
    for lineLevel in (100,300,500,700):
        fig.add_trace(
            go.Scatter(
                x = [0.5,850], y = [lineLevel, lineLevel],
                line = dict(color = '#000000', width = 2),
                mode = 'lines', hoverinfo = 'skip'
                )
            )
        
    #Set invisible axes
    fig.update_xaxes(visible = False, showgrid = False)
    fig.update_yaxes(visible = False, showgrid = False)
        
    #Add note images
    for noteInd in range(len(songNotes)):
        #Get the note name
        note = songNotes[noteInd]
        #Add image
        fig.add_layout_image(
            dict(
                source = buttonImg[note],
                xref = 'paper', yref = 'paper',
                x = 0.2 + (noteInd*0.1),
                y = buttonPlotVal[note] / (musicRangeY[1]-musicRangeY[0]),
                sizex = 0.25,
                sizey = 0.25,
                xanchor = 'center', yanchor = 'middle',
                layer = 'above'
            )
        )
    
    #Add treble clef image
    fig.add_layout_image(
        dict(
            source = clefImg,
            xref = 'paper', yref = 'paper',
            x = 0,
            y = 0.5,
            sizex = 0.125,
            sizey = 0.85,
            xanchor = 'left', yanchor = 'middle',
            layer = 'above'
        )
    )
    
    return fig, f'{songType} Song', songPower

#Run app
if __name__ == '__main__': 
    app.run_server()  

# %%% ----- End of app.py -----