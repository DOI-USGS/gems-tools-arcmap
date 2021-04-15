""" 
GeMS Tools Python toolbox for ArcMap
Evan Thoms
March 17, 2021

Notes about python toolboxes:
1. This toolbox describes parameter forms, but calls external tool scripts residing in the \Scripts folder
2. Each parameter form exists as a class in this script with a number of ESRI-defined functions
3. The tool script itself is imported in the execute function within each parameter form class.
4. Once imported, modules are cached and do not get imported again unless the reload() function is called,
   which makes things difficult when editing the tool script. I could not write an import_or_reload function 
   that worked or even include an if conditional to check for a debug flag so just import and immediately reload. 
5. The tool scripts should be callable both from this toolbox as well as from the command line. 
   In the case of the latter, the arguments will be strings. To make the script tool work with parameter 
   objects as well, we first construct a list of parameter.values and send that.
6. If called from the command line, sys.argv is populated with the list of arguments, but it is empty if  
   called from this toolbox. When called at the command line, an "if __name__ == '__main__':" conditional 
   is executed and the main() function is supplied with sys.arv[1:] (we slice the sys.argv list because 
   sys.argv[0] is the path to the file). If called from this toolbox, we call <GeMSTool>.main(parameter_values).

Parameter types: 
https://desktop.arcgis.com/en/arcmap/10.3/analyze/creating-tools/defining-parameter-data-types-in-a-python-toolbox.htm

The documentation at the page is good for ArcMap 10.3 and up, so we can't guarantee the tools will work with anything older than that.
"""

import arcpy
import sys, os, importlib 

# thought was working before. doesn't seem to do it now
# add the path to the \Scripts folder so tools can be imported as modules
# But workaround is to import <toolfile> in each def execute
local_path = os.path.abspath(os.path.dirname(__file__))
scripts_path = os.path.join(local_path, 'Scripts')
sys.path.append(scripts_path)

class Toolbox(object):
    def __init__(self):
        self.label = u'GeMS Tools'
        self.alias = ''
        # The list order here does not affect the order of the tools in the toolbox
        # Arc sorts and displays the tools alphabetically
        self.tools = [Deplanarize, CompactAndBackup, AttributeByKeyValues, CreateDatabase, 
                      DocxToDMU, MakePolys, MakeTopology, MapOutline, ProjectCrossSectionData, ProjectPointsToCrossSection, InclinationNumber, SetPlotAtScales, SetSymbols, SetIDvalues, FGDC_1, FGDC_2, FGDC_3, PurgeMetadata, RelationshipClasses,
                      FixStrings, TranslateToShape, SymbolToRGB, TopologyCheck, GeologicNamesCheck,
                      ValidateDatabase, DMUtoDocx, RebuildMapUnits]


class AttributeByKeyValues(object):
    """"GeMS_AttributeByKeyValues_Arc10.py"""
    def __init__(self):
        self.label = u'Attribute By Key Values'
        self.description = u'Script to step through an identified subset of feature classes in GeologicMap feature dataset and, for specified values of one or more independent fields, calculate values of dependent fields.'
        self.canRunInBackground = False
        self.category = u'Create and Edit'
        
    def getParameterInfo(self):
        # Input_geodatabase
        param_1 = arcpy.Parameter()
        param_1.name = u'Input_geodatabase'
        param_1.displayName = u'Input geodatabase'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEWorkspace'

        # Key_Value_file
        param_2 = arcpy.Parameter()
        param_2.name = u'Key_Value_file'
        param_2.displayName = u'Key Value file'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'DETextFile'

        # Overwrite_existing
        param_3 = arcpy.Parameter()
        param_3.name = u'Overwrite_existing'
        param_3.displayName = u'Overwrite existing'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.datatype = u'GPBoolean'

        return [param_1, param_2, param_3]
    
    def execute(self, parameters, messages):
        # import and reload the tool script to get the latest version; if making edits to the tool script
        import GeMS_AttributeByKeyValues_Arc10
        reload(GeMS_AttributeByKeyValues_Arc10)
        
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_AttributeByKeyValues_Arc10.main(parameter_values)

class CreateDatabase(object):
    """"GeMS_CreateDatabase_Arc10.py"""
    def __init__(self):
        self.label = u'Create New Database'
        self.description = u'Creates an empty GeMS-style geodatabase'
        self.canRunInBackground = False
        self.category = u'Create and Edit'
        
    def getParameterInfo(self):
        # Output_Workspace
        param_1 = arcpy.Parameter()
        param_1.name = u'Output_Workspace'
        param_1.displayName = u'Output Workspace'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEFolder'

        # Name_of_new_geodatabase
        param_2 = arcpy.Parameter()
        param_2.name = u'Name_of_new_geodatabase'
        param_2.displayName = u'Name of new geodatabase'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'GPString'

        # Spatial_reference_system
        param_3 = arcpy.Parameter()
        param_3.name = u'Spatial_reference_system'
        param_3.displayName = u'Spatial reference system'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.datatype = u'GPCoordinateSystem'

        # Optional_feature_classes__tables__and_feature_datasets
        param_4 = arcpy.Parameter()
        param_4.name = u'Optional_feature_classes__tables__and_feature_datasets'
        param_4.displayName = u'Optional feature classes, tables, and feature datasets'
        param_4.parameterType = 'Optional'
        param_4.direction = 'Input'
        param_4.datatype = u'GPString'
        param_4.multiValue = True
        param_4.filter.list = [u'CartographicLines', u'CorrelationOfMapUnits', u'DataSourcePolys', u'FossilPoints', u'GenericPoints', u'GeochronPoints', u'GeologicLines', u'IsoValueLines', u'MapUnitLines', u'MapUnitPoints', u'MapUnitOverlayPolys', u'MiscellaneousMapInformation', u'OrientationPoints', u'OverlayPolys', u'RepurposedSymbols', u'StandardLithology', u'Stations']

        # Number_of_cross_sections
        param_5 = arcpy.Parameter()
        param_5.name = u'Number_of_cross_sections'
        param_5.displayName = u'Number of cross sections'
        param_5.parameterType = 'Required'
        param_5.direction = 'Input'
        param_5.datatype = u'GPLong'
        param_5.value = u'0'

        # Enable_edit_tracking
        param_6 = arcpy.Parameter()
        param_6.name = u'Enable_edit_tracking'
        param_6.displayName = u'Enable edit tracking'
        param_6.parameterType = 'Required'
        param_6.direction = 'Input'
        param_6.datatype = u'GPBoolean'
        param_6.value = u'true'

        # Add_fields_for_cartographic_representations
        param_7 = arcpy.Parameter()
        param_7.name = u'Add_fields_for_cartographic_representations'
        param_7.displayName = u'Add fields for cartographic representations'
        param_7.parameterType = 'Required'
        param_7.direction = 'Input'
        param_7.datatype = u'GPBoolean'
        param_7.value = u'false'

        # Add_LTYPE_and_PTTYPE
        param_8 = arcpy.Parameter()
        param_8.name = u'Add_LTYPE_and_PTTYPE'
        param_8.displayName = u'Add LTYPE and PTTYPE'
        param_8.parameterType = 'Required'
        param_8.direction = 'Input'
        param_8.datatype = u'GPBoolean'
        param_8.value = u'false'

        # Add_standard_confidence_values
        param_9 = arcpy.Parameter()
        param_9.name = u'Add_standard_confidence_values'
        param_9.displayName = u'Add standard confidence values'
        param_9.parameterType = 'Required'
        param_9.direction = 'Input'
        param_9.datatype = u'GPBoolean'
        param_9.value = u'true'

        return [param_1, param_2, param_3, param_4, param_5, param_6, param_7, param_8, param_9]

    def execute(self, parameters, messages):
        # import and reload the tool script to get the latest version; if making edits to the tool script
        import GeMS_CreateDatabase_Arc10
        reload(GeMS_CreateDatabase_Arc10)
        
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_CreateDatabase_Arc10.main(parameter_values)

