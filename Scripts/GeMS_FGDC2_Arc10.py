## Note that Metadata Translation tools must run in 32-bit Python. This happens
## automatically if this script is run from an ArcGIS toolbox. 
# 3/35/22 
#   -added function __updateCSdom to add codeset domains, specifically for GeoMaterial
#   -re-wrote def __updateEdom to produce the same structure as the 'upgrade' function in mp
#   -re-wrote def __updateRdom to catch ESRI fields shape, shape_length, and shape_area

import sys, os, os.path, arcpy, copy, imp
from GeMS_utilityFunctions import *
from GeMS_Definition import enumeratedValueDomainFieldList, rangeDomainDict, unrepresentableDomainDict, attribDict, entityDict, GeoMatConfDict
from xml.dom.minidom import *
import codecs

debug = False

versionString = 'GeMS_FGDC2_Arc10.py, version of version of 8 May 2023'
rawurl = 'https://raw.githubusercontent.com/doi-usgs/gems-tools-arcmap/master/Scripts/GeMS_FGDC2_Arc10.py'
checkVersion(versionString, rawurl, 'gems-tools-arcmap')

addMsgAndPrint('  '+ versionString)
if debug:
    addMsgAndPrint(os.sys.path)
    addMsgAndPrint('Python version = '+str(sys.version))

gems = 'GeMS'
gemsFullRef = '"GeMS (Geologic Map Schema)--a standard format for the digital publication of geologic maps", available at http://ngmdb.usgs.gov/Info/standards/GeMS/'
EsriDefinedAttributes = ('OBJECTID','Shape','Shape_Length','Shape_area','Shape_Area')

esri_attribs = {
    'objectid': 'Internal feature number',
    'shape' : 'Internal geometry object',
    'shape_length' : 'Internal feature length, double',
    'shape_area' : 'Internal feature area, double'
}

translator = arcpy.GetInstallInfo("desktop")["InstallDir"]+'Metadata/Translator/ARCGIS2FGDC.xml'

#####################################

def __appendOrReplace(rootNode,newNode,nodeTag):
    try:
        if len(rootNode.getElementsByTagName(nodeTag)) == 0:
            rootNode.appendChild(newNode)
        else:
            rootNode.replaceChild(newNode,rootNode.getElementsByTagName(nodeTag)[0])
    except:
        addMsgAndPrint(newNode.toprettyxml())

def __newElement(dom,tag,text):
    nd = dom.createElement(tag)
    # dom needs bytes. For text coming from table fields, we need to decode it from unicode to bytes in case there are non-ASCII characters
    # tags coming from field names will never have non-ASCII characters
    ndText = dom.createTextNode(str(text).decode("utf-8"))
    nd.appendChild(ndText)
    return nd

def __updateAttrDef(fld,dom):
    ##element tag names are
    ## attr             = Attribute
    ## attrlabl         = Attribute_Label
    ## attrdef          = Attribute_Definition
    ## attrdefs         = Attribute_Definition_Source
    labelNodes = dom.getElementsByTagName('attrlabl')
    for attrlabl in labelNodes:
        if attrlabl.firstChild.data == fld:
            attr = attrlabl.parentNode       
            if fld.find('_ID') > -1:
                # substitute generic _ID field for specific
                attrdefText = attribDict['_ID']
                attrdefSource = gems
            elif fld.lower() in esri_attribs:
                attrdefText = esri_attribs[fld.lower()]
                attrdefSource = 'Esri'
            else:
                attrdefText = attribDict[fld]
                attrdefSource = gems
            attrdef = __newElement(dom,'attrdef',attrdefText)
            __appendOrReplace(attr,attrdef,'attrdef')
            attrdefs = __newElement(dom,'attrdefs',attrdefSource)
            __appendOrReplace(attr,attrdefs,'attrdefs')
    return dom

