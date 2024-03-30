import streamlit as st
import pandas as pd
import pyplus.streamlit as stp
from pyplus.sql import TableStructure

from pre import ex,table_selector
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
    input_schema,input_table = table_selector('input')


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