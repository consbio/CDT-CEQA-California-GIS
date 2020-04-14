import os
import arcpy
import datetime
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")

# Parcel Feature Classes to process. Use "*" to process all parcels.
input_parcels_fc_list = ["FRESNO_Parcels"]
input_parcels_fc_list = "*"
input_parcels_fc_list = ["ALPINE_Parcels", "SIERRA_Parcels"]

# Requirements to process. Use "*" to process all parcels.
requirements_to_process = ["0.1", "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7", "3.10", "3.12", "3.13", "8.1", "8.2", "8.3", "8.4", "8.5", "9.2", "9.3", "9.4", "9.5", "9.6", "9.7", "9.8"]
requirements_to_process = "*"

# Workspaces
input_parcels_gdb = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels_Projected_Delete_Identical.gdb"
output_gdb_data_basin = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs_for_DataBasin.gdb"
output_gdb_dev_team = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs_for_DevTeam.gdb'
intermediate_ws = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb"
scratch_ws = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Scratch\Scratch.gdb"

# Toolbox containing models for processing additional requirements (from Kai).
statewide_toolbox = r"\\loxodonta\GIS\Projects\CDT-CEQA_California_2019\Workspaces\CDT-CEQA_California_2019_kai_foster\Tasks\General_Tasks\Statewide.tbx"
statewide_toolbox_name = os.path.basename(statewide_toolbox).split(".")[0]
arcpy.ImportToolbox(statewide_toolbox)

# Kai's table
#additional_requirements_table = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\From_Kai\Transit_and_Infill.gdb\Sacramento_Parcels_MG_v7_3_14"
join_requirements_table = r"\\loxodonta\GIS\Projects\CDT-CEQA_California_2019\Workspaces\CDT-CEQA_California_2019_kai_foster\Tasks\General_Tasks\Data\Inputs\Inputs.gdb\Sacramento_Pilot\Sacramento_Parcels_MG"

# Fields from the original parcels feature class to keep in the output parcels for Data Basin & Dev.
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
# 0.1, 2.1
urbanized_area_prc_21071_fc = r"Database Connections\CBI Outputs.sde\cbioutputs.mike_gough.urbanized_area_prc_21071"

# 2.2
urban_area_prc_21094_5_fc = r"Database Connections\CBI Intermediate.sde\cbiintermediate.mike_gough.urban_area_prc_21094_5"

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

# Requirements that begin with 0 aren't applicable to any exemptions
requirements = {
    "0.1": "urbanized_area_prc_21071_unincorporated_0_1",
    # Location Requirements
    "2.1": "urbanized_area_prc_21071_2_1",
    "2.2": "urban_area_prc_21094_2_2",
    "2.3": "within_city_limits_2_3",
    "2.4": "unincorporated_2_4",
    "2.5": "within_mpo_2_5",
    "2.6": "covered_by_a_specific_plan_2_6",
    "2.7": "urbanized_area_or_urban_cluster_2_7",
    # Transit Proximity Requirements
    "3.1": "within_half_mile_major_transit_stop_3_1",
    "3.2": "within_quarter_mile_transit_corridor_3_2",
    "3.3": "transit_priority_area_3_3",
    "3.4": "within_half_mile_transit_corridor_3_4",
    "3.5": "within_half_mile_stop_transit_corridor_3_5",
    "3.6": "low_vmt_15_percent_below_regional_3_6",
    "3.7": "low_vmt_15_percent_below_city_3_7",
    "3.8": "low_vehicle_travel_area_3_8",
    "3.9": "planned_rtp_half_mile_major_transit_stop_3_9",
    "3.10": "planned_rtip_half_mile_major_transit_stop_3_10",
    "3.11": "planned_rtip_half_mile_stop_hqtc_3_11",
    "3.12": "planned_rtp_half_mile_hqtc_3_12",
    "3.13": "planned_rtp_quarter_mile_hqtc_3_13",
    "3.14": "within_half_mile_rail_transit_station_or_ferry_terminal_3_14",
    # Environmental Limitations
    "8.1": "wetlands_8_1",
    "8.2": "riparian_areas_8_2",
    "8.3": "special_habitats_8_3",
    #"8.4": "species_of_concern_8_4",
    "8.5": "rare_threatened_endangered_sp_8_5",
    # Hazards
    #"9.1": "sea_level_rise_9_1",
    "9.2": "earthquake_hazard_zone_9_2",
    "9.3": "wildfire_hazard_9_3",
    "9.4": "flood_plain_9_4",
    "9.5": "landslide_hazard_9_5",
    "9.6": "state_conservancy_9_6",
    "9.7": "local_coastal_zone_9_7",
    "9.8": "protected_area_mask_9_8",
}

