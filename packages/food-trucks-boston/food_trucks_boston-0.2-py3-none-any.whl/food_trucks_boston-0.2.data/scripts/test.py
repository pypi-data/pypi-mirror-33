#!python
import json
from jsonpath_ng import jsonpath, parse
import click
from esridump.dumper import EsriDumper
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import numpy as np
from prettytable import PrettyTable

THRESH = 73

@click.command()
@click.option('--day', default='', help='Choose day of week')
@click.option('--truck', default='', help='Truck to find Schedule of')
@click.option('--loc', default='', help='Location to search')


def day_schedule(day, truck, loc):
    x = PrettyTable()
    x.field_names = ["Truck", "Day", "Location"]
    
    d = EsriDumper('https://services.arcgis.com/sFnw0xNflSi8J0uh/arcgis/rest/services/food_trucks_schedule/FeatureServer/0')

    all_features = list(d)
    if day != '':
        day_dict = [1 if fuzz.partial_ratio(x["properties"]["Day"], day) > THRESH else 0 for x in all_features]
    else:
        day_dict = [1 for x in all_features]
    if truck != '':
        truck_dict = [1 if fuzz.partial_ratio(x["properties"]["Truck"], truck) > THRESH else 0 for x in all_features]
    else:
        truck_dict = [1 for x in all_features]
    if loc != '':
        loc_dict = [1 if fuzz.partial_ratio(x["properties"]["Loc"], loc) > THRESH else 0 for x in all_features]
    else:
        loc_dict = [1 for x in all_features]

    # Iterate over each feature

    selections = np.array(day_dict) & np.array(truck_dict) & np.array(loc_dict)
    for (feature, flag) in zip(all_features, selections):
    #    print(fuzz.partial_ratio(feature["properties"]["Loc"], loc))
        if flag:
#            print(feature["properties"]["Truck"]+ ":" + feature["properties"]['Loc'] + ":" + feature['properties']['Day'])
            x.add_row([feature["properties"]["Truck"], feature["properties"]["Day"], feature["properties"]["Loc"]])
    print(x)
        


if __name__ == '__main__':
    day_schedule()
