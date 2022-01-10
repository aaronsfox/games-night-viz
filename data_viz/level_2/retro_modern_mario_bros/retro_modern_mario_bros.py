# -*- coding: utf-8 -*-
"""

@author: 
    Aaron Fox
    Centre for Sport Research
    Deakin University
    aaron.f@deakin.edu.au
    
    Script that collates info from the Super Mario Bros data from level 2 of
    #GamesNightViz and creates some 'pixel art' from this
    
"""

# %% Import packages

import os
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.colors import ListedColormap
from matplotlib import font_manager
import pandas as pd
import requests
import shutil
import numpy as np
import random

# %% Define functions

#Convert image to black and white
def blackAndWhite(input_image_path, output_image_path):
   color_image = Image.open(input_image_path)
   bw = color_image.convert('L')
   bw.save(output_image_path)
    
#Function to resize pixels of image
def resizePixels(imagePath, resizeFactor, outputFile):
    """
    imagePath: path to image file
    resizeFactor: scale factor to apply to image (e.g. 0.5)
    outputFile: output file name
    
    """
    #read file
    img = Image.open(imagePath)

    #convert to resized image
    newSize = (int(img.size[0] * resizeFactor),
               int(img.size[1] * resizeFactor))
    newImg = img.resize(newSize,Image.BILINEAR)

    #Save output image
    newImg.save(outputFile)
    
#Function to create the colourmaps
def createColourMap(rgbTuple):
    N = 256
    colourMap = np.ones((N, 4))
    colourMap[:, 0] = np.linspace(rgbTuple[0]/256, 1, N) # R
    colourMap[:, 1] = np.linspace(rgbTuple[1]/256, 1, N) # G
    colourMap[:, 2] = np.linspace(rgbTuple[2]/256, 1, N)  # B
    newCmap = ListedColormap(colourMap)
    return newCmap

#Function to create pixel art characters
def superPixelBros(characterName, randomSeed):
    
    #Create a resized version of the image for better pixel art
    #33% looks like a good visual:time cost balance here
    resizePixels(f'img\\{characterName}_main.png', 1/3, f'img\\{characterName}_main_resized.png')
    
    #Load in the main image
    mainImg = Image.open(f'img\\{characterName}_main_resized.png')
    
    #Convert to RGB
    mainImgRGBA = mainImg.convert('RGBA')
    
    #Create figure
    #Determine ratio of figure size based on image size
    #Need to ensure that 10 is the max size on one of the lengths to ensure font
    #point size remains consistent across different figures
    if mainImgRGBA.size[1] / mainImgRGBA.size[0] < 1:
        fig, ax = plt.subplots(nrows = 1, ncols = 1,
                                figsize = (10, 10 * mainImgRGBA.size[1] / mainImgRGBA.size[0]))
    elif mainImgRGBA.size[1] / mainImgRGBA.size[0] > 1:
        fig, ax = plt.subplots(nrows = 1, ncols = 1,
                                figsize = (10 * mainImgRGBA.size[0] / mainImgRGBA.size[1], 10))
    else:
        fig, ax = plt.subplots(nrows = 1, ncols = 1,
                               figsize = (10, 10))
        
    
    #Set the axes limits to that of the image pixels
    ax.set_xlim([0,mainImgRGBA.size[0]])
    ax.set_ylim([0,mainImgRGBA.size[1]])
    
    #Match up axis origin with image
    ax.invert_yaxis()
    
    #Remove tick labels
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    
    #Get rid of ticks
    ax.tick_params(axis = 'both', length = 0)
    
    #Set tight layout to fill figure canvas
    plt.tight_layout()
    
    #Get the total pixel count
    totalPixelCount = mainImg.size[0] * mainImg.size[1]
    
    #Get total non-white pixel count
    blankPixelCount = 0
    for nrow in range(mainImgRGBA.size[0]):
        for ncol in range(mainImgRGBA.size[1]):
            if mainImgRGBA.getpixel((nrow,ncol))[3] == 0:
                blankPixelCount += 1
    dataPixelCount = totalPixelCount - blankPixelCount
            
    #Determine the number of each enemy/item required based on pixel count
    nItems = []
    for itemInd in range(len(countData)):
        #ROund up using ceil just to cover all data pixels
        nItems.append(int(np.ceil(countData['Proportion'][itemInd] * dataPixelCount)))
        
    #Create list of item names based on their count
    itemList = []
    for itemInd in range(len(countData)):
        itemList.append([countData['Name'][itemInd]] * nItems[itemInd])
    itemListFlat = [ii for sublist in itemList for ii in sublist]
    
    #Randomly sort list of enemies/items
    random.seed(randomSeed) #set seed for consistency
    random.shuffle(itemListFlat)
    
    #Set counter for grabbing images
    imgCounter = 0
    
    #Loop through image pixels and plot data
    for nrow in range(mainImgRGBA.size[0]):
        for ncol in range(mainImgRGBA.size[1]):
            
            #Check for non-white pixel
            if mainImgRGBA.getpixel((nrow,ncol))[3] != 0:
                
                #Get the current pixels RGB
                imgRGB = mainImgRGBA.getpixel((nrow,ncol))[0:3]
                
                #Create the colourmap for this iteration
                imgCmap = createColourMap(imgRGB)
                
                #Load the relevant image
                currImg = mpimg.imread(f'img\\{itemListFlat[imgCounter]}_BW.png')
                
                #Show the image and set it to the data coordinates using extent
                ax.imshow(currImg, cmap = imgCmap, origin = 'upper',
                          extent = (nrow-0.5,nrow+0.5,ncol+0.5,ncol-0.5),
                          alpha = mainImgRGBA.getpixel((nrow,ncol))[3]/255)
                
                #Add to the image counter to progress through the different images            
                imgCounter += 1
    
    #Remove axis
    ax.axis('off')
    
    #Add label using custom Mario Bros font
    fig.text(0.025, 0.95, characterName.upper(),
             font = 'Super Mario Bros.', fontsize = 50,
             ha = 'left', va = 'center')
    
    #Add data source and details text
    fig.text(0.025, 0,
             'Author: Aaron Fox (@aaron_s_fox) | Source: MarioWiki',
             fontsize = 8, fontweight = 'bold',
             ha = 'left', va = 'bottom')
    
    
    #Save figure
    plt.savefig(f'{characterName}_pixelArt.png', format = 'png', 
                facecolor = fig.get_facecolor(), edgecolor = 'none',
                dpi = 300)
    
    #Display confirmation
    print(f'Saved {characterName.capitalize()} pixel art.')
    
    #Close figure
    plt.close()

