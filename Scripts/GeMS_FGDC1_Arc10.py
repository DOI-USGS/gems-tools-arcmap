## Note that Metadata Translation tools must run in 32-bit Python. 

import sys, os, os.path, arcpy
from GeMS_utilityFunctions import *
from xml.dom.minidom import *

debug = False

versionString = 'GeMS_FGDC1_Arc10.py, version of 20 July 2020'
addMsgAndPrint('  '+ versionString)
if debug:
    addMsgAndPrint(os.sys.path)
    addMsgAndPrint('Python version = '+str(sys.version))

gems = 'GeMS'
gemsFullRef = '"GeMS (Geologic Map Schema)--a standard format for the digital publication of geologic maps", available at http://ngmdb.usgs.gov/Info/standards/GeMS/'
eaoverviewCitation = 'Detailed descriptions of entities, attributes, and attribute values are given in metadata for constituent elements of the database. See also '+gemsFullRef+'.'

translator = arcpy.GetInstallInfo("desktop")["InstallDir"]+'Metadata/Translator/ARCGIS2FGDC.xml'

###########################################
def __newElement(dom,tag,text):
    nd = dom.createElement(tag)
    ndText = dom.createTextNode(text)
    nd.appendChild(ndText)
    return nd

def __appendOrReplace(rootNode,newNode,nodeTag):
    if len(rootNode.getElementsByTagName(nodeTag)) == 0:
        rootNode.appendChild(newNode)
    else:
        rootNode.replaceChild(newNode,rootNode.getElementsByTagName(nodeTag)[0])

def purgeChildren(dom,nodeTag):
    nodes = dom.getElementsByTagName(nodeTag)
    for aNode in nodes:
        while len(aNode.childNodes) > 0:
            aNode.removeChild(aNode.lastChild)
    return dom

def eaoverviewDom(dom,eainfo,eaoverText,edcTxt):
    overview = dom.createElement('overview')
    eaover = __newElement(dom,'eaover',eaoverText)
    overview.appendChild(eaover)
    eadetcit = __newElement(dom,'eadetcit',edcTxt)
    overview.appendChild(eadetcit)
    eainfo.appendChild(overview)
    return dom

def addSupplinf(dom,supplementaryInfo):
    try:
        rtNode = dom.getElementsByTagName('descript')[0]
    except:
        rootNode = dom.getElementsByTagName('idinfo')[0]
        descNode = __newElement(dom,'descript','')
        rootNode.appendChild(descNode)
        rtNode = dom.getElementsByTagName('descript')[0]
        
    siNode = __newElement(dom,'supplinf',supplementaryInfo)
    __appendOrReplace(rtNode,siNode,'supplinf')
    return dom

def writeGdbDesc(gdb):
    desc = 'Database '+os.path.basename(gdb)+' contains the following elements: '
    arcpy.env.workspace = gdb
    for aTable in arcpy.ListTables():
        desc = desc+'non-spatial table '+ aTable+' ('+str(numberOfRows(aTable))+' rows); '
    for anFds in arcpy.ListDatasets():
        desc = desc + 'feature dataset '+anFds+' which contains '
        fcs = arcpy.ListFeatureClasses('','All',anFds)
        if len(fcs) == 1:
            desc = desc + 'feature class '+fcs[0]+' ('+str(numberOfRows(fcs[0]))+' features);  '
        else:
            for n in range(0,len(fcs)-1):
                desc = desc+'feature class '+fcs[n]+' ('+str(numberOfRows(fcs[n]))+' features), '
            lastn = len(fcs)-1
            desc = desc+'and feature class '+fcs[lastn]+' ('+str(numberOfRows(fcs[lastn]))+' features); '
    desc = desc[:-2]+'. '
    return desc

def writeDomToFile(workDir,dom,fileName):
    if debug:
        addMsgAndPrint(arcpy.env.workspace)
        addMsgAndPrint('fileName='+fileName)
    outf = open(os.path.join(workDir,fileName),'w')
    dom.writexml(outf)
    outf.close()

###########################################
inGdb = sys.argv[1]

inGdb = os.path.abspath(inGdb)
wksp = os.path.dirname(inGdb)
xmlGdb = inGdb[:-4]+'-metadata.xml'
mrXML = xmlGdb

dataSources = os.path.join(inGdb, 'DataSources')
addMsgAndPrint('  DataSources = '+dataSources)

# export master record
if debug:
    addMsgAndPrint('  inGdb = '+inGdb)
    addMsgAndPrint('  translator = '+translator)
    addMsgAndPrint('  mrXML = '+mrXML)
if os.path.exists(mrXML):
    os.remove(mrXML)
arcpy.ExportMetadata_conversion(inGdb,translator,mrXML)
addMsgAndPrint('  Metadata for '+os.path.basename(inGdb)+' exported to file ')
addMsgAndPrint('    '+mrXML)

# parse mrXML to DOM
try:
    domMR = xml.dom.minidom.parse(mrXML)
    addMsgAndPrint('  Master record parsed successfully')
except:
    addMsgAndPrint(arcpy.GetMessages())
    addMsgAndPrint('Failed to parse '+mrXML)
    raise arcpy.ExecuteError
    sys.exit()
    
