import streamlit as st
from pyplus.streamlit.external import check_password
from pyplus.streamlit.sql_util import r_d_sql
from pyplus.sql.pgplus import expand_foreign_column,get_table_list

if not check_password():
    st.stop()  # Do not continue if check_password is not True.


    
st_connff = st.connection(name='postgresql',type='sql')

with st.sidebar:
    df_list=get_table_list(st_connff)
    df_list

    input_schema = st.selectbox(label='Input of schema',options=df_list['table_schema'].unique())
    input_table = st.selectbox(label="Input of table",options=df_list['table_name'][df_list['table_schema']==input_schema])


st.subheader('total')
result_expand = expand_foreign_column(schema_name=input_schema,table_name=input_table,st_conn=st_connff)
st.dataframe(result_expand)
    
r_d_sql(input_schema,input_table,st_connff)

if st.button('rerun'):
    st.rerun()
    