# %% Set-up

#Add custom fonts for use with matplotlib
fontDir = [os.getcwd()+'\\fonts']
for font in font_manager.findSystemFonts(fontDir):
    font_manager.fontManager.addfont(font)

#Load the various datasets

#Enemy count
enemyCount = pd.read_csv('data\\enemyCount.csv')

#Item count
itemCount = pd.read_csv('data\\itemCount.csv')

#Image links
imgLinks = pd.read_csv('data\\imgLinks.csv')

# %% Download and clean sprite images

#Loop through images/items
for imgInd in range(len(imgLinks)):
    
    #Get the download link
    imgDownloadLink = imgLinks['Image'][imgInd]
    
    #Get the image data
    imgData = requests.get(imgDownloadLink, stream = True)
    
    #Get image name
    imgName = imgLinks['Name'][imgInd]
    
    #Save the image
    with open(f'img\\{imgName}.gif', 'wb') as outFile:
        shutil.copyfileobj(imgData.raw, outFile)
        
    #Convert to black and white png for easier use
    blackAndWhite(f'img\\{imgName}.gif', f'img\\{imgName}_BW.png')

# %% Calculate item/image proportion

#Sum enemies across worlds
enemySum = enemyCount.groupby(['Name']).sum().reset_index()

#Sum items across worlds
itemSum = itemCount.groupby(['Name']).sum().reset_index()

#Loop through enemies/items that have images and extract their counts

#Set dictionary to store data in
countDict = {'Name': [], 'Count': []}

#Loop through images
for imgInd in range(len(imgLinks)):
    #Append name to dictionary
    countDict['Name'].append(imgLinks['Name'][imgInd])
    #Check if enemy or item
    if imgLinks['Item/Enemy'][imgInd] == 'Enemy':
        #Get count from appropriate dataframe
        countDict['Count'].append(enemySum.loc[enemySum['Name'] == imgLinks['Name'][imgInd],
                                               ['Count']].values[0][0])
    else:
        #Get count from appropriate dataframe
        countDict['Count'].append(itemSum.loc[itemSum['Name'] == imgLinks['Name'][imgInd],
                                              ['Count']].values[0][0])
        
#Convert to dataframe
countData = pd.DataFrame.from_dict(countDict)

#Loop through enemies/items and determine relative in-game proportion
propVals = []
for itemInd in range(len(countData)):
    propVals.append(countData['Count'][itemInd] / countData['Count'].sum())
countData['Proportion'] = propVals
    
# %% Create pixel art

# NOTE: for some reason my Python console crashes when trying to run this function
# multiple times, hence I had to run each of the characters individually staring
# with a new console each time. Who knows why this or anything happens in Python...?

#Mario
superPixelBros('mario', 12345)

#Luigi
superPixelBros('luigi', 54321)

#Peach
superPixelBros('peach', 13579)

#Bowser
superPixelBros('bowser', 97531)

# %%% ----- End of retro_modern_mario_bros.py -----