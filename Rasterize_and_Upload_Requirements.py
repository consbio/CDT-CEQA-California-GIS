# NOTE!!!!!!!!: The import metadata tool doesn't work in 64 bit python. Run this script using 32 bit.
# The registration tool may not work with 64 bit.
import arcpy

arcpy.ImportToolbox(r"F:\data_management\script_tools\CBI Data Management Toolbox.tbx")

parcels_fc = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs.gdb\sacramento_parcels"
#parcels_fc = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs.gdb\sacramento_parcels_subset3"

output_ws = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Raster_Requirement_Dumps.gdb"
metadata_template = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Metadata\Metadata_Templates.gdb\raster_requirements_metadata"

lyr_file = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Lyr\requirements_raster_conversion.lyr"

resolution = 10

arcpy.env.workspace = output_ws

#fields = ["urbanized_area_prc_21071", "urban_area_prc_21094", "within_city_limits", "unincorporated_urbanized_area", "within_mpo"]
#fields = ["urban_area_prc_21094", "within_city_limits", "unincorporated_urbanized_area", "within_mpo"]
fields = [u'MajTS_3_1', u'HighQualTC_3_4', u'HighQualTC_3_2', u'StpTC_1_2m_3_5', u'Infill_PRC_4_1', u'Wetlands_8_1', u'RipWet_8_2', u'Spec_Habitat_8_3', u'WildHaz_9_3', u'EQFault_9_2']

for field in fields:
    output_raster = field
    print "Converting field values to raster: " + output_raster
    arcpy.PolygonToRaster_conversion(parcels_fc, field, output_raster, "", "", resolution)
    # Doesn't work in 64 bit python .

    print "Importing metadata..."
    arcpy.MetadataImporter_conversion(source=metadata_template, target=output_raster)

    print "Uploading raster to Data Basin..."
    arcpy.RegisterUploadCBIProducts_CBIDataManagementToolbox(output_raster, "Inputs", "", "", "", "1", "0", lyr_file, "consbio", "treerivergreen")


