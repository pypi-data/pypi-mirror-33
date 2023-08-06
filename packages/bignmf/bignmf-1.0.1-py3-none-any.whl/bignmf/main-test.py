from models.jnmf.IntegrativeJnmfClass import IntegrativeNmfClass
from datasets.Datasets import Datasets as data
import pandas as pd

def clean_df(x: pd.DataFrame, axis=1):
    if axis == 1:
        y = x[x.notna().all(axis=1)]
    if axis == 0:
        x = x.T
        y = x[x.notna().all(axis=1)]
        y = y.T 

    # y = x[x.notna().any(axis=1)]
    return y

d={}
d["gene"] = clean_df(pd.read_csv("/Users/haranrk/Documents/bignmf/bignmf/Gene.csv",index_col=0))
print(d["gene"])
k = 3
iter =100
trials = 50
lamb = 0.1 

a = IntegrativeNmfClass(d,k,lamb)
a.run(trials, iter, verbose=1)
print(a.error)
a.cluster_data()
a.calc_consensus_matrices()
a.calc_cophenetic_correlation()
print(a.max_class)