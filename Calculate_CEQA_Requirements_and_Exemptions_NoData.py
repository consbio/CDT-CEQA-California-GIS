import os
import arcpy
import datetime
arcpy.env.overwriteOutput = True

arcpy.CheckOutExtension("Spatial")

create_parcel_points = 0

# Workspaces
intermediate_ws = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb"
scratch_ws = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Scratch\Scratch.gdb"
output_ws_data_basin = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs_for_DataBasin.gdb'
output_ws_dev_team = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs_for_DevTeam.gdb'

#TEST
#output_ws_data_basin = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Test\Outputs_for_DataBasin.gdb'
#output_ws_dev_team = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Test\Outputs_for_DevTeam.gdb'
#output_ws_data_basin = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Test\Outputs_Check_Exemptions_For_DataBasin.gdb'
#output_ws_dev_team = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Test\Outputs_Check_Exemptions_For_DevTeam.gdb'


# Input & output parcel feature classes
input_parcels_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels.gdb\sacramento_parcels"
output_parcels_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs_for_DataBasin.gdb\sacramento_parcels_requirements"

#TEST
#output_parcels_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Test\Outputs_Check_Exemptions_For_DataBasin.gdb\parcels_to_test_with_requirements_one_parcel"

original_fields_to_keep = [
    "PARCEL_APN",
    "FIPS_CODE",
    "COUNTYNAME",
    "TAXAPN",
    "SITE_ADDR",
    "SITE_CITY",
    "SITE_STATE",
    "SITE_ZIP",
    "LATITUDE",
    "LONGITUDE",
    "CENSUS_TRACT",
    "CENSUS_BLOCK_GROUP",
    "Zoning",
    "LOT_SIZE_AREA",
    "LOT_SIZE_AREA_UNIT",
    "PARCEL_ID",
    "SHAPE_Length",
    "SHAPE_Area"
]


# Datasets used in calculating requirements:
# 0.1
urbanized_area_prc_21071_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb\urbanized_area_prc_21071"

# 0.1, 2.1, 2.2, 2.3
city_boundaries_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\CA_TIGER_2019_incorporated_cities_with_TIGER_2017_population"
unincorporated_islands = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb\CA_TIGER_Unincorporated_Islands_with_Population_Dissolve" #2.2

# 2.4
urbanized_area_urban_cluster_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\CA_urbanized_area_urban_cluster"
incorporated_and_unincorporated_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\CA_incorporated_and_unincorporated"

# 2.5
mpo_boundary_dissolve_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb\MPO_boundaries_dissolve"

# 8.5
rare_threatened_or_endangered_fc = r"Database Connections\CBI Intermediate.sde\cbiintermediate.mike_gough.CA_Rare_Threatened_or_Endangered_Erase_Impervious_del_fields"

# 9.3
wildfire_hazard_raster = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\wildfire_hazard_fthrt_14_2_reclass_3_5"

# 9.4
flood_plain_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\CA_100_Year_FEMA_Floodplain"

# 9.5
landslide_area_percent_threshold = 20 # The percent of the parcel that must have a very high landslide susceptibility value.
landslide_hazard_raster = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\CA_ms58_very_high_landslide_susceptibility_1s"

# 9.6
state_conservancy_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\CA_State_Conservancy_ds1754"

# 9.7
local_coastal_zone_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\CA_Coastal_Zone_Boundary_ds990"

# 9.8
protected_area_mask_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\CA_protected_area_mask"

parcel_points_fc = scratch_ws + os.sep + "parcels_point"

if create_parcel_points:
    arcpy.FeatureToPoint_management(output_parcels_fc, parcel_points_fc)

start_time = datetime.datetime.now()
print("Start Time: " + str(start_time))

# Requirements that begin with 0 aren't applicable to any exemptions
requirements = {
    0.1: "urbanized_area_prc_21071_unincorporated_0_1",
    # Location Requirements
    2.1: "urbanized_area_prc_21071_2_1",
    2.2: "urban_area_prc_21094_2_2",
    2.3: "within_city_limits_2_3",
    2.4: "unincorporated_2_4",
    2.5: "within_mpo_2_5",
    2.6: "covered_by_a_specific_plan_2_6",
    2.7: "urbanized_area_or_urban_cluster_2_7",
    # Transit Proximity Requirements
    3.1: "within_half_mile_major_transit_stop_3_1",
    3.2: "within_quarter_mile_transit_corridor_3_2",
    3.3: "transit_priority_area_3_3",
    3.4: "within_half_mile_transit_corridor_3_4",
    3.5: "within_half_mile_stop_transit_corridor_3_5",
    3.6: "low_vmt_15_percent_below_regional_3_6",
    3.7: "low_vmt_15_percent_below_city_3_7",
    3.8: "low_vehicle_travel_area_3_8",
    # Environmental Limitations
    8.1: "wetlands_8_1",
    8.2: "riparian_areas_8_2",
    8.3: "special_habitats_8_3",
    8.4: "species_of_concern_8_4",
    8.5: "rare_threatened_endangered_sp_8_5",
    # Hazards
    9.1: "sea_level_rise_9_1",
    9.2: "earthquake_hazard_zone_9_2",
    9.3: "wildfire_hazard_9_3",
    9.4: "flood_plain_9_4",
    9.5: "landslide_hazard_9_5",
    9.6: "state_conservancy_9_6",
    9.7: "local_coastal_zone_9_7",
    9.8: "protected_area_mask_9_8",
}

#####!!!!! Make sure that all the requirements specified for each exemption e.g., [2.3, 2.4]
##### will exist either through a requirement calculation or a join from other staff.
##### Otherwise, this script will abort when it calculates the exemptions.
exemptions = {
    1: ['21159.24', 'Resources Code', [2.1, 3.1, 8.1, 8.2, 8.3, 9.2, 9.3, 9.4, 9.5, 9.6]],
    2: ['21155.1', 'Resources Code', [2.5, [3.1, 3.4], 8.1, 8.2, 8.3, 9.2, 9.3, 9.4, 9.5]], # Remove requirement 3.2 and add requirement 3.1
    3: ['21155.2', 'Resources Code', [2.5, [3.1, 3.4]]],# Added 3.1 and 3.4
    4: ['21155.4', 'Resources Code', [2.5, 2.6, 3.3]],
    5: ['21094.5', 'Resources Code', [2.2, [3.1, 3.5, 3.8]]],# Removed 2.6 and 3.4
    6: ['65457', 'Government Code', [2.6]],# Removed 8.1 - 8.3. Removed 9.2-9.5
    8: ['15332', 'CEQA Guidelines', [2.3]],
    9: ['21159.25', 'Resources Code', [2.4, 2.7]],
    10: ['15303', 'CEQA Guidelines', [2.1]],
    11: ['21099', 'Resources Code', [3.3]],
    14: ['21159.28', 'Resources Code', [2.5]],
    15: ['15064.3', 'CEQA Guidelines', [[3.1, 3.5, 3.6, 3.7]]]# Remove 3.4. Add 3.5.
}

