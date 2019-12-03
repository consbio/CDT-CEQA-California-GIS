import os
import sys
import arcpy
import random
import datetime
arcpy.env.overwriteOutput = True

# If called multiple times from batch script to increase performance, get oids from batch file.
start_oid = sys.argv[1]
end_oid = sys.argv[2]

# Workspaces
intermediate_ws = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb"
output_ws = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs.gdb'

# Input & output parcel feature classes
input_parcels_fc = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Parcels.gdb\sacramento_parcels"
output_parcels_fc = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs.gdb\sacramento_parcels"
#output_parcels_fc = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs.gdb\sacramento_parcels_subset3"

# Datasets used in calculating requirements:

# 2.1, 2.2, 2.3
city_boundaries_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\CA_TIGER_2019_incorporated_cities_with_TIGER_2017_population"
unincorporated_islands = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb\CA_TIGER_Unincorporated_Islands_with_Population_Dissolve" #2.2

# 2.4
urbanized_area_urban_cluster_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\CA_urbanized_area_urban_cluster"
incorporated_and_unincorporated_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\CA_incorporated_and_unincorporated"

# 2.5
mpo_boundary_dissolve_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb\MPO_boundaries_dissolve"

start_time = datetime.datetime.now()
print("Start Time: " + str(start_time))

requirements = {
    # Location Requirements
    2.1: "urbanized_area_prc_21071",
    2.2: "urban_area_prc_21094",
    2.3: "within_city_limits",
    2.4: "unincorporated_urbanized_area",
    2.5: "within_mpo",
    # Transit Proximity Requirements
    3.1: "within_half_mile_major_transit_stop",
    3.2: "within_quarter_mile_transit_coordidor",
    3.3: "hundred_percent_affordable",
    3.4: "transit_priority_area",
    3.5: "within_half_mile_transit_cooridor",
    # Infill Requirements
    4.1: "infill",
    4.2: "previously_developed_or_75_next_to_urban",
    4.3: "qualified_urban_uses",
    # Environmental Limitations 
    8.1: "wetlands",
    8.2: "riparian_areas",
    8.3: "special_habitats",
    8.4: "species_of_concern",
    # Hazards
    9.1: "sea_level_rise",
    9.2: "earthquake_hazard_zone",
    9.3: "wildfire_hazard",
    9.4: "flood_plain",
    9.5: "landslide_hazard",
    # Public Health
    10.1: "rselhaz",
    10.2: "pesticide",
    10.3: "drinking_water",
    10.4: "cleanups",
    10.5: "groundwater",
    10.6: "hazardous_waste",
    10.7: "asthma",
    # Historical 
    11.1: "historical_resources",
    # General Plan 
    12.1: "open_space",
    12.2: "agriculture"
}

exemptions = { 
    1: ['21159.24', 'Resources Code', [1.1, 2.1, 3.1, 4.1, 8.1, 8.2, 8.3, 8.4, 9.1, 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 12.1]],
    2: ['21155.1', 'Resources Code', [1.2, [3.1, 3.2], 8.1, 8.2, 8.3, 8.4, 9.1, 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 11.1, 12.1]],
    3: ['21094.5', 'Resources Code', [1.2, 2.2, [3.1, 3.2, 3.3], 4.2]],
    4: ['21155.4', 'Resources Code', [1.2, 3.4, 4.2]],
    5: ['65457', 'Government Code', [1.3, 8.1, 8.2, 8.3, 8.4, 9.1, 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 12.1]],
    6: ['15183', 'CEQA Guidelines', [1.2, 8.1, 8.2, 8.3]],
    7: ['15332', 'CEQA Guidelines', [1.2, 2.3]],
    8: ['21159.25', 'Resources Code', [1.4, 4.2]],
    9: ['15303', 'CEQA Guidelines', [1.3, 2.1, 4.3]],
    #10: ['21099', 'Resources Code', []],
    11: ['21155.2', 'Resources Code', [2.5, [3.1, 3.5]]],
    #12: ['21159.23', 'Resources Code', []],
    13: ['21159.28', 'Resources Code', [2.5]]
}

