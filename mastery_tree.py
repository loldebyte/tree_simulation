"""Mastery Point and Mastery Tree definitions & utils."""
from __future__ import annotations
from typing import Dict, List, Optional
import string
import random

VALEUR_TOTALE = 47


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
                                               List[MasteryPoint]]] = None):
        self.species = species
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
        return VALEUR_TOTALE - self.get_current_value()

    def is_complete(self) -> bool:
        """
        Return True if current tree value is exactly VALEUR_TOTALE.

        Returns
        -------
        bool
            Whether the current tree value matches VALEUR_TOTALE or not.
        """
        return self.get_current_value() == VALEUR_TOTALE

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

# TODO: get tier from point's attributes
    def add_point(self, tier: int, point: MasteryPoint):
        """
        Add a point to the tree.

        Parameters
        ----------
        tier : int
            The point's tier.
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
        if self.get_current_value() + tier <= VALEUR_TOTALE:
            self.points[tier].append(point)
        else:
            raise ValueError(
                f"Unable to add point of value {tier} : current capacity is "
                f"at {self.get_current_value()}")

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
        return MasteryTree(f"fused {self.species} & {mastery_tree.species}",
                           {key: self.points[key].copy()
                            + mastery_tree.points[key].copy()
                            for key in range(1, 6)})

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


def generate_min_low_tiers() -> MasteryTree:
    """
    Create a new mastery tree with minimal amount of low tier points.

    Returns
    -------
    MasteryTree
        The newly create mastery tree.

    """
    return MasteryTree("Min low tiers",
                       {1: create_list_of_random_mp(1, 1, "MINLT"),
                        2: create_list_of_random_mp(2, 3, "MINLT"),
                        3: create_list_of_random_mp(3, 3, "MINLT"),
                        4: create_list_of_random_mp(4, 4, "MINLT"),
                        5: create_list_of_random_mp(5, 3, "MINLT")})


def generate_max_low_tiers() -> MasteryTree:
    """
    Create a new mastery tree with maximal amount of low tier points.

    Returns
    -------
    MasteryTree
        The newly create mastery tree..

    """
    return MasteryTree("Min low tiers",
                       {1: create_list_of_random_mp(1, 6, "MINLT"),
                        2: create_list_of_random_mp(2, 6, "MINLT"),
                        3: create_list_of_random_mp(3, 4, "MINLT"),
                        4: create_list_of_random_mp(4, 3, "MINLT"),
                        5: create_list_of_random_mp(5, 1, "MINLT")})


def generate_avg_distribution() -> MasteryTree:
    """
    Create a new mastery tree with average amount of low tier points.

    Returns
    -------
    MasteryTree
        The newly create mastery tree.

    """
    return MasteryTree("avg_distrib",
                       {key: (create_list_of_random_mp(key, 3, "AVG") if key != 2
                              else create_list_of_random_mp(key, 4, "AVG"))
                        for key in range(1, 6)})


# TODO: make this a method of MasteryTree
def get_random_by_tier(tree: MasteryTree, tier: int) -> MasteryPoint:
    """
    Return a random point of specified tier from a tree passed as argument.

    Parameters
    ----------
    tree : MasteryTree
        The tree from which to pick.
    tier : int
        The tier from which to pick.

    Returns
    -------
    MasteryPoint
        The chosen point.
    """
    return random.choice(tree.points[tier])


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

# %%


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
        if smallest_tier_available is None or smallest_tier_available > VALEUR_TOTALE - nt.get_current_value():
            return nt
        for tier in range(1, 6):
            if ((pool.get_number_of_points_by_tier(tier) > 0)
                    & (tier <= nt.get_available_space())):
                point = get_random_by_tier(pool, tier)
                if not nt.contains(point):
                    nt.add_point(tier, point)
    return nt