#02/13/2020 Adjustments for new requirement additions and other changes made by Helen + fix discrepencies.
exemptions = {
 1: ['21159.24', 'Resources Code', [2.1, 3.1, 8.1, 8.2, 8.3, 9.2, 9.3, 9.4, 9.5, 9.6]],
 2: ['21155.1', 'Resources Code', [2.5, [3.2, 3.13, 3.14], 8.1, 8.2, 8.3, 9.2, 9.3, 9.4, 9.5]], # Remove 3.1, 3.4. Add 3.2, 3.13, 3.14
 3: ['21155.2', 'Resources Code', [2.5, [3.1, 3.4, 3.9, 3.12]]], # Add 3.9, 3.12
 4: ['21155.4', 'Resources Code', [2.5, 2.6, 3.3]],
 5: ['21094.5', 'Resources Code', [2.2, [3.1, 3.5, 3.8, 3.10, 3.11]]], # Add 3.10, 3.11
 6: ['65457', 'Government Code', [2.6]],
 8: ['15332', 'CEQA Guidelines', [2.3]],
 9: ['21159.25', 'Resources Code', [2.4, 2.7]],
 10: ['15303', 'CEQA Guidelines', [2.1]],
 11: ['21099', 'Resources Code', [3.3]],
 14: ['21159.28', 'Resources Code', [2.5]],
 15: ['15064.3', 'CEQA Guidelines', [[3.1, 3.5, 3.6, 3.7]]]
}

#03/06/2020 Feb 18 version of Criteria Spreadsheet. Includes updates from Helen as well as the addition of the species requirement (8.5). Does not included 3.9 -3.14 (yellow stuff)
exemptions = {
    1: ['21159.24', 'Resources Code', [2.1, 3.1, 8.1, 8.2, 8.3, 8.5, 9.2, 9.3, 9.4, 9.5, 9.6]],
    2: ['21155.1', 'Resources Code', [2.5, [3.2], 8.1, 8.2, 8.3, 8.5, 9.2, 9.3, 9.4, 9.5]],
    3: ['21155.2', 'Resources Code', [2.5, [3.1, 3.4]]],
    4: ['21155.4', 'Resources Code', [2.5, 2.6, 3.3]],
    5: ['21094.5', 'Resources Code', [2.2, [3.1, 3.5, 3.8]]],
    6: ['65457', 'Government Code', [2.6]],
    #7: ['15183', ''], # No Requirements
    8: ['15332', 'CEQA Guidelines', [2.3, 8.5]],
    9: ['21159.25', 'Resources Code', [2.4, 2.7, 8.5]],
    #10: ['15303', 'CEQA Guidelines', [2.1]], # No Requirements
    11: ['21099', 'Resources Code', [3.3]],
    14: ['21159.28', 'Resources Code', [2.5]],
    15: ['15064.3', 'CEQA Guidelines', [[3.1, 3.5, 3.6, 3.7]]]
}

arcpy.env.workspace = output_ws_dev_team

if arcpy.Exists(output_parcels_fc):
    existing_output_fields = [field.name for field in arcpy.ListFields(output_parcels_fc)]

# ACTIONS ##############################################################################################################


def copy_parcels_fc():

    print "Copying Parcels Feature Class with the following fields..."

    # create an empty field mapping object
    mapS = arcpy.FieldMappings()
    # for each field, create an individual field map, and add it to the field mapping object
    for field in original_fields_to_keep:
        print field
        map = arcpy.FieldMap()
        map.addInputField(input_parcels_fc, field)
        mapS.addFieldMap(map)

    out_folder = os.path.dirname(output_parcels_fc)
    base_name = os.path.basename(output_parcels_fc)

    # Create the empty parcels feature class with the subset of original fields to keep
    arcpy.FeatureClassToFeatureClass_conversion(
        in_features=input_parcels_fc,
        out_path=out_folder, out_name=base_name, where_clause="",
        field_mapping=mapS,
        config_keyword="")


# Function Handler that calls the INDIVIDUAL REQUIREMENT function for processing.
def calculate_parcel_requirements(requirements_to_process, start_oid=False, end_oid=False):

    if arcpy.Exists(output_parcels_fc):
        existing_output_fields = [field.name for field in arcpy.ListFields(output_parcels_fc)]

    print "\nCalculating 1's and 0's for spatial requirements...."

    # For requirements requiring an update cursor
    if 0.1 in requirements_to_process:
        print "Calculating requirement 0.1...\n"
        field_to_calc = requirements[0.1]
        if not field_to_calc in existing_output_fields:
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
        calc_requirement_0_1(field_to_calc)

    # For requirements requiring an update cursor
    if 2.1 in requirements_to_process:
        print "Calculating requirement 2.1...\n"
        field_to_calc = requirements[2.1]
        if not field_to_calc in existing_output_fields:
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
        calc_requirement_2_1(field_to_calc, start_oid, end_oid)

    if 2.2 in requirements_to_process:
        print "Calculating requirement 2.2...\n"
        field_to_calc = requirements[2.2]
        if not field_to_calc in existing_output_fields:
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
        calc_requirement_2_2(field_to_calc)

    if 2.3 in requirements_to_process:
        print "Calculating requirement 2.3...\n"
        field_to_calc = requirements[2.3]
        if not field_to_calc in existing_output_fields:
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
        calc_requirement_2_3(field_to_calc)

    if 2.4 in requirements_to_process:
        print "Calculating requirement 2.4...\n"
        field_to_calc = requirements[2.4]
        if not field_to_calc in existing_output_fields:
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
        calc_requirement_2_4(field_to_calc)

    if 2.5 in requirements_to_process:
        print "Calculating requirement 2.5...\n"
        field_to_calc = requirements[2.5]
        if not field_to_calc in existing_output_fields:
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
        calc_requirement_2_5(field_to_calc)

    if 2.7 in requirements_to_process:
        print "Calculating requirement 2.7...\n"
        field_to_calc = requirements[2.7]
        if not field_to_calc in existing_output_fields:
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
        calc_requirement_2_7(field_to_calc)

    if 8.5 in requirements_to_process:
        print "Calculating requirement 8.5...\n"
        field_to_calc = requirements[8.5]
        if not field_to_calc in existing_output_fields:
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
        calc_requirement_8_5(field_to_calc)

    if 9.3 in requirements_to_process:
        print "Calculating requirement 9.3...\n"
        field_to_calc = requirements[9.3]
        if not field_to_calc in existing_output_fields:
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
        calc_requirement_9_3(field_to_calc)

    if 9.4 in requirements_to_process:
        print "Calculating requirement 9.4...\n"
        field_to_calc = requirements[9.4]
        if not field_to_calc in existing_output_fields:
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
        calc_requirement_9_4(field_to_calc)

    if 9.5 in requirements_to_process:
        print "Calculating requirement 9.5...\n"
        field_to_calc = requirements[9.5]
        if not field_to_calc in existing_output_fields:
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
        calc_requirement_9_5(field_to_calc)

    if 9.6 in requirements_to_process:
        print "Calculating requirement 9.6...\n"
        field_to_calc = requirements[9.6]
        if not field_to_calc in existing_output_fields:
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
        calc_requirement_9_6(field_to_calc)

    if 9.7 in requirements_to_process:
        print "Calculating requirement 9.7...\n"
        field_to_calc = requirements[9.7]
        if not field_to_calc in existing_output_fields:
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
        calc_requirement_9_7(field_to_calc)

    if 9.8 in requirements_to_process:
        print "Calculating requirement 9.8...\n"
        field_to_calc = requirements[9.8]
        if not field_to_calc in existing_output_fields:
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
        calc_requirement_9_8(field_to_calc)


