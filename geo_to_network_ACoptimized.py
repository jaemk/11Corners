#!/usr/bin/env python

"""
Convert geojson data (composed of LineString or MultLineString features)
to network graph of feature points and neighbors
"""

import json
import itertools
from collections import defaultdict
from math import sqrt


def load_json_input(data_file_name='psu_roads/AC/ac_geo_coords.json'):
    with open(data_file_name, 'r') as data_file:
        return json.load(data_file)


def write_json_to_file(data, out_file_name='ac_network_geo_coords.json'):
    with open(out_file_name, 'w') as out_file:
        json.dump(data, out_file)


def point_distance(a, b):
    """Euclidean point distance"""
    return sqrt(
                (a[0] - b[0])**2 + (a[1] - b[1])**2
            )


def collect_feature_points(data):
    """
    For each feature,
        - grab all point coords
        - save associated neighbors if multiple points exist
        - record points and neighbors

    return structure
        {
            (1.0, 2.0): [
                # list of neighbors
                {
                    'prev': {
                        'coord': (0.0, 1.0),
                        'dist': 1.0,
                    },
                    'next': {
                        'coord': (3.0, 3.0),
                        'dist': 2.0,
                    },
                },
            ],
            (2.0, 1.0): [
                ...
            ],
        }
    """
    feature_points = defaultdict(list)
    non_line_string_count = 0
    for feature in data['features'].values():
        if feature['geometry']['type'] == 'LineString':
            line_points = feature['geometry']['coordinates']
        else:
            # flatten MultiLineString coordinates so they become a LineString
            # [
            #   [
            #     [1, 2],
            #     [2, 1],
            #   ],
            #   [
            #     [1 ,3],
            #     [3, 1],
            #   ],
            # ]
            # into: [ [1, 2], [2, 1], [1, 3], [3, 1] ]
            coords = feature['geometry']['coordinates']
            line_points = list(itertools.chain(*feature['geometry']['coordinates']))
            non_line_string_count += 1

        n_points = len(line_points)
        for index in range(n_points):
            point   = tuple(line_points[index])
            prev    = tuple(line_points[index-1]) if index > 0 else None
            next_   = tuple(line_points[index+1]) if index < (n_points - 1) else None

            if prev is not None:
                dist = point_distance(point, prev)
                prev = {'coord': prev, 'dist': dist}

            if next_ is not None:
                dist = point_distance(point, next_)
                next_ = {'coord': next_, 'dist': dist}

            neighbors = {'prev': prev, 'next': next_}

            feature_points[point].append(neighbors)

    return feature_points, non_line_string_count


def sanity_check(data):
    big_points = 0
    for key, val in data.items():
        if len(val) > 1:
            big_points += 1
        else:
            print("Found more than 1 set of neighbors for: {}".format(key))

    print("Total points: {}".format(len(data)))
    print("big_points: {}".format(big_points))


def main():
    data = load_json_input()
    print("Number of features in this data set: {}".format(len(data['features'])))
    feature_points, non_line_string_count = collect_feature_points(data)
    print("Number of non-lineString features: {}".format(non_line_string_count))
    sanity_check(feature_points)
    write_json_to_file(feature_points)


if __name__ == '__main__':
    main()

