import arcpy
import random
arcpy.env.overwriteOutput = True

intermediate_ws = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb"
arcpy.env.workspace = intermediate_ws

output_ws = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs.gdb'

input_parcels_fc = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Parcels.gdb\sacramento_parcels"
output_parcels_fc = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs.gdb\sacramento_parcels"

# Requirement datasets
city_boundaries_fc = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Inputs\Inputs.gdb\CA_Cities"

def copy_parcels_fc():
    arcpy.CopyFeatures_management(input_parcels_fc, output_parcels_fc)

requirements = {
    # Type of Housing
    1.1: "res_or_mixed_25_com",
    1.2: "res_or_mixed",
    1.3: "res",
    1.4: "multifamily",
    # Location Requirements
    2.1: "urbanized_area",
    2.2: "urban_area",
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


def create_empty_tables():
    ''' Create the required tables '''

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
    ''' Populate the exemptions table '''

    ic = arcpy.da.InsertCursor("exemptions", ["exemption_id", "exemption_code", "exemption_source"])

    for k, v in exemptions.iteritems():
        ic.insertRow([k, v[0], v[1]])


def calculate_parcel_requirements():
    ''' For each requirement field, determine whether or not each parcel meets the requirement. Random numbers. '''

    uc = arcpy.da.UpdateCursor(output_parcels_fc, "*")
    
    fieldnames = []
    fields = arcpy.ListFields(output_parcels_fc)
    for field in fields:
        fieldnames.append(field.name)

    for row in uc:

        parcel_OID = row[0]

        requirement_2_1 = calc_requirement_2_1(parcel_OID)

        # TODO: Replace random number assignment with geoprocessing steps
        #for k, v in requirements.iteritems():
        #        rand = random.choice([0, 0, 0, 0, 0, 0, 0, 0, 1])
        #        if rand:
        #            row[fieldnames.index(v)] = 1
        #        else:
        #            row[fieldnames.index(v)] = 0

    uc.updateRow(row)
            
            
def calculate_parcel_exemptions():
    ''' Determines what parcels meet what exemptions based on the binary requirement fields in the parcels feature class. Output stored in the junction table (parcels_exemptions). '''
    
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
    arcpy.env.workspace = output_ws
    #parcels_name = arcpy.Describe(output_parcels_fc).Name
    #arcpy.CopyRows_management(output_parcels_fc, "requirements_table")

    all_fields = arcpy.ListFields(output_parcels_fc)
    parcel_fc_fields = ["SHAPE", "SHAPE_Length", "SHAPE_Area", "PARCEL_ID", "PARCEL_APN", "FIPS_CODE", "COUNTYNAME", "TAXAPN", "SITE_ADDR", "SITE_CITY", "SITE_STATE", "SITE_ZIP", "LATITUDE", "LONGITUDE", "CENSUS_TRACT", "CENSUS_BLOCK_GROUP", "Zoning", "LOT_SIZE_AREA", "LOT_SIZE_AREA_UNIT"]
    requirements_fields = []
    for field in all_fields:
        if field.name not in parcel_fc_fields and field.name not in ["OBJECTID", "SHAPE_Length", "SHAPE_Area"]:
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

#copy_parcels_fc()
#create_empty_tables()
calculate_parcel_requirements()
#populate_exemptions_table()
#create_outputs()

def calc_requirement_2_1(parcel_OID):

    city_boundaries_layer = arcpy.MakeFeatureLayer_management(city_boundaries_fc)
    output_parcels_layer = arcpy.MakeFeatureLayer_management(output_parcels_fc)

    # Select the current parcel
    query = '"OBJECTID" = %s' % str(parcel_OID)
    arcpy.SelectLayerByAttribute_management(output_parcels_layer, "NEW_SELECTION", query)

    # Select the city boundary that the parcel falls within and get the OBJECTID
    arcpy.SelectLayerByLocation_management(city_boundaries_layer, "CONTAINS", output_parcels_layer)
    arcpy.MakeFeatureLayer_management(city_boundaries_layer, "city_boundary_containing_parcel")

    ################################ INCORPORATED CITY CRITERIA  ########################################

    # Get the population of the selected city boundary
    city_boundary_containing_parcel_population = 0
    sc = arcpy.SearchCursor("city_boundary_containing_parcel")
    for row in sc:
        city_boundary_containing_parcel_population = row.getValue("POPULATION")

    # If the city boundary has a population > 100,000k, we're done(21017 a(1)).
    if city_boundary_containing_parcel_population > 100000:
        print "Population of city exceeds 100,000: " + str(city_boundary_containing_parcel_population)
        requirement_2_1 = 1


    # If the city boundary has a population < 100000k, but the total population with two contiguous cities > 100,000k
    else:
        # Select contiguous city boundaries.
        arcpy.SelectLayerByLocation_management(city_boundaries_layer, "SHARE_A_LINE_SEGMENT_WITH", "city_boundary_containing_parcel")

        # Get the sum of the top two contiguous city populations.
        city_boundary_sc = arcpy.SearchCursor(city_boundaries_layer)
        population_list = []
        for row in city_boundary_sc:
            population_list.append(row.getValue("POPULATION"))

        # If there are no more than two contiguous incorporated cities...
        if len(population_list) <= 2:
            sorted_pop_list = sorted(population_list)
            sum_largest_two_surrounding_pops = sorted_pop_list[-1] + sorted_pop_list[-2]
            sum_surrounding_populations = city_boundary_containing_parcel_population + sum_largest_two_surrounding_pops

            # ...and the selected city + the two largest surrounding cities  have a population > 100,000k, we're done
            if sum_surrounding_populations >= 10000:
                requirement_2_1 = 1

            ################################ UNINCORPORATED CITY CRITERIA  ########################################
            else:
                requirement_2_1 = 0

    return requirement_2_1

