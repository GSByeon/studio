from brightics.common.repr import BrtcReprBuilder
from brightics.common.repr import strip_margin
from brightics.common.repr import dict2MD
from brightics.common.repr import pandasDF2MD
from brightics.function.utils import _model_dict
from brightics.common.groupby import _function_by_group
from brightics.common.utils import check_required_parameters

from collections import Counter
import pandas as pd
import numpy as np


def add_row_number(table, group_by=None, **params):
    check_required_parameters(_add_row_number, params, ['table'])
    if group_by is not None:
        return _function_by_group(_add_row_number, table, group_by=group_by, **params)
    else:
        return _add_row_number(table, **params)

        
def _add_row_number(table, new_col='add_row_number'):
    n = len(table)
    out_table = table.copy()
    out_table[new_col] = range(n)
    columns = table.columns.insert(0, new_col)
    out_table = out_table.reindex(columns=columns)
    return {'out_table': out_table}


def discretize_quantile(table, group_by=None, **params):
    check_required_parameters(_discretize_quantile, params, ['table'])
    if group_by is not None:
        return _function_by_group(_discretize_quantile, table, group_by=group_by, **params)
    else:
        return _discretize_quantile(table, **params)

        
def _discretize_quantile(table, input_col, num_of_buckets=2, out_col_name='bucket_number'):
    out_table = table.copy()
    out_table[out_col_name], buckets = pd.qcut(table[input_col], num_of_buckets, labels=False, retbins=True, precision=10, duplicates='drop')    
                
    params = { 
        'input_col': input_col,
        'num_of_buckets': num_of_buckets,
        'out_col_name': out_col_name
    }

    cnt = Counter(out_table[out_col_name].values)
    
    # index_list, bucket_list
    index_list = []
    bucket_list = []
    cnt_list = []     
    for i in range(len(buckets) - 1):
        left = '[' if i == 0 else '('
        index_list.append(i)
        cnt_list.append(cnt[i])
        bucket_list.append("{left}{lower}, {upper}]".format(left=left, lower=buckets[i], upper=buckets[i + 1]))  # 'buckets' is tuple type data.  
   
    # Build model
    result = pd.DataFrame.from_items([ 
        ['bucket number', index_list],
        ['buckets', bucket_list],
        ['count', cnt_list]
    ])
    
    # Build model
    rb = BrtcReprBuilder()
    rb.addMD(strip_margin("""
    | ## Quantile-based Discretization Result
    | ### Result
    | {result}
    |
    | ### Parameters
    | {params} 
    """.format(result=pandasDF2MD(result), params=dict2MD(params))))
    
    model = _model_dict('discretize_quantile')
    model['result'] = result
    model['params'] = params
    model['_repr_brtc_'] = rb.get()
    
    return {'out_table': out_table, 'model': model}


def binarizer(table, column, threshold=0, threshold_type='greater', out_col_name=None):
    out_table = table.copy()
    if out_col_name is None:
        out_col_name = 'binarized_' + str(column)
    
    if threshold_type == 'greater':
        out_table[out_col_name] = np.where(table[column] > threshold, 1, 0)
    else:
        out_table[out_col_name] = np.where(table[column] >= threshold, 1, 0)
    return{'out_table':out_table}


def capitalize_variable(table, input_cols, replace, out_col_suffix=None):
    if out_col_suffix is None:
        out_col_suffix = '_' + replace
     
    out_table = table.copy()
    for input_col in input_cols: 
        out_col_name = input_col + out_col_suffix
        
        if replace == 'upper':
            out_table[out_col_name] = table[input_col].str.upper() 
        else:
            out_table[out_col_name] = table[input_col].str.lower()
    
    return {'out_table': out_table}
