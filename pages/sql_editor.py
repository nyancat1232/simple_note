import streamlit as st
import pandas as pd
from pandas.api.types import CategoricalDtype
from typing import List
from pyplus.sql.pgplus import read_from_server,get_foreign_keys,get_identity,get_default_value
from pyplus.streamlit.external import check_password


if not check_password():
    st.stop()  # Do not continue if check_password is not True.



def r_d_sql(schema_name,table_name,st_conn,expand_column=True):


    result = read_from_server(schema_name=schema_name,table_name=table_name,st_conn=st_conn)
    st.subheader(f'result of {schema_name}.{table_name}')
    st.dataframe(result)
    identity = get_identity(schema_name,table_name,st_conn)
    result = result.drop(columns=identity)
    
    df_foreign_keys = get_foreign_keys(schema_name,table_name,st_conn)
    list_foreign_keys = df_foreign_keys.index.to_list()
    try:
        if expand_column:
            columns = st.columns(len(list_foreign_keys))
            for index,row in enumerate(list_foreign_keys):
                with columns[index]:
                    r_d_sql(schema_name=df_foreign_keys.loc[row,'upper_schema'],table_name=df_foreign_keys.loc[row,'upper_table'],st_conn=st_conn,expand_column=False)
        else:
            for index,row in enumerate(list_foreign_keys):
                r_d_sql(schema_name=df_foreign_keys.loc[row,'upper_schema'],table_name=df_foreign_keys.loc[row,'upper_table'],st_conn=st_conn,expand_column=False)
    except:
        st.write("No foreign keys")

    st.subheader(f'upload {schema_name}.{table_name}')
    df_default_values = get_default_value(schema_name,table_name,st_conn)

    exclude_columns=[]
    if len(df_default_values.index)>0:
        st.subheader(f'select what you want to apply default')
        exclude_columns=dict(map(lambda column_name:(column_name,st.checkbox(f'{column_name}',value=True)),df_default_values.index))
        exclude_columns = dict(filter(lambda item:item[1],exclude_columns.items()))
        exclude_columns = list(map(lambda key:key,exclude_columns.keys()))
    

    result_to_append = result.copy()
    result_to_append = result_to_append.drop(labels=result.index,axis=0)
    result_to_append = result_to_append.drop(labels=exclude_columns,axis=1)

    #categorize foreign keys
    config_append_col = {}
    for foreign_key in df_foreign_keys.index:
        us = df_foreign_keys.at[foreign_key,'upper_schema']
        ut = df_foreign_keys.at[foreign_key,'upper_table']
        uc = df_foreign_keys.at[foreign_key,'upper_column_name']

        result_fk = read_from_server(schema_name=us,table_name=ut,st_conn=st_conn)
        result_fk['_display']=result_fk.apply(lambda columns:" ".join(list(map(str,columns))),axis=1)
        #result_fk['_display']
        config_append_col[foreign_key] = st.column_config.SelectboxColumn(options=result_fk[uc])


    result_to_append = st.data_editor(result_to_append,num_rows="dynamic",hide_index=True,column_config=config_append_col)
    if st.button(f'upload {schema_name}.{table_name}'):
        result_to_append.to_sql(name=table_name,con=st_conn.connect(),schema=schema_name,index=False,if_exists='append')
    
st_connff = st.connection(name='postgresql',type='sql')


input_schema = st.text_input('Input of schema')
input_table = st.text_input("Input of table")

try:
    r_d_sql(input_schema,input_table,st_connff)
except:
    st.write('not found')