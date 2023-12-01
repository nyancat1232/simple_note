import streamlit as st
import pandas as pd
from typing import List
from pyplus.sql.pgplus import read_from_server,get_foreign_keys,get_identity

conn = st.connection(name='postgresql',type='sql')

schema = st.text_input('Input of schema')
table = st.text_input("Input of table")

df_sql_read = read_from_server(schema,table,conn)
st.dataframe(df_sql_read,hide_index=True)
df_sql = df_sql_read.copy()
df_sql = df_sql.drop(labels=df_sql.index,axis=0)
fks = get_foreign_keys(schema,table,conn)
fks
for fki,fkr in fks.iterrows():
    r = read_from_server(fkr['upper_schema'],fkr['upper_table'],conn)
    r


identity = get_identity(schema,table,conn)
#identity
#df_sql
df_sql = df_sql.drop(columns=identity)
result = st.data_editor(df_sql,num_rows="dynamic",hide_index=True)
    


if st.button('upload'):
    result.to_sql(table,conn.connect(),schema=schema,index=False,if_exists='append')