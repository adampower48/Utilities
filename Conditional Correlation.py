import numpy as np
import pandas as pd


def cond_corr(_df, group_cols):
    """
    Computes correlation matrix grouped by the values in grouped_cols.
    Returns a MutliIndex dataframe with index (grouped_col, grouped_val, corr_matrix_index).
    """
    
    corrs = {}
    for col in group_cols:
        corrs[col] = {}
        for val, group in _df.groupby(col):
            corrs[col][val] = group.corr()
            
        corrs[col] = pd.concat(corrs[col].values(), keys=corrs[col].keys(), axis=0)
            
    return pd.concat(corrs.values(), keys=corrs.keys(), axis=0)


def flatten_corr(_df):
    """
    Flattens a correlation matrix.
    Returns flat DataFrame with columns (corr_col1, corr_col2, corr_value).
    """
    data = []
    for i in range(1, _df.shape[0]):
        for j in range(i):
            row = _df.index[i]
            col = _df.index[j]
            data.append([row, col, _df.loc[row, col]])
            
    return pd.DataFrame(columns=["var1", "var2", "val"], data=data)


def cond_corr_stats(_df, cols):
    """
    Computes statistics for conditional correlation matrix.
    Returns MultiIndex dataframe with index (grouped_col, statistic, corr_matrix_index).
    """
    
    _cc = cond_corr(_df, cols)
    data = {}
    
    for col in cols:
        data[col] = {
            "var": _cc.loc[col].var(level=1),
            "std": _cc.loc[col].std(level=1),
            "mean": _cc.loc[col].mean(level=1),
            "count": _df.groupby(col).count(),
        }
        
        data[col] = pd.concat(data[col].values(), keys=data[col].keys(), axis=0)
        
    
    return pd.concat(data.values(), keys=data.keys(), axis=0)