class DocxToDMU(object):
    """"GeMS_DMUtoDocx_Arc10.py"""
    def __init__(self):
        self.label = u'DOCX to DMU'
        self.description = u'Translates formatted Microsoft Word (.docx) file to incomplete DescriptionOfMapUnits table'
        self.canRunInBackground = False
        self.category = u'Create and Edit'
        
    def getParameterInfo(self):
        # DMU_manuscript_file
        param_1 = arcpy.Parameter()
        param_1.name = u'DMU_manuscript_file'
        param_1.displayName = u'DMU manuscript file'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEFile'
        
        # Geologic_map_geodatabase
        param_2 = arcpy.Parameter()
        param_2.name = u'Geologic_map_geodatabase'
        param_2.displayName = u'Geologic map geodatabase'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'DEWorkspace'

        return [param_1, param_2]
        
    def execute(self, parameters, messages): 
        # import and reload the tool script to get the latest version; if making edits to the tool script
        import GeMS_DocxToDMU_Arc10
        reload(GeMS_DocxToDMU_Arc10)
        
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_DocxToDMU_Arc10.main(parameter_values)

class CompactAndBackup(object):
    """"GeMS_CompactAndBackup_Arc10.py"""
    def __init__(self):
        self.label = u'Compact and Backup'
        self.description = u'Compacts database and copies to an archive version. Archive version is named with current date.'
        self.canRunInBackground = False
        self.category = u'Create and Edit'
        
    def getParameterInfo(self):
        # Input_geodatabase
        param_1 = arcpy.Parameter()
        param_1.name = u'Input_geodatabase'
        param_1.displayName = u'Input geodatabase'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEWorkspace'

        # Message_for_log_file
        param_2 = arcpy.Parameter()
        param_2.name = u'Message_for_log_file'
        param_2.displayName = u'Message for log file'
        param_2.parameterType = 'Optional'
        param_2.direction = 'Input'
        param_2.datatype = u'GPString'

        return [param_1, param_2]
        
    def execute(self, parameters, messages):
        # import and reload the tool script to get the latest version; if making edits to the tool script
        import GeMS_CompactAndBackup_Arc10
        reload(GeMS_CompactAndBackup_Arc10)
        
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_CompactAndBackup_Arc10.main(parameter_values)

class Deplanarize(object):
    """GeMS_Deplanarize_Arc10.py"""
    def __init__(self):
        self.label = u'Deplanarize CAF'
        self.description = u'Deplanarizes (removes excess nodes) arcs in ContactsAndFaults feature class of the GeologicMaps feature dataset. '
        self.canRunInBackground = False
        self.category = u'Create and Edit'        
        
    def getParameterInfo(self):
        # Input_geodatabase
        param_1 = arcpy.Parameter()
        param_1.name = u'Input_geodatabase'
        param_1.displayName = u'Input geodatabase'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEWorkspace'

        return [param_1]
        
    def execute(self, parameters, messages):
        # import and reload the tool script to get the latest version; if making edits to the tool script
        import GeMS_Deplanarize_Arc10
        reload(GeMS_Deplanarize_Arc10)
        
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_Deplanarize_Arc10.main(parameter_values)

class MakePolys(object):
    """GeMS_MakePolys_Arc10.py"""
    def __init__(self):
        self.label = u'Make Polygons'
        self.description = u'Creates (recreates) feature class MapUnitPolys from lines in ContactsAndFaults'
        self.canRunInBackground = False
        self.category = u'Create and Edit'
        
    def getParameterInfo(self):
        # Input_feature_dataset
        param_1 = arcpy.Parameter()
        param_1.name = u'Input_feature_dataset'
        param_1.displayName = u'Input feature dataset'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEFeatureDataset'

        # Save_old_MapUnitPolys
        param_2 = arcpy.Parameter()
        param_2.name = u'Save_old_MapUnitPolys'
        param_2.displayName = u'Save old MapUnitPolys'
        param_2.parameterType = 'Optional'
        param_2.direction = 'Input'
        param_2.datatype = u'GPBoolean'
        param_2.value = u'false'

        # Saved-layer_directory
        param_3 = arcpy.Parameter()
        param_3.name = u'Saved-layer_directory'
        param_3.displayName = u'Saved-layer directory'
        param_3.parameterType = 'Optional'
        param_3.direction = 'Input'
        param_3.datatype = u'DEFolder'

        # Label_points_feature_class
        param_4 = arcpy.Parameter()
        param_4.name = u'Label_points_feature_class'
        param_4.displayName = u'Label points feature class'
        param_4.parameterType = 'Optional'
        param_4.direction = 'Input'
        param_4.datatype = u'DEFeatureClass'

        return [param_1, param_2, param_3, param_4] 

    def execute(self, parameters, messages):
        # import and reload the tool script to get the latest version; if making edits to the tool script
        import GeMS_MakePolys_Arc10
        reload(GeMS_MakePolys_Arc10)
        
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_MakePolys_Arc10.main(parameter_values) 