def join_additional_requirements(additional_requirements_table, requirements_to_join):
    print "Joining additional fields..."
    all_additional_fields = arcpy.ListFields(additional_requirements_table)
    fields_to_join = []
    for field in all_additional_fields:
        try:
            requirement_id = float(field.name.split("_")[-2] + "." + field.name.split("_")[-1])
            if requirement_id in requirements_to_join:
                fields_to_join.append(field.name)
                # If the standardized field name exists in the output feature class delete it before renaming the new joined field.
                standardized_field_name = requirements[requirement_id]
                if standardized_field_name in existing_output_fields:
                    arcpy.DeleteField_management(output_parcels_fc, standardized_field_name)
        except:
            pass
    print "Fields to join..."
    print fields_to_join
    #arcpy.AddIndex_management(additional_requirements_table, "parcel_id", "parcel_id_index")
    #arcpy.AddIndex_management(output_parcels_fc, "parcel_id", "parcel_id_index")
    arcpy.JoinField_management(output_parcels_fc, "parcel_id", additional_requirements_table, "parcel_id", fields_to_join)


def rename_fields():
    """ This function will rename fields to match the standardized field names in the requirements dictionary
    It only works if the field to be renamed has the requirement code at the end of the field name (e.g., "8_3")
    It will operate on requirement codes that exist in the requirements dictionary.
    It will skip over any fields that have a name that's already in the requirements dictionary.
    """

    if arcpy.Exists(output_parcels_fc):
        existing_output_fields = [field.name for field in arcpy.ListFields(output_parcels_fc)]

    for input_field in existing_output_fields:

        print "Input field: " + input_field

        try:
            requirement_code = float(input_field.split("_")[-2] + "." + input_field.split("_")[-1])
            print "Requirement code in field name: " + str(requirement_code)

        except:
            requirement_code = False
            print "No requirement code"

        if requirement_code in requirements:

            standardized_field_name = requirements[requirement_code]

            if requirement_code in requirements and not (input_field == standardized_field_name):

                print(input_field + " will be renamed to " + standardized_field_name)

                # If the standardized field name already exists in the fc, just recalculate it using the input field name.
                if standardized_field_name in existing_output_fields:
                    print "1. Calculating field..."
                    arcpy.CalculateField_management(output_parcels_fc, standardized_field_name, "!" + input_field + "!", "PYTHON")
                    arcpy.DeleteField_management(output_parcels_fc, input_field)

                # Handles the case where an input field name is not all lower case, but otherwise matches the standardized field name.
                elif input_field.lower() == standardized_field_name:
                    arcpy.AddField_management(output_parcels_fc, standardized_field_name + "_lower", "SHORT")
                    arcpy.CalculateField_management(output_parcels_fc, standardized_field_name + "_lower", "!" + input_field + "!", "PYTHON")
                    arcpy.DeleteField_management(output_parcels_fc, input_field)
                    arcpy.AlterField_management(output_parcels_fc, standardized_field_name + "_lower", standardized_field_name)

                # If the length of the standardized field name is > 31, we have to add a new field (standardized_field_name), calculate it, and then delete the input_field.
                elif len(standardized_field_name) > 31:
                    print "2. Adding Field and Calculating Field..."
                    arcpy.AddField_management(output_parcels_fc, standardized_field_name, "SHORT")
                    arcpy.CalculateField_management(output_parcels_fc, standardized_field_name, "!" + input_field + "!", "PYTHON")
                    arcpy.DeleteField_management(output_parcels_fc, input_field)

                # Otherwise we just do what we came here to do: rename the field.
                else:
                    print "3. Altering Field..."
                    try:
                        arcpy.AlterField_management(output_parcels_fc, input_field, standardized_field_name)
                    except:
                        print "ERROR...could not alter field. There was likely more than one field with " + \
                              input_field.split("_")[-2] + "_" + input_field.split("_")[-1] + " on the end."


def create_parcel_masked_data_basin():
    expression = "protected_area_mask_9_8 = 1"
    arcpy.Select_analysis(output_parcels_fc, output_parcels_fc_mask, expression)

# TABLES FOR DEV TEAM


def create_parcel_fc_dev_team(mask):
    """ Create the parcels feature class for the dev team.
        If mask is true, it will copy the masked version with protected areas removed.
        If mask is false, it will copy the unmasked version without protected areas removed.
        It will have the same fields as the original input feature class.
    """

    # Only copy the original select input fields.
    mapS = arcpy.FieldMappings()
    # for each field, create an individual field map, and add it to the field mapping object
    for field in original_fields_to_keep:
        map = arcpy.FieldMap()
        map.addInputField(input_parcels_fc, field)
        mapS.addFieldMap(map)

    if mask:
        input_fc = output_parcels_fc_mask
        base_name = os.path.basename(input_parcels_fc) + "_mask"
    else:
        input_fc = output_parcels_fc
        base_name = os.path.basename(input_parcels_fc)

    out_folder = output_ws_dev_team

    print "Copying Parcels Feature Class..."

    # Create the empty parcels feature class with the subset of original fields to keep
    arcpy.FeatureClassToFeatureClass_conversion(
        in_features=input_fc,
        out_path=out_folder, out_name=base_name, where_clause="",
        field_mapping=mapS,
        config_keyword="")


def create_exemption_table_dev_team():
    print "Creating exemptions table..."

    # Create the exemptions table
    arcpy.CreateTable_management(output_ws_dev_team, "exemptions")
    arcpy.AddField_management("exemptions", "exemption_id", "SHORT")
    arcpy.AddField_management("exemptions", "exemption_code", "TEXT")
    arcpy.AddField_management("exemptions", "exemption_source", "TEXT")

    print "Populating the exemptions table..."

    ic = arcpy.da.InsertCursor("exemptions", ["exemption_id", "exemption_code", "exemption_source"])

    for k, v in exemptions.iteritems():
        ic.insertRow([k, v[0], v[1]])

    del ic


