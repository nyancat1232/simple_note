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


df_read = first_ts.read()
df_expanded = first_ts.read_expand()
df_edited = st.data_editor(df_expanded)

st.subheader('edit mode')

df_compare2=df_edited.compare(df_expanded,keep_equal=False,result_names=('new','old'))

df_new=filter_new(df_compare2)
recs = df_new.to_dict(orient='index')

for row in recs:
    row
    recs[row]

if st.button('upload'):
    for row in recs:
        row
        recs[row]
        first_ts.upload(row,**recs[row])


