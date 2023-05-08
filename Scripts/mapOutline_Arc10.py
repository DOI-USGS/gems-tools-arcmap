# MapOutline.py
#   generates rectangular (in lat-long) map outline and
#   appropriate tics in projection of user's choosing. Result is
#   stored in an existing geodatabase
#
#   For complex map outlines, try several runs and intersect the results.
#
# Ralph Haugerud, U.S. Geological Survey
#   rhaugerud@usgs.gov
#
# 21 February 2021.  Import GeMS_utilityFunctions, drop local version of addMsgAndPrint

import arcpy, sys, os, os.path
from GeMS_utilityFunctions import *

versionString = 'mapOutline_Arc10.py, version of 21 February 2021'
rawurl = 'https://raw.githubusercontent.com/doi-usgs/gems-tools-arcmap/master/Scripts/mapOutline_Arc10.py'
checkVersion(versionString, rawurl, 'gems-tools-arcmap')

"""
INPUTS
maxLongStr  # in D M S, separated by spaces. Decimals OK.
            #   Note that west values must be negative
            #   -122.625 = -122 37 30
            #   if value contains spaces it should be quoted
minLatStr   # DITTO
dLong       # in decimal degrees OR decimal minutes
            #   values <= 5 are assumed to be degrees
            #   values  > 5 are assumed to be minutes
dLat        # DITTO
            # default values of dLong and dLat are 7.5
ticInterval # in decimal minutes! Default value is 2.5
isNAD27     # NAD27 or NAD83 for lat-long locations
outgdb      # existing geodatabase to host output feature classes
outSpRef    # output spatial reference system
scratch     # scratch folder, must be writable
"""

c = ','
degreeSymbol = '°'
minuteSymbol = "'"
secondSymbol = '"'

def dmsStringToDD(dmsString):
    dms = dmsString.split()
    dd = abs(float(dms[0]))
    if len(dms) > 1:
        dd = dd + float(dms[1])/60.0
    if len(dms) > 2:
        dd = dd + float(dms[2])/3600.0
    if dms[0][0] == '-':
        dd = 0 - dd
    return(dd)

def ddToDmsString(dd):
    dd = abs(dd)
    degrees = int(dd)
    minutes = int((dd-degrees)* 60)
    seconds = int(round((dd-degrees-(minutes/60.0))* 3600))
    if seconds == 60:
        minutes = minutes+1
        seconds = 0
    dmsString = str(degrees)+degreeSymbol
    dmsString = dmsString+str(minutes)+minuteSymbol
    if seconds <> 0:
        dmsString = dmsString+str(seconds)+secondSymbol
    return dmsString
        

addMsgAndPrint(versionString)

## MAP BOUNDARY
# get and check inputs

SELongStr = sys.argv[1]
SELatStr = sys.argv[2]
dLong = float(sys.argv[3])
dLat = float(sys.argv[4])
ticInterval = float(sys.argv[5])
if sys.argv[6] == 'true':
    isNAD27 = True
else:
    isNAD27 = False

if isNAD27:
    xycs = 'GEOGCS["GCS_North_American_1927",DATUM["D_North_American_1927",SPHEROID["Clarke_1866",6378206.4,294.9786982]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433],AUTHORITY["EPSG",4267]]'
else:
    xycs = 'GEOGCS["GCS_North_American_1983",DATUM["D_North_American_1983",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433],AUTHORITY["EPSG",4269]]'


outgdb = sys.argv[7]
outSpRef = sys.argv[8]
scratch = sys.argv[9]

# set workspace
arcpy.env.workspace = outgdb
arcpy.env.scratchWorkspace = scratch
# calculate maxLong and minLat, dLat, dLong, minLong, maxLat
maxLong = dmsStringToDD(SELongStr)
minLat = dmsStringToDD(SELatStr)
if dLong > 5:
    dLong = dLong/60.0
if dLat > 5:
    dLat = dLat/60.0
minLong = maxLong - dLong
maxLat = minLat + dLat

# test for and delete any feature classes to be created
for xx in ['xxMapOutline','MapOutline','xxTics','Tics']:
    if arcpy.Exists(xx):
        arcpy.Delete_management(xx)
        addMsgAndPrint('  deleted feature class '+xx)