def create_parcel_exemptions_table_dev_team(mask, test_TAXAPN=False, test_exemption=False):
    """ Performs these functions:
        Creates the parcel_exemptions junction table.
        Populates the parcel_exemptions junction table.
        Populates the exemptions_count field in the requirements table.
    """

    arcpy.AddField_management(output_parcels_fc, "exemptions_count", "SHORT")

    if mask:
        parcel_exemptions_table = "parcel_exemptions_mask"
    else:
        parcel_exemptions_table = "parcel_exemptions"

    # Create the parcel - exemptions table (junction table)
    arcpy.CreateTable_management(output_ws_dev_team, parcel_exemptions_table)
    arcpy.AddField_management(parcel_exemptions_table, "parcel_id", "TEXT")
    arcpy.AddField_management(parcel_exemptions_table, "exemption_id", "LONG")

    # This fixed the following error: RuntimeError: workspace already in transaction mode
    # Be sure to stop editing at the end
    edit = arcpy.da.Editor(arcpy.env.workspace)
    edit.startEditing(False, False)

    print "Calculating parcel exemptions based on requirements (output stored in the junction table (parcels_exemptions))."
    
    requirements_uc = arcpy.da.UpdateCursor(output_parcels_fc, "*")
    exemptions_ic = arcpy.da.InsertCursor(parcel_exemptions_table, ['parcel_id', 'exemption_id'])

    # Iterate over each parcel in the requirements table.
    for row in requirements_uc:
        parcel_id = row[requirements_uc.fields.index('PARCEL_ID')]
        parcel_apn = row[requirements_uc.fields.index('TAXAPN')]
        count_exemptions = 0
        
        # For each exemption, iterate over the list of requirements
        for k, v in exemptions.iteritems():
            # build a list to see if this parcel meets all the requirements for this exemption, e.g., [1,1,1,1,1,0]
            check_requirements = []
            for requirement_id in v[2]:
                # If it's a list of OR requirements....make sure at least one of them is a 1.  
                if type(requirement_id) == list:
                    sum_or_requirements = 0
                    for r_id in requirement_id:
                        r = requirements[r_id]
                        yes_or_no = row[requirements_uc.fields.index(r)]
                        sum_or_requirements += yes_or_no
                    check_requirements.append(sum_or_requirements)
                else:
                    requirement = requirements[requirement_id]
                    try:
                        yes_or_no = row[requirements_uc.fields.index(requirement)]
                    except:
                        print "Requirement Missing from attribute table: " + requirement
                        print "ABORTING...."
                        exit()
                    check_requirements.append(yes_or_no)
                    
            # If this parcel meets all the requirements for this exemption (e.g, check_requirements == [1,1,1,1]), add a record to the junction table.
            # ...and add one to the exemption count.
            if test_TAXAPN and test_exemption:
                if parcel_apn == test_TAXAPN and exemptions[k][0] == test_exemption:
                    print "\n"
                    print "Parcel TAXAPN: " + parcel_apn
                    print "Parcel ID: " + parcel_id
                    print "Exemption Code: " + test_exemption
                    print "Exemption ID: " + str(k)
                    print "Requirements: " + str(exemptions[k][2])
                    print "Check Requirements: " + str(check_requirements)
                    print ("NOTE: A value of 1 means it meets the requirement at the same index as above. For OR conditions, the value represents the number of requirements it meets")
                    print "\n"
            if all(check_requirements):
                count_exemptions += 1
                exemptions_ic.insertRow([parcel_id, k])

        # Add the count of the number of exemptions to the parcels feature class. 
        row[requirements_uc.fields.index("exemptions_count")] = count_exemptions
        requirements_uc.updateRow(row)

    edit.stopEditing(True)


def create_requirements_table_dev_team(mask):
    """ Creates the requirements table & adds the exemptions_count field"""

    if arcpy.Exists(output_parcels_fc):
        existing_output_fields = [field.name for field in arcpy.ListFields(output_parcels_fc)]

    if mask:
        input_parcels_fc = output_parcels_fc_mask
        output_requirements_table_name = "requirements_mask"
    else:
        input_parcels_fc = output_parcels_fc
        output_requirements_table_name = "requirements"

    print "Fields to Keep..."

    # Keep PARCEL_ID field plus any requirement fields
    fields_to_keep = ["PARCEL_ID"]
    for field in existing_output_fields:
        if field in requirements.values():
            fields_to_keep.append(field)

    # Want this here in order to keep the exemptions count field at the end
    fields_to_keep.append("exemptions_count")

    # create an empty field mapping object
    mapS = arcpy.FieldMappings()
    # for each field, create an individual field map, and add it to the field mapping object
    for field in fields_to_keep:
        print field
        map = arcpy.FieldMap()
        map.addInputField(input_parcels_fc, field)
        mapS.addFieldMap(map)

    print "\nCreating Requirements table..."

    # Create the empty parcels feature class with the subset of original fields to keep
    arcpy.TableToTable_conversion(
        in_rows=input_parcels_fc,
        out_path=output_ws_dev_team, out_name=output_requirements_table_name, where_clause="",
        field_mapping=mapS,
        config_keyword="")

# INDIVIDUAL REQUIREMENTS ##############################################################################################


def calc_requirement_0_1(field_to_calc):
    """
        0.1
        Requirements that begin with 0 aren't applicable to any exemptions
        Requirement Long Name: Urbanized Area Prc 21071 Unincorporated
        Description: Select parcels that have their centers in the unincorporated islands of requirement 2.1. Yes = 1, No = 0
    """
    output_parcels_layer = arcpy.MakeFeatureLayer_management(output_parcels_fc)
    # Select Light Green areas, unincorporated areas meeting prc_21071
    expression = "community_type = 'Unincorporated Island' AND urbanized_area_prc_21071 = 1"
    urbanized_area_prc_21071_layer = arcpy.MakeFeatureLayer_management(urbanized_area_prc_21071_fc)
    urbanized_area_prc_21071_unincorporated_layer = arcpy.SelectLayerByAttribute_management(urbanized_area_prc_21071_layer, "NEW_SELECTION", expression)
    # Select parcels within the green areas
    arcpy.SelectLayerByLocation_management(output_parcels_layer, "HAVE_THEIR_CENTER_IN", urbanized_area_prc_21071_unincorporated_layer)
    arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 1, "PYTHON")
    arcpy.SelectLayerByAttribute_management(output_parcels_layer, "SWITCH_SELECTION")
    arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 0, "PYTHON")


