from pre import conn,ex,table_selector
ex()
import streamlit as st
import pyplus.sql as sqlp
import pyplus.streamlit as stp
import pandas as pd
from typing import Literal

with st.sidebar:
    schema,table=table_selector('select table')

first_ts = sqlp.TableStructure(schema,table,conn.engine)

def filter_new(df:pd.DataFrame,col='new')->pd.DataFrame:
    d={upper_col[0]:df[upper_col[0],col] for upper_col in df.columns}
    return pd.DataFrame(d)

def to_super_col(df:pd.DataFrame)->dict[str,str]:
    cols=df.columns.unique().tolist()
    m = {s:s[:s.find('.')] for s in cols}
    super_cols = tuple(set(s[:s.find('.')] for s in cols))
    return super_cols,m

def creation(type:Literal['bool','str'],rows,cols)->pd.DataFrame:
    match type:
        case 'bool':
            return pd.DataFrame({col:[False for _ in rows] for col in cols}).set_index(rows)
        case 'str':
            return pd.DataFrame({col:[None for _ in rows] for col in cols}).set_index(rows)

def get_foreign_id_from_value(df_read:pd.DataFrame,df_expand:pd.DataFrame,row,column):
    '''
        a.b c.d
    30  3   4

    get_foreign_id_from_value(.., .., 30, a.b)
    result : the foreign id of (30,a.b)
    '''
    def id_repeat(df:pd.DataFrame,df_expand:pd.DataFrame):
        df_copy = df.copy()
        col_sub = {col:col[:col.find('.')] for col in df_expand.columns if col.find('.')!=-1}
        for col in col_sub:
            df_copy[col] = df_copy[col_sub[col]]
        return df_copy
    df_repeat=id_repeat(df_read,df_expand)
    return df_repeat.loc[row,column]

def get_mode(df_compare:pd.DataFrame):
    df_mode = creation('str',df_compare.index,filter_new(df_compare).columns)
    for row in df_compare.index:
        for column in df_compare.columns:
            v = df_compare.loc[row,column[0]]
            na_new = v.loc['new'] is pd.NA
            na_old = v.loc['old'] is pd.NA
            if not na_new and not na_old:
                df_mode.loc[row,column[0]]='U'
            elif not na_new and na_old:
                df_mode.loc[row,column[0]]='A'
            elif na_new and not na_old:
                df_mode.loc[row,column[0]]='D'
    return df_mode
def filter_true(split_orient:dict):
    '''
    filter point which data is true.
    
    Parameters
    ----------
    split_orient : dict
        pd.to_dict(orient='split').
    '''
    temp = [[(split_orient['index'][ind],split_orient['columns'][col],val) 
            for col,val in enumerate(line) 
            if val == True] 
            for ind,line in enumerate(split_orient['data'])]
    ret = []
    for ll in temp:
        ret += ll
    ret = [l[:-1] for l in ret]
    return ret