def __updateEdom(fld, defs, dom):
    ##element tag names are
    ## attr             = Attribute
    ## attrdomv         = Attribute_Domain_Values
    ## edom             = Enumerated_Domain
    ## edomv            = Enumerated_Domain_Value
    ## edomd            = Enumerated_Domain_Definition
    ## edomvds          = Enumerated_Domain_Value_Definition_Source
    labelNodes = dom.getElementsByTagName('attrlabl')
    for attrlabl in labelNodes:
        if attrlabl.firstChild.data == fld:
            attr = attrlabl.parentNode
            # attrdomv = dom.createElement('attrdomv')
            for k in defs.iteritems():
                attrdomv = dom.createElement('attrdomv')
                edom = dom.createElement('edom')
                edomv = __newElement(dom,'edomv',k[0])
                edomvd = __newElement(dom,'edomvd',k[1][0])
                edom.appendChild(edomv)
                edom.appendChild(edomvd)
                if len(k[1][1]) > 0:
                    edomvds = __newElement(dom,'edomvds',k[1][1])
                    edom.appendChild(edomvds)                                
                attrdomv.appendChild(edom)
                attr.appendChild(attrdomv)
    return dom

def __updateRdom(fld,dom):
    labelNodes = dom.getElementsByTagName('attrlabl')
    for attrlabl in labelNodes:
        if attrlabl.firstChild.data == fld:
            attr = attrlabl.parentNode
            attrdomv = dom.createElement('attrdomv')
            rdom = dom.createElement('rdom')
            rdommin = __newElement(dom,'rdommin',rangeDomainDict[fld][0])
            rdom.appendChild(rdommin)
            rdommax = __newElement(dom,'rdommax',rangeDomainDict[fld][1])
            rdom.appendChild(rdommax)
            attrunit = __newElement(dom,'attrunit',rangeDomainDict[fld][2])
            rdom.appendChild(attrunit)
            attrdomv.appendChild(rdom)
            __appendOrReplace(attr,attrdomv,'attrdomv')
            return dom

def __updateUdom(fld,dom,udomTextString):
    labelNodes = dom.getElementsByTagName('attrlabl')
    for attrlabl in labelNodes:
        if attrlabl.firstChild.data == fld:
            attr = attrlabl.parentNode
            attrdomv = dom.createElement('attrdomv')
            udom = __newElement(dom,'udom',udomTextString)
            attrdomv.appendChild(udom)
            __appendOrReplace(attr,attrdomv,'attrdomv')
    return dom
   
# new function 3/25,22 to deal with codeset domains, specifically GeoMaterial
def __updateCSdom(fld, dom, csdomTextString, csdomSourceString):
    labelNodes = dom.getElementsByTagName('attrlabl')
    for attrlabl in labelNodes:
        if attrlabl.firstChild.data == fld:
            attr = attrlabl.parentNode
            attrdomv = dom.createElement('attrdomv')
            codesetd = dom.createElement('codesetd')
            codesetn = __newElement(dom, 'codesetn', csdomTextString)
            codesets = __newElement(dom, 'codesets', csdomSourceString)
            codesetd.appendChild(codesetn)
            codesetd.appendChild(codesets)
            attrdomv.appendChild(codesetd)
            __appendOrReplace(attr, attrdomv, 'attrdomv')
    return dom

def __findInlineRef(sourceID):
    # finds the Inline reference for each DataSource_ID
    query = '"DataSources_ID" = \'' + sourceID + '\''
    rows = arcpy.SearchCursor(dataSources, query)
    row = rows.next()
    if not row is None:
        return row.Source
    else:
        return ""

