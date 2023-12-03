import streamlit as st
import pandas as pd
from pyplus.streamlit.external import check_password
from pyplus.sql.pgplus import read_from_server,get_columns,write_to_server,create_empty_with_id_with_column,create_columns
from sqlutil.sql_util import table_selection

if not check_password():
    st.stop()  # Do not continue if check_password is not True.


def select_foreign_column(df) -> dict:
    df_data_columns = get_columns(schema_name=input.schema,table_name=input.table,st_conn=st_connff)
    foreign_column = st.multiselect(label='create as foreign key of',options=df.columns)
    st.write('rr')

    df_new_foreign = df[foreign_column].drop_duplicates()
    df_new_foreign
    _dict_col=df_data_columns.loc[foreign_column].to_dict()['data_type']
    return df_new_foreign, _dict_col

    
st_connff = st.connection(name='postgresql',type='sql')


with st.sidebar:
    input = table_selection(st_connff,'input')

st.subheader('total')
df_data = read_from_server(schema_name=input.schema,table_name=input.table,st_conn=st_connff)
st.dataframe(df_data)
df_foreign, foreign_columns = select_foreign_column(df_data)
foreign_columns
if st.button('write'):
    write_to_server(df_data,input.schema,input.table+'_backup',st_connff)

    foreign_table_inf={
        'schema_name':input.schema,
        'table_name':input.table+'_foreign',
        'st_conn':st_connff
    }

    create_empty_with_id_with_column(foreign_columns,**foreign_table_inf)
    write_to_server(df_foreign,**foreign_table_inf)

    df_result_foreign = read_from_server(**foreign_table_inf)
    df_result_foreign

    create_columns({input.table+'_foreign'+'_id':'bigint'},input.schema,input.table,
                        st_conn=st_connff)