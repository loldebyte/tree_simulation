"""Mastery Point and Mastery Tree definitions & utils."""
from __future__ import annotations
from typing import Dict, List, Optional, Callable
import string
import random
import os


class MasteryPoint:
    """
    Class that represents a single mastery point.

    Attributes
    ----------
    name : str
        The name of the mastery point.
    tier : int
        The tier of the mastery point.
    dependee : Optional[MasteryPoint], optional
        The point that this point depends on. The default is None.
    dependers : Optional[List[MasteryPoint]], optional
        The list of point that depends on this point. The default is None.

    Methods
    -------
    is_standalone()
        True if the point is unrelated to any other points.
    get_dependers()
        Returns the dependers attribute.
    is_root()
        True if point has no dependee.
    """

    def __init__(self, name: str, tier: int,
                 dependee: Optional[MasteryPoint] = None,
                 dependers: Optional[List[MasteryPoint]] = None):
        self.name = name
        self.tier = tier
        self.dependee = dependee
        self.dependers = dependers

    def __str__(self):
        """
        Return the string representation of the mastery point.

        Returns
        -------
        str
            The name of the mastery point.
        """
        return self.name

    def is_standalone(self) -> bool:
        """
        Return True if the point is unrelated to any other points.

        Returns
        -------
        bool
            Whether the point is unrelated to any others or not.
        """
        return self.dependers is None and self.dependee is None

    def get_dependers(self) -> List[MasteryPoint]:
        """
        Dependers getter.

        Returns
        -------
        List[MasteryPoint]
            The dependers attribute of the mastery point.

        """
        return self.dependers

    def is_root(self) -> bool:
        """
        Return True if the point has no dependee.

        Returns
        -------
        bool
            Whether the point has a dependee or not.
        """
        return self.dependee is None


