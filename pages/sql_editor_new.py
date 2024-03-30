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

def id_repeat(df:pd.DataFrame,df_expand:pd.DataFrame):
    df_copy = df.copy()
    col_sub = {col:col[:col.find('.')] for col in df_expand.columns if col.find('.')!=-1}
    for col in col_sub:
        df_copy[col] = df_copy[col_sub[col]]
    return df_copy
def get_foreign_id_from_value(df_read:pd.DataFrame,df_expand:pd.DataFrame,row,column):
    df_repeat=id_repeat(df_read,df_expand)
    return df_repeat.loc[row,column]