def calc_requirement_2_1(field_to_calc, start_oid, end_oid):
    """
        2.1
        Requirement Long Name: Urbanized Area PRC 21071
        Description: Complicated, see description here:
        https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PRC&sectionNum=21071.
        The basic idea is that we iterate over each parcel, pass the OID to a subfunction which determines whether or
        not it meets the requirements in the the link above.
    """

    def calc_requirement_2_1_iterate(parcel_OID):

        print "Parcel OBJECTID: " + str(parcel_OID)

        city_boundaries_layer = arcpy.MakeFeatureLayer_management(city_boundaries_fc)
        # NOTE: uses points....
        output_parcels_layer = arcpy.MakeFeatureLayer_management(parcel_points_fc)

        # Select the current parcel.
        query = '"OBJECTID" = %s' % str(parcel_OID)
        arcpy.SelectLayerByAttribute_management(output_parcels_layer, "NEW_SELECTION", query)

        # Select the city boundary that the parcel falls within and get the OBJECTID
        arcpy.SelectLayerByLocation_management(city_boundaries_layer, "CONTAINS", output_parcels_layer)
        arcpy.MakeFeatureLayer_management(city_boundaries_layer, "city_boundary_containing_parcel")

        is_city = 0

        # Determine if the parcel is in a city, and get the population of the selected city boundary
        sc = arcpy.SearchCursor("city_boundary_containing_parcel")
        for row in sc:
            is_city = 1
            city_boundary_containing_parcel_population = row.getValue("B01003_001E_Pop_Estimate_Total")

        # INCORPORATED CITY ############################################################################################
        if is_city:

            print "City Population: " + str(city_boundary_containing_parcel_population)

            # If the city boundary has a population > 100,000, we're done(21017 a(1)).
            if city_boundary_containing_parcel_population > 100000:
                print "Requirement met."
                requirement_2_1 = 1

            # If the city boundary has a population < 100,000, but the total population with two contiguous cities > 100,000
            else:
                # Select contiguous city boundaries.
                arcpy.SelectLayerByLocation_management(city_boundaries_layer, "SHARE_A_LINE_SEGMENT_WITH", "city_boundary_containing_parcel")
                arcpy.SelectLayerByLocation_management(city_boundaries_layer, "ARE_IDENTICAL_TO", "city_boundary_containing_parcel", "", "REMOVE_FROM_SELECTION")

                # Get the sum of the top two contiguous city populations.
                city_boundary_sc = arcpy.SearchCursor(city_boundaries_layer)
                population_list = []
                number_of_surrounding_cities = 0
                for row in city_boundary_sc:
                    population_list.append(row.getValue("B01003_001E_Pop_Estimate_Total"))
                    number_of_surrounding_cities += 1

                # If the city plus two contiguous incorporated cities total more than 100,000...
                sorted_pop_list = sorted(population_list)
                print "Number of surrounding cities: " + str(number_of_surrounding_cities) + "(Populations: " + ", ".join(map(str, sorted_pop_list)) + ")"

                del city_boundary_sc

                if number_of_surrounding_cities >= 1:
                    if number_of_surrounding_cities >= 2:
                        sum_largest_two_surrounding_pops = sorted_pop_list[-1] + sorted_pop_list[-2]
                    else:
                        sum_largest_two_surrounding_pops = sorted_pop_list[-1]

                    sum_surrounding_populations = city_boundary_containing_parcel_population + sum_largest_two_surrounding_pops

                    print "City Population including top two surrounding cities: " + str(sum_surrounding_populations)
                    # ...and the selected city + the two largest surrounding cities  have a population > 100,000k, we're done
                    if sum_surrounding_populations >= 100000:
                        print "Requirement met."
                        requirement_2_1 = 1

                    # UNINCORPORATED CITY ##################################################################################
                    else:
                        arcpy.MakeFeatureLayer_management(unincorporated_islands, "unincorporated_area_surrounded_layer")
                        # Select the surrounded unincorporated that the parcel falls within and get the OBJECTID
                        arcpy.SelectLayerByLocation_management(city_boundaries_layer, "CONTAINS", output_parcels_layer)
                        arcpy.MakeFeatureLayer_management(city_boundaries_layer, "city_boundary_containing_parcel")

                        requirement_2_1 = 0
                else:
                    print "Requirement not met."
                    requirement_2_1 = 0

        else:
            print "Unincorporated"
            # Check to see if the unincorporated parcel is in an area surrounded by city boundaries.
            arcpy.MakeFeatureLayer_management(unincorporated_islands, "unincorporated_islands_layer")
            arcpy.SelectLayerByLocation_management("unincorporated_islands_layer", "CONTAINS", output_parcels_layer)
            is_surrounded = int(arcpy.GetCount_management("unincorporated_islands_layer").getOutput(0))

            # If the area is surrounded by cities, get the population of the surrounding cities.
            if is_surrounded:
                print "Completely surrounded by one or more incorporated cities"
                # Get population of unincorporated area
                sc = arcpy.SearchCursor("unincorporated_islands_layer")
                for row in sc:
                    unincorporated_population = int(row.getValue("SUM_POP10"))
                    unincorporated_area = int(row.getValue("SHAPE_Area")) * 0.001

                unincorporated_density = unincorporated_population / unincorporated_area

                # Select the surrounding cities.
                arcpy.SelectLayerByLocation_management(city_boundaries_layer, "SHARE_A_LINE_SEGMENT_WITH", "unincorporated_islands_layer")
                sc = arcpy.SearchCursor(city_boundaries_layer)
                sum_surrounding_area = 0
                sum_surrounding_population = 0

                # Get the population and area of the surrounding cities.
                for row in sc:

                    sum_surrounding_population += int(row.getValue("B01003_001E_Pop_Estimate_Total"))
                    sum_surrounding_area += float(row.getValue("SHAPE_Area")) * 0.001

                # Calculate the density of the surrounding cities
                surrounding_density = sum_surrounding_population / sum_surrounding_area
                surrounding_population = unincorporated_population + sum_surrounding_population

                # Sum of unincorporated area and surrounding population
                combined_population = unincorporated_population + surrounding_population

                print "Combined Population: " + str(combined_population)
                print "Unincorporated Population Density: " + str(unincorporated_density)
                print "Surrounding Population Density: " + str(surrounding_density)

                if combined_population >= 100000 and unincorporated_density >= surrounding_density:
                    print "Requirement met."
                    requirement_2_1 = 1
                else:
                    print "Requirement not met."
                    requirement_2_1 = 0

            else:
                print "Not surrounded"
                print "Requirement not met"
                requirement_2_1 = 0

        print "\n"

        del sc

        return requirement_2_1

    print "Calculating requirements using an update cursor...\n"

    fieldnames = []
    fields = arcpy.ListFields(output_parcels_fc)
    for field in fields:
        fieldnames.append(field.name)

    if start_oid and end_oid:
        filter_records = "OBJECTID > %s and OBJECTID <= %s" % (start_oid, end_oid)
    else:
        filter_records = "#"
    uc = arcpy.da.UpdateCursor(output_parcels_fc, "*", filter_records)

    count = 0
    for row in uc:
        parcel_OID = row[0]

        if count == 0:
            print "Calculating requirement 2.1...\n"

        start_time_calc = datetime.datetime.now()

        # Call functions to calculate individual requirements
        requirement_2_1 = calc_requirement_2_1_iterate(parcel_OID)

        end_time_calc = datetime.datetime.now()
        calc_duration = end_time_calc - start_time_calc
        print("Duration: " + str(calc_duration))
        row[fieldnames.index(field_to_calc)] = requirement_2_1

        count += 1

        uc.updateRow(row)


