"""
Revisit in light of ESRI article
https://support.esri.com/en/technical-article/000011751
"""

# purges metadata of geoprocessing history
versionString = 'GeMS_PurgeMetadata_Arc10.py, version of 31 March 2021'
rawurl = 'https://raw.githubusercontent.com/usgs/gems-tools-arcmap/master/gems-toolbox/GeMS_PurgeMetadata_Arc10.py'

import arcpy, os.path, sys
import egis
from GeMS_utilityFunctions import *

def purgeGeoprocessingFGDC(table,metadataFile):
    addMsgAndPrint('  exporting metadata from ' + table)
    addMsgAndPrint('  exporting metadata to '+metadataFile)
    arcpy.ExportMetadata_conversion(table,translator,metadataFile)
    addMsgAndPrint('  clearing internal metadata')
    arcpy.ClearMetadata_usgs(table)
    addMsgAndPrint('  importing metadata from '+metadataFile)
    arcpy.ImportMetadata_conversion (metadataFile,"FROM_FGDC",table)

def main(parameters):
    addMsgAndPrint(versionString)
    checkVersion(versionString, rawurl, 'gems-tools-arcmap')
    
    inGdb = os.path.abspath(parameters[0])
    outDir = parameters[1]
    addMsgAndPrint('  Starting...')
    if outDir == '' or not arcpy.Exists(outDir):
        outDir = os.path.dirname(inGdb)
    if not outDir[-1:] in ('/','\\'):
        outDir = outDir+'/'

    arcpy.env.workspace = inGdb

    tables = arcpy.ListTables()
    # featureClasses = []
    fds = arcpy.ListDatasets()
    # arcpy.AddMessage(fds)
    # for fd in fds:
    #     arcpy.env.workspace = fd
    #     arcpy.AddMessage(fd)
    #     fc1 = arcpy.ListFeatureClasses()
    #     arcpy.AddMessage(fcl)
    #     if fc1 <> None:
    #       for fc in fc1:
    #         featureClasses.append(fd+'/'+fc)
    rasters = arcpy.ListRasters()

    arcpy.ImportToolbox(egis.Toolbox, "usgs")

    transDir = arcpy.GetInstallInfo("desktop")["InstallDir"]
    translator = os.path.join(transDir, r"Metadata\Translator\ARCGIS2FGDC.xml")
    arcpy.env.scratchWorkspace = arcpy.env.scratchGDB #After banging head against it this stopped me from having an "ERROR 000584: Implementation of this Tool's Validate is invalid."

    fileName=os.path.basename(inGdb)[:-4]+'-metadata.xml'
    arcpy.AddMessage(fileName)
    arcpy.AddMessage(outDir[:-1])
    metadataFile = outDir[:-1]+'\\'+fileName
    testAndDelete(metadataFile)
    addMsgAndPrint('  ')
    addMsgAndPrint(inGdb)
    purgeGeoprocessingFGDC(inGdb,metadataFile)

    arcpy.env.workspace = inGdb
    rootName = str(os.path.basename(inGdb)[:-4])

    # feature datasets
    for fd in fds:
        metadataFile = outDir[:-1]+'\\'+rootName+'-'+fd+'-metadata.xml'
        testAndDelete(metadataFile)
        addMsgAndPrint('  ')
        addMsgAndPrint('Feature dataset '+fd)
        purgeGeoprocessingFGDC(inGdb+"\\"+fd,metadataFile)
        arcpy.env.workspace = inGdb+'\\'+fd
        fcs = arcpy.ListFeatureClasses()
        arcpy.AddMessage(fcs)
        for fc in fcs:
            metadataFile = outDir[:-1]+'\\'+rootName+'-'+fd+'-'+fc+'-metadata.xml'
            testAndDelete(metadataFile)
            addMsgAndPrint('  ')
            addMsgAndPrint('Feature class '+fc)
            purgeGeoprocessingFGDC(inGdb+'\\'+fd+'\\'+fc,metadataFile)

    # tables
    for table in tables:
        metadataFile = outDir[:-1]+'\\'+rootName+'-'+table+'-metadata.xml'
        testAndDelete(metadataFile)
        addMsgAndPrint('  ')
        addMsgAndPrint('Table '+table)
        purgeGeoprocessingFGDC(inGdb+'\\'+table,metadataFile)

    # rasters
    for raster in rasters:
        metadataFile = outDir[:-1]+'\\'+rootName+'-'+raster+'-metadata.xml'
        testAndDelete(metadataFile)
        addMsgAndPrint('  ')
        addMsgAndPrint('Raster '+raster)
        purgeGeoprocessingFGDC(inGdb+'\\'+raster,metadataFile)

    addMsgAndPrint('  ')
    addMsgAndPrint('DONE')

if __name__ == '__main__':
    main(sys.argv[1:])