arcpy.env.workspace = intermediate_ws

# ACTIONS ##############################################################################################################

def copy_parcels_fc():
    print "Copying Parcels Feature Class..."
    arcpy.CopyFeatures_management(input_parcels_fc, output_parcels_fc)


def create_empty_exemption_tables():
    print "Creating empty tables..."

    # Create the parcel - exemptions table (junction table)
    arcpy.CreateTable_management(intermediate_ws, "parcel_exemptions")
    arcpy.AddField_management("parcel_exemptions", "parcel_id", "TEXT")
    arcpy.AddField_management("parcel_exemptions", "exemption_id", "TEXT")

    # Create the exemptions table
    arcpy.CreateTable_management(intermediate_ws, "exemptions")
    arcpy.AddField_management("exemptions", "exemption_id", "SHORT")
    arcpy.AddField_management("exemptions", "exemption_code", "TEXT")
    arcpy.AddField_management("exemptions", "exemption_source", "TEXT")

    # Add fields to the parcels feature class (one for each requirement)
    for k, v in requirements.iteritems():
        arcpy.AddField_management(output_parcels_fc, v, "SHORT")

    arcpy.AddField_management(output_parcels_fc, "exemptions_count", "SHORT")
    
    
def populate_exemptions_table():
    print "Populating the exemptions table..."

    ic = arcpy.da.InsertCursor("exemptions", ["exemption_id", "exemption_code", "exemption_source"])

    for k, v in exemptions.iteritems():
        ic.insertRow([k, v[0], v[1]])


# Function Handler that calls the INDIVIDUAL REQUIREMENT function for processing.
def calculate_parcel_requirements(requirements_to_process, start_oid=0, end_oid=0):

    print "Calculating 1's and 0's for the spatial requirements...."

    # For requirements requiring an update cursor
    if 2.1 in requirements_to_process:
        print "Calculating requirement 2.1...\n"
        field_to_calc = requirements[2.1]
        calc_requirement_2_1(field_to_calc, start_oid, end_oid)

    if 2.2 in requirements_to_process:
        print "Calculating requirement 2.2...\n"
        field_to_calc = requirements[2.2]
        calc_requirement_2_2(field_to_calc)

    if 2.3 in requirements_to_process:
        print "Calculating requirement 2.3...\n"
        field_to_calc = requirements[2.3]
        calc_requirement_2_3(field_to_calc)

    if 2.4 in requirements_to_process:
        print "Calculating requirement 2.4...\n"
        field_to_calc = requirements[2.4]
        calc_requirement_2_4(field_to_calc)

    if 2.5 in requirements_to_process:
        print "Calculating requirement 2.5...\n"
        field_to_calc = requirements[2.5]
        calc_requirement_2_5(field_to_calc)

            
def calculate_parcel_exemptions():
    print "Calculating parcel exemptions based on requirements (output stored in the junction table (parcels_exemptions)."
    
    parcels_uc = arcpy.da.UpdateCursor(output_parcels_fc, "*")
    exemptions_ic = arcpy.da.InsertCursor("parcel_exemptions", ['parcel_id', 'exemption_id'])

    for row in parcels_uc:
        parcel_id = row[parcels_uc.fields.index('PARCEL_ID')]
        
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
                        yes_or_no = row[parcels_uc.fields.index(r)]
                        sum_or_requirements += yes_or_no
                    check_requirements.append(sum_or_requirements)
                else:
                    requirement = requirements[requirement_id]
                    yes_or_no = row[parcels_uc.fields.index(requirement)]
                    check_requirements.append(yes_or_no)
                    
            # If this parcel meets all the requirements for this exemption, add a record to the junction table. 
            # e.g., [1,1,1,1,1]
            if all(check_requirements):
                count_exemptions += 1
                exemptions_ic.insertRow([parcel_id, v[0]])

        # Add the count of the number of exemptions to the parcels feature class. 
        row[parcels_uc.fields.index("exemptions_count")] = count_exemptions
        parcels_uc.updateRow(row)


