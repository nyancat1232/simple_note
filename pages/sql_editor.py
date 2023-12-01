import streamlit as st
from pyplus.streamlit.external import check_password
from pyplus.streamlit.sql_util import r_d_sql,table_selection
from pyplus.sql.pgplus import expand_foreign_column

if not check_password():
    st.stop()  # Do not continue if check_password is not True.



st_connff = st.connection(name='postgresql',type='sql')

with st.sidebar:
    input = table_selection(st_connff)
    
input_schema = input['schema']
input_table = input['table']

st.subheader('total')
result_expand = expand_foreign_column(schema_name=input_schema,table_name=input_table,st_conn=st_connff)
st.dataframe(result_expand)
    
r_d_sql(input_schema,input_table,st_connff)

if st.button('rerun'):
    st.rerun()
