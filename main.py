#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 29 23:20:55 2022

@author: loldebyte
"""
import mastery_tree
import argparse
import statistics


def get_args():
    parser = argparse.ArgumentParser(description="Simulate mastery tree hybridation")
    parser.add_argument("-t", "--trees", choices=["MINLT", "MAXLT", "AVG"], nargs=2, default=["AVG", "AVG"],
                        help="The trees to hybridize. Supported values : 'MINLT', 'MAXLT' & 'AVG'.")
    parser.add_argument("-p", "--precision", help="How many rolls to simulate.",
                        type=int, default=100000)
    parser.add_argument("-m", "--median", action="store_true", help="Specify to toggle on median # of points"
                        "per tier calculation.")
    parser.add_argument("--minmax", action="store_true", help="Specify to toggle on min/max calculations"
                        "# of points per tier calculation.")
    parser.add_argument("--tiers", action="store_true", help="Specify to calculate percentage of tiers"
                        "exhausted (all points taken in tier), by tier.")
    args = parser.parse_args()
    return  args.trees, args.precision, args.median, args.minmax, args.tiers


def get_tree_by_argname(name: str) -> mastery_tree.MasteryTree:
    d = {"AVG": mastery_tree.generate_avg_distribution,
         "MINLT": mastery_tree.generate_min_low_tiers,
         "MAXLT": mastery_tree.generate_max_low_tiers}
    return d[name]


def main():
    trees, p, med, minmax, tiers = get_args()
    first_tree_gen = get_tree_by_argname(trees[0])
    second_tree_gen = get_tree_by_argname(trees[1])
    hybrids = [mastery_tree.create_hybrid_tree(first_tree_gen(), second_tree_gen()) for _ in range(p)]
    viable = [1 if tree.is_viable() else 0 for tree in hybrids]
    fini = [1 if tree.is_finished() else 0 for tree in hybrids]
    print(f"% viable hybrids : {statistics.mean(viable)*100}%\n"
          f"% finished hybrids : {statistics.mean(fini)*100}%")
    if med:
        tier_lengths = {tier: [tree.get_number_of_points_by_tier(tier) for tree in hybrids]
                        for tier in range(1, 6)}
        print("Median # of points by tier :")
        for tier in range(1, 6):
            print(f"T{tier} : {statistics.median(tier_lengths[tier])}, "
                  f"quartiles : {statistics.quantiles(tier_lengths[tier])}")
    if minmax:
        max_pts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        min_pts = {1: 10, 2: 10, 3: 10, 4: 10, 5: 10}
        for tree in hybrids:
            for tier in range(1, 6):
                if max_pts[tier] < tree.get_number_of_points_by_tier(tier):
                    max_pts[tier] = tree.get_number_of_points_by_tier(tier)
                if min_pts[tier] > tree.get_number_of_points_by_tier(tier):
                    min_pts[tier] = tree.get_number_of_points_by_tier(tier)
        print("maximum # of points by tiers :\n")
        for tier in range(1, 6):
            print(f"T{tier}: {max_pts[1]}\n")
        print("minimum # of points by tiers :\n")
        for tier in range(1, 6):
            print(f"T{tier}: {min_pts[1]}\n")
    if tiers:
        print("The tiers option is not currently supported.")

if __name__ == "__main__":
    main()