def calc_requirement_2_2(field_to_calc):
    """
        2.2
        Requirement Long Name: Urban Area PRC 21094.5
        Description: Select parcels WITHIN a city. Yes = 1, No = 0
        If not in a city, check to see if WITHIN an unincorporated island
        If within an unincorporated island, check to see if the unincorporated island it's in meets both of the following requirements:
            (A) The population of the unincorporated area and the population of the surrounding incorporated cities equal a population of 100,000 or more.
            (B) The population density of the unincorporated area is equal to, or greater than, the population density of the surrounding cities.
    """

    # Make a city boundaries layer
    city_boundaries_layer = arcpy.MakeFeatureLayer_management(city_boundaries_fc)

    # Make a parcels layer
    output_parcels_layer = arcpy.MakeFeatureLayer_management(output_parcels_fc)

    # Find parcels within a city? Yes = 1
    arcpy.SelectLayerByLocation_management(output_parcels_layer, "HAVE_THEIR_CENTER_IN", city_boundaries_fc)
    arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 1, "PYTHON")

    # Find parcels not within a city = 0
    arcpy.SelectLayerByAttribute_management(output_parcels_layer, "SWITCH_SELECTION")
    arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 0, "PYTHON")

    # Parcels not within a city is selected.  Of those, select parcels within an unincorporated island).
    unincorporated_islands_layer = arcpy.MakeFeatureLayer_management(unincorporated_islands)
    # Use WITHIN here rather than HAVE CENTER IN so that the SBL below which uses CONTAINS (no "has center in equivalent") works.
    surrounded_parcels = arcpy.SelectLayerByLocation_management(output_parcels_layer, "WITHIN", unincorporated_islands_layer, "", "SUBSET_SELECTION")

    print "Number of unincorporated parcels surrounded: " + str(arcpy.GetCount_management(output_parcels_layer)[0])

    fieldnames = []
    fields = arcpy.ListFields(surrounded_parcels)
    for field in fields:
        fieldnames.append(field.name)

    # output_parcels_layer now consists of polygons that are completely surrounded. Iterate over each one.
    uc = arcpy.da.UpdateCursor(surrounded_parcels, "*")
    for uc_row in uc:

        parcel_OID = uc_row[fieldnames.index("OBJECTID")]
        print "Parcel OID: " + str(parcel_OID)

        this_surrounded_parcel = arcpy.SelectLayerByAttribute_management(output_parcels_layer, "NEW_SELECTION", "OBJECTID = " + str(parcel_OID))

        # Select the unincorporated island polygon containing this parcel
        this_unincorporated_island = arcpy.SelectLayerByLocation_management(unincorporated_islands_layer, "CONTAINS", this_surrounded_parcel)

        # Get population of unincorporated area
        sc = arcpy.SearchCursor(this_unincorporated_island)
        for row in sc:
            print row.getValue("OBJECTID")
            unincorporated_population = int(row.getValue("SUM_POP10"))
            unincorporated_area = int(row.getValue("SHAPE_Area")) * 0.001

        unincorporated_density = unincorporated_population / unincorporated_area

        # Select the surrounding cities.
        surrounding_cities = arcpy.SelectLayerByLocation_management(city_boundaries_layer, "SHARE_A_LINE_SEGMENT_WITH", this_unincorporated_island)
        sc = arcpy.SearchCursor(surrounding_cities)
        sum_surrounding_area = 0
        sum_surrounding_population = 0

        # Get the population and area of the surrounding cities.
        for row in sc:
            sum_surrounding_population += int(row.getValue("B01003_001E_Pop_Estimate_Total"))
            sum_surrounding_area += float(row.getValue("SHAPE_Area")) * 0.001

        # Calculate the density of the surrounding cities
        surrounding_density = sum_surrounding_population / sum_surrounding_area
        surrounding_population = unincorporated_population + sum_surrounding_population

        # Sum of unincorporated area and surrounding population
        combined_population = unincorporated_population + surrounding_population

        print "Combined Population: " + str(combined_population)
        print "Unincorporated Population Density: " + str(unincorporated_density)
        print "Surrounding Population Density: " + str(surrounding_density)

        # Check to see if both of these conditions are met:
        # (A) The population of the unincorporated area and the population of the surrounding incorporated cities equal a population of 100, 000 or more.
        # (B) The population density of the unincorporated area is equal to, or greater than, the population density of the surrounding cities.

        if combined_population >= 100000 and unincorporated_density >= surrounding_density:
            uc_row[fieldnames.index(field_to_calc)] = 1

        uc.updateRow(uc_row)


def calc_requirement_2_3(field_to_calc):
    """
        2.3
        Requirement Long Name: Within City Limit
        Description: Select parcels that have their centers in a city boundary. Yes = 1, No = 0
    """
    output_parcels_layer = arcpy.MakeFeatureLayer_management(output_parcels_fc)
    arcpy.SelectLayerByLocation_management(output_parcels_layer, "HAVE_THEIR_CENTER_IN", city_boundaries_fc)
    arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 1, "PYTHON")
    arcpy.SelectLayerByAttribute_management(output_parcels_layer, "SWITCH_SELECTION")
    arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 0, "PYTHON")


def calc_requirement_2_4(field_to_calc):
    """
        2.4
        Requirement Long Name: Unincorporated
        Select parcels where the CITY = Unincorporated
        Select parcels that HAVE THEIR CENTERS IN this layer
    """

    # Unincorporated areas
    incorporated_and_unincorporated_layer = arcpy.MakeFeatureLayer_management(incorporated_and_unincorporated_fc)
    unincorporated_layer = arcpy.SelectLayerByAttribute_management(incorporated_and_unincorporated_layer, "NEW_SELECTION", "CITY = 'Unincorporated'")

    # Select parcels that HAVE THEIR CENTERS IN the unincorporated area
    output_parcels_layer = arcpy.MakeFeatureLayer_management(output_parcels_fc)
    arcpy.SelectLayerByLocation_management(output_parcels_layer, "HAVE_THEIR_CENTER_IN", unincorporated_layer)

    # Calculate 1's and 0's
    arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 1, "PYTHON")
    arcpy.SelectLayerByAttribute_management(output_parcels_layer, "SWITCH_SELECTION")
    arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 0, "PYTHON")


