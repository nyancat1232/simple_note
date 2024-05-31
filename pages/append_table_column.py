import streamlit as st
from pre import ex,conn,table_selector,types
ex()

import pyplus.streamlit as stp
import pandas as pd

import pyplus.sql as sqlp


with st.sidebar:
    ts = table_selector()

read_result = ts.read_expand()
read_result

df = pd.DataFrame([{'name':'','type':''}])
sttype = {'type':st.column_config.SelectboxColumn('test',options=types+['_foreign'])}
result = st.data_editor(df,num_rows='dynamic',column_config=sttype)
result = {rec['name']:rec['type'] for rec in result.to_dict(orient='records')}
for col_local in [col for col in result if result[col] == '_foreign']:
    del result[col_local]
    ts = table_selector(f'{col_local} to a table ')
    df_foreign = ts.read()

    f'{col_local} to a table'
    df_foreign

    result[col_local] = f'_foreign:{ts.schema_name}.{ts.table_name}'
result

if st.button('append columns'):
    ts.append_column(**result)