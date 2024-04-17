import streamlit as st
from pre import ex,conn,table_selector,types
ex()

import pyplus.streamlit as stp
import pandas as pd

import pyplus.sql as sqlp


with st.sidebar:
    schema,table = table_selector('input')
    st.button('refresh',on_click=st.rerun)


ts = sqlp.TableStructure(schema_name=schema,table_name=table,
                         engine=conn.engine)

read_result = ts.read_expand()
read_result

df = pd.DataFrame([{'name':'','type':''}])
sttype = {'type':st.column_config.SelectboxColumn('test',options=types+['_foreign'])}
result = st.data_editor(df,num_rows='dynamic',column_config=sttype)
result = {rec['name']:rec['type'] for rec in result.to_dict(orient='records')}
for col_local in [col for col in result if result[col] == '_foreign']:
    del result[col_local]
    schema,table = table_selector(f'{col_local} to a table ')
    ts = sqlp.TableStructure(schema,table,conn.engine)
    df_foreign = ts.read()

    f'{col_local} to a table'
    df_foreign

    result[col_local] = f'_foreign:{schema}.{table}'
result

if st.button('append columns'):
    ts.append_column(**result)