def calc_requirement_2_5(field_to_calc):
    """
        2.5
        Requirement Long Name: Within a Metropolitan Planning Organization boundary
        Description: Select parcels that HAVE THEIR CENTERS IN an MPO boundary. Yes = 1, No = 0
    """
    arcpy.MakeFeatureLayer_management(output_parcels_fc, "output_parcels_layer")
    arcpy.SelectLayerByLocation_management("output_parcels_layer", "HAVE_THEIR_CENTER_IN", mpo_boundary_dissolve_fc)
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 1, "PYTHON")
    arcpy.SelectLayerByAttribute_management("output_parcels_layer", "SWITCH_SELECTION")
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 0, "PYTHON")


def calc_requirement_2_7(field_to_calc):
    """
        2.7
        Requirement Long Name: Urbanized area or urban cluster
        Select parcels that HAVE THEIR CENTERS IN this layer.
    """

    # Select parcels that HAVE THEIR CENTERS IN the unincorporated urbanized area or urban cluster
    output_parcels_layer = arcpy.MakeFeatureLayer_management(output_parcels_fc)
    arcpy.SelectLayerByLocation_management(output_parcels_layer, "HAVE_THEIR_CENTER_IN", urbanized_area_urban_cluster_fc)

    # Calculate 1's and 0's
    arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 1, "PYTHON")
    arcpy.SelectLayerByAttribute_management(output_parcels_layer, "SWITCH_SELECTION")
    arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 0, "PYTHON")


def calc_requirement_8_5(field_to_calc):

    """
        8.5
        Requirement Long Name:  Rare, Threatened, or Endangered Species
        Description: Select parcels that intersect the Rare, Threatened, or Endangered Species Dataset. Yes = 0, No = 1
    """
    arcpy.MakeFeatureLayer_management(output_parcels_fc, "output_parcels_layer")
    arcpy.SelectLayerByLocation_management("output_parcels_layer", "INTERSECT", rare_threatened_or_endangered_fc)
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 0, "PYTHON")
    arcpy.SelectLayerByAttribute_management("output_parcels_layer", "SWITCH_SELECTION")
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 1, "PYTHON")


def calc_requirement_9_3(field_to_calc):
    """
        9.3
        Requirement Long Name: Wildfire Hazard
        Description: Select parcels that intersect the Wildfire Hazard Zones 3-5(High - Extreme)(Yes = 0, No = 1)
    """
    print "Calculating Zonal Statistics..."
    # Calculate zonal stats to get a count of the number of wildfire hazard pixels within each parcel.
    tmp_zonal_stats_table = scratch_ws + os.sep + "wildfire_hazard_zonal_stats_subset"
    arcpy.sa.ZonalStatisticsAsTable(output_parcels_fc, "PARCEL_ID", wildfire_hazard_raster, tmp_zonal_stats_table, "", "SUM")

    print "Joining Zonal Stats table to the parcels dataset..."
    # Join the zonal stats table (just the "COUNT" field) to the parcels feature class.
    arcpy.JoinField_management(output_parcels_fc, "PARCEL_ID", tmp_zonal_stats_table, "PARCEL_ID", "COUNT")

    # Loop over each row and determine whether or not > 20% of the parcel has a wildfire hazard pixel.
    uc = arcpy.da.UpdateCursor(output_parcels_fc, ["SHAPE_Area", "COUNT", field_to_calc, "OBJECTID"])
    for row in uc:

        # If no join record or no pixel, no wildfire hazard
        if not row[1] or row[1] == 0:
            row[2] = 1

        else:
            row[2] = 0

        uc.updateRow(row)

    arcpy.DeleteField_management(output_parcels_fc, "COUNT")


def calc_requirement_9_4(field_to_calc):
    """
        9.4
        Requirement Long Name: Flood Plain
        Description: Select parcels that intersect the 100 Year Floodplain. Yes = 0, No = 1
        Field Values defining the floodplain come from here: https://waterresources.saccounty.net/stormready/PublishingImages/100-year-floodplain-map-small.jpg
    """
    arcpy.MakeFeatureLayer_management(output_parcels_fc, "output_parcels_layer")
    arcpy.SelectLayerByLocation_management("output_parcels_layer", "INTERSECT", flood_plain_fc)
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 0, "PYTHON")
    arcpy.SelectLayerByAttribute_management("output_parcels_layer", "SWITCH_SELECTION")
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 1, "PYTHON")


def calc_requirement_9_5(field_to_calc):
    """
        9.5
        Requirement Long Name: Landslide Hazard
        Description: Select parcels that intersect the Landslide Hazard dataset. Yes = 0, No = 1
    """
    # Get the resolution of the landslide hazard raster
    landslide_hazard_raster_resolution = float(arcpy.GetRasterProperties_management(landslide_hazard_raster, "CELLSIZEX")[0])

    print "Calculating Zonal Statistics..."
    # Calculate zonal stats to get a count of the number of landslide hazard pixels within each parcel.
    tmp_zonal_stats_table = scratch_ws + os.sep + "landslide_hazard_zonal_stats_subset"
    arcpy.sa.ZonalStatisticsAsTable(output_parcels_fc, "PARCEL_ID", landslide_hazard_raster, tmp_zonal_stats_table, "", "SUM")

    print "Joining Zonal Stats table to the parcels dataset..."
    # Join the zonal stats table (just the "COUNT" field) to the parcels feature class.
    arcpy.JoinField_management(output_parcels_fc, "PARCEL_ID", tmp_zonal_stats_table, "PARCEL_ID", "COUNT")

    # Loop over each row and determine whether or not > 20% of the parcel has a landslide hazard pixel.
    uc = arcpy.da.UpdateCursor(output_parcels_fc, ["SHAPE_Area", "COUNT", field_to_calc, "OBJECTID"])
    for row in uc:

        # If no join record, no pixel, no landslide hazard
        if not row[1]:
            row[2] = 1

        # Otherwise see if the parcel is > the 20% threshold.
        else:
            #Calculate the area of the landslide hazard pixels.
            landslide_hazard_sq_meters = row[1] * pow(landslide_hazard_raster_resolution, 2)
            parcel_area = row[0]

            #Calculate the percent of the landslide hazard pixels with the parcel
            percent_high_landslide = (float(landslide_hazard_sq_meters) / parcel_area) * 100

            # If it's > the threshold, it's not elligible.
            if percent_high_landslide >= landslide_area_percent_threshold:
                row[2] = 0

            else:
                row[2] = 1

        uc.updateRow(row)

    arcpy.DeleteField_management(output_parcels_fc, "COUNT")