def __updateEntityAttributes(fc, fldList, dom, logFile):
    """For each attribute (field) in fldList,
        adds attribute definition and definition source,
        classifies as range domain, unrepresentable-value domain or enumerated-value domain, and 
            for range domains, adds rangemin, rangemax, and units;
            for unrepresentable value domains, adds unrepresentable value statement; 
            for enumerated value domains:
            1) Finds all controlled-vocabulary fields in the table sent to it
            2) Builds a set of unique terms in each field, ie, the domain
            3) Matches each domain value to an entry in the glossary
            4) Builds a dictionary of term:(definition, source) items
            5) Takes the dictionary items and put them into the metadata
              document as Attribute_Domain_Values
        Field MapUnit in table DescriptionOfMapUnits is treated as a special case.
        """
    cantfindTerm = []
    cantfindValue = []
    dataSourceValues = []
    fcShortName = os.path.basename(fc)
    for fld in fldList:      
        addMsgAndPrint( '      Field: '+ fld)
        # if is _ID field or if field definition is available or if OBJECTID, update definition
        #if fld.find('_ID') > -1 or attribDict.has_key(fld) or fld == 'OBJECTID':
        if fld.find('_ID') > -1 or attribDict.has_key(fld) or fld.lower() in esri_attribs:
            dom = __updateAttrDef(fld,dom)
        else:
            if not fld in EsriDefinedAttributes:
                cantfindTerm.append(fld)
        #if this is an _ID field
        if fld.find('_ID') > -1:
            dom = __updateUdom(fld,dom,unrepresentableDomainDict['_ID'])
        #or if this is another unrepresentable-domain field
        elif unrepresentableDomainDict.has_key(fld):
            dom = __updateUdom(fld,dom,unrepresentableDomainDict[fld])
        #or if this is a defined range-domain field
        elif rangeDomainDict.has_key(fld):
            dom = __updateRdom(fld,dom)
        #or if this is MapUnit in DMU
        elif fld == 'MapUnit' and fc == 'DescriptionOfMapUnits':
            dom = __updateUdom(fld,dom,unrepresentableDomainDict['default'])
        elif fld == 'GeoMaterial':
            dom = __updateCSdom(fld, dom, 'GeoMaterial Dictionary', 'GeMS')
        #if this is a defined Enumerated Value Domain field
        elif fld in enumeratedValueDomainFieldList:
            if debug: addMsgAndPrint('this is a recognized enumeratedValueDomainField')

            #create a search cursor on the field
            rows = arcpy.da.SearchCursor(fc, fld)
            # and get a list of all values 
            valList = [row[0] for row in rows if not row[0] is None]
            #uniquify the list by converting it to a set object
            valList = set(valList)
            
            #create an empty dictionary object to hold the matches between the unique terms
            #and their definitions (grabbed from the glossary)
            defs = {}
            #for each unique term, try to create a search cursor of just one record where the term
            #matchs a Term field value from the glossary
            if fld == 'MapUnit' and fc <> 'DescriptionOfMapUnits':
                for t in valList:            
                    query = '"MapUnit" = \'' + t + '\''
                    rows = arcpy.SearchCursor(DMU, query)
                    row = rows.next()
                    #if the searchcursor contains a row
                    if row:
                        #create an entry in the dictionary of term:[definition, source] key:value pairs
                        #this is how we will enumerate through the enumerated_domain section
                        defs[t] = []
                        if row.FullName <> None:
                            defs[t].append(row.FullName.encode('utf-8'))
                            defs[t].append('this report, table DescriptionOfMapUnits')
                        else:
                            addMsgAndPrint('MapUnit = '+t+', FullName not defined')
                            defs[t].append(row.Name.encode('utf-8'))
                            defs[t].append('this report, table DescriptionOfMapUnits')
                    else:
                        if not t in ('',' '): cantfindValue.append([fld,t])
                        
            elif fld == 'GeoMaterialConfidence' and fc == 'DescriptionOfMapUnits':
                if debug:
                    addMsgAndPrint('DMU / GeoMaterialsConfidence')
                defs = GeoMatConfDict
            elif fld == 'GeoMaterial' and fc == 'DescriptionOfMapUnits':
                if debug:
                    addMsgAndPrint('DMU / GeoMaterials!')
                for t in valList:
                    query = '"GeoMaterial" = \'' + t + '\''
                    if debug:
                        addMsgAndPrint('query='+query)
                    rows = arcpy.SearchCursor(gmDict, query)
                    row = rows.next()
                    #if the searchcursor contains a row
                    if row:
                        if debug:
                            addMsgAndPrint(row.GeoMaterial+' : '+row.Definition.encode('utf-8'))
                        #create an entry in the dictionary of term:[definition, source] key:value pairs
                        #this is how we will enumerate through the enumerated_domain section
                        defs[t] = []
                        defs[t].append(row.Definition.encode('utf-8'))
                        defs[t].append(' GeMS documentation')
                    else:
                        addMsgAndPrint('GeoMaterial = '+t+': not defined in GeoMaterialDict')
                        cantfindValue.append([fld,t])       
                
            elif fld.find('SourceID') > -1:  # is a source field
                for t in valList:
                    if debug:
                        addMsgAndPrint('Field '+fld+', appending '+t+' to dataSourceValues')
                    dataSourceValues.append(t)
                    query = '"DataSources_ID" = \'' + t + '\''
                    rows = arcpy.SearchCursor(dataSources, query)
                    row = rows.next()
                    #if the searchcursor contains a row
                    if row:
                        #create an entry in the dictionary of term:[definition, source] key:value pairs
                        #this is how we will enumerate through the enumerated_domain section
                        defs[t] = []
                        defs[t].append(row.Source.encode('utf-8'))
                        defs[t].append('this report, table DataSources')
                    else:
                        cantfindValue.append([fld,t])
            else:
                for t in valList:
                    query = '"Term" = '+"'"+ t + "'"
                    if debug:
                        addMsgAndPrint('query='+query)
                    rows = arcpy.SearchCursor(gloss, query)
                    row = rows.next()
                    #if the searchcursor contains a row
                    if row:
                        #create an entry in the dictionary of term:[definition, source] key:value pairs
                        #this is how we will enumerate through the enumerated_domain section
                        defs[t] = []
                        defs[t].append(row.Definition.encode('utf-8'))
                        defs[t].append(__findInlineRef(row.DefinitionSourceID).encode('utf-8'))
                    else:
                        if fld <> 'GeoMaterial' and fc <> 'GeoMaterialDict':
                            cantfindValue.append([fld,t])
            dom = __updateEdom(fld, defs, dom)
        else:  #presumed to be an unrepresentable domain
            dom = __updateUdom(fld,dom,unrepresentableDomainDict['default'])
    if len(cantfindValue) > 0:
        logFile.write('Missing enumerated-domain values\n')
        logFile.write('  ENTITY     TERM     VALUE\n')
        for term in cantfindValue:
            logFile.write('  '+fcShortName+'  '+term[0]+' **'+term[1]+'**\n')
    if len(cantfindTerm) > 0:
        logFile.write('Missing terms\n')
        logFile.write('  ENTITY     TERM\n')
        for term in cantfindTerm:
            logFile.write('  '+fcShortName + '  '+term+'\n')
    dataSourceValues = set(dataSourceValues)
    return dom, dataSourceValues

