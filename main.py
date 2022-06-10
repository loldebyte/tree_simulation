"""
Command line script that simulates hybridation between Mastery Trees.

@author: loldebyte
"""
import mastery_tree
import argparse
import statistics
import pathlib


def get_args():
    """Retrieve command line arguments."""
    parser = argparse.ArgumentParser(
        description="Simulate mastery tree hybridation")
    parser.add_argument("-t", "--trees", choices=["MINLT", "MAXLT", "AVG"],
                        nargs=2, default=["AVG", "AVG"],
                        help="The trees to hybridize. Supported values : "
                        "'MINLT', 'MAXLT' & 'AVG'.")
    parser.add_argument("-p", "--precision",
                        help="How many rolls to simulate.",
                        type=int, default=100000)
    parser.add_argument("-m", "--median", action="store_true",
                        help="Specify to toggle on median # of points"
                        "per tier calculation.")
    parser.add_argument("--minmax", action="store_true",
                        help="Specify to toggle on min/max calculations"
                        "# of points per tier calculation.")
    parser.add_argument("--tiers", action="store_true",
                        help="Specify to calculate percentage of tiers"
                        "exhausted (all points taken in tier), by tier.")
    parser.add_argument("--tree1", type=pathlib.Path,
                        help="The path to the file describing Tree #1\n"
                        "The format is : # of points of tier matching line "
                        "number, ie: on line 1, # of T1 points, on line 2, # "
                        "of T2 points etc..")
    parser.add_argument("--tree2", type=pathlib.Path,
                        help="The path to the file describing Tree #2. For "
                        "the file's format see --tree1")
    args = parser.parse_args()
    return (args.trees, args.precision, args.median, args.minmax, args.tiers,
            args.tree1, args.tree2)


def get_tree_by_argname(name: str) -> mastery_tree.MasteryTree:
    """Return the function that instantiates the correct Mastery Tree."""
    d = {"AVG": mastery_tree.generate_avg_distribution,
         "MINLT": mastery_tree.generate_min_low_tiers,
         "MAXLT": mastery_tree.generate_max_low_tiers}
    return d[name]


def main():
    """Simulates hybridation according to command line arguments."""
    trees, p, med, minmax, tiers, t1, t2 = get_args()
    if t1 is None and t2 is None:
        first_tree_gen = get_tree_by_argname(trees[0])
        second_tree_gen = get_tree_by_argname(trees[1])
    elif t1 is not None and t2 is not None:
        first_tree_gen = mastery_tree.generate_from_file(t1)
        second_tree_gen = mastery_tree.generate_from_file(t2)
    else:
        raise ValueError("A mix of --file1 and -t arguments is not supported. "
                         "Use either of those but not both at the same time.")
    hybrids = [mastery_tree.create_hybrid_tree(first_tree_gen(),
                                               second_tree_gen())
               for _ in range(p)]
    viable = [1 if tree.is_viable() else 0 for tree in hybrids]
    fini = [1 if tree.is_finished() else 0 for tree in hybrids]
    print(f"% viable hybrids : {statistics.mean(viable)*100}%\n"
          f"% finished hybrids : {statistics.mean(fini)*100}%")
    if med:
        tier_lengths = {tier: [tree.get_number_of_points_by_tier(tier)
                               for tree in hybrids]
                        for tier in range(1, 6)}
        print("Median # of points by tier :")
        for tier in range(1, 6):
            print(f"T{tier} : {statistics.median(tier_lengths[tier])}, "
                  f"quartiles : {statistics.quantiles(tier_lengths[tier])}")
    if minmax:
        max_pts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        min_pts = {1: 999, 2: 999, 3: 999, 4: 999, 5: 999}
        for tree in hybrids:
            for tier in range(1, 6):
                nb = tree.get_number_of_points_by_tier(tier)
                if max_pts[tier] < nb:
                    max_pts[tier] = nb
                if min_pts[tier] > nb:
                    min_pts[tier] = nb
        print("maximum # of points by tiers :\n")
        for tier in range(1, 6):
            print(f"T{tier}: {max_pts[tier]}\n")
        print("minimum # of points by tiers :\n")
        for tier in range(1, 6):
            print(f"T{tier}: {min_pts[tier]}\n")
    if tiers:
        print("The tiers option is not currently supported.")


if __name__ == "__main__":
    main()