def calc_requirement_9_6(field_to_calc):
    """
        9.6
        Requirement Long Name: State Conservancy
        Description: Select parcels that intersect the State Conservancy Dataset. Yes = 0, No = 1
    """
    arcpy.MakeFeatureLayer_management(output_parcels_fc, "output_parcels_layer")
    arcpy.SelectLayerByLocation_management("output_parcels_layer", "INTERSECT", state_conservancy_fc)
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 0, "PYTHON")
    arcpy.SelectLayerByAttribute_management("output_parcels_layer", "SWITCH_SELECTION")
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 1, "PYTHON")


def calc_requirement_9_7(field_to_calc):
    """
        9.7
        Requirement Long Name: Local Coastal Zone
        Description: Select parcels that intersect the Local Coastal Zone Dataset. Yes = 0, No = 1
    """
    arcpy.MakeFeatureLayer_management(output_parcels_fc, "output_parcels_layer")
    arcpy.SelectLayerByLocation_management("output_parcels_layer", "INTERSECT", local_coastal_zone_fc)
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 0, "PYTHON")
    arcpy.SelectLayerByAttribute_management("output_parcels_layer", "SWITCH_SELECTION")
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 1, "PYTHON")


def calc_requirement_9_8(field_to_calc):
    """
        9.8
        Requirement Long Name: Protected Area Mask
        Description: Select parcels that intersect the Protected Area Mask Dataset. Yes = 0, No = 1
    """
    arcpy.MakeFeatureLayer_management(output_parcels_fc, "output_parcels_layer")
    arcpy.SelectLayerByLocation_management("output_parcels_layer", "INTERSECT", protected_area_mask_fc)
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 0, "PYTHON")
    arcpy.SelectLayerByAttribute_management("output_parcels_layer", "SWITCH_SELECTION")
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 1, "PYTHON")


# EXTRA FUNCTIONS ######################################################################################################


def create_parcels_fc_for_data_basin():
    #### !!!!!!!!!!!!!!!!! MAYBE NOT NEEDED. Only use if Original requirements_mask fc is too large to upload.
    """ This function prepares a dataset for Data Basin upload by deleting all the select fields and removing
    any parcels that are within the protected area mask (requirement 9.8)
    """
    print "Creating masked parcel layer for Data Basin"
    expression = '"protected_area_mask_9_8" = 1'
    arcpy.Select_analysis(output_parcels_fc, output_parcels_fc_mask, expression)

    all_fields = [field.name for field in arcpy.ListFields(output_parcels_fc)]
    fields_to_keep = ["OBJECTID", "PARCEL_APN", "PARCEL_ID", "SHAPE", "SHAPE_Area", "SHAPE_Length"]
    fields_to_keep.extend(requirements.values())
    fields_to_delete = list(set(all_fields) - set(fields_to_keep))

    print "Deleting fields"
    arcpy.DeleteField_management(output_parcels_fc, fields_to_delete)


def list_fields():
    field_dict = {}

    for input_field in existing_output_fields:

        if input_field in requirements.values():
            requirement_code = float(input_field.split("_")[-2] + "." + input_field.split("_")[-1])
            field_dict[requirement_code] = input_field

    sorted_list = sorted(field_dict.iteritems(), key=lambda (x, y): float(x))

    for field in sorted_list:
        print str(field[0]) + ": " + field[1]


def copy_parcels_fc_with_select_orig_and_requirement_fields():

        input_parcels_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs_for_DataBasin.gdb\sacramento_parcels_requirements"

        output_base_name = "sacramento_parcels_requirements_del_fields"

        fields_to_keep = original_fields_to_keep

        for field in existing_output_fields:
            if field in requirements.values():
                fields_to_keep.append(field)

        # create an empty field mapping object
        mapS = arcpy.FieldMappings()
        # for each field, create an individual field map, and add it to the field mapping object
        for field in fields_to_keep:
            print field
            map = arcpy.FieldMap()
            map.addInputField(input_parcels_fc, field)
            mapS.addFieldMap(map)

        print "Copying Parcels Feature Class (for Dev team) with the following fields..."

        out_folder = os.path.dirname(output_parcels_fc)

        # Create the empty parcels feature class with the subset of original fields to keep
        arcpy.FeatureClassToFeatureClass_conversion(
            in_features=input_parcels_fc,
            out_path=out_folder, out_name=output_base_name, where_clause="",
            field_mapping=mapS,
            config_keyword="")


# Function Calls #######################################################################################################

#copy_parcels_fc()

# Requirements: If called multiple times from batch script to increase performance, get oids from batch file.
#start_oid = sys.argv[1]
#end_oid = sys.argv[2]
#calculate_parcel_requirements(requirements_to_process=[2.1], start_oid=start_oid, end_oid=end_oid)
#calculate_parcel_requirements(requirements_to_process=[0.1])

# Join Additional Requirement Fields (From Kai and other staff)
#fields_to_join = ["MajTS_3_1", "HighQualTC_3_4", "HighQualTC_3_2", "StpTC_1_2m_3_5", "Wetlands_8_1", "RipWet_8_2", "Spec_Habitat_8_3", "WildHaz_9_3", "EQFault_9_2", "B15per_RegAv_3_6", "Below_RegAv_3_8"]
#fields_to_join = ["RipVeg_8_2", "B15per_RegAv_3_6", "Below_RegAv_3_8"]
#fields_to_join = ["HighQualTC_3_2", "HighQualTC_3_4", "StpTC_1_2m_3_5", "TS_FT_1_2m_3_14"]
additional_requirements_table = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\From_Kai\Transit_and_Infill.gdb\Sacramento_Parcels_MG_v7_3_14"
requirements_to_join = [8.2, 3.6, 3.8, 3.2, 3.4, 3.5, 3.14]
join_additional_requirements(additional_requirements_table, requirements_to_join)
#rename_fields()

#create_parcel_fc_dev_team(mask=False)

#create_exemption_table_dev_team()

#create_parcel_exemptions_table_dev_team(mask=False, test_TAXAPN='277-0160-021-0000', test_exemption='21094.5')

#create_parcel_exemptions_table_dev_team(mask=False, test_TAXAPN=False, test_exemption=False)

#create_requirements_table_dev_team(mask=False)


# Extra functions (NOT NEEDED)

#create_parcel_masked_data_basin()
#copy_parcels_fc_with_select_orig_and_requirement_fields()
#list_fields()

end_time = datetime.datetime.now()
duration = end_time - start_time

print("Start Time: " + str(start_time))
print("End Time: " + str(end_time))
print("Duration: " + str(duration))

