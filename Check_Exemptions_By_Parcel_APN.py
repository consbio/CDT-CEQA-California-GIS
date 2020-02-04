import arcpy

parcels_fc = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs_for_DataBasin.gdb\sacramento_parcels_requirements'
parcel_exemptions_table = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs_for_DevTeam.gdb\parcel_exemptions'
exemptions_table = r'P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Outputs\Outputs_for_DevTeam.gdb\exemptions'

TAXAPNs = {
    '006-0224-025-0000': ['65457'],
    '007-0012-011-0000': ['21155.2'],
    '277-0134-003-0000': ['65457', '21155.4'],
    '277-0134-004-0000': ['65457', '21155.4'],
    '277-0134-005-0000': ['65457', '21155.4'],
    '007-0103-001-0000': ['21155.2'], # 2500 J Street
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

exemptions = {
    '21159.24': [2.1, 3.1, 8.1, 8.2, 8.3, 8.4, 9.2, 9.3, 9.4, 9.5, 9.6],
    '21155.1': [2.5, [3.2, 3.4, 8.1, 8.2, 8.3, 8.4, 9.2, 9.3, 9.4, 9.5]],
    '21155.2': [2.5],
    '21155.4': [2.5, 2.6, 3.3],
    '21094.5': [2.2, 2.6, [3.1, 3.4, 3.5, 3.8, 4.2]],
    '65457': [2.6, 8.1, 8.2, 8.3, 8.4, 9.2, 9.3, 9.4, 9.5],
    '15183':  [],
    '15332':  [2.3],
    '21159.25': [2.4],
    '15303': [2.1],
    '21099': [3.3],
    '21155.2': [2.5, [3.1, 3.5]],
    #13: ['21159.23': [],
    '21159.28': [2.5],
    '15064.3':  [3.1, 3.5, 3.6, 3.7]
}

results_dict = {}

apn_lookup_dict = {}
exemption_lookup_dict = {}


PARCEL_IDs = []

APN_expression = "TAXAPN in (" + ','.join("'{0}'".format(APN) for APN in TAXAPNs.keys()) + ")"
with arcpy.da.SearchCursor(parcels_fc, ['TAXAPN', 'PARCEL_ID'], APN_expression) as sc:
    for row in sc:
        parcel_id = row[1]
        apn = row[0]
        if parcel_id not in apn_lookup_dict:
            apn_lookup_dict[parcel_id] = apn
        PARCEL_IDs.append(row[1])

# Exemptions
with arcpy.da.SearchCursor(exemptions_table, ['exemption_id', 'exemption_code']) as sc:

    for row in sc:
        exemption_id = row[0]
        exemption_code = row[1]
        exemption_lookup_dict[exemption_id] = exemption_code


# Parcel Exemptions
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

#for k, v in results_dict.iteritems():
#    print "\n" + k + ":"
#    for code in v:
#        print "\t" + code

for k, v in TAXAPNs.iteritems():
    apn = k
    for exemption_check in v:
        if exemption_check in results_dict[apn]:
            print apn + " " + exemption_check + "(PASSED)"
        else:
            print apn + " " + exemption_check + "(FAILED)"
            print [requirement for requirement in exemptions[exemption_check]]



#sc = arcpy.da.SearchCursor(requirements_table, ['parcel_id, exemption_id'])









