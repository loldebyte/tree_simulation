"""Asserts that all combinations of alterations are represented and coherent.

Created on Wed Jun 29 16:48:35 2022

@author: loldebyte
"""
import pandas as pd
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


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
t1_bi = t1[t1["Tier 1 Réactif 2"].isnull()].drop(columns="Tier 1 Réactif 2")
t1_tri = t1.dropna(subset="Tier 1 Réactif 2")
t2 = df.iloc[:, 4:8].dropna(subset="Tier 2 Produit")
t2_bi = t2[t2["Tier 2 Réactif 2"].isnull()].drop(columns="Tier 2 Réactif 2")
t2_tri = t2.dropna(subset="Tier 2 Réactif 2")
t3 = df.iloc[:, 8:12].dropna(subset="Tier 3 Produit")


def check_all_combinations() -> bool:
    """Return True if all combinations of reagents exist in the dataframe."""
    # call following function with appropriate parameters
    two_reg = (check_2_reagents_combinations(t1_bi)
               and check_2_reagents_combinations(t2_bi))
    three_reg = (check_3_reagents_combinations(t1_tri)
                 and check_3_reagents_combinations(t2_tri)
                 and check_3_reagents_combinations(t3))
    return two_reg and three_reg


def check_2_reagents_combinations(df: pd.DataFrame) -> bool:
    """
    Return True if all combinations involving 2 alterations exist in the df.

    Returns
    -------
    bool
        True if all 2 alterations combinations are good, else False.

    """
    cols = df.columns.to_list()

    def to_apply(series):
        reordered_series = pd.Series({cols[0]: series[cols[1]],
                                      cols[1]: series[cols[0]],
                                      cols[2]: series[cols[2]]})
        return check_if_exists_in_df(reordered_series, df)
    exists = df.apply(to_apply, axis=1)
    if exists.all():
        return True
    else:
        for idx, x in enumerate(exists):
            if not x:
                print(f"Series # {idx}: {list(df.iloc[idx, :].array)} "
                      "has no equivalent.")


def check_if_exists_in_df(s: pd.Series, df: pd.DataFrame) -> bool:
    """
    Return True if passed series exists in the df.

    Parameters
    ----------
    s : pd.Series
        The series whose existence to check.

    Returns
    -------
    bool
        True if passed series exists, False otherwise.
    """
    return (s == df).all(1).any()


def check_3_reagents_combinations() -> bool:
    """
    Return True if all combinations involving 3 alterations exist in the df.

    Returns
    -------
    bool
        True if all 2 alterations combinations are good, else False.

    """
    return False


def check_coherent_results() -> bool:
    """Return True if all different recipes yield the same Alteration."""
    # si les check d'avant passent, alors toutes recettes sont cohérentes
    # ssi il n'y a aucun doublons sur les recettes, càd aucun cas ou on a
    # 1 recette pour 2 produits
    # TODO: s'assurer qu'il n'y a aucun doublon sur les recettes
    return False


assert check_all_combinations()

assert check_coherent_results()
