import streamlit as st
import pandas as pd
from typing import List
from pyplus.sql.pgplus import read_from_server,get_foreign_keys,get_identity,get_default_value

def r_d_sql(schema_name,table_name,st_conn,expand_column=True):
    result = read_from_server(schema_name=schema_name,table_name=table_name,st_conn=st_conn)
    st.subheader(f'result of {schema_name}.{table_name}')
    st.dataframe(result)
    identity = get_identity(schema_name,table_name,st_conn)
    result = result.drop(columns=identity)
    
    fks = get_foreign_keys(schema_name,table_name,st_conn)
    columns_for_tab = fks.index.to_list()
    try:
        if expand_column:
            columns = st.columns(len(columns_for_tab))
            for index,row in enumerate(columns_for_tab):
                with columns[index]:
                    r_d_sql(schema_name=fks.loc[row,'upper_schema'],table_name=fks.loc[row,'upper_table'],st_conn=st_conn,expand_column=False)
        else:
            for index,row in enumerate(columns_for_tab):
                r_d_sql(schema_name=fks.loc[row,'upper_schema'],table_name=fks.loc[row,'upper_table'],st_conn=st_conn,expand_column=False)
    except:
        st.write("No foreign keys")

    st.subheader(f'upload {schema_name}.{table_name}')
    df_default_values = get_default_value(schema_name,table_name,st_conn)
    exclude_columns=dict(map(lambda column_name:(column_name,st.checkbox(f'{column_name}',value=True)),df_default_values.index))
    exclude_columns = dict(filter(lambda item:item[1],exclude_columns.items()))
    exclude_columns = list(map(lambda key:key,exclude_columns.keys()))
    exclude_columns
    result_to_append = result.copy()
    result_to_append = result_to_append.drop(labels=result.index,axis=0)
    result_to_append = result_to_append.drop(labels=exclude_columns,axis=1)
    result_to_append = st.data_editor(result_to_append,num_rows="dynamic",hide_index=True)
    if st.button(f'upload {schema_name}.{table_name}'):
        result_to_append.to_sql(name=table_name,con=st_conn.connect(),schema=schema_name,index=False,if_exists='append')
    
st_connff = st.connection(name='postgresql',type='sql')

input_schema = st.text_input('Input of schema')
input_table = st.text_input("Input of table")


cols = st.tabs(['append','edit'])



r_d_sql(input_schema,input_table,st_connff)