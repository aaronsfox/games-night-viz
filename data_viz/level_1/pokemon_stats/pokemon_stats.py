# -*- coding: utf-8 -*-
"""
@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Data: https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_base_stats_(Generation_I)
    
"""

# %%% Import packages

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib import rcParams
from matplotlib import gridspec
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import FancyBboxPatch, Rectangle
import os
import numpy as np
import cv2

# %%% Define functions

#Function to crop the whitespace from the sprite images
#See: https://stackoverflow.com/questions/63001988/how-to-remove-background-of-images-in-python

def cropWhiteSpace(imgFile, outFile):    
    
    # load image
    img = cv2.imread(imgFile)
    
    # convert to graky
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # threshold input image as mask
    mask = cv2.threshold(gray, 250, 255, cv2.THRESH_BINARY)[1]
    
    # negate mask
    mask = 255 - mask
    
    # linear stretch so that 127.5 goes to 0, but 255 stays 255
    mask = (2*(mask.astype(np.float32))-255.0).clip(0,255).astype(np.uint8)
    
    # put mask into alpha channel
    result = img.copy()
    result = cv2.cvtColor(result, cv2.COLOR_BGR2BGRA)
    result[:, :, 3] = mask
    
    # save resulting masked image
    cv2.imwrite(outFile, result)

# %%% Set-up

#Add custom fonts for use with matplotlib
fontDir = [os.getcwd()+'\\fonts']
for font in font_manager.findSystemFonts(fontDir):
    font_manager.fontManager.addfont(font)
    
#Set other matplotlib parameters
rcParams['font.weight'] = 'bold'
rcParams['axes.labelsize'] = 12
rcParams['axes.titlesize'] = 16
rcParams['axes.linewidth'] = 1.5
rcParams['axes.labelweight'] = 'bold'
rcParams['legend.fontsize'] = 10
rcParams['xtick.major.width'] = 1.5
rcParams['ytick.major.width'] = 1.5
rcParams['legend.framealpha'] = 0.0
rcParams['savefig.dpi'] = 300
rcParams['savefig.format'] = 'pdf'

#Set colouring for stat values
statColours = ['#e13620', '#6376b8', '#f4ab6f', '#23afcc']

#Set stat list to work through
statList = ['attack', 'defense', 'speed', 'special']

#Set y-level to plot each stat at
statY = [0.7, 0.5, 0.3, 0.1]

#Load the pokemon stats dataset
pokemonData = pd.read_csv('data\\pokemonStats_gen1.csv')

#Slightly tweak the order of the data frame to set the starters in the right order
#Create new order
newOrder = np.concatenate((np.array((1,4,5,2,6,7,3,8,9)),
                          np.linspace(10,151,151-9, dtype = int)),
                          axis = 0)
#Add to dataframe
pokemonData['plotOrder'] = newOrder
#Sort the dataframe with new order and reset the index
pokemonData.sort_values('plotOrder', inplace = True)
pokemonData.reset_index(drop = True, inplace = True)

#Create new versions of sprite images with background removed
for pokemon in list(pokemonData['name']):
    #Get the pokemon idNo
    idNo = pokemonData.loc[pokemonData['name'] == pokemon, ['idNo']].values[0][0]
    #Crop the white space
    cropWhiteSpace(f'img\\sprites\\{idNo}.png',
                   f'img\\sprites\\{idNo}_bgRemoved.png')

# %% Create visualisation

#Set up the figure at ~A3 size
fig = plt.figure(figsize = (11,16))

#Set figure colouring
fig.patch.set_facecolor('#fffaf0')

#Create the desired grid of axes to work with

#Set grid size for axes
gridSpec = gridspec.GridSpec(18, 24)

#Update spacing of grid
gridSpec.update(left = 0.05, right = 0.95,
                bottom = 0.05, top = 0.75, 
                wspace = 0.1, hspace = 0.2)

#Create first row of axes for starter pokemon
for nGrid in range(6):
    plt.subplot(gridSpec.new_subplotspec((0,nGrid*4), colspan = 4, rowspan = 4))
    
#Create second row of axes for starter pokemon evolutions
for nGrid in range(12):
    plt.subplot(gridSpec.new_subplotspec((4,nGrid*2), colspan = 2, rowspan = 2))
    
#Create remaining rows for the rest of the pokemon
#This requires and extra 6 rows
for nRow in range(6,18):
    for nGrid in range(24):
        plt.subplot(gridSpec.new_subplotspec((nRow,nGrid), colspan = 1, rowspan = 1))
        
#Get all axes off the figure
allAx = fig.get_axes()
    
#Get every second axes starting at the first to allocate to pokemon sprite images
pokemonAx = allAx[::2]

#Get every second axes starting at the second to allocate the stats bars to
statsAx = allAx[1::2]

