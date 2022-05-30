#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun May 29 15:49:29 2022

@author: loldebyte

"""
from __future__ import annotations
from typing import Dict, List, Optional
import string
import random

VALEUR_TOTALE = 47


class MasteryPoint:
    
    def __init__(self, name: str, tier: int,
                 dependee: Optional[MasteryPoint] = None,
                 dependers: Optional[List[MasteryPoint]] = None):
        self.name = name
        self.tier = tier
        self.dependee = dependee
        self.dependers = dependers

    def __str__(self):
        return self.name

    def is_standalone(self) -> bool:
        return self.dependers is None and self.dependee is None

    def get_dependers(self) -> List[MasteryPoint]:
        return self.dependers
    
    def is_root(self) -> bool:
        return self.dependee is None


class MasteryTree:
    
    def __init__(self, species: str, mastery_points: Optional[Dict[int, List[MasteryPoint]]] = None):
        self.species = species
        if mastery_points is None:
            self.points = {1: [], 2: [], 3: [], 4: [], 5: []}
        else:
            self.points = mastery_points

    def __str__(self):
        return str({key: [str(_) for _ in value] for key, value in self.points.items()})

    def get_tier_value(self, tier: int) -> int:
        return len(self.points[tier]) * tier

    def get_cumulative_tier_value(self, tier: int) -> int:
        if tier < 1 or tier > 5:
            raise ValueError(f"Value '{tier}' is not a tier.")
        val = 0
        for k in range(1, tier + 1):
            val += self.get_tier_value(k)
        return val

    def is_viable(self) -> bool:
        return ((self.get_cumulative_tier_value(1) >= 1) & (self.get_cumulative_tier_value(2) >= 3)
                & (self.get_cumulative_tier_value(3) >= 6) & (self.get_cumulative_tier_value(4) >= 10))

    def get_current_value(self) -> int:
        return self.get_cumulative_tier_value(5)

    def get_available_space(self) -> int:
        return VALEUR_TOTALE - self.get_current_value()

    def is_complete(self) -> bool:
        return self.get_current_value() == VALEUR_TOTALE

    def is_finished(self) -> bool:
        return self.is_viable() & self.is_complete()
    
    def add_point(self, tier: int, point: MasteryPoint):
        if self.get_current_value() + tier <= VALEUR_TOTALE:
            self.points[tier].append(point)
        else:
            raise ValueError(f"Unable to add point of value {tier} : current capacity is at {self.get_current_value()}")

    def get_number_of_points_by_tier(self, tier: int) -> int:
        return len(self.points[tier])
    
    def get_total_number_of_points(self) -> int:
        val = 0
        for l in self.points.values():
            val += len(l)
        return val
    
    def get_min_tier_available(self) -> Optional[int]:
        for tier in range(1, 6):
            if self.get_tier_value(tier) > 0:
                return tier
        return None
    
    def fuse(self, mastery_tree: MasteryTree) -> MasteryTree:
        return MasteryTree(f"fused {self.species} & {mastery_tree.species}",
                           {key: self.points[key].copy() + mastery_tree.points[key].copy() for key in range(1, 6)})

    def contains(self, point: MasteryPoint) -> bool:
        if point in self.points[point.tier]:
            return True
        else:
            return False


def create_random_mp(tier: int, prefiVALEUR_TOTALE: str = "") -> MasteryPoint:
    return MasteryPoint(prefiVALEUR_TOTALE + ''.join(random.choices(string.ascii_letters, k=6)), tier=tier)

def create_list_of_random_mp(tier: int, n: int, prefiVALEUR_TOTALE: str = ""):
    return [create_random_mp(tier, f"{prefiVALEUR_TOTALE}_t{tier}_{nb}_") for nb in range(n)]


def generate_min_low_tiers() -> MasteryTree:
    return MasteryTree("Min low tiers",
                       {1: create_list_of_random_mp(1, 1, "MINLT"),
                        2: create_list_of_random_mp(2, 3, "MINLT"),
                        3: create_list_of_random_mp(3, 3, "MINLT"),
                        4: create_list_of_random_mp(4, 4, "MINLT"),
                        5: create_list_of_random_mp(5, 3, "MINLT")})

def generate_max_low_tiers() -> MasteryTree:
    return MasteryTree("Min low tiers",
                       {1: create_list_of_random_mp(1, 6, "MINLT"),
                        2: create_list_of_random_mp(2, 6, "MINLT"),
                        3: create_list_of_random_mp(3, 4, "MINLT"),
                        4: create_list_of_random_mp(4, 3, "MINLT"),
                        5: create_list_of_random_mp(5, 1, "MINLT")})


def generate_avg_distribution() -> MasteryTree:
    return MasteryTree("avg_distrib",
                       {key: (create_list_of_random_mp(key, 3, "AVG") if key != 2
                              else create_list_of_random_mp(key, 4, "AVG"))
                        for key in range(1, 6)})

def get_random_by_tier(tree: MasteryTree, tier: int) -> MasteryPoint:
    return random.choice(tree.points[tier])

def get_smallest_free_tier(tree: MasteryTree, pool: MasteryTree) -> int:
    for tier in range(1, 6):
        if not set(pool.points[tier]).issubset(tree.points[tier]):
            return tier
    return None

# %%

def create_hybrid_tree(first_tree: MasteryTree, second_tree: MasteryTree) -> MasteryTree:
    pool = first_tree.fuse(second_tree)
    nt = MasteryTree(f"{first_tree.species} & {second_tree.species} hybrid")
    while not nt.is_finished():
        smallest_tier_available = get_smallest_free_tier(nt, pool)
        if smallest_tier_available is None or smallest_tier_available > VALEUR_TOTALE - nt.get_current_value():
            return nt
        for tier in range(1, 6):
            if (pool.get_number_of_points_by_tier(tier) > 0) & (tier <= nt.get_available_space()):
                point = get_random_by_tier(pool, tier)
                if not nt.contains(point):
                    nt.add_point(tier, point)
    return nt
