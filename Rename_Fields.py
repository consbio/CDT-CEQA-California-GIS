import arcpy

input_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs.gdb\sacramento_parcels"

standardized_field_names = {
    # Location Requirements
    2.1: "urbanized_area_prc_21071_2_1",
    2.2: "urban_area_prc_21094_2_2",
    2.3: "within_city_limits_2_3",
    2.4: "unincorporated_urbanized_area_2_4",
    2.5: "within_mpo_2_5",
    # Transit Proximity Requirements
    3.1: "within_half_mile_major_transit_stop_3_1",
    3.2: "within_quarter_mile_transit_corridor_3_2",
    3.3: "hundred_percent_affordable_3_3",
    3.4: "transit_priority_area_3_4",
    3.5: "within_half_mile_transit_corridor_3_5",
    # Infill Requirements
    4.1: "infill_4_1",
    4.2: "previously_developed_or_75_next_to_urban_4_2",
    4.3: "qualified_urban_uses_4_3",
    # Environmental Limitations
    8.1: "wetlands_8_1",
    8.2: "riparian_areas_8_2",
    8.3: "special_habitats_8_3",
    8.4: "species_of_concern_8_4",
    # Hazards
    9.1: "sea_level_rise_9_1",
    9.2: "earthquake_hazard_zone_9_2",
    9.3: "wildfire_hazard_9_3",
    9.4: "flood_plain_9_4",
    9.5: "landslide_hazard_9_5",
    9.6: "state_conservancy_9_6",
    9.7: "local_coastal_zone_9_7",
    9.8: "protected_area_mask_9_8",
    # Public Health
    10.1: "rselhaz_10_1",
    10.2: "pesticide_10_2",
    10.3: "drinking_water_10_3",
    10.4: "cleanups_10_4",
    10.5: "groundwater_10_5",
    10.6: "hazardous_waste_10_6",
    10.7: "asthma_10_7",
    # Historical
    11.1: "historical_resources_11_1",
    # General Plan
    12.1: "open_space_12_1",
    12.2: "agriculture_12_2"
}


input_fields = [field.name for field in arcpy.ListFields(input_fc)]

for input_field in input_fields:

    print "Input field: " + input_field

    try:
        requirement_code = float(input_field.split("_")[-2] + "." + input_field.split("_")[-1])
        print "Requirement code in field name: " + str(requirement_code)

    except:
        requirement_code = False
        print "No requirement code"

    if requirement_code in standardized_field_names:

        standardized_field_name = standardized_field_names[requirement_code]

        if requirement_code in standardized_field_names and not (input_field == standardized_field_name):

            print(input_field + " will be renamed to " + standardized_field_name)

            # If the standardized field name already exists in the fc, just recalculate it using the input field name.
            if standardized_field_name in input_fields:
                print "1. Calculating field..."
                arcpy.CalculateField_management(input_fc, standardized_field_name, "!" + input_field + "!", "PYTHON")
                arcpy.DeleteField_management(input_fc, input_field)

            # If the length of the standardized field name is > 31, we have to add a new field (standardized_field_name), calculate it, and then delete the input_field.
            elif len(standardized_field_name) > 31:
                print "2. Adding Field and Calculating Field..."
                arcpy.AddField_management(input_fc, standardized_field_name, "SHORT")
                arcpy.CalculateField_management(input_fc, standardized_field_name, "!" + input_field + "!", "PYTHON")
                arcpy.DeleteField_management(input_fc, input_field)

            # Otherwise we just do what we came here to do: rename the field.
            else:
                print "3. Altering Field..."
                try:
                    arcpy.AlterField_management(input_fc, input_field, standardized_field_name)
                except:
                    print "ERROR...could not alter field. There was likely more than one field with " + input_field.split("_")[-2] + "_" + input_field.split("_")[-1] + " on the end."








