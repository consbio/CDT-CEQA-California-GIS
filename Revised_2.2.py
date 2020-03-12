import arcpy

scratch_ws = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Scratch\Scratch.gdb"

urbanized_area_prc_21071_input = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb\urbanized_area_prc_21071"
urban_area_prc_21094_5_output = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb\urban_area_prc_21094_5"

#arcpy.CopyFeatures_management(urbanized_area_prc_21071_input, urban_area_prc_21094_5_output)
arcpy.AddField_management(urban_area_prc_21094_5_output, "urban_area_prc_21094_5", "SHORT")

urban_area_prc_21094_5_output_layer = arcpy.MakeFeatureLayer_management(urban_area_prc_21094_5_output)
expression = "community_type = 'Incorporated City' or urbanized_area_prc_21071 = 1"

arcpy.SelectLayerByAttribute_management(urban_area_prc_21094_5_output_layer, "NEW_SELECTION", expression)
arcpy.CalculateField_management(urban_area_prc_21094_5_output_layer, "urban_area_prc_21094_5", 1)
arcpy.SelectLayerByAttribute_management(urban_area_prc_21094_5_output_layer, "SWITCH_SELECTION")
arcpy.CalculateField_management(urban_area_prc_21094_5_output_layer, "urban_area_prc_21094_5", 0)