def create_outputs():
    print "Creating outputs..."
    arcpy.env.workspace = output_ws

    all_fields = arcpy.ListFields(output_parcels_fc)
    parcel_fc_fields_to_keep = ["SHAPE", "SHAPE_Length", "SHAPE_Area", "PARCEL_ID", "PARCEL_APN", "FIPS_CODE", "COUNTYNAME", "TAXAPN", "SITE_ADDR", "SITE_CITY", "SITE_STATE", "SITE_ZIP", "LATITUDE", "LONGITUDE", "CENSUS_TRACT", "CENSUS_BLOCK_GROUP", "Zoning", "LOT_SIZE_AREA", "LOT_SIZE_AREA_UNIT"]
    requirements_fields = []
    for field in all_fields:
        if field.name not in parcel_fc_fields_to_keep and field.name not in ["OBJECTID", "SHAPE_Length", "SHAPE_Area"]:
            requirements_fields.append(field.name)
   
    fmap = arcpy.FieldMappings()
    fmap.addTable(output_parcels_fc)
    fields = {f.name: f for f in arcpy.ListFields(output_parcels_fc)}

    # clean up field map
    for fname, fld in fields.iteritems():
        if fld.type not in ('OID', 'Geometry') and 'shape' not in fname.lower():
            if fname not in requirements_fields: 
                fmap.removeFieldMap(fmap.findFieldMapIndex(fname))
    
    print "Deleting fields from requirements table"
    #arcpy.DeleteField_management("requirements_table", parcel_fc_fields)
    
    print "Deleting fields from parcels table"
    arcpy.DeleteField_management(output_parcels_fc, requirements_fields)


# INDIVIDUAL REQUIREMENTS ##############################################################################################

def calc_requirement_2_1(field_to_calc, start_oid, end_oid):

    def calc_requirement_2_1_iterate(parcel_OID):

        print "Parcel OBJECTID: " + str(parcel_OID)

        city_boundaries_layer = arcpy.MakeFeatureLayer_management(city_boundaries_fc)
        output_parcels_layer = arcpy.MakeFeatureLayer_management(output_parcels_fc)

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

            # If the city boundary has a population > 100,000k, we're done(21017 a(1)).
            if city_boundary_containing_parcel_population > 100000:
                print "Requirement met."
                requirement_2_1 = 1

            # If the city boundary has a population < 100000k, but the total population with two contiguous cities > 100,000k
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

                # If the city plus two contiguous incorporated cities total more than 100,000k...
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

    filter_records = "OBJECTID > %s and OBJECTID <= %s" % (start_oid, end_oid)
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

    # Make a city boundaries layer
    arcpy.MakeFeatureLayer_management(city_boundaries_fc, "city_boundaries_layer")

    # Make a parcels layer
    arcpy.MakeFeatureLayer_management(output_parcels_fc, "output_parcels_layer")

    # Within a city? Yes = 1
    arcpy.SelectLayerByLocation_management("output_parcels_layer", "WITHIN", city_boundaries_fc)
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 1, "PYTHON")

    # Not within a city = 0
    arcpy.SelectLayerByAttribute_management("output_parcels_layer", "SWITCH_SELECTION")
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 0, "PYTHON")

    # Not within a city is selected.  Of those, select parcels within an unincorporated island).
    unincorporated_islands_layer = arcpy.MakeFeatureLayer_management(unincorporated_islands)
    surrounded_parcels = arcpy.SelectLayerByLocation_management("output_parcels_layer", "WITHIN", unincorporated_islands_layer, "", "SUBSET_SELECTION")

    print "Number of unincorporated parcels surrounded: " + str(arcpy.GetCount_management("output_parcels_layer")[0])

    fieldnames = []
    fields = arcpy.ListFields(surrounded_parcels)
    for field in fields:
        fieldnames.append(field.name)

    # output_parcels_layer now consists of polygons that are completely surrounded.
    uc = arcpy.da.UpdateCursor(surrounded_parcels, "*")
    for uc_row in uc:

        parcel_OID = uc_row[fieldnames.index("OBJECTID")]
        print "Parcel OID: " + str(parcel_OID)

        this_surrounded_parcel = arcpy.SelectLayerByAttribute_management("output_parcels_layer", "NEW_SELECTION", "OBJECTID = " + str(parcel_OID))

        # Select the unincorporated island polygon containing this parcel
        this_unincorporated_island = arcpy.SelectLayerByLocation_management(unincorporated_islands_layer, "CONTAINS", this_surrounded_parcel)

        # Get population of unincorporated area
        sc = arcpy.SearchCursor(this_unincorporated_island)
        for row in sc:
            unincorporated_population = int(row.getValue("SUM_POP10"))
            unincorporated_area = int(row.getValue("SHAPE_Area")) * 0.001

        unincorporated_density = unincorporated_population / unincorporated_area

        # Select the surrounding cities.
        surrounding_cities = arcpy.SelectLayerByLocation_management("city_boundaries_layer", "SHARE_A_LINE_SEGMENT_WITH", this_unincorporated_island)
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

    arcpy.MakeFeatureLayer_management(output_parcels_fc, "output_parcels_layer")
    arcpy.SelectLayerByLocation_management("output_parcels_layer", "WITHIN", city_boundaries_fc)
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 1, "PYTHON")
    arcpy.SelectLayerByAttribute_management("output_parcels_layer", "SWITCH_SELECTION")
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 0, "PYTHON")


