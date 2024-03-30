import streamlit as st

import pyplus.streamlit as stp

from pre import ex,conn,table_selector
ex()

import pyplus.sql as sqlp


with st.sidebar:
    schema,table = table_selector('input')
    st.button('refresh',on_click=st.rerun)


ts = sqlp.TableStructure(schema_name=schema,table_name=table,
                         engine=conn.engine)

read_result = ts.expand_read()
read_result

types=['bigint','double precision','text','timestamp with time zone','boolean']

cols = {'':None}
sttype = {'value':st.column_config.SelectboxColumn('test',options=types)}
result = st.data_editor(cols,num_rows='dynamic',column_config=sttype)
result

if st.button('append columns'):
    ts.append_column(**result)