# add supplinfo
addMsgAndPrint('  Adding supplinfo')
gdbDesc1 = (' is a composite geodataset that conforms to '+gemsFullRef+'. '+
'Metadata records associated with each element within the geodataset contain '+
'more detailed descriptions of their purposes, constituent entities, and attributes. ')
gdbDesc2 = ('An OPEN shapefile versions of the dataset is also available. It consists '+
'of shapefiles, DBF files, and delimited text files and retains all information in the native '+
'geodatabase, but some programming will likely be necessary to assemble these components into '+
'usable formats.')
supplementaryInfo = os.path.basename(inGdb)+gdbDesc1+gdbDesc2
supplementaryInfo = supplementaryInfo+ ' These metadata were prepared with the aid of script '+versionString+'.'

domMR = addSupplinf(domMR,supplementaryInfo)

# identify/create dataqual node
addMsgAndPrint('  Adding dataqual')              
try:
    dataqual = domMR.getElementsByTagName('dataqual')[0]
except:
    rtNode = domMR.getElementsByTagName('metadata')[0]
    dataqual = domMR.createElement('dataqual')
    rtNode.appendChild(dataqual)
    
# dataqual/attracc/attraccr (statement referring user to IdConf and ExConf fields)
attraccrText = 'Confidence that a feature exists and confidence that a feature is correctly identified are described in per-feature attributes ExistenceConfidence and IdentityConfidence.'
attraccr = __newElement(domMR,'attraccr',attraccrText)
attracc = domMR.createElement('attracc')
attracc.appendChild(attraccr)
dataqual.appendChild(attracc)

# dataqual/posacc/horizpa/horizpar (statement referring user to LCM fields in fc)
horizparText = 'Estimated accuracy of horizontal location is given on a per-feature basis by attribute LocationConfidenceMeters. Values are expected to be correct within a factor of 2.  A LocationConfidenceMeters value of -9 or -9999 indicates that no value has been assigned.' 
horizpar = __newElement(domMR,'horizpar',horizparText)
horizpa = domMR.createElement('horizpa')
posacc = domMR.createElement('posacc')
horizpa.appendChild(horizpar)
posacc.appendChild(horizpa)
dataqual.appendChild(posacc)

# add dataqual/lineage/srcinfo
if arcpy.Exists(dataSources):
    if numberOfRows(dataSources) > 0:
        ## lineage node
        try:
            lineage = domMR.getElementsByTagName('lineage')[0]
        except:
            rtNode = domMR.getElementsByTagName('dataqual')[0]
            lineage = domMR.createElement('lineage')
            rtNode.appendChild(lineage)
        ## get rid of any existing srcinfo nodes
        domMr = purgeChildren(domMR,'srcinfo')
        ## add successive srcinfo nodes
        fields = ['DataSources_ID','Source','Notes','URL']
        ## for each row in dataSources, create
        ##   srcinfo
        ##      srccite
        ##         citeinfo
        ##            title  Source
        ##            onlink URL
        ##      srccitea  DataSource_ID
        with arcpy.da.SearchCursor(dataSources, fields) as cursor:
            for row in cursor:
                addMsgAndPrint(row[0])
                srcinfo = domMR.createElement('srcinfo')
                srccite = domMR.createElement('srccite')
                citeinfo = domMR.createElement('citeinfo')
                titleText = str(row[1].encode("ASCII",'ignore'))
                if row[2] <> None:
                    titleText = titleText + ' '+str(row[2])
                title = __newElement(domMR,'title',titleText)
                citeinfo.appendChild(title)
                if row[3] <> None:
                    onlink = __newElement(domMR,'onlink',row[3])
                    citeinfo.appendChild(onlink)
                srccite.appendChild(citeinfo)
                srcinfo.appendChild(srccite)
                srccitea = __newElement(domMR,'srccitea',row[0])
                srcinfo.appendChild(srccitea)
                lineage.appendChild(srcinfo)

### add eaoverview
addMsgAndPrint('  Adding eainfo')
# get rid of any existing eainfo
domMr = purgeChildren(domMR,'eainfo')
#  ensure that there is an eainfo node
try:
    addMsgAndPrint('    getting eainfo 1a')
    eanode = domMR.getElementsByTagName('eainfo')[0]
except:
    addMsgAndPrint('    getting eainfo 1b')
    rtNode = domMR.getElementsByTagName('metadata')[0]
    addMsgAndPrint('    getting eainfo 1b1')
    eanode = domMR.createElement('eainfo')
    addMsgAndPrint('    getting eainfo 1b2')
    rtNode.appendChild(eanode)

addMsgAndPrint('    getting eainfo 3')
eainfo = domMR.getElementsByTagName('eainfo')[0]
addMsgAndPrint('    getting eainfo 4')
gdbDesc = writeGdbDesc(inGdb)  # listing of all tables, feature datasets, feature classes
addMsgAndPrint('    getting eainfo 5')
domMR = eaoverviewDom(domMR,eainfo,gdbDesc,eaoverviewCitation)

# write domMR to mrXML
testAndDelete(mrXML)
addMsgAndPrint('  Writing Dom to file')
writeDomToFile(wksp,domMR,mrXML)

addMsgAndPrint('DONE')


