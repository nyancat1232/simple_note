import streamlit as st
from pre import ex,conn,init_schema,types
ex()

import pyplus.sql as sqlp
import pyplus.streamlit as stp


schema_name = init_schema()
table_name = st.text_input('table name')


cols = {'':None}
sttype = {'value':st.column_config.SelectboxColumn('test',options=types)}
result_type = st.data_editor(cols,num_rows='dynamic',column_config=sttype)
result_type
if st.button('create table'):
    ss = sqlp.SchemaStructure(schema_name=schema_name,engine=conn.engine)
    res = ss.create_table(table_name,**result_type)
    st.toast('succeed')
    #res.upload_append(**{key:"" for key in result_type})