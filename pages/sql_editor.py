import streamlit as st
from pyplus.streamlit.external import check_password
from sqlutil.sql_util import r_d_sql
from sqlutil.sql_util_new import table_selector
from pyplus.sql.pgplus import expand_foreign_column,get_identity

if not check_password():
    st.stop()  # Do not continue if check_password is not True.



st_connff = st.connection(name='simple_note',type='sql')


with st.sidebar:
    schema,table = table_selector(st_connff,'input')
    st.button('refresh',on_click=st.rerun)


st.subheader('total')
result_expand = expand_foreign_column(schema_name=schema,table_name=table,st_conn=st_connff)

st.dataframe(result_expand)
    
r_d_sql(schema,table,st_connff)

