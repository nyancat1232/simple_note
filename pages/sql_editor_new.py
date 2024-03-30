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

def filter_self(df:pd.DataFrame)->pd.DataFrame:
    d={upper_col[0]:df[upper_col[0],'self'] for upper_col in df.columns}
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
