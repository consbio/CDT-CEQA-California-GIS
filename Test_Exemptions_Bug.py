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

requirements_to_skip = [2.6, 3.3, 3.7, 8.4, 9.1, 4.2, 3.4]

for k, v in exemptions.items():

    new_e_list = []

    #exemption list
    for e in v[2]:

        if isinstance(e, list):
            new_sub_e_list = []
            for sub_e in e:
                if sub_e not in requirements_to_skip:
                    new_sub_e_list.append(sub_e)
            new_e_list.append(new_sub_e_list)

        elif e not in requirements_to_skip:
            new_e_list.append(e)

        v[2] = new_e_list

print exemptions[5]
