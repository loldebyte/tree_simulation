#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 16:48:35 2022

@author: loldebyte
"""
import pandas as pd


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


def check_all_combinations() -> bool:
    return False


def check_coherent_results() -> bool:
    return False


assert check_all_combinations()

assert check_coherent_results()
