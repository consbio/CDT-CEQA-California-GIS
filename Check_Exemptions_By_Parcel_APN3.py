import arcpy

parcels_fc = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs_for_DataBasin.gdb\sacramento_parcels_requirements'
parcel_exemptions_table = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs_for_DevTeam.gdb\parcel_exemptions'
exemptions_table = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs_for_DevTeam.gdb\exemptions'

#parcels_fc = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Test\Outputs_Check_Exemptions_For_DataBasin.gdb\parcels_to_test_with_requirements'
#parcel_exemptions_table = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Test\Outputs_Check_Exemptions_For_DevTeam.gdb\parcel_exemptions'
#exemptions_table = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Test\Outputs_Check_Exemptions_For_DevTeam.gdb\exemptions'

# The APNs and Exemptions to Test.
TAXAPNs = {
    '006-0224-025-0000': ['65457'],
    '007-0012-011-0000': ['21155.2'],
    '277-0134-003-0000': ['65457', '21155.4'],
    '277-0134-004-0000': ['65457', '21155.4'],
    '277-0134-005-0000': ['65457', '21155.4'],
    '007-0103-001-0000': ['21155.2'],
    '277-0160-002-0000': ['21094.5'],
    '277-0160-003-0000': ['21094.5'],
    '277-0160-021-0000': ['21094.5'],
    '277-0160-033-0000': ['21094.5'],
    '277-0160-040-0000': ['21094.5'],
    '277-0160-073-0000': ['21094.5'],
    '277-0160-074-0000': ['21094.5'],
    '277-0261-011-0000': ['21094.5'],
    '277-0261-031-0000': ['21094.5'],
    '277-0261-039-0000': ['21094.5'],
    '277-0261-040-0000': ['21094.5'],
    '277-0261-042-0000': ['21094.5'],
}

#TAXAPNs = {'277-0134-004-0000': ['65457', '21155.4']}

requirements = {
    # Location Requirements
    2.1: "urbanized_area_prc_21071_2_1",
    2.2: "urban_area_prc_21094_2_2",
    2.3: "within_city_limits_2_3",
    2.4: "unincorporated_urbanized_area_2_4",
    2.5: "within_mpo_2_5",
    2.6: "covered_by_a_specific_plan_2_6",
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


exemptions = {
    1: ['21159.24', 'Resources Code', [2.1, 3.1, 8.1, 8.2, 8.3, 8.4, 9.2, 9.3, 9.4, 9.5, 9.6]],
    2: ['21155.1', 'Resources Code', [2.5, [3.2, 3.4], 8.1, 8.2, 8.3, 8.4, 9.2, 9.3, 9.4, 9.5]],
    3: ['21155.2', 'Resources Code', [2.5]],
    4: ['21155.4', 'Resources Code', [2.5, 2.6, 3.3]],
    5: ['21094.5', 'Resources Code', [2.2, 2.6, [3.1, 3.4, 3.5, 3.8], 4.2]],
    6: ['65457', 'Government Code', [2.6, 8.1, 8.2, 8.3, 8.4, 9.2, 9.3, 9.4, 9.5]],
    #7: ['15183', 'CEQA Guidelines', []],
    8: ['15332', 'CEQA Guidelines', [2.3]],
    9: ['21159.25', 'Resources Code', [2.4]],
    10: ['15303', 'CEQA Guidelines', [2.1]],
    11: ['21099', 'Resources Code', [3.3]],
    12: ['21155.2', 'Resources Code', [2.5, [3.1, 3.5]]],
    #13: ['21159.23', 'Resources Code', []],
    14: ['21159.28', 'Resources Code', [2.5]],
    15: ['15064.3', 'CEQA Guidelines', [3.1, 3.5, 3.6, 3.7]]
}

# Reverse the requirements dictionary to create a dictionary of requirements: code
requirements_reverse_dict = dict([(value, key) for key, value in requirements.items()])

results_dict = {}
apn_lookup_dict = {}
exemption_lookup_dict = {}
parcel_apn_requirement_dict = {}

# Create a list of the needed fields in the parcels feature class
requirement_fields = [field for field in requirements.values()]
fields_in_parcels = [field.name for field in arcpy.ListFields(parcels_fc)]
parcel_fields_to_use = ['TAXAPN', 'PARCEL_ID']
for requirement_field in requirement_fields:
    if requirement_field in fields_in_parcels:
        parcel_fields_to_use.append(requirement_field)

APN_expression = "TAXAPN in (" + ','.join("'{0}'".format(APN) for APN in TAXAPNs.keys()) + ")"

#APN_expression = "TAXAPN in ('277-0134-004-0000')"

PARCEL_IDs = []

# Build a dictionary consisting of the APN and the requirements 0 or 1
with arcpy.da.SearchCursor(parcels_fc, parcel_fields_to_use, APN_expression) as sc:
    for row in sc:
        parcel_id = row[1]
        apn = row[0]
        if parcel_id not in apn_lookup_dict:
            apn_lookup_dict[parcel_id] = apn
        PARCEL_IDs.append(row[1])

        requirement_dict = {}
        #print sc.fields
        #print row

        # Create a dictionary of {2.6:0, 2.4: 1]
        requirement_dict = {requirements_reverse_dict[k]: v for k, v in zip(sc.fields, row) if k not in ['TAXAPN', 'PARCEL_ID']}

        parcel_apn_requirement_dict[apn] = requirement_dict

# Exemptions
with arcpy.da.SearchCursor(exemptions_table, ['exemption_id', 'exemption_code']) as sc:

    for row in sc:
        exemption_id = row[0]
        exemption_code = row[1]
        exemption_lookup_dict[exemption_id] = exemption_code


# Create a search cursor on the parcel exemptions table using just the parcels in the parcel list to check.
ID_expression = "parcel_id in (" + ','.join("'{0}'".format(parcel_id) for parcel_id in PARCEL_IDs) + ")"
with arcpy.da.SearchCursor(parcel_exemptions_table, ['parcel_id', 'exemption_id'], ID_expression) as sc:
    for row in sc:
        parcel_id = row[0]
        exemption_id = row[1]

        apn = apn_lookup_dict[parcel_id]
        if apn not in results_dict:
            results_dict[apn] = []

        exemption_id = exemption_lookup_dict[exemption_id]

        if exemption_id in TAXAPNs[apn]:
            results_dict[apn].append(str(exemption_id))

        else:
            results_dict[apn].append(str(exemption_id))

for k, v in TAXAPNs.iteritems():
    apn = k
    exemption_list_to_check = v

    for exemption_check in exemption_list_to_check:

        #print "Requirements " + str(requirement_list_for_this_exemption)
        #print "Requirements: " + str(requirements)
        #print results_dict[apn]
        if exemption_check in results_dict[apn]:
            print apn + ", " + exemption_check + ", PASSED"
        else:

            failed_message = apn + ", " + exemption_check + ", FAILED ("

            # Which requirements did this apn fail?

            this_parcel_requirement_dict = parcel_apn_requirement_dict[apn]

            # Get the list of requirements for this exemption that we're checking
            requirement_list_for_this_exemption = [i[2] for i in exemptions.values() if exemption_check == i[0]]

           # print this_parcel_requirement_dict
            #print requirement_list_for_this_exemption


            for k, v in this_parcel_requirement_dict.iteritems():
                if v == 0 and k in requirement_list_for_this_exemption[0]:
                    failed_message += str(k)
                    failed_message += ": " + requirements[k]

            failed_message += ")"

            print failed_message


