import streamlit as st
import pandas as pd

import pre as stglobal

import pyplus.sql as sqlp
import pyplus.streamlit as stp


def upload_button(func,label):
    if st.button(label):
        func()
        st.rerun()

tp = stp.TabsPlus(layout='tab',titles=['create a table'])
with tp['create a table']:
    schema_name = stglobal.init_schema()
    table_name = st.text_input('table name')


    cols = {'':None}
    sttype = {'value':st.column_config.SelectboxColumn('test',options=st.session_state['types'])}
    result_type = st.data_editor(cols,num_rows='dynamic',column_config=sttype)
    result_type

    def upload_create():
        ss = sqlp.SchemaStructure(schema_name=schema_name,engine=st.session_state['conn'].engine)
        ss.create_table(table_name,**result_type)

    upload_button(upload_create,'create table')
