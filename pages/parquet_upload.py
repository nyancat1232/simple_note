import streamlit as st
import pandas as pd
from pyplus.streamlit.streamlit_plus_utility import FileDescription,FileExecutor
from pyplus.streamlit.streamlit_plus import write_columns
from pyplus.sql.pgplus import read_from_server,get_identity,get_foreign_keys,write_to_server
from sqlutil.sql_util import table_selection

def get_direction(df_file:pd.DataFrame,df_to:pd.DataFrame):
    st.subheader("move columns")
    
    ret_dict={}

    for col_file in df_file.columns:
        if st.checkbox(f'move {col_file}',value=True):
            ret_dict[col_file]=st.selectbox(f' move {col_file} to',df_to.columns)

    return ret_dict

conn = st.connection(name='simple_note',type='sql')
with st.sidebar:
    fe = FileExecutor()
    fe.behaviors.append(FileDescription("^[A-Za-z0-9_]+.parquet$",pd.read_parquet))
    
    dfs = fe.execute_file_descriptions()


for key in dfs:
    input = table_selection(st_conn=conn,label='input')
    schema = input.schema
    table = input.table

    df_from = dfs[key].reset_index()

    df_to = read_from_server(table_name=table,st_conn=conn,schema_name=schema)
    to_ids = get_identity(schema_name=schema,table_name=table,st_conn=conn)
    
    df_to=df_to.drop(columns=to_ids.to_list())

    write_columns(df_from,df_to)

    directions = get_direction(df_from,df_to)
    not_in_directions = list(filter(lambda value:value not in directions.values(),df_to.columns))
    default_values={}
    for column in not_in_directions:
        if st.checkbox(f'fill {column}',value=True):
            default_values[column] = st.text_input(f'{column}')
    with st.expander('direction'):
        directions
        default_values

    df_to_fks = get_foreign_keys(schema_name=schema,table_name=table,st_conn=conn)
    df_to_fks
    for direction in directions:
        try:
            df_fk_inf = df_to_fks.loc[directions[direction]]
            df_fk_data = read_from_server(df_fk_inf['upper_schema'],df_fk_inf['upper_table'],conn)
            

            df_fk_to = st.selectbox(f'{direction} to column of {df_fk_inf["upper_schema"]}.{df_fk_inf["upper_table"]}',options=df_fk_data.columns)
            df_fk_data = df_fk_data[[df_fk_inf['upper_column_name'],df_fk_to]]
            df_fk_data

            df_from_filter = df_from[direction]
            df_merged=pd.merge(df_from_filter,df_fk_data,left_on=direction,right_on=df_fk_to,how='left').drop(columns=df_fk_to)
            df_to[directions[direction]] = df_merged[df_fk_inf['upper_column_name']]

        except:
            st.toast(f'{directions[direction]} is not a foreign key')
            df_to[directions[direction]] = df_from[direction]
    
    st.dataframe(df_to.dropna())

    st.button(f'upload to server {schema}.{table}',on_click=write_to_server,args=[df_to.dropna(),schema,table,conn])