# If county is missing data for a requirement (as indicated below), a field will be added to the county for that requirement with null values in it.
requirements_with_no_data = {
    "ALL_COUNTIES": ["3.3", "3.9", "3.14"],
    "alameda": [],
    "alpine": [],
    "amador": [],
    "butte": [],
    "calaveras": [],
    "colusa": [],
    "contracosta": [],
    "delnorte": [],
    "eldorado": [],
    "fresno": [],
    "glenn": [],
    "humboldt": [],
    "imperial": [],
    "inyo": [],
    "kern": [],
    "kings": [],
    "lake": [],
    "lassen": [],
    "losangeles": [],
    "madera": [],
    "marin": [],
    "mariposa": [],
    "mendocino": [],
    "merced": [],
    "modoc": [],
    "mono": [],
    "monterey": [],
    "napa": [],
    "nevada": [],
    "orange": [],
    "placer": [],
    "plumas": [],
    "riverside": [],
    "sacramento": [],
    "sanbenito": [],
    "sanbernardino": [],
    "sandiego": [],
    "sanfrancisco": [],
    "sanjoaquin": [],
    "sanluisobispo": [],
    "sanmateo": [],
    "santabarbara": [],
    "santaclara": [],
    "santacruz": [],
    "shasta": [],
    "sierra": [],
    "siskiyou": [],
    "solano": [],
    "sonoma": [],
    "stanislaus": [],
    "sutter": [],
    "tehama": [],
    "trinity": [],
    "tulare": [],
    "tuolumne": [],
    "ventura": [],
    "yolo": [],
    "yuba": [],
}

# 03/12/2020 Feb 18 version of Criteria Spreadsheet. Includes updates from Helen as well as the addition of the species requirement (8.5). Includes 3.9 -3.14 (yellow stuff)
exemptions = {
    "21159.24": ["2.1", "3.1", "8.1", "8.2", "8.3", "8.5", "9.2", "9.3", "9.4", "9.5", "9.6"],
    "21155.1": ["2.5", ["3.2", "3.13", "3.14"], "8.1", "8.2", "8.3", "8.5", "9.2", "9.3", "9.4", "9.5"],
    "21155.2": ["2.5", ["3.1", "3.4", "3.9", "3.12"]],
    "21155.4": ["2.5", "2.6", "3.3"],
    "21094.5": ["2.2", ["3.1", "3.5", "3.8", "3.10", "3.11"]],
    "65457": ["2.6"],
    #7: ["15183"", ""], # No Requirements
    "15332": ["2.3", "8.5"],
    "21159.25": ["2.4", "2.7", "8.5"],
    #10: ["15303", "CEQA Guidelines", ["2.1"]], # No Requirements
    "21099": ["3.3"],
    "21159.28": ["2.5"],
    "15064.3": [["3.1", "3.5", "3.6", "3.7"]]
}


# DATA PROCESSING FUNCTIONS ############################################################################################

def copy_parcels_fc(input_parcels_fc, output_parcels_fc):
    """ Copies the original parcels feature class with only a subset of the original fields.
        Used to create both the Data Basin output which will be populated with requirements and exemptions,
        as well as the Parcels Feature Class for the Dev Team without the requirements and exemptions fields.
    """

    print "Copying the original parcels Feature Class with only the user specified fields to keep..."
    print output_parcels_fc

    # create an empty field mapping object
    mapS = arcpy.FieldMappings()
    # for each field, create an individual field map, and add it to the field mapping object
    for field in original_fields_to_keep:
        map = arcpy.FieldMap()
        map.addInputField(input_parcels_fc, field)
        mapS.addFieldMap(map)

    output_gdb = os.path.dirname(output_parcels_fc)
    output_fc_name = os.path.basename(output_parcels_fc)

    # Create the empty parcels feature class with the subset of original fields to keep
    arcpy.FeatureClassToFeatureClass_conversion(
        in_features=input_parcels_fc,
        out_path=output_gdb, out_name=output_fc_name, where_clause="",
        field_mapping=mapS,
        config_keyword="")