class MasteryTree:
    """
    Class that represents Mastery Trees.

    Attributes
    ----------
    species: str
        The name of the species this tree corresponds to. Acts as a tree name.
    points : [Dict[int, List[MasteryPoint]]
        The points of the tree, stored in a {tier: [list_of_points]} fashion.

    Methods
    -------
    get_current_value()
        return the tree's current tree value.
    get_available_space()
        return how much tree value is left for new points.
    is_finished()
        return whether the tree is finished or not.
    add_point(tier, point)
        add mastery point _point_ to the tree at tier _tier_.
    get_total_number_of_points()
        return the number of points in the tree
    get_min_tier_available()
        return the lowest non-empty tier's value.
    fuse(mastery_tree)
        return a new tree with all points from both self & argument trees.
    contains(point)
        return True if _point_ is present in the tree, False otherwise.
    """

    def __init__(self, species: str,
                 mastery_points: Optional[Dict[int,
                                               List[MasteryPoint]]] = None,
                 maximum_tree_value: int = 47):
        self.species = species
        self.maximum_tree_value = maximum_tree_value
        if mastery_points is None:
            self.points = {1: [], 2: [], 3: [], 4: [], 5: []}
        else:
            self.points = mastery_points

    def __str__(self) -> str:
        """
        Return the string representation of the mastery tree.

        Returns
        -------
        str
            The string rep. of a dictionnary mapping {tiers: [str(points)]}.
        """
        return str({key: [str(_) for _ in value]
                    for key, value in self.points.items()})

    def get_tier_value(self, tier: int) -> int:
        """
        Return the tree value of points of a specific tier.

        Parameters
        ----------
        tier : int
            The tier whose value to calculate.

        Returns
        -------
        int
            The tree value of points of tier _tier_.
        """
        return len(self.points[tier]) * tier

    def get_cumulative_tier_value(self, tier: int) -> int:
        """
        Return the tree value of points in all tiers up to _tier_, inclusive.

        Parameters
        ----------
        tier : int
            The highest tier to include.

        Raises
        ------
        ValueError
            Raises if the tier argument is a not a tier value (1-5 inclusive).

        Returns
        -------
        int
            The tree value of all points in tiers up to _tier_.
        """
        if tier < 1 or tier > 5:
            raise ValueError(f"Value '{tier}' is not a tier.")
        val = 0
        for k in range(1, tier + 1):
            val += self.get_tier_value(k)
        return val

    def is_viable(self) -> bool:
        """
        Return True if all points in tree are accessible.

        T1 points are always accessible.
        T2 points are accessible if there is at least 1 T1 point.
        T3 points are accessible if there are at least 3 T<=2 points.
        T4 points are accessible if there are at least 6 T<=3 points.
        T5 points are accessible if there are at least 10 T<=4 points.

        Returns
        -------
        bool
            Whether all points are accessible or not.
        """
        return ((self.get_cumulative_tier_value(1) >= 1)
                & (self.get_cumulative_tier_value(2) >= 3)
                & (self.get_cumulative_tier_value(3) >= 6)
                & (self.get_cumulative_tier_value(4) >= 10))

    def get_current_value(self) -> int:
        """
        Return the current tree value.

        Tree value is capped by VALEUR_TOTALE.
        A tree is completed once its tree value reaches VALEUR_TOTALE.
        Every point counts for its tier, e.g every T1 point is worth 1,
        every T2, 2 etc...

        Returns
        -------
        int
            The tree's current tree value.
        """
        return self.get_cumulative_tier_value(5)

    def get_available_space(self) -> int:
        """
        Return the tree value available for new points.

        Since tree value is capped at VALEUR_TOTALE, the tree value available
        is VALEUR_TOTALE - current tree value.

        Returns
        -------
        int
            The current tree value available for new points.
        """
        return self.maximum_tree_value - self.get_current_value()

    def is_complete(self) -> bool:
        """
        Return True if current tree value is exactly VALEUR_TOTALE.

        Returns
        -------
        bool
            Whether the current tree value matches VALEUR_TOTALE or not.
        """
        return self.get_current_value() == self.maximum_tree_value

    def is_finished(self) -> bool:
        """
        Return True if the tree is finished.

        A tree is finished if all points in the tree are available and the
        current tree value matches VALEUR_TOTALE.

        Returns
        -------
        bool
            Whether the tree is finished or not.
        """
        return self.is_viable() & self.is_complete()

    def add_point(self, point: MasteryPoint):
        """
        Add a point to the tree.

        Parameters
        ----------
        point : MasteryPoint
            The point to add.

        Raises
        ------
        ValueError
            Raises if the point's value would make the tree's tree value exceed
            VALEUR_TOTALE.

        Returns
        -------
        None.
        """
        if self.get_current_value() + point.tier <= self.maximum_tree_value:
            self.points[point.tier].append(point)
        else:
            raise ValueError(
                f"Unable to add point of value {point.tier} : current "
                f"capacity is at {self.get_current_value()}")

    def get_number_of_points_by_tier(self, tier: int) -> int:
        """
        Return the number of points in tier _tier_.

        Parameters
        ----------
        tier : int
            The tier whose number of points is searched.

        Returns
        -------
        int
            The number of points of tier _tier_.

        """
        return len(self.points[tier])

    def get_total_number_of_points(self) -> int:
        """
        Return the number of points in the tree.

        Returns
        -------
        int
            The total number of points in the whole tree.
        """
        val = 0
        for _ in self.points.values():
            val += len(_)
        return val

    def get_min_tier_available(self) -> Optional[int]:
        """
        Return the lowest tier containing at least 1 point.

        Returns
        -------
        Optional[int]
            The lowest tier containing at least a point as int, or None if the
            tree contains no points.
        """
        for tier in range(1, 6):
            if self.get_tier_value(tier) > 0:
                return tier
        return None

    def fuse(self, mastery_tree: MasteryTree) -> MasteryTree:
        """
        Return a new tree with all points from both trees.

        Parameters
        ----------
        mastery_tree : MasteryTree
            The tree whose point to add to the current tree's points.

        Returns
        -------
        MasteryTree
            A new tree with all points from both trees.

        """
        if self.maximum_tree_value == mastery_tree.maximum_tree_value:
            return MasteryTree(f"fuse {self.species} & {mastery_tree.species}",
                               {key: self.points[key].copy()
                                + mastery_tree.points[key].copy()
                                for key in range(1, 6)},
                               self.maximum_tree_value)
        else:
            raise ValueError(f"Trees {self.species} and {mastery_tree.species}"
                             " have different maximum tree values !")

    def contains(self, point: MasteryPoint) -> bool:
        """
        Return True if the passed point exists in the tree.

        Parameters
        ----------
        point : MasteryPoint
            The point to search for.

        Returns
        -------
        bool
            True if the point is in the tree, else False.
        """
        if point in self.points[point.tier]:
            return True
        else:
            return False

    def get_random_by_tier(self, tier: int) -> MasteryPoint:
        """
        Return a random point of specified tier from the tree.

        Parameters
        ----------
        tier : int
            The tier from which to pick.

        Returns
        -------
        MasteryPoint
            The chosen point.
        """
        return random.choice(self.points[tier])


