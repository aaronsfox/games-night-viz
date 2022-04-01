# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    TODO:
        - Consider extra facts to hover on Link picture?
            > Hover on Navi to note that a song prompts them
            > Hover on the ocarina to discover where to find the different versions
            > Hover on Link's head to talk about the scarecrow song
            > Hover on the master sword to discover how a song links to this
    
"""

# %% Import packages

# import plotly.express as px
import plotly.io as pio
# pio.renderers.default = 'browser'
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
buttonPlotVal = {'A': 0, 'down': 200, 'right': 400, 'left': 500, 'up': 700}

#Set list for note names
noteList = ['note1', 'note2', 'note3', 'note4', 'note5', 'note6', 'note7', 'note8']

#Set note image size
notePointSize = 100

#Load treble clef image
clefImg = Image.open('img\\treble_clef.png')

# %% Create static map figure

##### TODO: consider extra hover points over link image

#Create blank figure
mapFig = go.Figure()

#Add map image
mapFig.add_layout_image(
    dict(
        source = mapImg,
        xref = 'x', yref = 'y', x = 0, y = 0,
        sizex = mapImg.size[0], sizey = mapImg.size[1],
        xanchor = 'left', yanchor = 'bottom',
        layer = 'below'       
        )
    )

#Add map border
mapFig.add_trace(
    go.Scatter(
        x = [0, mapImg.size[0], mapImg.size[0], 0, 0],
        y = [0, 0, mapImg.size[1], mapImg.size[1], 0],
        line = dict(color = '#000000', width = 3),
        mode = 'lines', hoverinfo = 'skip'
        )
    )

#Add Link image
mapFig.add_layout_image(
    dict(
        source = linkImg,
        xref = 'x', yref = 'y',
        x = -10, y = 0,
        sizex = linkImg.size[0] * (mapImg.size[1] / linkImg.size[1]), sizey = mapImg.size[1],
        xanchor = 'right', yanchor = 'bottom',
        layer = 'above'
    )
)

#Update figure layout
mapFig.update_layout(
    #Sizing
    autosize = False,
    width = mapImg.size[0] + (linkImg.size[0] * (mapImg.size[1] / linkImg.size[1])) + 10 + 10,
    height = mapImg.size[1] + 20,
    #Figure boundaries
    margin = dict(l = 10,
                  r = 10,
                  t = 10,
                  b = 10),
    #Axis limits
    xaxis_range = [(linkImg.size[0] * (mapImg.size[1] / linkImg.size[1]) * -1) - 10, 1000.5],
    yaxis_range = [-0.5,565.5],
    #Figure & background colour
    paper_bgcolor = 'rgba(255, 255, 255, 0)',
    plot_bgcolor = 'rgba(255, 255, 255, 0)',
    #Turn off legend
    showlegend = False,
    #Hover label font
    hoverlabel = dict(bgcolor = "white",
                      font_size = 14, font_family = 'Arial')
    )

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
            xref = 'x', yref = 'y',
            x = songData['learntWhere_X'][songInd] - (songPointSize * 0.65 / 2),
            y = songData['learntWhere_Y'][songInd] - (ocarinaSmallImg.size[1] * ((songPointSize * 0.65) / ocarinaSmallImg.size[0]) / 2),
            sizex = songPointSize * 0.65,
            sizey = ocarinaSmallImg.size[1] * ((songPointSize * 0.65) / ocarinaSmallImg.size[0]),
            xanchor = 'left', yanchor = 'bottom',
            layer = 'above'
        )
    )

# #Show figure
# fig.show()

#Test write to HTML
mapFig.write_html('testHTML.html', auto_open = True,
               config = dict(displayModeBar=False))

# #Test write to PNG
# fig.write_image('testPNG.png')



# %% Sample static song figure

#Set song
songName = "Bolero of Fire"
songInd = songData.index[songData['song'] == songName].tolist()[0]

#Calculate figure size ratio for plotting notes
musicFigWidth = 500
musicFigHeight = 120
ySizeRatio = musicFigWidth / musicFigHeight
notePointSizeY = notePointSize * ySizeRatio

#Set axis ranges for calculations
musicRangeX = [0.5, 850]
musicRangeY = [-350,1100]

#Calculate treble clef size
clefSizeX = 200
clefSizeY = clefSizeX * ySizeRatio

#Get notes in list form
songNotes = songData[noteList].iloc[songInd].dropna().tolist()

#Create blank figure
fig = go.Figure()

#Update figure layout
fig.update_layout(
    #Sizing
    autosize = False,
    width = musicFigWidth,
    height = musicFigHeight,
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
            xref = 'x', yref = 'y',
            x = ((noteInd+1) * 100) + (notePointSize / 4),
            y = buttonPlotVal[note] - (notePointSizeY / 2),
            sizex = notePointSize,
            sizey = notePointSizeY,
            xanchor = 'right', yanchor = 'bottom',
            layer = 'above'
        )
    )
    
#Add treble clef image
fig.add_layout_image(
    dict(
        source = clefImg,
        xref = 'x', yref = 'y',
        x = 7.5,
        y = 0,
        sizex = clefSizeX / 2,
        sizey = clefSizeY,
        xanchor = 'left', yanchor = 'bottom',
        layer = 'above'
    )
)

# #Show figure
# fig.show()

#Test write to HTML
fig.write_html('testHTML.html', auto_open = True,
               config = dict(displayModeBar=False))

# fig.write_image('testPNG.png')

# %% Start testing Dash


#### TODO:
    #### > Layout structure, side by side etc.
        #https://medium.com/analytics-vidhya/dash-for-beginners-dash-plotly-python-fcd1fe02b749
        #https://dash.plotly.com/interactive-graphing
        #https://community.plotly.com/t/horizontally-stack-components/10806
    #### > Clean up code
    #### > Change font type in dropwdown
    #### > Add text box element for description
    #### > Consider playing the song?
    #### > Ensure that images are in appropriate 'assets' folder for deploying
    #### > Pale coloured background
    #### > Add heading
        #https://stackoverflow.com/questions/69662148/how-to-use-a-local-font-otf-file-in-dash-python
    #### > Add general text description of how to use
    #### > Add title to song graph?
    #### > Add title to dropdown box
    

#Create the app
app = dash.Dash()

#Create app layout
app.layout = html.Div(id = 'parent', children = [
        
        #Add map display figure
        dcc.Graph(figure = mapFig,
                  config = {'displayModeBar': False}),
        
        #Create dropdown
        dcc.Dropdown(id = 'songDropDown',
        options = [{'label': songName, 'value': songName} for songName in songData['song']],
        value = "Zelda's Lullaby"),
        
        #Add song graph
        dcc.Graph(id = 'songGraph',
                  config = {'displayModeBar': False}),
        
    ])

#Create the app callbacks
@app.callback(Output(component_id = 'songGraph', component_property = 'figure'),
              [Input(component_id = 'songDropDown', component_property = 'value')])

#Define function to update song graph
def graph_update(songDropDownValue):
    
    #### TODO: can probably pull a few basic variables out of this to make it 
    #### more legible and easy to digest...
    
    #Set song
    songName = songDropDownValue
    songInd = songData.index[songData['song'] == songName].tolist()[0]

    #Calculate figure size ratio for plotting notes
    musicFigWidth = 500
    musicFigHeight = 120
    ySizeRatio = musicFigWidth / musicFigHeight
    notePointSizeY = notePointSize * ySizeRatio

    #Set axis ranges for calculations
    musicRangeX = [0.5, 850]
    musicRangeY = [-350,1100]

    #Calculate treble clef size
    clefSizeX = 200
    clefSizeY = clefSizeX * ySizeRatio

    #Get notes in list form
    songNotes = songData[noteList].iloc[songInd].dropna().tolist()

    #Create blank figure
    fig = go.Figure()

    #Update figure layout
    fig.update_layout(
        #Sizing
        autosize = False,
        width = musicFigWidth,
        height = musicFigHeight,
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
                xref = 'x', yref = 'y',
                x = ((noteInd+1) * 100) + (notePointSize / 4),
                y = buttonPlotVal[note] - (notePointSizeY / 2),
                sizex = notePointSize,
                sizey = notePointSizeY,
                xanchor = 'right', yanchor = 'bottom',
                layer = 'above'
            )
        )
        
    #Add treble clef image
    fig.add_layout_image(
        dict(
            source = clefImg,
            xref = 'x', yref = 'y',
            x = 7.5,
            y = 0,
            sizex = clefSizeX / 2,
            sizey = clefSizeY,
            xanchor = 'left', yanchor = 'bottom',
            layer = 'above'
        )
    )
    
    return fig 

#Run app
if __name__ == '__main__': 
    app.run_server()    

# %% ----- End of zelda_oot_songs.py -----