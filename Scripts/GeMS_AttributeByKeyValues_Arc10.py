# Script to step through an identified subset of feature classes in GeologicMap feature dataset
# and, for specified values of independent fields, calculate values of dependent fields.
# Useful for translating Alacarte-derived data into NCGMP09 format, and for using NCGMP09
# to digitize data in Alacarte mode.
#

usage = """
Usage: GeMS_AttributeByKeyValues.py <geodatabase> <file.txt>
  <geodatabase> is an NCGMP09-style geodatabase--with mapdata in feature
     dataset GeologicMap
  <file.txt> is a formatted text file that specifies feature classes,
     field names, values of independent fields, and values of dependent fields.
     See Dig24K_KeyValues.txt for an example and format instructions.
     """

import arcpy, sys
from GeMS_utilityFunctions import *

versionString = 'GeMS_AttributeByKeyValues_Arc10.py, version of 7 March 2021'
rawurl = 'https://raw.githubusercontent.com/usgs/gems-tools-arcmap/master/Scripts/GeMS_AttributeByKeyValues_Arc10.py'
checkVersion(versionString, rawurl, 'gems-tools-arcmap')

separator = '|'

def makeFieldTypeDict(fds,fc):
    fdict = {}
    fields = arcpy.ListFields(fds+'/'+fc)
    for fld in fields:
        fdict[fld.name] = fld.type
        #print fld.name, fld.type
    return fdict

addMsgAndPrint('  '+versionString)
if len(sys.argv) <> 4:
    addMsgAndPrint(usage)
    sys.exit()

gdb = sys.argv[1]
keylines1 = open(sys.argv[2],'r').readlines()
if sys.argv[3] == 'true':
    addMsgAndPrint("Forcing the overwriting of existing fields")
    forceCalc = True
else:
    forceCalc = False

arcpy.env.workspace = gdb
listFDSInGDB = arcpy.ListDatasets()
for finalfds in listFDSInGDB:  # this goes through all the FDS is that needed?
    arcpy.env.workspace = finalfds
    featureClasses = arcpy.ListFeatureClasses()
    arcpy.AddMessage(featureClasses)
    arcpy.env.workspace = gdb

    if gdb.find('.mdb') > 0:
        isMDB = True
    else:
        isMDB = False

    # remove empty lines from keylines1
    keylines = []
    for lin in keylines1:
        lin = lin.strip()
        if len(lin) > 1 and lin[0:1] <> '#':
            keylines.append(lin)
    #arcpy.AddMessage(len(keylines))
    countPerLines = []
    for line in keylines:
        countPerLines.append(len(line.split(separator)))
    #arcpy.AddMessage(countPerLines)
    #arcpy.AddMessage(len(countPerLines))

    n = 0
    while n < len(keylines):
        terms = keylines[n].split(separator) # remove newline and split on commas
        arcpy.AddMessage(terms)
        if len(terms) == 1:
            fClass = terms[0]
            arcpy.AddMessage(fClass)
            if fClass in featureClasses:
                mFieldTypeDict = makeFieldTypeDict(finalfds, fClass)
                n = n+1
                mFields = keylines[n].split(separator)
                for i in range(len(mFields)):
                    mFields[i] = mFields[i].strip() # remove leading and trailing whitespace
                    numMFields = len(mFields)
                    addMsgAndPrint('  ' + finalfds + " " + fClass)
            else:
                if len(fClass) > 0:  # catch trailing empty lines
                    addMsgAndPrint('  ' + fClass + ' not in ' + gdb + "\\" + finalfds)
                    while countPerLines[n+1]>1: #This advances the loop till the number of items in the terms list is again one
                        #, which is when the next feature class is considered
                        #arcpy.AddMessage("loop count = " + str(n))
                        if n < len(countPerLines)-2:
                            #arcpy.AddMessage("count per line = " + str(countPerLines[n]))
                            n=n+1
                        elif n == len(countPerLines)-2:
                            n= len(countPerLines)
                            break
                        else:
                            arcpy.warnings("Unexpected condition meet")

        else:  # must be a key-value: dependent values line
            vals = keylines[n].split(separator)
            if len(vals) <> numMFields:
                addMsgAndPrint('\nline:\n  '+keylines[n]+'\nhas wrong number of values. Exiting.')
                sys.exit()
            for i in range(len(vals)):  # strip out quotes
                vals[i] = vals[i].replace("'",'')
                vals[i] = vals[i].replace('"','')
                # remove leading and trailing whitespace
                vals[i] = vals[i].strip()
            # iterate through mFields 0--len(mFields)
            #  if i == 0, make table view, else resel rows with NULL values for attrib[i] and calc values
            arcpy.env.overwriteOutput = True  # so we can reuse table tempT
            for i in range(len(mFields)):
                if isMDB:
                    selField = '['+mFields[i]+']'
                else:
                    selField = '"'+mFields[i]+'"'
                if i == 0:  # select rows with specified independent value
                    whereClause = selField+' = '+"'"+vals[0]+"'"
                    arcpy.MakeTableView_management(finalfds + "\\" + fClass, 'tempT', whereClause)
                    nSel = int(str(arcpy.GetCount_management('tempT'))) # convert from Result object to integer
                    if nSel == -1:
                        addMsgAndPrint('    appears to be no value named: '+vals[0]+" in: "+mFields[0])
                    else:
                        addMsgAndPrint('    selected '+mFields[0]+' = '+vals[0]+', n = '+str(nSel))
                else:  # reselect rows where dependent values are NULL and assign new value
                    if forceCalc:
                        if nSel > 0:
                            if mFieldTypeDict[mFields[i]] == 'String':
                                arcpy.CalculateField_management('tempT', mFields[i], '"' + str(vals[i]) + '"')
                            elif mFieldTypeDict[mFields[i]] in ['Double', 'Single', 'Integer', 'SmallInteger']:
                                arcpy.CalculateField_management('tempT', mFields[i], vals[i])
                            addMsgAndPrint('        calculated ' + mFields[i] + ' = ' + str(vals[i]))
                    elif nSel > 0:
                        whereClause = selField+' IS NULL' # OR '+selField+" = ''"
                        if mFieldTypeDict[mFields[i]] == 'String':
                            whereClause = whereClause+' OR '+selField+" = ''"+' OR '+selField+" = ' '"
                        elif mFieldTypeDict[mFields[i]] in ['Double','Single','Integer','SmallInteger']:
                            whereClause = whereClause+' OR '+selField+' = 0'
                        arcpy.SelectLayerByAttribute_management('tempT','NEW_SELECTION',whereClause)
                        nResel = int(str(arcpy.GetCount_management('tempT'))) # convert result object to int
                        addMsgAndPrint('      reselected '+ mFields[i]+' = NULL, blank, or 0, n = '+str(nResel))
                        if nResel > 0:
                            if mFieldTypeDict[mFields[i]] == 'String':
                                arcpy.CalculateField_management('tempT',mFields[i],'"'+str(vals[i])+'"')
                            elif mFieldTypeDict[mFields[i]] in ['Double','Single','Integer','SmallInteger']:
                                arcpy.CalculateField_management('tempT',mFields[i],vals[i])
                            addMsgAndPrint('        calculated '+mFields[i]+' = '+str(vals[i]))
        n = n+1