class MakeTopology(object):
    """GeMS_MakeTopology_Arc10.py"""
    def __init__(self):
        self.label = u'Make Topology'
        self.canRunInBackground = False
        self.description = u'Creates and validates a topology feature class within an GeMS-style feature dataset.'
        self.category = u'Create and Edit'
        
    def getParameterInfo(self):
        # Input_feature_dataset
        param_1 = arcpy.Parameter()
        param_1.name = u'Input_feature_dataset'
        param_1.displayName = u'Input feature dataset'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEFeatureDataset'

        # use_MUP_rules
        param_2 = arcpy.Parameter()
        param_2.name = u'use_MUP_rules'
        param_2.displayName = u'use MUP rules'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'GPBoolean'
        param_2.value = u'true'

        return [param_1, param_2]
        
    def execute(self, parameters, messages):
        # import and reload the tool script to get the latest version; if making edits to the tool script
        import GeMS_MakeTopology_Arc10
        reload(GeMS_MakeTopology_Arc10)
        
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_MakeTopology_Arc10.main(parameter_values) 

class MapOutline(object):
    """mapOutline_Arc10.py"""
    def __init__(self):
        self.label = u'MapOutline'
        self.description = u'Calculates lat-long outline and tics in NAD27 or NAD83 and projects to user-defined map projection'
        self.canRunInBackground = False
        self.category = u'Create and Edit'
        
    def getParameterInfo(self):
        # SE_longitude
        param_1 = arcpy.Parameter()
        param_1.name = u'SE_longitude'
        param_1.displayName = u'SE longitude'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'GPString'

        # SE_latitude
        param_2 = arcpy.Parameter()
        param_2.name = u'SE_latitude'
        param_2.displayName = u'SE latitude'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'GPString'

        # width__longitudinal_extent_
        param_3 = arcpy.Parameter()
        param_3.name = u'width__longitudinal_extent_'
        param_3.displayName = u'width (longitudinal extent)'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.datatype = u'GPDouble'
        param_3.value = u'7.5'

        # height__latitudinal_extent_
        param_4 = arcpy.Parameter()
        param_4.name = u'height__latitudinal_extent_'
        param_4.displayName = u'height (latitudinal extent)'
        param_4.parameterType = 'Required'
        param_4.direction = 'Input'
        param_4.datatype = u'GPDouble'
        param_4.value = u'7.5'

        # tic_spacing
        param_5 = arcpy.Parameter()
        param_5.name = u'tic_spacing'
        param_5.displayName = u'tic spacing'
        param_5.parameterType = 'Required'
        param_5.direction = 'Input'
        param_5.datatype = u'GPDouble'
        param_5.value = u'2.5'

        # Is_NAD27
        param_6 = arcpy.Parameter()
        param_6.name = u'Is_NAD27'
        param_6.displayName = u'Is NAD27'
        param_6.parameterType = 'Required'
        param_6.direction = 'Input'
        param_6.datatype = u'GPBoolean'
        param_6.value = u'false'

        # output_geodatabase
        param_7 = arcpy.Parameter()
        param_7.name = u'output_geodatabase'
        param_7.displayName = u'output geodatabase'
        param_7.parameterType = 'Required'
        param_7.direction = 'Input'
        param_7.datatype = (u'DEWorkspace', u'DEFeatureDataset')

        # output_coordinate_system
        param_8 = arcpy.Parameter()
        param_8.name = u'output_coordinate_system'
        param_8.displayName = u'output coordinate system'
        param_8.parameterType = 'Required'
        param_8.direction = 'Input'
        param_8.datatype = u'GPCoordinateSystem'

        # scratch_workspace
        param_9 = arcpy.Parameter()
        param_9.name = u'scratch_workspace'
        param_9.displayName = u'scratch workspace'
        param_9.parameterType = 'Required'
        param_9.direction = 'Input'
        param_9.datatype = u'DEFolder'

        return [param_1, param_2, param_3, param_4, param_5, param_6, param_7, param_8, param_9]

    def execute(self, parameters, messages):
        # import and reload the tool script to get the latest version; if making edits to the tool script
        import mapOutline_Arc10
        reload(mapOutline_Arc10)
        
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        mapOutline_Arc10.main(parameter_values) 