def create_random_mp(tier: int, prefix: str = "") -> MasteryPoint:
    """
    Create a new randomized mastery point of specified tier.

    Parameters
    ----------
    tier : int
        The tier of the point to create.
    prefix : str, optional
        The string to add before each mastery point's name. The default is "".

    Returns
    -------
    MasteryPoint
        The newly create mastery point.

    """
    return MasteryPoint(prefix
                        + ''.join(random.choices(string.ascii_letters, k=6)),
                        tier=tier)


def create_list_of_random_mp(tier: int, n: int, prefix: str = ""):
    """
    Create a new list of specifiec length of random points of specified tier.

    Parameters
    ----------
    tier : int
        The tier of points to create.
    n : int
        The number of points to create.
    prefix: str, optional
        The string to add before each mastery point's name. The default is "".

    Returns
    -------
    list
        DESCRIPTION.

    """
    return [create_random_mp(tier, f"{prefix}_t{tier}_{nb}_")
            for nb in range(n)]


def evenly_fill_tree(mt: MasteryTree) -> MasteryTree:
    """
    Fill a tree with points until its tree_value matches _tree_value_.

    Adds 1 point of every tier successively, starting from the heavier tier.

    Parameters
    ----------
    mt : MasteryTree
        The tree to fill with new points.

    Returns
    -------
    MasteryTree
        The filled tree.

    """
    while mt.get_current_value() < mt.maximum_tree_value:
        for tier in range(5, 0, -1):
            if mt.get_available_space() >= tier:
                mt.add_point(create_random_mp(tier, f"t{tier}"))
    return mt


def heavy_fill_tree(mt: MasteryTree) -> MasteryTree:
    """
    Fill a tree with points until its tree_value matches _tree_value_.

    Adds as many points of the heaviest tiers as possible.

    Parameters
    ----------
    mt : MasteryTree
        The tree to fill with new points.

    Returns
    -------
    MasteryTree
        The filled tree.

    """
    for tier in range(5, 0, -1):
        while mt.maximum_tree_value - mt.get_current_value() > tier:
            mt.add_point(create_random_mp(tier, f"t{tier}"))
    return mt


def light_fill_tree(mt: MasteryTree) -> MasteryTree:
    """
    Fill a tree with points until its tree_value matches _tree_value_.

    Adds as many points of tier 1 as possible.

    Parameters
    ----------
    mt : MasteryTree
        The tree to fill with new points.

    Returns
    -------
    MasteryTree
        The filled tree.

    """
    while mt.get_current_value() < mt.maximum_tree_value:
        mt.add_point(create_random_mp(1, "t1"))
    return mt


def generate_heavy_viable(name, tree_value=47) -> MasteryTree:
    """
    Return a new incomplete tree that is viable and has many high tier points.

    Parameters
    ----------
    name : str
        the name of the tree.

    tree_value: int
        the maximum tree value of the tree

    Returns
    -------
    MasteryTree
        The newly created tree.
    """
    return MasteryTree(name, {1: create_list_of_random_mp(1, 1, name),
                              2: create_list_of_random_mp(2, 2, name),
                              3: create_list_of_random_mp(3, 3, name),
                              4: create_list_of_random_mp(4, 4, name),
                              5: create_list_of_random_mp(5, 1, name)})


def generate_light_viable(name, tree_value=47) -> MasteryTree:
    """
    Return a new incomplete tree that is viable and has few high tier points.

    Parameters
    ----------
    name : TYPE
        the name of the tree.

    tree_value: int
        the maximum tree value of the tree

    Returns
    -------
    MasteryTree
        The newly created tree.
    """
    return MasteryTree(name, {1: create_list_of_random_mp(1, 4, name),
                              2: create_list_of_random_mp(2, 3, name),
                              3: create_list_of_random_mp(3, 2, name),
                              4: create_list_of_random_mp(4, 1, name),
                              5: create_list_of_random_mp(5, 1, name)})


