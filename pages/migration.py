import streamlit as st
import pandas as pd
from pyplus.streamlit.external import check_password
from pyplus.sql.pgplus import read_from_server,get_columns
if not check_password():
    st.stop()  # Do not continue if check_password is not True.


    
st_connff = st.connection(name='postgresql',type='sql')


input_schema = st.text_input('Input of schema')
input_table = st.text_input("Input of table")

to_schema = st.text_input('To of schema')
to_table = st.text_input("To of table")

st.subheader('total')
df_data = read_from_server(schema_name=to_schema,table_name=to_table,st_conn=st_connff)