class ProjectCrossSectionData(object):
    """GeMS_ProjectCrossSectionData_Arc10.py"""
    def __init__(self):
        self.label = u'Project Map Data to Cross Section'
        self.description = u'Generates backdrop feature coverages useful in constructing a geologic cross section. Inputs include the GeologicMap feature dateset of an NCGMP09-style geodatabase, a cross-section line, and a DEM.'
        self.canRunInBackground = False
        self.category = u'Create and Edit'        
        
    def getParameterInfo(self):
        # GeMS_style_geodatabase
        param_1 = arcpy.Parameter()
        param_1.name = u'GeMS_style_geodatabase'
        param_1.displayName = u'GeMS-style geodatabase'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEWorkspace'

        # Project_all_features_in_GeologicMap
        param_2 = arcpy.Parameter()
        param_2.name = u'Project_all_features_in_GeologicMap'
        param_2.displayName = u'Project all features in GeologicMap'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'GPBoolean'
        param_2.value = u'true'

        # Feature_classes_to_Project
        param_3 = arcpy.Parameter()
        param_3.name = u'Feature_classes_to_Project'
        param_3.displayName = u'Feature classes to Project'
        param_3.parameterType = 'Optional'
        param_3.direction = 'Input'
        param_3.datatype = u'DEFeatureClass'
        param_3.multiValue = True

        # DEM
        param_4 = arcpy.Parameter()
        param_4.name = u'DEM'
        param_4.displayName = u'DEM'
        param_4.parameterType = 'Required'
        param_4.direction = 'Input'
        param_4.datatype = u'DERasterDataset'

        # Section_line
        param_5 = arcpy.Parameter()
        param_5.name = u'Section_line'
        param_5.displayName = u'Section line'
        param_5.parameterType = 'Required'
        param_5.direction = 'Input'
        param_5.datatype = u'GPFeatureLayer'

        # Start_quadrant
        param_6 = arcpy.Parameter()
        param_6.name = u'Start_quadrant'
        param_6.displayName = u'Start quadrant'
        param_6.parameterType = 'Required'
        param_6.direction = 'Input'
        param_6.datatype = u'GPString'
        param_6.filter.list = [u'LOWER_LEFT', u'LOWER_RIGHT', u'UPPER_LEFT', u'UPPER_RIGHT']

        # Output_name_token
        param_7 = arcpy.Parameter()
        param_7.name = u'Output_name_token'
        param_7.displayName = u'Output name token'
        param_7.parameterType = 'Required'
        param_7.direction = 'Input'
        param_7.datatype = u'GPString'

        # Vertical_exaggeration
        param_8 = arcpy.Parameter()
        param_8.name = u'Vertical_exaggeration'
        param_8.displayName = u'Vertical exaggeration'
        param_8.parameterType = 'Required'
        param_8.direction = 'Input'
        param_8.datatype = u'GPDouble'
        param_8.value = u'1'

        # Selection_distance
        param_9 = arcpy.Parameter()
        param_9.name = u'Selection_distance'
        param_9.displayName = u'Selection distance'
        param_9.parameterType = 'Required'
        param_9.direction = 'Input'
        param_9.datatype = u'GPDouble'

        # Add_LTYPE_and_PTTYPE
        param_10 = arcpy.Parameter()
        param_10.name = u'Add_LTYPE_and_PTTYPE'
        param_10.displayName = u'Add LTYPE and PTTYPE'
        param_10.parameterType = 'Required'
        param_10.direction = 'Input'
        param_10.datatype = u'GPBoolean'
        param_10.value = u'false'

        # Force_exit
        param_11 = arcpy.Parameter()
        param_11.name = u'Force_exit'
        param_11.displayName = u'Force exit'
        param_11.parameterType = 'Required'
        param_11.direction = 'Input'
        param_11.datatype = u'GPBoolean'
        param_11.value = u'false'

        # Scratch_workspace
        param_12 = arcpy.Parameter()
        param_12.name = u'Scratch_workspace'
        param_12.displayName = u'Scratch workspace'
        param_12.parameterType = 'Optional'
        param_12.direction = 'Input'
        param_12.datatype = (u'DEWorkspace', u'DEFeatureDataset')

        # Save_intermediate_data
        param_13 = arcpy.Parameter()
        param_13.name = u'Save_intermediate_data'
        param_13.displayName = u'Save intermediate data'
        param_13.parameterType = 'Required'
        param_13.direction = 'Input'
        param_13.datatype = u'GPBoolean'
        param_13.value = u'false'

        return [param_1, param_2, param_3, param_4, param_5, param_6, param_7, param_8, param_9, param_10, param_11, param_12, param_13]

    def execute(self, parameters, messages):
        # import and reload the tool script to get the latest version; if making edits to the tool script
        import GeMS_ProjectCrossSectionData_Arc10
        reload(GeMS_ProjectCrossSectionData_Arc10)
        
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_ProjectCrossSectionData_Arc10.main(parameter_values) 

class ProjectPointsToCrossSection(object):
    """GeMS_ProjectPtsToCrossSection_Arc10"""
    def __init__(self):
        self.label = u'Project Points to Cross Section'
        self.description = u'Projects points within specified distance of cross-section line to plane of cross section. Section may be vertically exaggerated. For orientation data, calculates apparent dip'
        self.canRunInBackground = False
        self.category= u'Create and Edit'
        
    def getParameterInfo(self):
        # Featureclass_that_contains_cross-section_line
        param_1 = arcpy.Parameter()
        param_1.name = u'Featureclass_that_contains_cross-section_line'
        param_1.displayName = u'Featureclass that contains cross-section line'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEFeatureClass'

        # Cross-section_Label
        param_2 = arcpy.Parameter()
        param_2.name = u'Cross-section_Label'
        param_2.displayName = u'Cross-section Label'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'GPString'

        # Point_class_to_be_projected
        param_3 = arcpy.Parameter()
        param_3.name = u'Point_class_to_be_projected'
        param_3.displayName = u'Point class to be projected'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.datatype = u'DEFeatureClass'

        # Key_field
        param_4 = arcpy.Parameter()
        param_4.name = u'Key_field'
        param_4.displayName = u'Key field'
        param_4.parameterType = 'Required'
        param_4.direction = 'Input'
        param_4.datatype = u'Field'
        param_4.parameterDependencies = ['2']

        # Vertical_exaggeration
        param_5 = arcpy.Parameter()
        param_5.name = u'Vertical_exaggeration'
        param_5.displayName = u'Vertical exaggeration'
        param_5.parameterType = 'Required'
        param_5.direction = 'Input'
        param_5.datatype = u'GPLong'

        # DEM
        param_6 = arcpy.Parameter()
        param_6.name = u'DEM'
        param_6.displayName = u'DEM'
        param_6.parameterType = 'Required'
        param_6.direction = 'Input'
        param_6.datatype = u'DERasterDataset'

        # Max_projection_distance
        param_7 = arcpy.Parameter()
        param_7.name = u'Max_projection_distance'
        param_7.displayName = u'Max projection distance'
        param_7.parameterType = 'Required'
        param_7.direction = 'Input'
        param_7.datatype = u'GPLong'

        # Output_feature_dataset
        param_8 = arcpy.Parameter()
        param_8.name = u'Output_feature_dataset'
        param_8.displayName = u'Output feature dataset'
        param_8.parameterType = 'Required'
        param_8.direction = 'Input'
        param_8.datatype = u'DEFeatureDataset'

        # Output_feature_class_name
        param_9 = arcpy.Parameter()
        param_9.name = u'Output_feature_class_name'
        param_9.displayName = u'Output feature class name'
        param_9.parameterType = 'Required'
        param_9.direction = 'Input'
        param_9.datatype = u'GPString'

        # Scratch_workspace
        param_10 = arcpy.Parameter()
        param_10.name = u'Scratch_workspace'
        param_10.displayName = u'Scratch workspace'
        param_10.parameterType = 'Optional'
        param_10.direction = 'Input'
        param_10.datatype = (u'DEWorkspace', u'DEFeatureDataset')

        return [param_1, param_2, param_3, param_4, param_5, param_6, param_7, param_8, param_9, param_10]
        
    def execute(self, parameters, messages):
        # import and reload the tool script to get the latest version; if making edits to the tool script
        import GeMS_ProjectPtsToCrossSection_Arc10
        reload(GeMS_ProjectPtsToCrossSection_Arc10)
        
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_ProjectPtsToCrossSection_Arc10.main(parameter_values)         

