########################################################################################################################
# File name: Prepare_Parcels.py
# Author: Mike Gough
# Date created: 02/28/2020
# Date last modified: 02/28/2020
# Python Version: 2.7
# Description:
# Projects all of the parcels data for the state of California and deletes parcels with duplicate geometries
########################################################################################################################

import arcpy
import glob
import os

parcels_dir = r"\\loxodonta\GIS\Source_Data\planningCadastre\state\CA\CoreLogic_Parcels\Counties\PARCEL_DATA"
output_gdb = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels_Projected_Delete_Identical.gdb"

gdb_list = glob.glob(parcels_dir + "/*/*.gdb")

for gdb in gdb_list:
    arcpy.env.workspace = gdb
    parcels_fc = arcpy.ListFeatureClasses("*Parcels")[0]
    print parcels_fc
    output_parcels_fc = output_gdb + os.sep + parcels_fc
    print "Projecting..."
    arcpy.Project_management(parcels_fc, output_parcels_fc, "PROJCS['NAD_1983_California_Teale_Albers',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['False_Easting',0.0],PARAMETER['False_Northing',-4000000.0],PARAMETER['Central_Meridian',-120.0],PARAMETER['Standard_Parallel_1',34.0],PARAMETER['Standard_Parallel_2',40.5],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]", "", "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", "NO_PRESERVE_SHAPE", "", "NO_VERTICAL")
    print "Deleting Identical..."
    arcpy.DeleteIdentical_management(output_parcels_fc, "SHAPE", "", "0")
