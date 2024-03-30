import streamlit as st
import pandas as pd
from pyplus.streamlit.external import check_password
from pyplus.sql.pgplus import read_from_server

from pre import ex,table_selector
from pre import conn as st_conn
ex()
    

columns = st.columns(2)
with columns[0]:
    input = table_selector('input')
    st.subheader('input')
    df_input_data = read_from_server(schema_name=input.schema,table_name=input.table,st_conn=st_conn)
    df_input_data

with columns[1]:
    output = table_selector('output')
    st.subheader('output')
    df_output_data = read_from_server(schema_name=output.schema,table_name=output.table,st_conn=st_conn)
    df_output_data

df_new_data=pd.DataFrame()
for column in df_input_data.columns:
    if not st.checkbox(f'ignore {column}',value=True):
        direction_to=st.selectbox(f"{column} to",df_output_data.columns)
        df_new_data[direction_to]=df_input_data[column]
df_new_data

if st.button(f'upload'):
        df_new_data.to_sql(name=output.table,con=st_conn.connect(),schema=output.schema,index=False,if_exists='append')
if st.button('rerun'):
    st.rerun()