#Loop through Pokemon and plot data
for pokemon in list(pokemonData['name']):
    
    #Get the pokemon index and idNo
    ind = pokemonData.index[pokemonData['name'] == pokemon][0]
    idNo = pokemonData.loc[pokemonData['name'] == pokemon, ['idNo']].values[0][0]
    
    #Check id no range to specify plotting parameters
    if ind < 3:
        #Zoom factor for sprite
        zoomFac = 2 #for starter pokemon
        #Font size for hp font
        hpFontSize = 6
        #Linewidth for boxes
        lineWidth = 1
    elif ind >= 3 and ind <= 8:
        #Zoom factor for sprite
        zoomFac = 1 #for starter evolutions
        #Font size for hp font
        hpFontSize = 4
        #Linewidth for boxes
        lineWidth = 2/3
    else:
        #Zoom factor for sprite
        zoomFac = 0.4
        #Font size for hp font
        hpFontSize = 2
        #Linewidth for boxes
        lineWidth = 1/3
        
    #Grab axes to plot on from lists
    spriteAx = pokemonAx[ind]
    dataAx = statsAx[ind]
        
    #Create the sprite axes
    
    #Remove background
        
    #Add the sprite image to the axes
    #Load image
    pokemonImg = plt.imread(f'img\\sprites\\{idNo}_bgRemoved.png')
    #Create offset image
    imOffset = OffsetImage(pokemonImg, zoom = zoomFac)
    #Create annotation box
    annBox = AnnotationBbox(imOffset, (0.5,0.5),
                            frameon = False,
                            box_alignment = (0.5,0.5),
                            xycoords = spriteAx.transAxes,
                            pad = 0)
    #Add image
    spriteAx.add_artist(annBox)
    
    #Turn sprite axis off
    spriteAx.axis('off')
    
    #Create the stats axis
    
    #Adjust x-axis limit for spacing
    dataAx.set_xlim([0,1.6])
    
    #HP bar
    #Get the current pokemons absolute hp and normalised to highest of all pokemon
    hp = pokemonData['hp'][ind]
    hpNorm = pokemonData['hp'][ind] / np.max(pokemonData['hp'].to_numpy())
    #Create the fancy hp box
    hpBox = FancyBboxPatch((0.025,0.9),
                           hpNorm-0.05, 0,
                           boxstyle = 'round,pad=0.025',
                           clip_on = False,
                           edgecolor = '#3d3d3d', facecolor = '#3d3d3d')
    #Add hp box to axes
    dataAx.add_patch(hpBox)
    #Add hp text
    dataAx.text(hpNorm+0.05, 0.9, f'{hp} / {hp} HP',
                font = 'PKMN RBYGSC', color = 'black', fontsize = hpFontSize,
                ha = 'left', va = 'top', clip_on = False)
    
    #Stats
    #Loop through the list of stats to plot
    for statNo in range(len(statList)):
        #Get stat value
        statVal = pokemonData[statList[statNo]][ind]
        #Get divisible by 10 and remainder
        stat10 = int(np.floor(statVal/10))
        statRem = statVal % 10 / 10
        #Loop through the round 10 blocks
        for blockNo in range(stat10):
            #Create the square
            statBox = Rectangle((blockNo / 20 / dataAx.get_data_ratio(),
                                 statY[statNo] - 0.025),
                                0.05 / dataAx.get_data_ratio(), 0.05,
                                clip_on = False,
                                edgecolor = 'black',
                                linewidth = lineWidth,
                                facecolor = statColours[statNo])
            #Add to axis
            dataAx.add_patch(statBox)
        #Add the remainder block
        #Create box
        statBox = Rectangle((stat10 / 20 / dataAx.get_data_ratio(),
                             statY[statNo] - 0.025),
                            0.05 * statRem / dataAx.get_data_ratio(), 0.05,
                            clip_on = False,
                            edgecolor = 'black',
                            linewidth = lineWidth,
                            facecolor = statColours[statNo])
        #Add to axis
        dataAx.add_patch(statBox)
    
    #Turn data axis off
    dataAx.axis('off')

#Turn off extra axes
allAx[-1].axis('off')
allAx[-2].axis('off')
allAx[-3].axis('off')
allAx[-4].axis('off')
    
#Add pokemon logo header
#Load image
logoImg = plt.imread('img\\logo\\pokemonBlack.png')
#Use first axes to map the image as a reference against
logoAx = allAx[0]
#Create offset image
imOffset = OffsetImage(logoImg, zoom = 0.20)
#Create annotation box
annBox = AnnotationBbox(imOffset, (0.5,0.925),
                        frameon = False,
                        box_alignment = (0.5,0.5),
                        xycoords = fig.transFigure,
                        pad = 0)
#Add image
logoAx.add_artist(annBox)

#Add generation one text header
fig.text(0.5, 0.84,
         'Generation I',
         font = 'Pokemon Solid', fontsize = 25,
         ha = 'center', va = 'center')

#Add descriptive text
fig.text(0.5, 0.80,
         'Base HP and stats of generation I Pokemon',
         font = 'Lato Regular', fontsize = 10,
         ha = 'center', va = 'center')
fig.text(0.5, 0.78,
         'Each block represents 10 stat points for the category',
         font = 'Lato Regular', fontsize = 10,
         ha = 'center', va = 'center')

#Add legend text
fig.text(0.5, 0.76,
         '          Attack               Defense               Speed               Special',
         font = 'Lato Regular', fontsize = 7,
         ha = 'center', va = 'center')

#Add legend patches
#Set x-locations on figure (manually & tediously determined)
legPatchLocs = [0.362, 0.44, 0.525, 0.603]
#Loop through and add patches
for legPatchNo in range(len(statColours)):
    #Create the square
    statBox = Rectangle((legPatchLocs[legPatchNo],0.756),
                        0.01, 0.01,
                        clip_on = False,
                        edgecolor = 'black',
                        linewidth = 1,
                        facecolor = statColours[legPatchNo],
                        transform = fig.transFigure)
    #Add to axis
    logoAx.add_patch(statBox)

#Add data source and details text
fig.text(0.995, 0,
         'Author: Aaron Fox (@aaron_s_fox) | Source: Bulbapedia',
         font = 'Lato Regular', fontsize = 10,
         ha = 'right', va = 'bottom')

#Save figure
plt.savefig('pokemon_stats.png', format = 'png', 
            facecolor = fig.get_facecolor(), edgecolor = 'none',
            dpi = 600)

# %%% ----- End of pokemon_stats.py -----