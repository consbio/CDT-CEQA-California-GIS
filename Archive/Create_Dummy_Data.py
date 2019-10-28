import arcpy
import random
arcpy.env.overwriteOutput = True

intermediate_ws = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Intermediate.gdb"
parcels_fc = "P:\Projects3\CDT-CEQA_California_2019_mike_gough\Tasks\CEQA_Parcel_Exemptions\Data\Intermediate\Parcels.gdb\sacramento_parcels"

arcpy.env.workspace = intermediate_ws

requirements = [
    # Type of Housing
    "res_or_mixed_25_com", 
    "res_or_mixed", 
    "res", 
    "multifamily",
    # Location Requirements 
    "urbanized_area",
    "urban_area",
    "within_city_limits",
    "unincorporated_urbanized_area",
    # Transit Proximity Requirements
    "within_half_mile_major_transit",
    "within_half_mile_transit_coordior",
    "hundred_percent_affordable",
    "transit_priority_area",
    # Infill Requirements
    "infill",
    "previously_developed_or_75_next_to_urban",
    "qualified_urban_uses",
    # Environmental Limitations 
    "wetlands",
    "riparian_areas",
    "special_habitats",
    "species_of_concern",
    # Hazards
    "sea_level_rise",
    "earthquake_hazard_zone",
    "wildfire_hazard",
    "flood_plain",
    "landslide_hazard",
    # Public Health - CAL EPA
    "rselhaz",
    "pesticide",
    "drinking_water",
    "cleanups",
    "groundwater",
    "hazardous_waste",
    "asthma",
    "historical_resources",
    # General Plan 
    "open_space",
    "agriculture",
]

exemptions = [
    [1, '21159.24', 'Resources Code'],
    [2, '21155.1', 'Resources Code'],
    [3, '21094.5', 'Resources Code'],
    [4, '21155.4', 'Resources Code'],
    [5, '65457', 'Government Code'],
    [6, '15183', 'CEQA Guidelines'],
    [7, '15332', 'CEQA Guidelines'],
    [8, '21159.25', 'Resources Code'],
    [9, '15303', 'CEQA Guidelines'],
    [10, '20181.3', 'Resources Code'],
    [11, '21099', 'Resources Code'],
    [12, '21155.2', 'Resources Code'],
    [13, '21155.3', 'Resources Code'],
    [14, '21159.22', 'Resources Code'],
    [15, '21159.23', 'Resources Code'],
    [16, '21159.28', 'Resources Code'],
]

def create_tables():

    arcpy.CreateTable_management(intermediate_ws, "parcel_exemptions")
    arcpy.AddField_management("parcel_exemptions", "parcel_id", "TEXT")
    arcpy.AddField_management("parcel_exemptions", "exemption_id", "TEXT")

    arcpy.CreateTable_management(intermediate_ws, "exemptions")
    arcpy.AddField_management("exemptions", "exemption_id", "SHORT")
    arcpy.AddField_management("exemptions", "exemption_code", "TEXT")
    arcpy.AddField_management("exemptions", "exemption_source", "TEXT")

    for requirement in requirements:
        arcpy.AddField_management(parcels_fc, requirement, "SHORT")

    arcpy.AddField_management(parcels_fc, "exemptions_count", "SHORT")
    
    
def populate_exemptions_table():

    ic = arcpy.da.InsertCursor("exemptions", ["exemption_id", "exemption_code", "exemption_source"])

    for item in exemptions:
        print item
        ic.insertRow(item)


def calculate_parcel_requirements():

    uc = arcpy.da.UpdateCursor(parcels_fc, "*")
    
    fieldnames = []
    fields = arcpy.ListFields(parcels_fc)
    for field in fields:
        fieldnames.append(field.name)

    for row in uc:
        zoning = row[fieldnames.index("Zoning")]
        if not zoning:
            zoning = ""
        
        # Res or Mixed Use (up to 25%?)
        if "R" in zoning or "MIXED" in zoning:
            row[fieldnames.index('res_or_mixed_25')] = 1
        else:
            row[fieldnames.index('res_or_mixed_25')] = 0
            
        # Res or Mixed Use    
        if "R" in zoning or "MIXED" in zoning:
            row[fieldnames.index('res_or_mixed')] = 1
        else:
            row[fieldnames.index('res_or_mixed')] = 0
            
        # Res 
        if "R" in zoning:
            row[fieldnames.index('res')] = 1
        else:
            row[fieldnames.index('res')] = 0

        # Multifamily
        if "R2" in zoning:
            row[fieldnames.index('multifamily')] = 1
        else:
            row[fieldnames.index('multifamily')] = 0

        # Replace random number assignment with geoprocessing steps
        for requirement in requirements: 
            if requirement not in ['res_or_mixed_25', 'res_or_mixed', 'res', 'multifamily']:
                rand = random.randint(0, 1)
                if rand:
                    row[fieldnames.index(requirement)] = 1
                else:
                    row[fieldnames.index(requirement)] = 0

        uc.updateRow(row)
            
def calculate_parcel_exemptions():
    
    sc = arcpy.SearchCursor(parcels_fc)

    requirement_dict = {}
    exemptions_dict = {}
    
    for row in sc:
        
        if all([row.getValue('res_or_mixed_25_com'),
               row.getValue('urbanized_area'),
               row.getValue('within_half_mile_major_transit'),
               row.getValue('infill'),
               # Environmental Limitations
               row.getValue('wetlands'),
               row.getValue('riparian_areas'),
               row.getValue('special_habitats'),
               row.getValue('species_of_concern'),
               # Hazards
               row.getValue('sea_level_rise'),
               row.getValue('earthquake_hazard_zone'),
               row.getValue('wildfire_hazard'),
               row.getValue('flood_plain'),
               row.getValue('landslide_hazard'),
                # Public Health - CAL EPA
               row.getValue('rselhaz'),
               row.getValue('pesticide'),
               row.getValue('drinking_water'),
               row.getValue('cleanups'),
               row.getValue('groundwater'),
               row.getValue('hazardous_waste'),
               row.getValue('asthma'),
               row.getValue('historical_resources'),
                # General Plan 
               row.getValue('open_space'),
               row.getValue('agriculture')]): exemptions_dict['parcel_id'] = '21159.24'
        
        if all([row.getValue('res_or_mixed'),
                row.getValue('urbanized_area'),
                (row.getValue('within_half_mile_major_transit') or row.getValue('within_half_mile_transit_coordior')),
                # Environmental Limitations
                row.getValue('wetlands'),
                row.getValue('riparian_areas'),
                row.getValue('special_habitats'),
                row.getValue('species_of_concern'),
                # Hazards
                row.getValue('sea_level_rise'),
                row.getValue('earthquake_hazard_zone'),
                row.getValue('wildfire_hazard'),
                row.getValue('flood_plain'),
                row.getValue('landslide_hazard'),
                # Public Health - CAL EPA
                row.getValue('rselhaz'),
                row.getValue('pesticide'),
                row.getValue('drinking_water'),
                row.getValue('cleanups'),
                row.getValue('groundwater'),
                row.getValue('hazardous_waste'),
                row.getValue('asthma'),
                row.getValue('historical_resources'),
                # General Plan 
                row.getValue('open_space'),
                row.getValue('agriculture')]): exemptions_dict['parcel_id'] = '21159.24' 
    
        ic = arcpy.da.InsertCursor("parcel_exemptions", ['parcel_id', 'exemptions_id']) 
        
        for k, v in exemptions_dict.iteritems():
            ic.insert([k, v])

create_tables()
populate_exemptions_table()
calculate_parcel_requirements()
calculate_parcel_exemptions()

