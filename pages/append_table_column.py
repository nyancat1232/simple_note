import streamlit as st
from pre import ex,conn,table_selector,types
ex()

import pyplus.streamlit as stp
import pandas as pd

import pyplus.sql as sqlp


with st.sidebar:
    ts_first = table_selector()

read_result = ts_first.read_expand()
read_result

df = pd.DataFrame([{'name':'','type':''}])
sttype = {'type':st.column_config.SelectboxColumn('test',options=types+['_foreign'])}
result = st.data_editor(df,num_rows='dynamic',column_config=sttype)
result = {rec['name']:rec['type'] for rec in result.to_dict(orient='records')}
for col_local in [col for col in result if result[col] == '_foreign']:
    del result[col_local]
    ts_foreign = table_selector(f'{col_local} to a table ')
    df_foreign = ts_foreign.read()

    f'{col_local} to a table'
    df_foreign

    result[col_local] = f'_foreign:{ts_foreign.schema_name}.{ts_foreign.table_name}'
result

if st.button('append columns'):
    ts_first.append_column(**result)