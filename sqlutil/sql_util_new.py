import streamlit as st
import sqlalchemy
from pyplus.sql.oopgplus import TableStructure,get_table_list

def table_selector(engine:sqlalchemy.Engine,label:str):
    df_list=get_table_list(engine)

    schema = st.selectbox(label=f'{label} of schema',options=df_list['table_schema'].unique())
    table = st.selectbox(label=f"{label} of table",options=df_list['table_name'][df_list['table_schema']==schema])
    return schema, table
