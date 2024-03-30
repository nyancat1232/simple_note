import streamlit as st
import pyplus.streamlit as stp
import pyplus.sql as sqlp

def ex():
    if not stp.check_password():
        st.stop()
if 'conn' not in st.session_state:
    st.session_state['conn'] = st.connection('myaddress',type='sql')

conn = st.session_state['conn']

def table_selector(label:str):
    df_list=sqlp.get_table_list(conn.engine)

    schema = st.selectbox(label=f'{label} of schema',options=df_list['table_schema'].unique())
    table = st.selectbox(label=f"{label} of table",options=df_list['table_name'][df_list['table_schema']==schema])
    return schema, table