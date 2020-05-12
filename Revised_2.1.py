import arcpy
import os

intermediate_ws = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb"
scratch_ws = r"P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Scratch\Scratch.gdb"

cities_with_population_fc = r"Database Connections\CBI Inputs.sde\cbiinputs.mike_gough.CA_TIGER_2019_incorporated_cities_with_TIGER_2017_population"
unincorporated_islands_with_population_fc = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb\CA_TIGER_Unincorporated_Islands_with_Population_Dissolve"
urbanized_area_prc_21071 = intermediate_ws + os.sep + "urbanized_area_prc_21071"

arcpy.Union_analysis([cities_with_population_fc, unincorporated_islands_with_population_fc], urbanized_area_prc_21071)

fields_to_drop = [
    "FID_CA_TIGER_2019_incorporated_cities_with_TIGER_2017_population",
    "placens",
    "classfp",
    "funcstat",
    "aland",
    "awater",
    "intptlat",
    "intptlon",
    "FID_CA_TIGER_Unincorporated_Islands_with_Population_Dissolve",
    "FID_CA_TIGER_2019_Unincorporated_Islands"
]

# arcpy.DeleteField_management(in_table=urbanized_area_prc_21071, drop_field=fields_to_drop)

arcpy.AddField_management(urbanized_area_prc_21071, "city_name", "TEXT")
arcpy.AddField_management(urbanized_area_prc_21071, "community_type", "TEXT")
arcpy.AddField_management(urbanized_area_prc_21071, "area_km2", "DOUBLE")
arcpy.AddField_management(urbanized_area_prc_21071, "population_estimate", "LONG")
arcpy.AddField_management(urbanized_area_prc_21071, "population_density", "DOUBLE")
arcpy.AddField_management(urbanized_area_prc_21071, "surrounding_city_count", "LONG")
arcpy.AddField_management(urbanized_area_prc_21071, "surrounding_population_list", "TEXT", "", "", 500)
arcpy.AddField_management(urbanized_area_prc_21071, "surrounding_population_total", "LONG")
arcpy.AddField_management(urbanized_area_prc_21071, "surrounding_area_total", "DOUBLE")
arcpy.AddField_management(urbanized_area_prc_21071, "surrounding_population_density", "LONG")
arcpy.AddField_management(urbanized_area_prc_21071, "urbanized_area_prc_21071", "SHORT")

# Calculate the area in Square Kilometers
arcpy.CalculateField_management(urbanized_area_prc_21071,'area_km2','!shape.area! * 0.000001','PYTHON')

fields = [
    "urbanized_area_prc_21071",  # 0
    "namelsad",  # 1
    "b01003_001e_pop_estimate_total",  # 2
    "SUM_POP10",  # 3
    "shape_Area",  # 4
    "city_name",  # 5
    "population_estimate",  # 6
    "OBJECTID",  # 7
    "surrounding_city_count",  # 8
    "surrounding_population_list",  # 9
    "surrounding_population_total",  # 10
    "surrounding_area_total",  # 11
    "population_density",  # 12
    "area_km2",  # 13
    "surrounding_population_density",  # 14
    "community_type",  # 15

]

urbanized_area_prc_21071_layer = arcpy.MakeFeatureLayer_management(urbanized_area_prc_21071)

# Need to get population estimates in there first in order to be able to look at the population of surrounding cities.
with arcpy.da.UpdateCursor(urbanized_area_prc_21071, fields) as uc:
    for row in uc:
        namelsad = row[1]

        if namelsad:
            # City Name Field
            row[5] = namelsad
            # Set Community Type Field
            community_type = "Incorporated City"
            print community_type
            row[15] = community_type
            population_estimate = row[2]
            row[6] = int(population_estimate)

        else:
            # Set City Name Field
            row[5] = "Unincorporated Island"
            # Set Community Type Field
            community_type = row[5]
            print community_type
            row[15] = community_type
            population_estimate = row[3]
            row[6] = int(population_estimate)

        uc.updateRow(row)


