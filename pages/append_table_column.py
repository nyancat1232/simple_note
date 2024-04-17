import streamlit as st
from pre import ex,conn,table_selector,types
ex()

import pyplus.streamlit as stp


import pyplus.sql as sqlp


with st.sidebar:
    schema,table = table_selector('input')
    st.button('refresh',on_click=st.rerun)


ts = sqlp.TableStructure(schema_name=schema,table_name=table,
                         engine=conn.engine)

read_result = ts.read_expand()
read_result

cols = {'':None}
sttype = {'value':st.column_config.SelectboxColumn('test',options=types)}
result = st.data_editor(cols,num_rows='dynamic',column_config=sttype)
result

if st.button('append columns'):
    ts.append_column(**result)