class InclinationNumber(object):
    """GeMS_InclinationNumbers_Arc10.py"""
    def __init__(self):
        self.label = u'Inclination Numbers'
        self.description = u'Creates annotation feature class OrientationPointLabels with dip and plunge numbers for appropriate features within OrientationPoints. Adds the new annotation feature class to your map composition. '
        self.canRunInBackground = False
        self.category = u'Cartography'
        
    def getParameterInfo(self):
        # Feature_dataset
        param_1 = arcpy.Parameter()
        param_1.name = u'Feature_dataset'
        param_1.displayName = u'Feature dataset'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEFeatureDataset'

        # Map_scale_denominator
        param_2 = arcpy.Parameter()
        param_2.name = u'Map_scale_denominator'
        param_2.displayName = u'Map scale denominator'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'GPDouble'

        return [param_1, param_2]

    def execute(self, parameters, messages):
        # import and reload the tool script to get the latest version; if making edits to the tool script
        import GeMS_InclinationNumbers_Arc10
        reload(GeMS_InclinationNumbers_Arc10)
        
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_InclinationNumbers_Arc10.main(parameter_values)  

class SetPlotAtScales(object):
    """GeMS_SetPlotAtScales_Arc10.py"""
    def __init__(self):
        self.label = u'Set PlotAtScale values'
        self.description = u'Sets values of item PlotAtScale so that a definition query ( [PlotAtScale] >= map scale ) limits displayed features to those that can be shown without crowding at the specified map scale'
        self.canRunInBackground = False
        self.category = u'Cartography'
        
    def getParameterInfo(self):
        # Feature_class
        param_1 = arcpy.Parameter()
        param_1.name = u'Feature_class'
        param_1.displayName = u'Feature class'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEFeatureClass'

        # Minimum_separation__mm_
        param_2 = arcpy.Parameter()
        param_2.name = u'Minimum_separation__mm_'
        param_2.displayName = u'Minimum separation (mm)'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'GPDouble'
        param_2.value = u'8'

        # Maximum_value_of_PlotAtScale
        param_3 = arcpy.Parameter()
        param_3.name = u'Maximum_value_of_PlotAtScale'
        param_3.displayName = u'Maximum value of PlotAtScale'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.datatype = u'GPDouble'
        param_3.value = u'500000'

        return [param_1, param_2, param_3]

    def execute(self, parameters, messages):
        # import and reload the tool script to get the latest version; if making edits to the tool script
        import GeMS_SetPlotAtScales_Arc10
        reload(GeMS_SetPlotAtScales_Arc10)
        
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_SetPlotAtScales_Arc10.main(parameter_values) 

class SetSymbols(object): 
    """GeMS_SetSymbols_Arc10.py"""
    def __init__(self):
        self.label = u'Set Symbol Values'
        self.canRunInBackground = False
        self.description = u'Sets the Symbol attribute for some features in an GeMS-style geodatabase to match symbol IDs in the GSC implementation of the FGDC Digital Cartographic Standard for Geologic Map Symbolization (FGDC-STD-013-2006).'
        self.category = u'Cartography'
        
    def getParameterInfo(self):
        # Feature_dataset
        param_1 = arcpy.Parameter()
        param_1.name = u'Feature_dataset'
        param_1.displayName = u'Feature dataset'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEFeatureDataset'

        # Map_scale_denominator
        param_2 = arcpy.Parameter()
        param_2.name = u'Map_scale_denominator'
        param_2.displayName = u'Map scale denominator'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'GPDouble'

        # Certain_to_approximate_threshold__mm_on_map
        param_3 = arcpy.Parameter()
        param_3.name = u'Certain_to_approximate_threshold__mm_on_map'
        param_3.displayName = u'Certain to approximate threshold, mm on map'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.datatype = u'GPDouble'
        param_3.value = u'1'

        # Use__inferred___short_dash___line_symbols
        param_4 = arcpy.Parameter()
        param_4.name = u'Use__inferred___short_dash___line_symbols'
        param_4.displayName = u'Use "inferred" (short dash)  line symbols'
        param_4.parameterType = 'Required'
        param_4.direction = 'Input'
        param_4.datatype = u'GPBoolean'
        param_4.value = u'false'

        # Approximate_to_inferred_threshold__mm_on_map
        param_5 = arcpy.Parameter()
        param_5.name = u'Approximate_to_inferred_threshold__mm_on_map'
        param_5.displayName = u'Approximate to inferred threshold, mm on map'
        param_5.parameterType = 'Optional'
        param_5.direction = 'Input'
        param_5.datatype = u'GPDouble'

        # Use_approximate_strike-and-dip_symbols
        param_6 = arcpy.Parameter()
        param_6.name = u'Use_approximate_strike-and-dip_symbols'
        param_6.displayName = u'Use approximate strike-and-dip symbols'
        param_6.parameterType = 'Required'
        param_6.direction = 'Input'
        param_6.datatype = u'GPBoolean'
        param_6.value = u'true'

        # OrientationConfidenceDegrees_threshold
        param_7 = arcpy.Parameter()
        param_7.name = u'OrientationConfidenceDegrees_threshold'
        param_7.displayName = u'OrientationConfidenceDegrees threshold'
        param_7.parameterType = 'Required'
        param_7.direction = 'Input'
        param_7.datatype = u'GPDouble'
        param_7.value = u'8'

        # Set_polygon_symbols_and_labels
        param_8 = arcpy.Parameter()
        param_8.name = u'Set_polygon_symbols_and_labels'
        param_8.displayName = u'Set polygon symbols and labels'
        param_8.parameterType = 'Required'
        param_8.direction = 'Input'
        param_8.datatype = u'GPBoolean'
        param_8.value = u'true'

        return [param_1, param_2, param_3, param_4, param_5, param_6, param_7, param_8]
        
    def execute(self, parameters, messages):
        # import and reload the tool script to get the latest version; if making edits to the tool script
        import GeMS_SetSymbols_Arc10
        reload(GeMS_SetSymbols_Arc10)
        
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_SetSymbols_Arc10.main(parameter_values) 

