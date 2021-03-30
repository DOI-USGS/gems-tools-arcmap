"""
Geologic Names Check
name-fullname - This version checks for Geolex names in both the name and fullname and then processes the set 
with the fewest entries to minimize the number of Geolex names and usages that are reported.

Arguments: 
    DMU - GeMS DescriptionOfMapUnits table. Geodatabase, CSV, tab delimeted TXT, or DBF. Required.
    Extent - one or more (comma separated) state or US region abbreviations. Required.
    open report - open the Excel report file when finished. True (default) or False. Optional.
    
Enclose any arguments with spaces within double-quotes.

Arguments are sent to \Resources\GeMS_GeolexCheck.exe which contains bundled Python 3 libraries used in the original development
rather than requiring the user to install the equivalent Python 2.7 versions
"""

import os, sys
import arcpy
import re
from distutils.util import strtobool
from GeMS_utilityFunctions import *

versionString = "GeMS_GeolexCheck_Arc10.py, 1/12/2021"
rawurl = 'https://raw.githubusercontent.com/usgs/gems-tools-arcmap/master/Scripts/GeMS_GeolexCheck_Arc10.py'

def main(parameters):
    if not len(parameters) >= 2:
        print(__doc__)
        quit()

    arcpy.AddMessage(versionString)
    checkVersion(versionString, rawurl, 'gems-tools-arcmap')
    
    # collect the path to the DMU table
    dmu = parameters[0]
    arcpy.AddMessage("Evaluating {}".format(dmu))
           
    # get parent directory
    head_tail = os.path.split(dmu)
    dmu_home = head_tail[0]
    dmu_name = os.path.splitext(head_tail[1])[0]

    # if the input is a gdb table, convert to csv
    # with the ArcMap parameter form, the EXE will never be sent a GDB table
    if os.path.splitext(dmu_home)[1] == '.gdb':
        out_dir = os.path.dirname(dmu_home)
        csv_f = "{}.csv".format(dmu_name)
        out_path = os.path.join(out_dir, csv_f)
        if arcpy.Exists(out_path): arcpy.Delete_management(out_path)
        arcpy.TableToTable_conversion(dmu, out_dir, csv_f)
        in_table = out_path
    else:
        in_table = dmu
      
    # collect and clean the extent of the DMU. 
    # can be single state or list of states, comma separated,
    # can be upper or lower case
    dmu_str = parameters[1]

    # open the report after running?
    if len(parameters) == 3:
        open_xl = bool(strtobool(parameters[2]))
    else:
        open_xl = True

    # location of GeMS_GeolexCheck.exe
    # it is hard dealing with possible spaces in the path name
    # when sending this argument to the exe file so we'll just
    # cd to \Resources first and then call the exe by name alone
    this_py = os.path.realpath(__file__)
    this_dir = os.path.dirname(this_py)
    toolbox_dir = os.path.dirname(this_dir)
    os.chdir(os.path.join(toolbox_dir, 'Resources'))
    #geolex_exe = os.path.join(toolbox_dir, 'Resources', 'GeMS_GeolexCheck.exe')

    arcpy.AddMessage("Sending parameters to GeMS_GeolexCheck.exe")
    arcpy.AddMessage("A terminal window will open to display output messages.")

    os.system('GeMS_GeolexCheck.exe "{}" "{}" {} & pause'.format(in_table, dmu_str, open_xl))

if __name__ == '__main__':
    main(sys.argv[1:])