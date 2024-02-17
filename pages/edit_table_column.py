import streamlit as st

import pyplus.streamlit as stp
if not stp.check_password():
    st.stop()

conn=st.connection('simple_note',type='sql')

import pyplus.sql as sqlp
from sqlutil.sql_util_new import table_selector


with st.sidebar:
    schema,table = table_selector(conn,'input')
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