with arcpy.da.UpdateCursor(urbanized_area_prc_21071, fields) as uc:
    for row in uc:

        oid = row[7]
        print "\nOBJECTID: " + str(oid)

        namelsad = row[1]  # City Name of this polygon
        area_km2 = row[13]  # Area of this polygon
        population_estimate = row[6]  # Population estimate of this polygon

        community_type = row[15]

        population_density = population_estimate / area_km2
        row[12] = population_density  # Population density of this polygon

        # Iterate over the cities surrounding this polygon and total up information about the surrounding cities.
        this_polygon = arcpy.SelectLayerByAttribute_management(urbanized_area_prc_21071_layer, "NEW_SELECTION", "OBJECTID = " + str(row[7]))
        surrounding_cities_layer = arcpy.SelectLayerByLocation_management(urbanized_area_prc_21071_layer, "SHARE_A_LINE_SEGMENT_WITH", this_polygon)

        with arcpy.da.SearchCursor(surrounding_cities_layer, fields) as sc:
            surrounding_city_count = 0
            surrounding_area_total = 0
            surrounding_population_total = 0
            surrounding_population_list = []

            for surrounding_cities_row in sc:
                surrounding_city_oid = surrounding_cities_row[7]
                # If the polygon that shares a line segment with this polygon is not this polygons itself add to the totals.
                if oid != surrounding_city_oid:
                    surrounding_city_count += 1  # Count Surrounding City
                    surrounding_area = surrounding_cities_row[13]  # Area Surrounding City
                    surrounding_area_total += surrounding_area  # Area Surrounding City Total
                    surrounding_city_population = surrounding_cities_row[6]  # Surrounding Population
                    surrounding_population_total += surrounding_city_population  # Surrounding Population Total
                    surrounding_population_list.append(surrounding_city_population)  # List of surrounding population.

            surrounding_population_list_sorted = sorted(surrounding_population_list)

            print " Surrounding City Count:" + str(surrounding_city_count)
            print " Surrounding Population List:" + str(surrounding_population_list_sorted)
            print " Surrounding Population:" + str(surrounding_population_total)
            print " Surrounding Area:" + str(surrounding_area)

        # If there area surrounding cities, populate surrounding city fields. If not, leave NULL <null>.
        row[8] = surrounding_city_count
        if surrounding_city_count > 0:
            row[9] = ",".join(str(i) for i in surrounding_population_list_sorted)
            row[10] = surrounding_population_total
            row[11] = surrounding_area_total
            surrounding_density = surrounding_population_total / surrounding_area_total
            row[14] = surrounding_density

        result = 0

        # Incorporated City
        if community_type == "Incorporated City":
            print "Incorporated City"
            if population_estimate > 100000:
                result = 1

            elif surrounding_city_count != 0:
                # If there is only one surrounding city, get population of surrounding city
                if surrounding_city_count == 1:
                    sum_largest_two_surrounding_populations = surrounding_population_list_sorted[0]

                # If more than one surrounding city, sum the populations of the two largest surrounding cities
                else:
                    sum_largest_two_surrounding_populations = surrounding_population_list_sorted[-1] + surrounding_population_list_sorted[-2]

                # Add the population of the surrounding city or cites to the population of the current city in the cursor
                city_pop_plus_largest_two_surrounding_populations = population_estimate + sum_largest_two_surrounding_populations
                print "City Population including top two surrounding cities: " + str(city_pop_plus_largest_two_surrounding_populations)

                # if the selected city + the two largest surrounding cities  have a population > 100,000, result = 1.
                if city_pop_plus_largest_two_surrounding_populations >= 100000:
                    result = 1

        # Unincorporated
        else:
            print "Unincorporated Island"

            # Add the population of the unincorporated polygon and the population of the surrounding incorporated city or cities.
            unincorporated_pop_plus_surrounding_populations = population_estimate + surrounding_population_total

            # If unincorporated, check to make sure both of the following conditions are met:
            # (i) The population of the unincorporated area and the population of the surrounding incorporated city or cities equals not less than 100,000 persons.
            # (ii) The population density of the unincorporated area at least equals the population density of the surrounding city or cities.

            # Both conditions i and ii must be met.
            if unincorporated_pop_plus_surrounding_populations >= 100000 and population_density >= surrounding_density:
                result = 1

        row[0] = result
        uc.updateRow(row)
