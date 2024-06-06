import streamlit as st
import pandas as pd

import pre as stglobal
stglobal.ex()

import pyplus.sql as sqlp
import pyplus.streamlit as stp

def upload_button(func,label):
    if st.button(label):
        func()
        st.toast(f'Succeed: {label}')

with tp['create a table']:
    schema_name = stglobal.init_schema()
    table_name = st.text_input('table name')


    cols = {'':None}
    sttype = {'value':st.column_config.SelectboxColumn('test',options=stglobal.types)}
    result_type = st.data_editor(cols,num_rows='dynamic',column_config=sttype)
    result_type

    def upload_create():
        ss = sqlp.SchemaStructure(schema_name=schema_name,engine=stglobal.conn.engine)
        ss.create_table(table_name,**result_type)

    upload_button(upload_create,'create table')

with tp['append a column']:
    if (ts_first := stglobal.table_selector()) is not None:
        read_result = ts_first.read_expand()
        read_result

        df = pd.DataFrame([{'name':'','type':''}])
        sttype = {'type':st.column_config.SelectboxColumn('test',options=stglobal.types)}
        result = st.data_editor(df,num_rows='dynamic',column_config=sttype)
        result = {rec['name']:rec['type'] for rec in result.to_dict(orient='records')}
        result

        if st.button('append columns'):
            ts_first.append_column(**result)
            st.rerun()

with tp['change a column order']:
    if (ts_first := stglobal.table_selector('select a table for changing a order')) is not None:
        read_result = ts_first.read_expand()
        read_result

        columns=read_result.columns
        df_order = pd.DataFrame({'name':columns,'order':range(len(columns))})
        tp_order = stp.TabsPlus('column','before','after')
        with tp_order['before']:
            df_order = st.data_editor(df_order,column_config={'name':st.column_config.Column(disabled=True)})
        with tp_order['after']:
            columns_after = [df_order['name'][ind] for ind in df_order['order']]
            df_order_after = pd.DataFrame({'name':columns_after}) 
            df_order_after