class SetIDvalues(object): 
    """\Scripst\GeMS_reID_Arc10.py"""       
    def __init__(self):
        self.label = u'Set ID values'
        self.canRunInBackground = False
        self.description = u'GeMS-style geodatabases use _ID values as primary keys and ID values as foreign keys to tie various tables together. This script (re)generates _ID values while preserving any links established by existing _ID and ID values. As an option, GUIDs may be substituted for plain-text _ID and ID values.'
        self.category = u'Finalize'
        
    def getParameterInfo(self):
        # Input_GeMS_style_geodatabase
        param_1 = arcpy.Parameter()
        param_1.name = u'Input_GeMS_style_geodatabase'
        param_1.displayName = u'Input GeMS-style geodatabase'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEWorkspace'

        # Use_GUIDs
        param_2 = arcpy.Parameter()
        param_2.name = u'Use_GUIDs'
        param_2.displayName = u'Use GUIDs'
        param_2.parameterType = 'Optional'
        param_2.direction = 'Input'
        param_2.datatype = u'GPBoolean'
        param_2.value = u'false'

        # Do_not_reset_DataSource_IDs
        param_3 = arcpy.Parameter()
        param_3.name = u'Do_not_reset_DataSource_IDs'
        param_3.displayName = u'Do not reset DataSource_IDs'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.datatype = u'GPBoolean'
        param_3.value = u'true'

        return [param_1, param_2, param_3]
        
    def execute(self, parameters, messages):
        # import and reload the tool script to get the latest version; if making edits to the tool script
        import GeMS_reID_Arc10
        reload(GeMS_reID_Arc10)
        
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_reID_Arc10.main(parameter_values) 

class FGDC_1(object):
    """GeMS_FGDC1_Arc10.py"""
    def __init__(self):
        self.label = u'FGDC metadata, step 1'
        self.canRunInBackground = False
        self.category = u'Finalize'
        
    def getParameterInfo(self):
        # GeMS_style_database
        param_1 = arcpy.Parameter()
        param_1.name = u'GeMS_style_database'
        param_1.displayName = u'GeMS-style database'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEWorkspace'

        return [param_1]

    def execute(self, parameters, messages):
        import GeMS_FGDC1_Arc10
        reload(GeMS_FGDC1_Arc10)
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_FGDC1_Arc10.main(parameter_values) 

class FGDC_2(object):
    """GeMS_FGDC2_Arc10.py"""
    def __init__(self):
        self.label = u'FGDC metadata, step 2'
        self.canRunInBackground = False
        self.category = u'Finalize'
        
    def getParameterInfo(self):
        # GeMS_style_database
        param_1 = arcpy.Parameter()
        param_1.name = u'GeMS_style_database'
        param_1.displayName = u'GeMS-style database'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEWorkspace'

        # XML_metadata
        param_2 = arcpy.Parameter()
        param_2.name = u'XML_metadata'
        param_2.displayName = u'XML metadata'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'DETextFile'

        # definitionExtensions
        param_3 = arcpy.Parameter()
        param_3.name = u'definitionExtensions'
        param_3.displayName = u'definitionExtensions'
        param_3.parameterType = 'Optional'
        param_3.direction = 'Input'
        param_3.datatype = u'DETextFile'

        return [param_1, param_2, param_3]

    def execute(self, parameters, messages):
        import GeMS_FGDC2_Arc10
        reload(GeMS_FGDC2_Arc10)
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_FGDC2_Arc10.main(parameter_values)

class FGDC_3(object):
    """GeMS_FGDC3_Arc10.py"""   
    def __init__(self):
        self.label = u'FGDC metadata, step 3'
        self.canRunInBackground = False
        self.category = u'Finalize'
        
    def getParameterInfo(self):
        # GeMS_style_geodatabase
        param_1 = arcpy.Parameter()
        param_1.name = u'GeMS_style_geodatabase'
        param_1.displayName = u'GeMS-style geodatabase'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEWorkspace'

        # xml_directory
        param_2 = arcpy.Parameter()
        param_2.name = u'xml_directory'
        param_2.displayName = u'xml directory'
        param_2.parameterType = 'Optional'
        param_2.direction = 'Input'
        param_2.datatype = u'DEFolder'

        return [param_1, param_2]

    def execute(self, parameters, messages):
        import GeMS_FGDC3_Arc10
        reload(GeMS_FGDC3_Arc10)
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_FGDC3_Arc10.main(parameter_values)
        
class PurgeMetadata(object):
    """GeMS_PurgeMetadata"""
    def __init__(self):
        self.label = u'Purge Metadata'
        self.description = u'Purges metadata of geoprocessing history. (1) Exports existing metadata as FGDC CSDGM2 metadata, (2) clears metadata with USGS EGIS clear internal metadata tool, and (3) imports exported CSDGM2 metadata.\r\n\r\n'
        self.canRunInBackground = False
        self.category = u'Finalize'
        
    def getParameterInfo(self):
        # Input_geodatabase
        param_1 = arcpy.Parameter()
        param_1.name = u'Input_geodatabase'
        param_1.displayName = u'Input geodatabase'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEWorkspace'

        # Output_directory
        param_2 = arcpy.Parameter()
        param_2.name = u'Output_directory'
        param_2.displayName = u'Output directory'
        param_2.parameterType = 'Optional'
        param_2.direction = 'Input'
        param_2.datatype = u'DEFolder'

        return [param_1, param_2]
     
    def execute(self, parameters, messages):
        import GeMS_PurgeMetadata_Arc10
        reload(GeMS_PurgeMetadata_Arc10)
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_PurgeMetadata_Arc10.main(parameter_values)
        
class RelationshipClasses(object):
    """GeMS_RelationshipClasses1_Arc10.py"""

    def __init__(self):
        self.label = u'Relationship Classes'
        self.description = u'Adds numerous relationship classes to a GeMS database'
        self.canRunInBackground = False
        self.category = u'Finalize'
        
    def getParameterInfo(self):
        # GeMS_geodatabase
        param_1 = arcpy.Parameter()
        param_1.name = u'GeMS_geodatabase'
        param_1.displayName = u'GeMS geodatabase'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEWorkspace'

        return [param_1]
        
    def execute(self, parameters, messages):
        import GeMS_RelationshipClasses1_Arc10
        reload(GeMS_RelationshipClasses1_Arc10)
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_RelationshipClasses1_Arc10.main(parameter_values)
        
