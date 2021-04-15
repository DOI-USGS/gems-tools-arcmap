"""GeMS_RebuildMapUnits
A simpler version of the GeMS Make Polys tool
1) Will not build MapUnitPolys from scratch. Use the ArcGIS Feature to Polygon tool for that.
2) Does not concatenate a label points feature class from map units converted to points
   and an optional label points feature class. It uses one or the other.
3) No error checking between polygon and optional label points attributes. 
   Use colored label points for that.
   
Use this tool in ArcMap while editing ContactsAndFaults linework to quickly rebuild the 
MapUnitPolygons feature class as you change the shape of polygons or want to add new ones.
"""

import arcpy
import os
import sys
import re
from GeMS_utilityFunctions import *

versionString = 'GeMS_RebuildMapUnits_Arc10.py, version of 14 April 2021'
rawurl = 'https://raw.githubusercontent.com/usgs/gems-tools-arcmap/master/Scripts/GeMS_RebuildMapUnits_Arc10.py'
checkVersion(versionString, rawurl, 'gems-tools-arcmap')

def get_trailing_number(s):
    m = re.search(r'\d+$', s)
    return int(m.group()) if m else 0

def findLyr(lname):
    mxd = arcpy.mapping.MapDocument('CURRENT')
    #for df in arcpy.mapping.ListDataFrames(mxd):
    lList = arcpy.mapping.ListLayers(mxd, '*', mxd.activeDataFrame)
    for lyr in lList:
        if lyr.longName == lname:
            pos = lList.index(lyr)
            if pos == 0:
                refLyr = lList[pos + 1]
                insertPos = "BEFORE"
            else:
                refLyr = lList[pos - 1]
                insertPos = "AFTER"
                
            return [lyr, mxd.activeDataFrame, refLyr, insertPos]

def pm(msg, severity=0): 
	# prints msg to screen and adds msg to the geoprocessor (in case this is run as a tool) 
	# pm(msg) 
	try: 
	  for string in msg.split('\n'): 
		# Add appropriate geoprocessing message 
		if severity == 0: 
			arcpy.AddMessage(string) 
		elif severity == 1: 
			arcpy.AddWarning(string) 
		elif severity == 2: 
			arcpy.AddError(string) 
	except: 
		pass
            
#********************************************************************************************
#Get the parameters
lineLayer = arcpy.GetParameterAsText(0)
polyLayer = arcpy.GetParameterAsText(1)
labelPoints = arcpy.GetParameterAsText(2)
saveMUP = arcpy.GetParameterAsText(3)

#collect the findLyr properties
lyrProps = findLyr(polyLayer)
lyr = lyrProps[0]                               #the layer object
df = lyrProps[1]                                #the data frame within which the layer resides
refLyr = lyrProps[2]                            #a layer above or below which the layer resides
insertPos = lyrProps[3]                         #index above or below the reference layer
newPolys = lyr.dataSource                       #the path to the dataSource of the polygon layer
discName = os.path.basename(lyr.dataSource)     #the name in the geodatabase of the datasource

# save a temporary layer file for the polygons to save rendering and other settings
# including joins to other tables
# .lyr is saved to the folder of the geodatabase
# lyr.workspacePath returnd the gdb, not a feature dataset
lyrPath = os.path.join(os.path.dirname(lyr.workspacePath), lyr.name + '.lyr')
if arcpy.Exists(lyrPath):
    os.remove(lyrPath)
		
pm("  saving " + polyLayer + ' to ' + lyrPath)
arcpy.SaveToLayerFile_management(lyr, lyrPath, "RELATIVE")

#set the workspace variable to the workspace of the feature class
#and get the name of the feature dataset
dsPath = os.path.dirname(newPolys)
arcpy.env.workspace = dsPath

try:
	#remove join if one is there
	arcpy.RemoveJoin_management(lyr)
except:
	pass

# make a labelPoints feature class if one was not provided
if labelPoints in ['#', '', None]:
    #create the labelPoints name
    labelPoints = discName + '_tempLabels'
    testAndDelete(labelPoints)

    #check for an old copy of labelpoints
    if arcpy.Exists(labelPoints):
        arcpy.Delete_management(labelPoints)
    
    #create points from the attributed polygons
    arcpy.FeatureToPoint_management(lyr.dataSource, labelPoints, 'INSIDE')

#and now remove the layer from the map
arcpy.mapping.RemoveLayer(df, lyr)

#save a copy of the polygons fc or delete
if saveMUP == 'true':
    # get new name
    pfcs = arcpy.ListFeatureClasses(discName + "*", "Polygon")
    maxN = 0
    for pfc in pfcs:
        try:
            n = int(get_trailing_number(pfc))
            if n > maxN:
                maxN = n
        except:
            pass
    oldPolys = lyr.dataSource + str(maxN + 1)
    pm("  saving " + polyLayer + ' to ' + oldPolys)
   
    try:
        oldPolysPath = os.path.join(dsPath, oldPolys)
        arcpy.Copy_management(lyr.dataSource, oldPolysPath, "FeatureClass")
    except:
        pm("  arcpy.Copy_management(mup,oldPolys) failed. Maybe you need to close ArcMap?")
        sys.exit()


pm("  deleting " + lyr.dataSource)
arcpy.Delete_management(lyr.dataSource)
pm("  recreating " + newPolys + " from new linework")

# select all unconcealed lines
where = '"IsConcealed"  NOT IN (\'Y\',\'y\')'

arcpy.SelectLayerByAttribute_management(lineLayer, "NEW_SELECTION", where)
arcpy.FeatureToPolygon_management(lineLayer, newPolys, '#', '#', labelPoints)
arcpy.RefreshCatalog(arcpy.env.workspace)
arcpy.SelectLayerByAttribute_management(lineLayer, "CLEAR_SELECTION")

# add the layer file 
pm("  adding " + lyrPath + " to the map")
addLyr = arcpy.mapping.Layer(lyrPath)
arcpy.mapping.InsertLayer(df, refLyr, addLyr, insertPos)
