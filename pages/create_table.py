import streamlit as st
from sqlutil.sql_util_new import table_selector
import pyplus.sql as sqlp
import pyplus.streamlit as stp

if not stp.check_password():
    st.stop()  # Do not continue if check_password is not True.


conn=st.connection('simple_note',type='sql')

@stp.init_session('list_of_schema')
def init_schema():
    lists=sqlp.get_table_list(conn.engine)
    return lists['table_schema'].unique().tolist()

schema_list = init_schema(refresh=True)

types=['bigint','double precision','text','timestamp with time zone']

schema_list
schema_name = st.text_input('schema name')
table_name = st.text_input('table name')


cols = {'':None}
sttype = {'value':st.column_config.SelectboxColumn('test',options=types)}
result = st.data_editor(cols,num_rows='dynamic',column_config=sttype)
result

if st.button('create table'):
    ts = sqlp.TableStructure(schema_name=schema_name,table_name=table_name,engine=conn.engine)
    res = ts.create_table(**result)
    res