def calc_requirement_2_4(field_to_calc):

    # Unincorporated areas
    arcpy.MakeFeatureLayer_management(incorporated_and_unincorporated_fc, "incorporated_and_unincorporated_layer")
    arcpy.SelectLayerByAttribute_management("incorporated_and_unincorporated_layer", "NEW_SELECTION", "CITY = 'Unincorporated'")

    # Urbanized area or urban cluster
    arcpy.MakeFeatureLayer_management(urbanized_area_urban_cluster_fc, "urbanized_area_urban_cluster_layer")

    # Unincorporated Urbanized area or urban cluster
    unincorporated_urbanized_area_or_urban_cluster_fc = intermediate_ws + os.sep + "unincorporated_urbanized_area_or_urban_cluster"
    arcpy.Intersect_analysis(["incorporated_and_unincorporated_layer", "urbanized_area_urban_cluster_layer"], unincorporated_urbanized_area_or_urban_cluster_fc)

    arcpy.MakeFeatureLayer_management(output_parcels_fc, "output_parcels_layer")
    arcpy.SelectLayerByLocation_management("output_parcels_layer", "WITHIN", unincorporated_urbanized_area_or_urban_cluster_fc)

    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 1, "PYTHON")
    arcpy.SelectLayerByAttribute_management("output_parcels_layer", "SWITCH_SELECTION")
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 0, "PYTHON")


def calc_requirement_2_5(field_to_calc):

    arcpy.MakeFeatureLayer_management(output_parcels_fc, "output_parcels_layer")
    arcpy.SelectLayerByLocation_management("output_parcels_layer", "WITHIN", mpo_boundary_dissolve_fc)
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 1, "PYTHON")
    arcpy.SelectLayerByAttribute_management("output_parcels_layer", "SWITCH_SELECTION")
    arcpy.CalculateField_management("output_parcels_layer", field_to_calc, 0, "PYTHON")


#copy_parcels_fc()
#create_empty_exemption_tables()
#populate_exemptions_table()

calculate_parcel_requirements(requirements_to_process=[2.1], start_oid=start_oid, end_oid=end_oid)
#calculate_parcel_requirements(requirements_to_process=[2.3], start_oid=0, end_oid=456000)

#create_outputs()

end_time = datetime.datetime.now()
duration = end_time - start_time

print("Start Time: " + str(start_time))
print("End Time: " + str(end_time))
print("Duration: " + str(duration))