## MAP OUTLINE
# make XY file for map outline
addMsgAndPrint('  writing map outline file')
genf = open(scratch+'/xxxbox.csv','w')
genf.write('LONGITUDE,LATITUDE\n')
genf.write(str(minLong)+c+str(maxLat)+'\n')
genf.write(str(maxLong)+c+str(maxLat)+'\n')
genf.write(str(maxLong)+c+str(minLat)+'\n')
genf.write(str(minLong)+c+str(minLat)+'\n')
genf.write(str(minLong)+c+str(maxLat)+'\n')
genf.close()
# convert XY file to .dbf table
boxdbf = arcpy.CreateScratchName('xxx','.dbf','',scratch)
boxdbf = os.path.basename(boxdbf)
arcpy.TableToTable_conversion(scratch+'/xxxbox.csv',scratch,boxdbf)
# make XY event layer from .dbf table
arcpy.MakeXYEventLayer_management(scratch+'/'+boxdbf,'LONGITUDE','LATITUDE','boxlayer',xycs)
# convert event layer to preliminary line feature class with PointsToLine_management
arcpy.PointsToLine_management('boxlayer','xxMapOutline')
# densify MapOutline
arcpy.Densify_edit('xxMapOutline','DISTANCE',0.0001)

# project to correct spatial reference
### THIS ASSUMES THAT OUTPUT COORDINATE SYSTEM IS HARN AND WE ARE IN OREGON OR WASHINGTON!!
if isNAD27:
    geotransformation = 'NAD_1927_To_NAD_1983_NADCON;NAD_1983_To_HARN_OR_WA'
else:
    geotransformation = 'NAD_1983_To_HARN_OR_WA'

geotransformation = ''

arcpy.Project_management('xxMapOutline', 'MapOutline', outSpRef, geotransformation,xycs)

## TICS
# calculate minTicLong, minTicLat, maxTicLong, maxTiclat
ticInterval = ticInterval / 60.0 # convert minutes to degrees
minTicLong = int(round(0.1 + minLong // ticInterval)) 
maxTicLong = int(round(1.1 + maxLong // ticInterval))
minTicLat = int(round(0.1 + minLat // ticInterval)) 
maxTicLat = int(round(1.1 + maxLat // ticInterval))
if minTicLong < 0:
    minTicLong = minTicLong + 1
if maxTicLong < 0:
    maxTicLong = maxTicLong + 1
# make xy file for tics
addMsgAndPrint('  writing tic file')
genf = open(scratch+'/xxxtics.csv','w')
genf.write('ID,LONGITUDE,LATITUDE\n')
nTic = 1
for y in range(minTicLat,maxTicLat):
    ticLat = y * ticInterval
    for x in range(minTicLong,maxTicLong):
        ticLong = x * ticInterval
        genf.write(str(nTic)+c+str(ticLong)+c+str(ticLat)+'\n')
        nTic = nTic+1
genf.close()
# convert to dbf
ticdbf = arcpy.CreateScratchName('xxx','.dbf','',scratch)
print ticdbf
ticdbf = os.path.basename(ticdbf)
print ticdbf
arcpy.TableToTable_conversion(scratch+'/xxxtics.csv',scratch,ticdbf)
# make XY event layer from table
arcpy.MakeXYEventLayer_management(scratch+'/'+ticdbf,'LONGITUDE','LATITUDE','ticlayer',xycs)
# copy to point featureclass
arcpy.FeatureToPoint_management('ticlayer','xxtics')

# project to correct coordinate system
arcpy.Project_management('xxtics', 'tics', outSpRef, geotransformation,xycs)

# add attributes 
for fld in ['Easting','Northing']:
    arcpy.AddField_management('tics',fld,'DOUBLE')
for fld in ['LatDMS','LongDMS']:
    arcpy.AddField_management('tics',fld,'TEXT',"","",20)
arcpy.AddXY_management('tics')
# calc Easting = Point_X, Northing = Point_Y
arcpy.CalculateField_management('tics','Easting','!Point_X!','PYTHON')
arcpy.CalculateField_management('tics','Northing','!Point_Y!','PYTHON')

# create update cursor, cycle through tics, and add LatDMS and LongDMS
addMsgAndPrint('  adding lat-long text strings')
rows = arcpy.UpdateCursor('tics')
for row in rows:
    row.LatDMS = ddToDmsString(row.LATITUDE)
    row.LongDMS = ddToDmsString(row.LONGITUDE)
    rows.updateRow(row)
del row
del rows

# delete csv files, dbf files, and preliminary featureclasses
addMsgAndPrint('  cleaning up scratch workspace')
for xx in [boxdbf,boxdbf+'.xml',ticdbf,ticdbf+'.xml']:  #,'xxxbox.csv','xxxtics.csv']:
    os.remove(scratch+'/'+xx)
addMsgAndPrint('  deleting temporary feature classes')
arcpy.Delete_management('xxtics')
arcpy.Delete_management('xxMapOutline')

#sys.exit()   # force exit with failure