def eaoverviewDom(dom,eainfo,eaoverText,edcTxt):
    overview = dom.createElement('overview')
    eaover = __newElement(dom,'eaover',eaoverText)
    overview.appendChild(eaover)
    eadetcit = __newElement(dom,'eadetcit',edcTxt)
    overview.appendChild(eadetcit)
    eainfo.appendChild(overview)
    return dom

def updateTableDom(dom,fc,logFile):
    addMsgAndPrint('    Updating E-A stuff')
    desc = arcpy.Describe(fc)
    if desc.datasetType == 'FeatureClass' and desc.FeatureType == 'Annotation':
        isAnno = True
    else: isAnno = False
    if desc.datasetType == 'FeatureDataset':
        isDataset = True
    else: isDataset = False

    fcShortName = os.path.basename(fc)
    if entityDict.has_key(fcShortName):
        hasDesc = True
        descText = entityDict[fcShortName]
        descSourceText = gems
    else:
        hasDesc = False
        if not isAnno:
            descText = '**Need Description of '+fcShortName+'**'
            descSourceText = '**Need Description Source**'
            logFile.write('No description for entity '+fcShortName+'\n')
            logFile.write('No description source for entity '+fcShortName+'\n')
                   
    eainfo = dom.getElementsByTagName('eainfo')[0]
    # DELETE EXISTING CHILD NODES
    while len(eainfo.childNodes) > 0:
        eainfo.removeChild(eainfo.lastChild)
    if isAnno:
        if hasDesc: eaoverText = descText
        else: eaoverText = 'annotation feature class'
        if hasDesc: edcTxt = descSourceText
        else: edcTxt = 'See ESRI documentation for structure of annotation feature classes.'
        # add overview to dom
        dom = eaoverviewDom(dom,eainfo,eaoverText,edcTxt)
        dataSourceValues = []
    elif isDataset:
        eaoverText = descText
        edcTxt = descSourceText
        # add overview to dom
        dom = eaoverviewDom(dom,eainfo,eaoverText,edcTxt)
        dataSourceValues = []
    else:  # is table or non-Anno feature class
        # check for e-a detailed node, add if necessary
        if len(eainfo.getElementsByTagName('detailed')) == 0:
            #add detailed/enttyp/enttypl nodes
            detailed = dom.createElement('detailed')
            enttyp = dom.createElement(b'enttyp')
            enttypl = __newElement(dom, 'enttypl', fcShortName)
            enttypd = __newElement(dom, 'enttypd', descText)
            enttypds = __newElement(dom, 'enttypds', descSourceText)
            for nd in enttypl,enttypd,enttypds:
                enttyp.appendChild(nd)
            detailed.appendChild(enttyp)
            eainfo.appendChild(detailed)
            
        ##check that each field has a corresponding attr node
        #get a list of the field names in the fc
        fldNameList = fieldNameList(fc)    
        #get list of attributes in this metadata record
        #  we assume there eainfoNode has only one 'detailed' child
        attrlablNodes = eainfo.getElementsByTagName('attrlabl')
        attribs = []
        detailed = dom.getElementsByTagName('detailed')[0]
        for nd in attrlablNodes:
            attribs.append(nd.firstChild.data)
        for fieldName in fldNameList:
            if not fieldName in attribs:
                attr = dom.createElement('attr')
                attrlabl = __newElement(dom,'attrlabl',fieldName)
                attr.appendChild(attrlabl)
                detailed.appendChild(attr)                
        #update the entity description and entity description source
        if entityDict.has_key(fc) or ( fc[0:2] == 'CS' and entityDict.has_key(fc[2:]) ):
            enttypl = dom.getElementsByTagName('enttypl')
            if len(enttypl) > 0:
                enttyp = enttypl[0].parentNode
                # entity description node
                if fc[0:2] == 'CS':
                    descriptionText = entityDict[fc[2:]]
                else:
                    descriptionText = entityDict[fc]
                newEnttypd = __newElement(dom,'enttypd',descriptionText)
                __appendOrReplace(enttyp,newEnttypd,'enttypd')
                # entity description source node
                newEnttypds = __newElement(dom,'enttypds',gems)
                __appendOrReplace(enttyp,newEnttypds,'enttypds')                           
        #update attribute descriptions and value domains
        dom, dataSourceValues = __updateEntityAttributes(fc, fldNameList, dom, logFile)
    return dom, dataSourceValues