def generate_min_low_tiers(tree_value: int) -> Callable:
    """
    Return a function that returns a new Mastery tree with few low tier points.

    The new tree's tree_value is _tree_value_.

    Parameters
    ----------
    tree_value : int
        The tree value the generated tree must reach.

    Returns
    -------
    Callable
        A function that instantiates random such trees.
    """

    def mlt_from_tree_value():
        return heavy_fill_tree(generate_heavy_viable("MINLT", tree_value))
    return mlt_from_tree_value


def generate_max_low_tiers(tree_value: int) -> Callable:
    """
    Return a function that creates a mastery tree with many low tier points.

    The new tree's tree_value is _tree_value_.

    Parameters
    ----------
    tree_value : int
        The tree value the generated tree must reach.

    Returns
    -------
    Callable
        A function that instantiates random such trees.
    """
    def maxlt_from_tree_value():
        return light_fill_tree(generate_light_viable("MAXLT", tree_value))
    return maxlt_from_tree_value


def generate_avg(tree_value: int) -> Callable:
    """
    Return a function that creates a mastery tree with avg low tier points.

    The new tree's tree_value is _tree_value_.

    Parameters
    ----------
    tree_value : int
        The tree value the generated tree must reach.

    Returns
    -------
    Callable
        A function that instantiates random such trees.
    """
    def avglt_from_tree_value():
        return evenly_fill_tree(generate_light_viable("AVG", tree_value))
    return avglt_from_tree_value


def generate_from_dict(dic: Dict[int, int], name: str) -> MasteryTree:
    """
    Return a new tree from a {tier: number_of_points} dictionnary.

    Parameters
    ----------
    dic : Dict[int, int]
        A dictionnary mapping tiers to the number of points in that tier.
    name : str
        The name of the new tree.

    Returns
    -------
    MasteryTree
        The newly created tree.

    """
    return MasteryTree(name,
                       {tier: create_list_of_random_mp(tier, value)
                        for tier, value in dic.items()},
                       sum([tier*n_pts for tier, n_pts in dic.items()]))


def get_smallest_free_tier(tree: MasteryTree,
                           pool: MasteryTree) -> Optional[int]:
    """
    Return the lowest tier different in the two trees.

    Parameters
    ----------
    tree : MasteryTree
        .
    pool : MasteryTree
        .

    Returns
    -------
    Optional[int]
        The tier that has different points in the two trees, or None if no such
        tier exists.
    """
    for tier in range(1, 6):
        if not set(pool.points[tier]).issubset(tree.points[tier]):
            return tier
    return None


def create_hybrid_tree(first_tree: MasteryTree,
                       second_tree: MasteryTree) -> MasteryTree:
    """
    Return a new tree containing random points from both passed trees.

    Parameters
    ----------
    first_tree : MasteryTree
        The first tree to pick points from.
    second_tree : MasteryTree
        The second tree to pick points from.

    Returns
    -------
    MasteryTree
        The newly created tree.

    """
    pool = first_tree.fuse(second_tree)
    nt = MasteryTree(f"{first_tree.species} & {second_tree.species} hybrid")
    while not nt.is_finished():
        smallest_tier_available = get_smallest_free_tier(nt, pool)
        if smallest_tier_available is None or smallest_tier_available > nt.maximum_tree_value - nt.get_current_value():
            return nt
        for tier in range(1, 6):
            if ((pool.get_number_of_points_by_tier(tier) > 0)
                    & (tier <= nt.get_available_space())):
                point = pool.get_random_by_tier(tier)
                if not nt.contains(point):
                    nt.add_point(point)
    return nt


def tree_from_file(path: str) -> MasteryTree:
    """
    Return a new tree whose points by tier repartition is specified by a file.

    Parameters
    ----------
    path : str
        The path to the file specifying points by tier repartition.

    Returns
    -------
    MasteryTree
        The newly created Mastery Tree.
    """
    d = {}
    with open(path, "r") as f:
        for tier in range(1, 6):
            d[tier] = int(f.readline().strip())
    return generate_from_dict(d, "tree_" + os.path.basename(path))


def generate_from_file(path: str) -> Callable:
    """
    Return a function that wraps around tree_from_file and takes no arguments.

    Parameters
    ----------
    path : str
        The path to pass to tree_from_file inside our wrapper function.

    Returns
    -------
    Callable
        A function that takes no arguments and behaves like tree_from_file does
        when passed _path_.

    """
    def tree_from_specific_file():
        return tree_from_file(path)
    return tree_from_specific_file
