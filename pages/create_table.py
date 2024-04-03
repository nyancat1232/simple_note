import streamlit as st
import pyplus.sql as sqlp
import pyplus.streamlit as stp

from pre import ex,conn
ex()

def init_schema():
    lists=sqlp.get_table_list(conn.engine)
    return lists['table_schema'].unique().tolist()

schema_list = init_schema()

types=['bigint','double precision','text','timestamp with time zone','boolean']

schema_list
schema_name = st.text_input('schema name')
table_name = st.text_input('table name')


cols = {'':None}
sttype = {'value':st.column_config.SelectboxColumn('test',options=types)}
result = st.data_editor(cols,num_rows='dynamic',column_config=sttype)
result

if st.button('create table'):
    ss = sqlp.SchemaStructure(schema_name=schema_name,engine=conn.engine)
    res = ss.create_table(table_name,**result)
    res