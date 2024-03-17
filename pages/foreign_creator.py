import streamlit as st
import pandas as pd
import pyplus.streamlit as stp
from pyplus.sql import TableStructure
from sqlutil.sql_util_new import table_selector

from pre import ex
from pre import conn as st_connff
ex()

def create_new_foreign(ts:TableStructure) -> pd.DataFrame:
    df = ts.read()
    df_data_columns = df.columns
    st.write(df,df_data_columns)
    
    foreign_column = st.multiselect(label='create as foreign key of',options=df_data_columns)

    df_new_foreign = df[foreign_column].drop_duplicates().reset_index(drop=True)
    df_new_foreign
    return df_new_foreign

    

with st.sidebar:
    input_schema,input_table = table_selector(st_connff,'input')


st.subheader('total')
ts  = TableStructure(schema_name=input_schema,table_name=input_table,
                     engine=st_connff)
df_foreign_columns = create_new_foreign(ts)
ts_foreign = TableStructure(schema_name=input_schema,
                            table_name=f'{input_table}_foreign',
                            engine=st_connff)
if st.button('create_new_foreign'):
    df_foreign_columns.to_sql(schema=input_schema,
                              name=f'{input_table}_foreign',
                              con=st_connff.engine,index=True)

st.stop()
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