class FixStrings(object):
    """GeMS_FixStrings_Arc10"""
    def __init__(self):
        self.label = u'Fix string values'
        self.description = u'Cleans up text strings in a GeMS database. Removes leading and trailing spaces and fixes bad <null> values.'
        self.canRunInBackground = False
        self.category = u'Finalize'        
        
    def getParameterInfo(self):
        # Input_geodatabase
        param_1 = arcpy.Parameter()
        param_1.name = u'Input_geodatabase'
        param_1.displayName = u'Input geodatabase'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEWorkspace'

        return [param_1]
        
    def execute(self, parameters, messages):
        import FixStrings
        reload(FixStrings)
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        FixStrings.main(parameter_values)  

class TranslateToShape(object):
    """GeMS_TranslateToShape_Arc10""" 
    def __init__(self):
        self.label = u'Translate To Shapefiles'
        self.description = u'Translates geodatabase to shapefiles and (for long fields) pipe-delimited text files. '
        self.canRunInBackground = False
        self.category = u'Finalize'  
        
    def getParameterInfo(self):
        # Input_geodatabase
        param_1 = arcpy.Parameter()
        param_1.name = u'Input_geodatabase'
        param_1.displayName = u'Input geodatabase'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEWorkspace'

        # Output_workspace
        param_2 = arcpy.Parameter()
        param_2.name = u'Output_workspace'
        param_2.displayName = u'Output workspace'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'DEFolder'

        return [param_1, param_2]
        
    def execute(self, parameters, messages):
        import GeMS_TranslateToShape_Arc10
        reload(GeMS_TranslateToShape_Arc10)
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_TranslateToShape_Arc10.main(parameter_values) 
        
class SymbolToRGB(object):
    """GeMS_WPGCMYK_RGB"""
    def __init__(self):
        self.label = u'Symbol to RGB'
        self.description = u'Calculates values of AreaFillRGB in table DescriptionOfMapUnits.  Symbol values must be present and are assumed to reference the WPGCYMK color set.'
        self.canRunInBackground = False
        self.category = u'Finalize' 
        
    def getParameterInfo(self):
        # Input_geodatabase
        param_1 = arcpy.Parameter()
        param_1.name = u'Input_geodatabase'
        param_1.displayName = u'Input geodatabase'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEWorkspace'

        return [param_1]

    def execute(self, parameters, messages):
        import GeMS_WPGCMYK_RGB
        reload(GeMS_WPGCMYK_RGB)
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_WPGCMYK_RGB.main(parameter_values)
        
class TopologyCheck(object):
    """GeMS_TopologyCheck_Arc10"""
    def __init__(self):
        self.label = u'Topology Check'
        self.canRunInBackground = False
        self.category = u'Create and Edit'
        
    def getParameterInfo(self):
        # Feature_dataset
        param_1 = arcpy.Parameter()
        param_1.name = u'Feature_dataset'
        param_1.displayName = u'Feature dataset'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEFeatureDataset'

        # HKey_test_value
        param_2 = arcpy.Parameter()
        param_2.name = u'HKey_test_value'
        param_2.displayName = u'HKey test value'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'GPString'

        return [param_1, param_2]

    def execute(self, parameters, messages):
        import GeMS_TopologyCheck_Arc10
        reload(GeMS_TopologyCheck_Arc10)
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_TopologyCheck_Arc10.main(parameter_values)
        
class GeologicNamesCheck(object):
    """GeMS_GeolexCheck_Arc10"""
    def __init__(self):
        self.label = u'Geologic Names Check'
        self.description = u"This tool automates some of the steps in a geologic names review as required by USGS publication policy. It searches within a supplied list of map units for names and usages found in the U.S. Geologic Names Lexicon (Geolex) and provides a report template in spreadsheet form for the author and reviewer to use during the review process. The input is a GeMS-compliant DescriptionOfMapUnits (DMU) table and a list of U.S. state abbreviations within which the DMU is relevant. The tool reports the Geolex names found within the map unit name, the usages associated with those names, and whether or not the author's choice of geographic extent matches that found in Geolex. Comparisons of age and status (formal vs informal) are not at this time considered. "
        self.canRunInBackground = False
        self.category = u'Finalize'  
        
    def getParameterInfo(self):
        # DMU_Table
        param_1 = arcpy.Parameter()
        param_1.name = u'DMU_Table'
        param_1.displayName = u'DMU Table'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DETable'

        # States_extent
        param_2 = arcpy.Parameter()
        param_2.name = u'States_extent'
        param_2.displayName = u'States extent'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'GPString'

        # open_report_when_completed_
        param_3 = arcpy.Parameter()
        param_3.name = u'open_report_when_completed_'
        param_3.displayName = u'open report when completed?'
        param_3.parameterType = 'Optional'
        param_3.direction = 'Input'
        param_3.datatype = u'GPBoolean'
        param_3.value = u'true'

        return [param_1, param_2, param_3]
        
    def execute(self, parameters, messages):
        import GeMS_GeolexCheck_Arc10
        reload(GeMS_GeolexCheck_Arc10)
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_GeolexCheck_Arc10.main(parameter_values)
        
class ValidateDatabase(object):
    """GeMS_ValidateDatabase_Arc10"""
    def __init__(self):
        self.label = u'Validate Database'
        self.description = u'Checks an NCGMP09-style database for validity. Are required elements present? Are fields properly defined? Are invalid nulls present? Are required Glossary entries present? Are internally referenced objects (data sources, ...) present?'
        self.canRunInBackground = False
        self.category = u'Finalize'  
        
    def getParameterInfo(self):
        # Input_geodatabase
        param_1 = arcpy.Parameter()
        param_1.name = u'Input_geodatabase'
        param_1.displayName = u'Input geodatabase'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'DEWorkspace'

        # Output_workspace
        param_2 = arcpy.Parameter()
        param_2.name = u'Output_workspace'
        param_2.displayName = u'Output workspace'
        param_2.parameterType = 'Optional'
        param_2.direction = 'Input'
        param_2.datatype = u'DEFolder'

        # Refresh_GeoMaterialDict
        param_3 = arcpy.Parameter()
        param_3.name = u'Refresh_GeoMaterialDict'
        param_3.displayName = u'Refresh GeoMaterialDict'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.datatype = u'GPBoolean'
        param_3.value = u'false'

        # Skip_topology_checks
        param_4 = arcpy.Parameter()
        param_4.name = u'Skip_topology_checks'
        param_4.displayName = u'Skip topology checks'
        param_4.parameterType = 'Required'
        param_4.direction = 'Input'
        param_4.datatype = u'GPBoolean'
        param_4.value = u'false'

        # Delete_unused_Glossary_and_DataSources_rows
        param_5 = arcpy.Parameter()
        param_5.name = u'Delete_unused_Glossary_and_DataSources_rows'
        param_5.displayName = u'Delete unused Glossary and DataSources rows'
        param_5.parameterType = 'Required'
        param_5.direction = 'Input'
        param_5.datatype = u'GPBoolean'
        param_5.value = u'false'

        return [param_1, param_2, param_3, param_4, param_5]
        
    def execute(self, parameters, messages):
        import GeMS_ValidateDatabase_Arc10
        reload(GeMS_ValidateDatabase_Arc10)
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_ValidateDatabase_Arc10.main(parameter_values)
        
