import streamlit as st
import pandas as pd
from pyplus.streamlit.streamlit_plus_utility import FileDescription,execute_file_descriptions
from typing import List
import re
def read_from_server(table_name,conn,schema_name):
    with conn.connect() as conn_conn:
        return pd.read_sql_table(table_name=table_name,con=conn_conn,schema=schema_name)

def get_direction(df_file:pd.DataFrame,df_to:pd.DataFrame):
    st.subheader("move columns")
    
    ret_dict={}

    for col_file in df_file.reset_index().columns:
        if st.checkbox(f'move {col_file}',value=True):
            ret_dict[col_file]=st.selectbox(f' move {col_file} to',df_to.columns)

    return ret_dict

conn = st.connection(name='postgresql',type='sql')
with st.sidebar:
    fds : List[FileDescription] = []
    fds.append(FileDescription("^[A-Za-z0-9_]+.parquet$",pd.read_parquet))
    dfs = execute_file_descriptions(fds)


for key in dfs:
    schema = st.text_input('Input of schema')
    table = st.text_input("Input of table")
    df_from = dfs[key]
    df_to = read_from_server(table,conn,schema)

    direction = get_direction(df_from,df_to)
    not_in_directions = list(filter(lambda value:value not in direction.values(),df_to.columns))
    default_values={}
    for column in not_in_directions:
        if st.checkbox(f'fill {column}',value=True):
            default_values[column] = st.text_input(f'{column}')
    with st.expander('direction'):
        direction
        default_values
    if st.button(f'{key} upload to server'):
        df_file_sql = dfs[key].copy()
        df_file_sql = df_file_sql.rename(columns=direction)
        try:
            df_file_sql.index = df_file_sql.index.rename(direction[df_file_sql.index.name])
            _indexed = True
        except:
            _indexed = False
            st.write('no index in sql')
        for key,val in default_values.items():
            df_file_sql[key] = val
        df_file_sql
        with conn.connect() as conn_conn:
          df_file_sql.to_sql(table,conn_conn,schema,if_exists='append',index=_indexed)