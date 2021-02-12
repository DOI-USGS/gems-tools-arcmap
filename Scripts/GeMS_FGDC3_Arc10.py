versionString = 'GeMS_FGDC3_Arc10.py version of 6 August 2020'
rawurl = 'https://raw.githubusercontent.com/usgs/gems-tools-arcmap/master/Scripts/GeMS_FGDC3_Arc10.py'
checkVersion(versionString, rawurl, 'gems-tools-arcmap')

import arcpy, os, sys, glob
from GeMS_utilityFunctions import *

debug = False

gdb = sys.argv[1]
xmlDir = sys.argv[2]
if xmlDir == '#':
    xmlDir = os.path.dirname(gdb)
"""
Following doesn't work 'cause egis module is no longer available

if sys.argv[3].upper() == 'TRUE':
    purgeProcessing = True
else:
    purgeProcessing = False

if purgeProcessing:
    import egis
    arcpy.ImportToolbox(egis.Toolbox, "usgs")
"""
    
purgeProcessing = True 

######################################
def clearImport(objName,gdbObj,gdb,purgeProcessing):
    gdbName = os.path.basename(gdb)[:-4]
    xmlFile = xmlDir+'/'+gdbName+objName+'-metadata.xml'
    #if purgeProcessing:
    #    arcpy.ClearMetadata_usgs(gdbObj,'True','ALWAYS')
    addMsgAndPrint('  Importing metadata from '+os.path.basename(xmlFile))
    arcpy.ImportMetadata_conversion(xmlFile,'FROM_FGDC',gdbObj,'ENABLED')
    return

######################################
addMsgAndPrint('  '+versionString)

arcpy.env.workspace = gdb

tables = arcpy.ListTables()
fcs = arcpy.ListFeatureClasses()
for table in tables:
    objName = '_'+table
    gdbObj = gdb+'/'+table
    clearImport(objName,gdbObj,gdb,purgeProcessing)

for fc in fcs:
    objName = '_'+fc
    gdbObj = gdb+'/'+fc
    clearImport(objName,gdbObj,gdb,purgeProcessing)

fds = arcpy.ListDatasets('','Feature')
for fd in fds:
    objName = '_'+fd
    gdbObj = gdb+'/'+fd
    clearImport(objName,gdbObj,gdb,purgeProcessing)
    
    arcpy.env.workspace = gdb+'/'+fd
    fcs = arcpy.ListFeatureClasses()
    for fc in fcs:
        objName = '_'+fc
        gdbObj = gdb+'/'+fd+'/'+fc
        clearImport(objName,gdbObj,gdb,purgeProcessing)

# database as a whole
objName = ''
gdbObj = gdb
clearImport(objName,gdbObj,gdb,purgeProcessing)

if not debug:
    addMsgAndPrint('  Deleting log files')
    logfiles = glob.glob(gdb[:-4]+'*'+'.log')
    for lf in logfiles:
        os.remove(lf)               
    
addMsgAndPrint('DONE')