def calculate_requirements(requirements_to_process=requirements.keys()):

    county_name = os.path.basename(output_parcels_fc).split("_")[0].lower()

    # Get a list of all the requirements that this county  doesn't have data for.
    requirements_with_no_data_this_county = requirements_with_no_data[county_name] + requirements_with_no_data["ALL_COUNTIES"]

    # Add a field for each of the requirements with "No Data". Will get set to <null> but default.
    for requirement_with_no_data_this_county in requirements_with_no_data_this_county:
        field_to_calc = requirements[requirement_with_no_data_this_county]
        if field_to_calc not in existing_output_fields:
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
            existing_output_fields.append(field_to_calc)

    # Create an object that contains all the requirement processing functions.
    requirement_functions = RequirementFunctions()

    # For each requirement passed in...
    for requirement in requirements_to_process:
        print "\nProcessing requirement: " + requirement
        field_to_calc = requirements[requirement]
        if field_to_calc not in existing_output_fields:
            print "Adding field: " + field_to_calc
            arcpy.AddField_management(output_parcels_fc, field_to_calc, "SHORT")
        if requirement not in requirements_with_no_data_this_county:
            print "Calling function to calculate values for this requirement..."
            requirement_functions.do_command(requirement, output_parcels_fc, field_to_calc)
        else:
            print "No data for this requirement. A field has been added with <null> values."


