import csv
import sys
import json
import math
import pandas as pd
import ast
from collections import Counter
from pprint import pprint

def main():
    if len(sys.argv) < 2:
        print("***Usage: python main.py starting-system shopping-cart.csv***")
    filename = sys.argv[2]
    start_point = sys.argv[1]
    desired_components = []
    with open(filename, newline='') as shoppingList:
        reader = csv.DictReader(shoppingList)
        raw_list = list(reader)
        for component in raw_list:
            desired_components.append(component['Name'])

    #open up the csv and go row by row calling filter function dropping None lines then converting the results to a list
    df = pd.read_csv('ShipComponents.csv', header=None)    
    df["parsed"] = df[0].apply(lambda row: parse_and_filter(row, desired_components))
    filtered_df = df.dropna(subset=["parsed"]).reset_index(drop=True)
    result_df = filtered_df["parsed"].tolist()

    possible_locations = {}
    for item in result_df:
        for location in item['locations']:
            segments = location.split('-')
            if ">" in location:
                useful_segment = " - ".join(segments[:2])
            else:
                useful_segment = " - ".join(segments[:3])
            
            if useful_segment not in possible_locations and (useful_segment.upper()).startswith(start_point.upper()):
                possible_locations[useful_segment] = []
            if(useful_segment.upper()).startswith(start_point.upper()):    
                possible_locations[useful_segment].append(item['name'])
 
    best_destinations = []
    shopped_parts = []
    location_with_parts_to_shop = []
    remaining_components = desired_components.copy()
    dest_coords = []
    
    while remaining_components:      
        if len(remaining_components) <= 2:
            #create a flattened list of components in the possible locations dictionary
            all_components = [comp for comps in possible_locations.values() for comp in comps]
            #add counter
            comp_occurances = Counter(all_components)
            #for every component check their count
            for comp,count in comp_occurances.items():
                if comp not in remaining_components:
                    continue
                #if only 1 location add the destination to best_destinations and remove it from the shopping list
                if count == 1:
                    for location, comps in possible_locations.items():
                        if comp in comps:
                            location_with_parts_to_shop.append((location, [comp], get_coords(location, search_term_sanitization(location))))
                            best_destinations.append(location)
                            shopped_parts.append(comp)
                            remaining_components.remove(comp)
                            break
                else:
                #if count > 1 loop through the locations and add their coords to potential stops
                    potential_stops = []
                    for location, comps in possible_locations.items():
                        if comp in comps:
                            search_term = search_term_sanitization(location)
                            result = get_coords(location, search_term)
                            if result is not None:
                                potential_stops.append(result)
                        
                    for dest_name, dest_coord in dest_coords:
                        closest_location, _ = get_distances([(dest_name, dest_coord)], potential_stops)
                        if closest_location:
                            location_with_parts_to_shop.append((closest_location, [comp], get_coords(closest_location, search_term_sanitization(closest_location))))
                            best_destinations.append(closest_location)
                            shopped_parts.append(comp)
                            remaining_components.remove(comp)
                            break
                    
        #for location in best destination add it's coord to destinations list        
        for index, loc in enumerate(best_destinations):
            search_term = search_term_sanitization(loc)
            result = get_coords(loc,search_term)
            if result is not None:
                dest_coords.append(result)
        # Rank locations by how many remaining components they offer
        
        ranked = sorted(
            possible_locations.items(),
            key=lambda item: sum(
                any(part.startswith(comp) for comp in remaining_components)
                for part in item[1]
            ),
            reverse=True
        )
        
        if not ranked or all(
            sum(any(part.startswith(comp) for comp in remaining_components) for part in loc[1]) == 0
            for loc in ranked
        ):
            break  # no further matches can be found
        location_with_parts_to_shop.append((ranked[0][0], ranked[0][1], get_coords(ranked[0][0], search_term_sanitization(ranked[0][0]))))
        best_location, parts_at_location = ranked[0]
        best_destinations.append(best_location)
        for part in parts_at_location:
            for comp in remaining_components[:]:  
                if part.startswith(comp):
                    shopped_parts.append(part)
                    remaining_components.remove(comp)

    
    path = sort_final_locations(location_with_parts_to_shop)
    for stop in path:
        print(stop[0], stop[1])
    

def get_distances(coord_list1, coord_list2):
    closest_pair = (None, float('inf'))
    for destination_name, destination_coord in coord_list1:        
        for potential_stop_name, potential_stop_coord in coord_list2:
            distance = distance_between_stops(destination_coord, potential_stop_coord)
            if distance < closest_pair[1]:
                closest_pair = (potential_stop_name, distance)
    return  closest_pair

def sort_final_locations(final_locations):
    unvisited_locations = final_locations[:]
    path = [unvisited_locations.pop(0)]
    while unvisited_locations:
        current = path[-1][2][1]
        next_point = min(unvisited_locations, key=lambda p: distance_between_stops(current, p[2][1]))
        path.append(next_point)
        unvisited_locations.remove(next_point)
    return path

def parse_and_filter(row, target_names):
    uncaught_qualifiers = ['-','EX', 'SL', 'XL', 'Pro']
    try:
        parsed = ast.literal_eval(row)
        if isinstance(parsed, dict):
            name = parsed.get('name')
            for target in target_names:
                if name.startswith(target) and not any(name[len(target):].startswith(qualifier) for qualifier in uncaught_qualifiers):
                    return parsed
    except Exception:
        return None

def get_coords(loc, search_term):
    with open('LocationData.json') as f:
        data = json.load(f)
        results = [obj for obj in data if obj.get('InternalName').upper().startswith(search_term.upper())]
        if(len(results)==1):
            return (loc, (results[0]["XCoord"], results[0]["YCoord"], results[0]["ZCoord"],))
        elif(len(results)>1):
            new_results = [item for item in results if not item.get('Type').startswith(("Naval", "Asteroid"))]
            return (loc, (new_results[0]["XCoord"], new_results[0]["YCoord"], new_results[0]["ZCoord"],))

def distance_between_stops(p1,p2):
    return math.sqrt(
        (p2[0]-p1[0])**2 +
        (p2[1]-p1[1])**2 +
        (p2[2]-p1[2])**2 
    )

def search_term_sanitization(loc):
    if ">" in loc:
        first_narrow = loc.split('>')
        final_narrow = first_narrow[1].split('-')
        search_term = final_narrow[0].strip().upper()
    else:
        first_narrow = loc.split(" - ")
        if len(first_narrow[1].strip()) == 3:
            search_term = (first_narrow[1]+"-"+first_narrow[2]).strip().upper()
        else:
            search_term = first_narrow[2].strip().upper()
    match search_term:
        case 'ORISON'|'SERAPHIM STATION':
            search_term = 'Stanton2'
        case 'NEW BABBAGE'| 'PORT TRESSLER':
            search_term = 'Stanton4'
        case 'AREA 18'|'BAIJINI POINT':
            search_term = 'Stanton3'
        case 'LORVILLE' | 'EVERUS HARBOR':
            search_term = 'Stanton1'
    return search_term

if __name__ == "__main__":
    main()