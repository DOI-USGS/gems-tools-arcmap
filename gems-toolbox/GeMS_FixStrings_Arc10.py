#   Script to clean up string fields in a GeMS database
##      Removes leading and trailing spaces
##      Converts "<null>", "" and similar to <null> (system nulls).
#       Ralph Haugerud, 28 July 2020

import arcpy, os, os.path, sys
from GeMS_utilityFunctions import *

versionString = 'GeMS_FixStrings_Arc10.py, version of 31 March 2021'
rawurl = 'https://raw.githubusercontent.com/usgs/gems-tools-arcmap/master/gems-toolbox/GeMS_FixStrings_Arc10.py'

def fixTableStrings(fc):
    fields1 = arcpy.ListFields(fc,'','String')
    fields = ['OBJECTID']
    for f in fields1:
        fields.append(f.name)
    with arcpy.da.UpdateCursor(fc, fields) as cursor:
        for row in cursor:
            trash = ''
            updateRowFlag = False
            row1 = [row[0]]
            for f in row[1:]:
                updateFieldFlag = False
                f0 = f
                if f <> None:
                    if f <> f.strip():
                        f = f.strip()
                        updateFieldFlag = True
                    if f.lower() == '<null>' or f == '':
                        f = None
                        updateFieldFlag = True
                    if updateFieldFlag:
                        updateRowFlag = True
                        addMsgAndPrint( ' '+str(row[0])+' **'+ str(f0)+'**')
                row1.append(f)
            if updateRowFlag:
                try:
                    cursor.updateRow(row1)
                except:
                    addMsgAndPrint('failed to update row '+str(row[0])+'. Perhaps a field is not nullable')
    del cursor, row
    
#########################
def main(parameters):
    addMsgAndPrint(versionString)
    checkVersion(versionString, rawurl, 'gems-tools-arcmap')
    
    db = parameters[1]

    arcpy.env.workspace = db

    tables = arcpy.ListTables()
    for tb in tables:
        addMsgAndPrint(' ')
        addMsgAndPrint(os.path.basename(tb))
        fixTableStrings(tb)

    datasets = arcpy.ListDatasets(feature_type='feature')
    datasets = [''] + datasets if datasets is not None else []
    for ds in datasets:
        for fc in arcpy.ListFeatureClasses(feature_dataset=ds):
            path = os.path.join(arcpy.env.workspace, ds, fc)
            addMsgAndPrint(' ')
            addMsgAndPrint(os.path.basename(fc))
            try:
                fixTableStrings(path)
            except:
                addMsgAndPrint('  failed to fix strings')

    addMsgAndPrint('DONE')
    
if __name__ == '__main__':
    main(sys.argv[1:])
