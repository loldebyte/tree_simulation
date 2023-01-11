"""Asserts that all combinations of alterations are represented and coherent.

Created on Wed Jun 29 16:48:35 2022

@author: loldebyte
"""
import pandas as pd
import itertools
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


f = "./Modifications d'État - Arbre des Altérations.csv"
df = pd.read_csv(f, dtype="string")

for i in range(3):
    df.iloc[0, i*4:4*i+4] = (df.iloc[0, i*4:4*i+4]
                             .apply(lambda x: f"{df.columns[i*4]} {x}"))
for i in range(12, 14):
    df.iloc[0, i:i+1] = (df.iloc[0, i:i+1]
                         .apply(lambda x: f"{df.columns[i]} {x}"))
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
    return (check_2_reagents_combinations(t1_bi)
            & check_2_reagents_combinations(t2_bi)
            & check_3_reagents_combinations(t1_tri)
            & check_3_reagents_combinations(t2_tri)
            & check_3_reagents_combinations(t3))


def check_2_reagents_combinations(df_: pd.DataFrame) -> bool:
    """
    Return True if all combinations involving 2 alterations exist in the df.

    Returns
    -------
    bool
        True if all 2 alterations combinations are good, else False.

    """
    cols = df_.columns.to_list()

    def to_apply(series):
        reordered_series = pd.Series({cols[0]: series[cols[1]],
                                      cols[1]: series[cols[0]],
                                      cols[2]: series[cols[2]]})
        return check_if_exists_in_df(reordered_series, df_)
    exists = df_.apply(to_apply, axis=1)
    if exists.all():
        return True
    else:
        for idx, x in exists.items():
            if not x:
                print(f"Series # {idx+2}: {list(df_.loc[idx, :].array)} "
                      "has no equivalent.")
        return False


def check_if_exists_in_df(s: pd.Series, df_: pd.DataFrame) -> bool:
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
    return (s == df_).all(1).any()


def check_3_reagents_combinations(df_: pd.DataFrame) -> bool:
    """
    Return True if all combinations involving 3 alterations exist in the df.

    Returns
    -------
    bool
        True if all 3 alterations combinations are good, else False.

    """
    missing_combinations = set()

    def to_apply(series):
        for reordered_series in get_tricombinations_series(series):
            ret = check_if_exists_in_df(reordered_series, df_)
            if not ret:
                missing_combinations.add("Missing combination "
                                         f"{list(reordered_series.values)} "
                                         "corresponding to recipe "
                                         f"line {df_[df_.eq(series).all(axis=1)].index[0]+2} "
                                         f"{list(series.values)}")
                return False
            else:
                return True
    exists = df_.apply(to_apply, axis=1)
    for _ in missing_combinations:
        print(_)
    if exists.all():
        return True
    else:
        return False


def get_autres(series: pd.Series, alteration_principale: str) -> tuple:
    """
    Return a tuple that completes the set.

    Return the tuple of alterations contained in series that complete the set
        started by alteration_principale. This tuple has to be in alphabetical
        order.

    Parameters
    ----------
    series : pd.Series
        The series to take alterations from.
    alteration_principale : str
        The alteration that starts the combination.

    Returns
    -------
    tuple
        A tuple of alterations, of type Tuple[str, str].

    """
    return tuple(sorted([_ for _ in list(series.values)
                         if _ != alteration_principale]))


def get_tricombinations_series(s: pd.Series) -> list:
    """
    Return a list of reordered Series.

    For every recipe we must have exactly 3 combinations : one with each
        alteration as main reagent, and the other alterations by
        alphabetical order.

    Parameters
    ----------
    s : pd.Series
        The original Series to reorder.

    Returns
    -------
    list
        List of reordered Series.

    """
    # TODO: schéma : permutation r=1 + sort alphabetic des autres
    cols = s.index.to_list()
    combinations = [_ + get_autres(s[:3], _[0])
                    for _ in itertools.permutations(list(s.values)[:3], r=1)
                    if _[0] != s[0]]
    return [pd.Series({cols[0]: _[0], cols[1]: _[1], cols[2]: _[2],
                       cols[3]: s[cols[3]]})
            for _ in combinations]


def check_coherent_results(dataframe: pd.DataFrame) -> bool:
    """Return True if all different recipes yield the same Alteration."""
    # si les check d'avant passent, alors toutes recettes sont cohérentes
    # ssi il n'y a aucun doublons sur les recettes, càd aucun cas ou on a
    # 1 recette pour 2 produits
    # TODO: check doublons pour 3 tiers
    dupes_index = dataframe.index[dataframe.duplicated(dataframe.columns[:-1],
                                                       keep=False)] + 2
    if not dupes_index.empty:
        print(f"List of duplicated lines : {dupes_index.to_list()}")
        return False
    return True


def check_all_coherent_results() -> bool:
    """
    Return True if no dataframe has duplicates.

    Returns
    -------
    bool
        True if no dataframe has duplicates, False otherwise.

    """
    return all([check_coherent_results(dataframe=dataframe)
                for dataframe in [t1, t2, t3]])


assert check_all_combinations()

assert check_all_coherent_results()