class DMUtoDocx(object):
    """GeMS_DMUtoDocx_Arc10"""
    def __init__(self):
        self.label = u'DMU to .docx'
        self.description = u'Reads table DescriptionOfMapUnits in an NCGMP09-style geodatabase and creates formatted Microsoft Word .docx file "Description of Map Units", using paragraph styles defined in USGS Pubs template MapManuscript_v1-0_04-11.dotx'
        self.canRunInBackground = False
        self.category = u'Create and Edit'       
        
    def getParameterInfo(self):
        # Source_geodatabase
        param_1 = arcpy.Parameter()
        param_1.name = u'Source_geodatabase'
        param_1.displayName = u'Source geodatabase'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = (u'DEWorkspace', u'DeFeatureDataset')

        # Output_workspace
        param_2 = arcpy.Parameter()
        param_2.name = u'Output_workspace'
        param_2.displayName = u'Output workspace'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'DEFolder'

        # Output_filename
        param_3 = arcpy.Parameter()
        param_3.name = u'Output_filename'
        param_3.displayName = u'Output filename'
        param_3.parameterType = 'Required'
        param_3.direction = 'Input'
        param_3.datatype = u'GPString'

        # Use_MapUnit_as_UnitLabl
        param_4 = arcpy.Parameter()
        param_4.name = u'Use_MapUnit_as_UnitLabl'
        param_4.displayName = u'Use MapUnit as UnitLabl'
        param_4.parameterType = 'Required'
        param_4.direction = 'Input'
        param_4.datatype = u'GPBoolean'
        param_4.value = u'true'

        # List_of_Map_Units
        param_5 = arcpy.Parameter()
        param_5.name = u'List_of_Map_Units'
        param_5.displayName = u'List of Map Units'
        param_5.parameterType = 'Required'
        param_5.direction = 'Input'
        param_5.datatype = u'GPBoolean'
        param_5.value = u'false'

        return [param_1, param_2, param_3, param_4, param_5]
        
    def execute(self, parameters, messages):
        import GeMS_DMUtoDocx_Arc10
        reload(GeMS_DMUtoDocx_Arc10)
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_DMUtoDocx_Arc10.main(parameter_values)
        
class RebuildMapUnits(object):
    """GeMS_RebuildMapUnits_Arc10.py"""
    def __init__(self):
        self.label = u'Rebuild MapUnit Polygons'
        self.canRunInBackground = False
        self.description = u'Rebuilds MapUnit Polygons from edited ContactsAndFaults'
        self.category = u'Create and Edit'
        #self.params = arcpy.GetParameterInfo()
        
    def getParameterInfo(self):
        # ContactsAndFaults
        param_1 = arcpy.Parameter()
        param_1.name = u'ContactsAndFaults'
        param_1.displayName = u'ContactsAndFaults'
        param_1.parameterType = 'Required'
        param_1.direction = 'Input'
        param_1.datatype = u'GPFeatureLayer'
        param_1.filter.list = ["Polyline"]

        # MapUnits
        param_2 = arcpy.Parameter()
        param_2.name = u'MapUnits'
        param_2.displayName = u'MapUnits'
        param_2.parameterType = 'Required'
        param_2.direction = 'Input'
        param_2.datatype = u'GPFeatureLayer'
        param_2.filter.list = ["Polygon"]

        # MapUnit_label_points
        param_3 = arcpy.Parameter()
        param_3.name = u'MapUnit_label_points'
        param_3.displayName = u'MapUnit label points'
        param_3.parameterType = 'Optional'
        param_3.direction = 'Input'
        param_3.datatype = u'GPFeatureLayer'
        param_3.filter.list = ["Point"]

        # save_copy_of_polygons_
        param_4 = arcpy.Parameter()
        param_4.name = u'save_copy_of_polygons_'
        param_4.displayName = u'save copy of polygons?'
        param_4.parameterType = 'Optional'
        param_4.direction = 'Input'
        param_4.datatype = u'Boolean'

        return [param_1, param_2, param_3, param_4]
        
    # def updateParameters(self, parameters):
        # validator = getattr(self, 'ToolValidator', None)
        # if validator:
             # return validator(parameters).updateParameters()
             
    def updateMessages(self, parameters):
        if parameters[1].value:
            #self.params[1].setErrorMessage(self.params[1].value.longName)
            if self.CheckEditSession(parameters[1].value):
                parameters[1].setErrorMessage("Save edits and close edit session first!")
             
    def CheckEditSession(self, lyr):
        """Check for an active edit session on an fc or table.
        Return True of edit session active, else False"""
        edit_session = True
        row1 = None
        try:
            # attempt to open two cursors on the input
            # this generates a RuntimeError if no edit session is active
            OID = "OBJECTID" 
            with arcpy.da.UpdateCursor(lyr.dataSource, OID) as rows:
                row = next(rows)
                with arcpy.da.UpdateCursor(lyr.dataSource, OID) as rows2:
                    row2 = next(rows2)
        except RuntimeError as e:
            if e.message == "workspace already in transaction mode":
                # this error means that no edit session is active
                edit_session = False
            else:
                # we have some other error going on, report it
                raise
        return edit_session
        
    def execute(self, parameters, messages):
        # import and reload the tool script to get the latest version; if making edits to the tool script
        import GeMS_RebuildMapUnits_Arc10
        reload(GeMS_RebuildMapUnits_Arc10)
        
        # construct a list of parameter.valueAsText strings to send to the tool
        parameter_values = [parameter.valueAsText for parameter in parameters]
        
        # the script tool has been imported as a module. Now call the main function
        GeMS_RebuildMapUnits_Arc10.main(parameter_values) 