class RequirementFunctions(object):

    # ARCPY FUNCTIONS

    def calc_requirement_0_1(self, output_parcels_fc, field_to_calc):
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

    def calc_requirement_2_1(self, output_parcels_fc, field_to_calc):
        """
            2.1
            Requirement Long Name: Urbanized Area PRC 21071
            Description: Complicated, see description here:
            https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?lawCode=PRC&sectionNum=21071.
            The basic idea is that we iterate over each parcel, pass the OID to a subfunction which determines whether or
            not it meets the requirements in the the link above.
        """

        output_parcels_layer = arcpy.MakeFeatureLayer_management(output_parcels_fc)

        urbanized_area_prc_21071_layer = arcpy.MakeFeatureLayer_management(urbanized_area_prc_21071_fc)

        query = "urbanized_area_prc_21071 = 1"
        urbanized_area_prc_21071_layer_1s = arcpy.SelectLayerByAttribute_management(urbanized_area_prc_21071_layer, "NEW_SELECTION", query)

        arcpy.SelectLayerByLocation_management(output_parcels_layer, "HAVE_THEIR_CENTER_IN", urbanized_area_prc_21071_layer_1s)
        arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 1, "PYTHON")
        arcpy.SelectLayerByAttribute_management(output_parcels_layer, "SWITCH_SELECTION")
        arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 0, "PYTHON")

    def calc_requirement_2_2(self, output_parcels_fc, field_to_calc):
        """
            2.2
            Requirement Long Name: Urban Area PRC 21094.5
            Description: Select parcels WITHIN a city. Yes = 1, No = 0
            If not in a city, check to see if WITHIN an unincorporated island
            If within an unincorporated island, check to see if the unincorporated island it's in meets both of the following requirements:
                (A) The population of the unincorporated area and the population of the surrounding incorporated cities equal a population of 100,000 or more.
                (B) The population density of the unincorporated area is equal to, or greater than, the population density of the surrounding cities.
        """

        output_parcels_layer = arcpy.MakeFeatureLayer_management(output_parcels_fc)

        urban_area_prc_21094_5_layer = arcpy.MakeFeatureLayer_management(urban_area_prc_21094_5_fc)

        query = "urban_area_prc_21094_5 = 1"
        urban_area_prc_21094_5_layer_1s = arcpy.SelectLayerByAttribute_management(urban_area_prc_21094_5_layer, "NEW_SELECTION", query)

        arcpy.SelectLayerByLocation_management(output_parcels_layer, "HAVE_THEIR_CENTER_IN", urban_area_prc_21094_5_layer_1s)
        arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 1, "PYTHON")
        arcpy.SelectLayerByAttribute_management(output_parcels_layer, "SWITCH_SELECTION")
        arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 0, "PYTHON")

    def calc_requirement_2_3(self, output_parcels_fc, field_to_calc):
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

    def calc_requirement_2_4(self, output_parcels_fc, field_to_calc):
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

    def calc_requirement_2_5(self, output_parcels_fc, field_to_calc):
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

    def calc_requirement_2_7(self, output_parcels_fc, field_to_calc):
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

    def calc_requirement_8_5(self, output_parcels_fc, field_to_calc):

        """
            8.5
            Requirement Long Name:  Rare, Threatened, or Endangered Species
            Description: Select parcels that intersect the Rare, Threatened, or Endangered Species Dataset. Yes = 0, No = 1
        """
        output_parcels_layer = arcpy.MakeFeatureLayer_management(output_parcels_fc)
        arcpy.SelectLayerByLocation_management(output_parcels_layer, "INTERSECT", rare_threatened_or_endangered_fc)
        arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 0, "PYTHON")
        arcpy.SelectLayerByAttribute_management(output_parcels_layer, "SWITCH_SELECTION")
        arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 1, "PYTHON")

    def calc_requirement_9_3(self, output_parcels_fc, field_to_calc):
        """
            9.3
            Requirement Long Name: Wildfire Hazard
            Description: Select parcels that intersect the Wildfire Hazard Zones 3-5(output_parcels_fc, High - Extreme)(Yes = 0, No = 1)
            """
        print "Calculating Zonal Statistics..."
        # Calculate zonal stats to get a count of the number of wildfire hazard pixels within each parcel.
        tmp_zonal_stats_table = scratch_ws + os.sep + "wildfire_hazard_zonal_stats_subset"
        arcpy.sa.ZonalStatisticsAsTable(output_parcels_fc, "PARCEL_ID", wildfire_hazard_raster, tmp_zonal_stats_table, "", "SUM")

        print "Joining Zonal Stats table to the parcels dataset..."
        # Join the zonal stats table (output_parcels_fc, just the "COUNT" field) to the parcels feature class.
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

    def calc_requirement_9_4(self, output_parcels_fc, field_to_calc):
        """
            9.4
            Requirement Long Name: Flood Plain
            Description: Select parcels that intersect the 100 Year Floodplain. Yes = 0, No = 1
            Field Values defining the floodplain come from here: https://waterresources.saccounty.net/stormready/PublishingImages/100-year-floodplain-map-small.jpg
        """
        output_parcels_layer = arcpy.MakeFeatureLayer_management(output_parcels_fc)
        arcpy.SelectLayerByLocation_management(output_parcels_layer, "INTERSECT", flood_plain_fc)
        arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 0, "PYTHON")
        arcpy.SelectLayerByAttribute_management(output_parcels_layer, "SWITCH_SELECTION")
        arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 1, "PYTHON")

    def calc_requirement_9_5(self, output_parcels_fc, field_to_calc):
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
        # Join the zonal stats table (output_parcels_fc, just the "COUNT" field) to the parcels feature class.
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

    def calc_requirement_9_6(self, output_parcels_fc, field_to_calc):
        """
            9.6
            Requirement Long Name: State Conservancy
            Description: Select parcels that intersect the State Conservancy Dataset. Yes = 0, No = 1
        """
        output_parcels_layer = arcpy.MakeFeatureLayer_management(output_parcels_fc)
        arcpy.SelectLayerByLocation_management(output_parcels_layer, "INTERSECT", state_conservancy_fc)
        arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 0, "PYTHON")
        arcpy.SelectLayerByAttribute_management(output_parcels_layer, "SWITCH_SELECTION")
        arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 1, "PYTHON")

    def calc_requirement_9_7(self, output_parcels_fc, field_to_calc):
        """
            9.7
            Requirement Long Name: Local Coastal Zone
            Description: Select parcels that intersect the Local Coastal Zone Dataset. Yes = 0, No = 1
        """
        output_parcels_layer = arcpy.MakeFeatureLayer_management(output_parcels_fc)
        arcpy.SelectLayerByLocation_management(output_parcels_layer, "INTERSECT", local_coastal_zone_fc)
        arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 0, "PYTHON")
        arcpy.SelectLayerByAttribute_management(output_parcels_layer, "SWITCH_SELECTION")
        arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 1, "PYTHON")

    def calc_requirement_9_8(self, output_parcels_fc, field_to_calc):
        """
            9.8
            Requirement Long Name: Protected Area Mask
            Description: Select parcels that intersect the Protected Area Mask Dataset. Yes = 0, No = 1
        """
        output_parcels_layer = arcpy.MakeFeatureLayer_management(output_parcels_fc)
        arcpy.SelectLayerByLocation_management(output_parcels_layer, "INTERSECT", protected_area_mask_fc)
        arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 0, "PYTHON")
        arcpy.SelectLayerByAttribute_management(output_parcels_layer, "SWITCH_SELECTION")
        arcpy.CalculateField_management(output_parcels_layer, field_to_calc, 1, "PYTHON")

    # MODELS
        # Calling a model from arcpy after the toolbox has been imported:
        # arcpy.ModelName_ToolboxAlias() #Note that it's ModelName not Label.
        # arcpy.SpecificPlan26_Statewide(output_parcels_fc, field_to_calc)

    def calc_requirement_2_6(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r26"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_3_1(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r31"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_3_2(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r32"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_3_3(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r33"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_3_4(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r34"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_3_5(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r35"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_3_6(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r36"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_3_7(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r37"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_3_8(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r38"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_3_9(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r39"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_3_10(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r310"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_3_11(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r311"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_3_12(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r312"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_3_13(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r313"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_3_14(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r314"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_8_1(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r81"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_8_2(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r82"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_8_3(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r83"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def calc_requirement_9_2(self, output_parcels_fc, field_to_calc):
        # This is the name of the model (not the label)
        model_name = "r92"
        full_model_name = model_name + "_" + statewide_toolbox_name
        run_model_command = "arcpy." + full_model_name + "(r'%s', '%s')" % (output_parcels_fc, field_to_calc)
        exec run_model_command

    def default_function(self, *args):
        print "No function for this requirement. Values will not be calculated."

    def do_command(self, requirement_id, *args):
        return getattr(self, "calc_requirement_" + requirement_id.replace(".", "_"), self.default_function)(*args)


def join_additional_requirements(join_table, requirements_to_join):

    #Create index on join table once.
    #arcpy.AddIndex_management(join_table, "parcel_id", "parcel_id_index")

    fields_to_join = []
    for requirement_id in requirements_to_join:
        # Find the field name in join_table
        field_code = requirement_id.replace(".", "_")
        matching_field = arcpy.ListFields(join_table, "*" + field_code)[0].name
        print "Field to join: " + matching_field
        fields_to_join.append(matching_field)

        # Delete standardized field name if it exists.
        standardized_field_name = requirements[requirement_id]
        print "Standardized field name: " + standardized_field_name
        if standardized_field_name in existing_output_fields:
            print "The standardized field above already exists. Deleting it to avoid conflicts when the rename function is called..."
            arcpy.DeleteField_management(output_parcels_fc, standardized_field_name)

    print "Performing join of additional fields..."
    arcpy.JoinField_management(output_parcels_fc, "parcel_id", join_table, "parcel_id", fields_to_join)


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
            #requirement_code = float(input_field.split("_")[-2] + "." + input_field.split("_")[-1])
            requirement_code = input_field.split("_")[-2] + "." + input_field.split("_")[-1]
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


def calculate_exemptions(exemptions_to_calculate=exemptions.keys()):

    print "\nCalculating Exemptions..."

    existing_output_fields = [field.name for field in arcpy.ListFields(output_parcels_fc)]

    if not "exemptions_count" in existing_output_fields:
        print "\nAdding exemptions_count field"
        arcpy.AddField_management(output_parcels_fc, "exemptions_count", "SHORT")

    print "Calculating 0's in the 'exemptions_count' field."
    arcpy.CalculateField_management(output_parcels_fc, "exemptions_count", 0, "PYTHON")

    # Add a field for each exemption to calculate if it doesn't already exist.
    for exemption_to_calculate in exemptions_to_calculate:
        # Add a field for the exemption
        exemption_field_name = "E_" + exemption_to_calculate.replace(".", "_")
        if not exemption_field_name in existing_output_fields:
            print "\nAdding exemption field " + exemption_field_name
            arcpy.AddField_management(output_parcels_fc, exemption_field_name, "SHORT")

    # Create an update cursor on the parcels feature class
    with arcpy.da.UpdateCursor(output_parcels_fc, "*") as uc:

        # For Every Row in the parcels table...
        print "\nStarting update cursor loop to calculate exemptions..."
        for row in uc:
            exemptions_count = row[uc.fields.index("exemptions_count")]

            # Do this for each exemption.
            for exemption_to_calculate in exemptions_to_calculate:

                exemption_field_name = "E_" + exemption_to_calculate.replace(".", "_")

                # Get a list of the requirement ids for the exemption
                requirement_ids = exemptions[exemption_to_calculate]

                check_requirements = []

                # For each Requirement, pull the values for these requirements out of the attribute table.
                # Make one list for the ORs, and one list of the Ands
                for requirement_id in requirement_ids:
                    #ORs
                    if type(requirement_id) == list:
                        or_values = []
                        for or_id in requirement_id:
                            requirement_field_name = requirements[or_id]
                            try:
                                field_value = row[uc.fields.index(requirement_field_name)]
                            except:
                                print "Missing field for requirement " + requirement_field_name
                                print "Either add it to the requirements_with_no_data dictionary (if this county is missing data for this requirement), or run the calculate_requirements function on it."
                                exit()
                            or_values.append(field_value)

                        # If any of the OR requirements are met
                        if any(or_values):
                            check_requirements.append(1)
                        # If there is a NULL value for one of the requirements, and no 1's, we can't be certain.
                        elif None in or_values:
                            check_requirements.append(None)
                        # Otherwise all the OR requirements are zeros.
                        else:
                            check_requirements.append(0)

                    #ANDs
                    else:
                        requirement_field_name = requirements[requirement_id]
                        try:
                            field_value = row[uc.fields.index(requirement_field_name)]
                        except:
                            print "Missing field for requirement " + requirement_field_name
                            print "Either add it to the requirements_with_no_data dictionary (if this county is missing data for this requirement), or run the calculate_requirements function on it."
                            exit()
                        check_requirements.append(field_value)

                # ALL 1's. All requirements met.
                if all(check_requirements):
                    exemptions_count += 1
                    exemption_status = 1

                # At least one 0. Requirements not met.
                elif 0 in check_requirements:
                    exemption_status = 0

                # No 0's, but didn't meet ALL condition, so there's a None in there.
                else:
                    exemption_status = None

                # Insert exemption status.
                row[uc.fields.index(exemption_field_name)] = exemption_status
                row[uc.fields.index("exemptions_count")] = exemptions_count
                uc.updateRow(row)


# TABLES FOR DEV TEAM ##################################################################################################

def create_requirements_table_dev_team():
    """ Creates the requirements table & adds the exemptions_count field"""

    if arcpy.Exists(output_parcels_fc):
        existing_output_fields = [field.name for field in arcpy.ListFields(output_parcels_fc)]

    output_requirements_table_name = "requirements"

    # Keep PARCEL_ID field plus any requirement fields
    fields_to_keep = ["PARCEL_ID", "COUNTYNAME"]
    for field in existing_output_fields:
        if field in requirements.values():
            fields_to_keep.append(field)

    # create an empty field mapping object
    mapS = arcpy.FieldMappings()
    # for each field, create an individual field map, and add it to the field mapping object
    for field in fields_to_keep:
        map = arcpy.FieldMap()
        map.addInputField(output_parcels_fc, field)
        mapS.addFieldMap(map)


    output_table = output_gdb_dev_team + os.sep + output_requirements_table_name

    # If no requirements table exists, create it.
    if not arcpy.Exists(output_table):
        print "\nCreating Requirements table..."
        arcpy.TableToTable_conversion(
            in_rows=output_parcels_fc,
            out_path=output_gdb_dev_team, out_name=output_requirements_table_name, where_clause="",
            field_mapping=mapS,
            config_keyword="")

    # Otherwise, append the rows
    else:
        print "\nAppending rows to the Requirements table..."
        tmp_table = scratch_ws + os.sep + "tmp_table_requirements"
        arcpy.CopyRows_management(output_parcels_fc, tmp_table)
        #table_view = arcpy.MakeTableView_management(output_parcels_fc)
        arcpy.Append_management(
            inputs=tmp_table,
            target=output_table,
            schema_type="NO_TEST",
            field_mapping=mapS,
            subtype="")


def create_exemptions_table_dev_team():
    """ Creates the requirements table & adds the exemptions_count field"""

    if arcpy.Exists(output_parcels_fc):
        existing_output_fields = [field.name for field in arcpy.ListFields(output_parcels_fc)]

    output_exemptions_table_name = "exemptions"

    # Add a field for each exemption to calculate
    exemption_fields = []
    for exemption in exemptions.keys():
        # Add a field for the exemption
        exemption_field_name = "E_" + exemption.replace(".", "_")
        exemption_fields.append(exemption_field_name)

    # Keep PARCEL_ID field plus any requirement fields
    fields_to_keep = ["PARCEL_ID", "COUNTYNAME"]
    for field in existing_output_fields:
        if field in exemption_fields:
            fields_to_keep.append(field)
    fields_to_keep.append("exemptions_count")

    # create an empty field mapping object
    mapS = arcpy.FieldMappings()
    # for each field, create an individual field map, and add it to the field mapping object
    for field in fields_to_keep:
        map = arcpy.FieldMap()
        map.addInputField(output_parcels_fc, field)
        mapS.addFieldMap(map)

    output_table = output_gdb_dev_team + os.sep + output_exemptions_table_name

    # If no requirements table exists, create it.
    if not arcpy.Exists(output_table):
        print "\nCreating Exemptions table..."
        arcpy.TableToTable_conversion(
            in_rows=output_parcels_fc,
            out_path=output_gdb_dev_team, out_name=output_exemptions_table_name, where_clause="",
            field_mapping=mapS,
            config_keyword="")

    # Otherwise, append the rows
    else:
        print "\nAppending rows to the Exemptions table..."
        tmp_table = scratch_ws + os.sep + "tmp_table_exemptions"
        arcpy.CopyRows_management(output_parcels_fc, tmp_table)
        arcpy.Append_management(
            inputs=tmp_table,
            target=output_table,
            schema_type="NO_TEST",
            field_mapping=mapS,
            subtype="")


# EXTRA FUNCTIONS ######################################################################################################

def list_fields():
    field_dict = {}

    for input_field in existing_output_fields:

        if input_field in requirements.values():
            requirement_code = float(input_field.split("_")[-2] + "." + input_field.split("_")[-1])
            field_dict[requirement_code] = input_field

    sorted_list = sorted(field_dict.iteritems(), key=lambda (x, y): float(x))

    for field in sorted_list:
        print str(field[0]) + ": " + field[1]


# BEGIN PROCESSING #####################################################################################################

start_time = datetime.datetime.now()
print("\nStart Time: " + str(start_time))

arcpy.env.workspace = input_parcels_gdb

if input_parcels_fc_list == "*":
    input_parcels_fc_list = arcpy.ListFeatureClasses()
if requirements_to_process == "*":
    requirements_to_process = requirements.keys()

arcpy.env.workspace = output_gdb_dev_team

# For each parcel in the user defined list....
for input_parcels_fc_name in input_parcels_fc_list:

    print "\nProcessing parcels: " + input_parcels_fc_name

    # Get the path to the county parcels.
    input_parcels_fc = input_parcels_gdb + os.sep + input_parcels_fc_name

    # Set the output Feature Class names.
    output_parcels_fc = output_gdb_data_basin + os.sep + input_parcels_fc_name.lower() + "_" + "requirements_and_exemptions"
    output_parcels_fc_dev_team = output_gdb_dev_team + os.sep + input_parcels_fc_name.lower()

    # Create output Feature Class for Data Basin and for Dev Team if they don't already exist ##############
    if not arcpy.Exists(output_parcels_fc):
        copy_parcels_fc(input_parcels_fc, output_parcels_fc)
    if not arcpy.Exists(output_parcels_fc_dev_team):
        copy_parcels_fc(input_parcels_fc, output_parcels_fc_dev_team)

    # Get a list of the fields that currently exist in the output feature class.
    existing_output_fields = [field.name for field in arcpy.ListFields(output_parcels_fc)]

    #################################### Choose Data Processing Functions ########################################

    calculate_requirements(requirements_to_process)

    # Join Additional Requirement Fields (From Kai and other staff). Field names must have requiement ID at the end (e.g., 3_10)
    #requirements_to_join = ["3.10", "3.11", "3.12", "3.13"]
    #join_additional_requirements(join_requirements_table, requirements_to_join)
    #rename_fields() # Only necessary if joining additional requirement fields.

    calculate_exemptions()

    # NOTE: If the dev team tables already exist, the functions below will APPEND new rows.
    # So if re-running a county, the records for this county need to be deleted in this table first.
    # Or, delete the entire table first. Need to come up with a way to automate this.
    create_requirements_table_dev_team()

    create_exemptions_table_dev_team()

    end_time = datetime.datetime.now()
    duration = end_time - start_time

print("Start Time: " + str(start_time))
print("End Time: " + str(end_time))
print("Duration: " + str(duration))