def pruneSrcInfo(dom,dataSourceValues):
    # removes dataqual/lineage/srcinfo branches 
    # with srccitea values that are not in dataSourceValues
    addMsgAndPrint('    Pruning unused srcinfo branches')
    srcciteaNodes = dom.getElementsByTagName('srccitea')
    for sn in srcciteaNodes:
        tagValue = sn.firstChild.nodeValue
        if not tagValue in dataSourceValues:
            parent = sn.parentNode
            grandparent = parent.parentNode
            grandparent.removeChild(parent)
    return dom

def replaceSpatialStuff(dom, arcXML):
    md = dom.getElementsByTagName('metadata')[0]
    # spdoinfo and spref from arcXML and plants it in dom
    spds = arcXML.getElementsByTagName('spdoinfo')
    if len(spds) > 0:
        addMsgAndPrint('    Replacing spdoinfo and spref')
        __appendOrReplace(md,spds[0],'spdoinfo')
        try:
            spr = arcXML.getElementsByTagName('spref')[0]
            __appendOrReplace(md,spr,'spref')
        except Exception as error:
            arcpy.AddMessage('      Spatial reference is "Unknown"')
    return dom

def replaceTitleSupplinf(objectType,aTable,gdb,dom):
    addMsgAndPrint('    Replacing title and suppplinf')
    titleNode = dom.getElementsByTagName('title')[0]
    oldTitle = titleNode.firstChild.nodeValue
    newTitle = objectType+' '+aTable+', part of '+oldTitle
    newTitleNode = __newElement(dom,'title',newTitle)
    citeinfo = dom.getElementsByTagName('citeinfo')[0]
    __appendOrReplace(citeinfo,newTitleNode,'title')
    newSiText = objectType+' '+aTable+' is part of '+gdb+', a composite dataset that conforms to '+gemsFullRef+'.'
    newSeText = newSiText + ' These metadata were prepared with the aid of script '+versionString+'.'
    newSiNode = __newElement(dom,'supplinf',newSiText)
    descript = dom.getElementsByTagName('descript')[0]
    __appendOrReplace(descript,newSiNode,'supplinf')         
    return dom

