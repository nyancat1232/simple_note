import streamlit as st
from pyplus.streamlit.external import check_password
from sqlutil.sql_util import r_d_sql,table_selection
from pyplus.sql.pgplus import expand_foreign_column,get_identity

if not check_password():
    st.stop()  # Do not continue if check_password is not True.



st_connff = st.connection(name='postgresql',type='sql')


input = None
with st.sidebar:
    input = table_selection(st_connff,'input')


st.subheader('total')
result_expand = expand_foreign_column(schema_name=input.schema,table_name=input.table,st_conn=st_connff)

st.dataframe(result_expand)
    
r_d_sql(input.schema,input.table,st_connff)

