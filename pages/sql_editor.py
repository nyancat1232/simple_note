import streamlit as st
from pyplus.streamlit.external import check_password
from pyplus.streamlit.sql_util import r_d_sql


if not check_password():
    st.stop()  # Do not continue if check_password is not True.


    
st_connff = st.connection(name='postgresql',type='sql')


input_schema = st.text_input('Input of schema')
input_table = st.text_input("Input of table")

try:
    r_d_sql(input_schema,input_table,st_connff)
except:
    st.write('not found')