def fixObjXML(objName,objType,objLoc,domMR, fdDataSourceValues=[]):
    addMsgAndPrint('  '+objName)
    arcXMLfile = wksp+'/'+objName+'.xml'
    testAndDelete(arcXMLfile)
    arcpy.ExportMetadata_conversion(objLoc,translator,arcXMLfile)
    with open(arcXMLfile) as xml:
       arcXML = parse(xml)
       
    #arcXML = xml.dom.minidom.parse(arcXMLfile)
    dom = copy.deepcopy(domMR)
    
    # updateTableDom updates entity-attribute info, also returns dataSourceValues
    dom, dataSourceValues = updateTableDom(dom,objLoc,logFile)
    
    if objType <> 'Feature dataset':
        # delete unused dataqual/lineage/srcinfo branches
        dom = pruneSrcInfo(dom,dataSourceValues)
    else:
        dom = pruneSrcInfo(dom,fdDataSourceValues)
    
    # add spdoinfo and spref from arcXML
    dom = replaceSpatialStuff(dom, arcXML)
    
    # redo title and supplinfo
    dom = replaceTitleSupplinf(objType,objName,gdb,dom)
    domName = gdb[:-4]+'_'+objName+'-metadata.xml'
    writeDomToFile(wksp,dom,domName)
    if not debug:
        os.remove(arcXMLfile)
    
    return dataSourceValues

def writeDomToFile(workDir,dom,fileName):
    if debug:
        addMsgAndPrint(arcpy.env.workspace)
        addMsgAndPrint('fileName='+fileName)
    addMsgAndPrint('    Writing XML to '+fileName)
    
    tempxml = os.path.join(workDir, 'xml_temp.xml')
    outxml = os.path.join(workDir, fileName)
    
    for f_path in [tempxml, outxml]:
        if os.path.exists(f_path):
            os.remove(f_path)
        
    with codecs.open(tempxml, "w", encoding="utf-8", errors="xmlcharrefreplace") as out:
        dom.writexml(out, encoding="utf-8", addindent="\t")
    
    # mp.exe (called through USGSMPTranslator) does an excellent job of 
    # 1) sorting out of order elements
    # 2) removing unnecessary new lines
    # 3) adding newline characters after the closing tag for each element
    arcpy.USGSMPTranslator_conversion(tempxml, "", "XML", outxml)
    os.remove(tempxml)
    
#####################################

inGdb = sys.argv[1]
## mrXML is XML metadata record for inGdb as a whole, complete and passes mp
mrXML = sys.argv[2]
## Supplemental entity and field dictionaries beyond those in GeMS_Definition
if sys.argv[3] <> '#':
    if os.path.exists(sys.argv[2]):
        myDefs = imp.load_source('module1',sys.argv[3])
        myDefs.addDefs()

inGdb = os.path.abspath(inGdb)
wksp = os.path.dirname(inGdb)
gdb = os.path.basename(inGdb)

gloss = os.path.join(inGdb, 'Glossary')
dataSources = os.path.join(inGdb, 'DataSources')
DMU = os.path.join(inGdb, 'DescriptionOfMapUnits')
gmDict = os.path.join(inGdb, 'GeoMaterialDict')
logFileName = inGdb+'-metadataLog.txt'

# read mrXML into domMR
addMsgAndPrint('  Parsing '+mrXML)
try:    
    with open(mrXML) as xml:
       domMR = parse(xml)
    #domMR = xml.dom.minidom.parse(mrXML)
    addMsgAndPrint('  Master record parsed successfully')
except:
    addMsgAndPrint(arcpy.GetMessages())
    addMsgAndPrint('Failed to parse '+mrXML)
    raise arcpy.ExecuteError
    sys.exit()

# inventory inGdb: tables, rasters, featureDatasets, featureClasses
logFile = open(logFileName,'w')
arcpy.env.workspace = inGdb

tables = arcpy.ListTables()
for aTable in tables:
    objName = aTable
    objType = 'Non-spatial table'
    objLoc = inGdb+'/'+aTable
    fixObjXML(objName,objType,objLoc,domMR)

fcs = arcpy.ListFeatureClasses()
for fc in fcs:
    objName = fc
    objType = 'Feature class'
    objLoc = inGdb+'/'+fc
    fixObjXML(objName,objType,objLoc,domMR)

fds = arcpy.ListDatasets('','Feature')
for fd in fds:
    arcpy.env.workspace = inGdb+'/'+fd
    fcs = arcpy.ListFeatureClasses()
    arcpy.env.workspace = inGdb
    fdDS = []  # inventory of all DataSource_IDs used in feature dataset
    for fc in fcs:
        objName = fc
        objType = 'Feature class'
        objLoc = inGdb+'/'+fd+'/'+fc
        localDS = fixObjXML(objName,objType,objLoc,domMR)
        for ds in localDS:
            fdDS.append(ds)
    objName = fd
    objType = 'Feature dataset'
    objLoc = inGdb+'/'+fd
    fixObjXML(objName,objType,objLoc,domMR,set(fdDS))

logFile.close()
