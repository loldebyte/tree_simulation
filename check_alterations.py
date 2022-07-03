"""Asserts that all combinations of alterations are represented and coherent.

Created on Wed Jun 29 16:48:35 2022

@author: loldebyte
"""
import pandas as pd
import itertools


f = "/media/hdd/Downloads/Modifications d'État - Arbre des Altérations.csv"
df = pd.read_csv(f, dtype="string")

for i in range(3):
    df.iloc[0, i*4:4*i+4] = df.iloc[0, i*4:4*i+4].apply(lambda x: f"{df.columns[i*4]} {x}")
for i in range(12, 14):
    df.iloc[0, i:i+1] = df.iloc[0, i:i+1].apply(lambda x: f"{df.columns[i]} {x}")
df.columns = df.iloc[0, :]
df = df.iloc[1:, :]

cols_to_ffill = ([f"Tier {x} Altération d'État" for x in range(1, 4)]
                 + [f"Tier {x} Réactif 1" for x in range(1, 4)])
df[cols_to_ffill] = df[cols_to_ffill].fillna(method="ffill")

t1 = df.iloc[:, :4].dropna(subset="Tier 1 Produit")
t2 = df.iloc[:, 4:8].dropna(subset="Tier 2 Produit")
t3 = df.iloc[:, 8:12].dropna(subset="Tier 3 Produit")


def check_all_combinations() -> bool:
    """Return True if all combinations of reagents exist in the dataframe."""
    # TODO: itertools.combinations()
    return False


def check_coherent_results() -> bool:
    """Return True if all different recipes yield the same Alteration."""
    return False


assert check_all_combinations()

assert check_coherent_results()
