import streamlit as st
import pandas as pd

import pre as stglobal
stglobal.ex()

import pyplus.sql as sqlp
import pyplus.streamlit as stp

tp = stp.TabsPlus('tab','create a table','append a column')

with tp['create a table']:
    schema_name = stglobal.init_schema()
    table_name = st.text_input('table name')


    cols = {'':None}
    sttype = {'value':st.column_config.SelectboxColumn('test',options=stglobal.types)}
    result_type = st.data_editor(cols,num_rows='dynamic',column_config=sttype)
    result_type
    if st.button('create table'):
        ss = sqlp.SchemaStructure(schema_name=schema_name,engine=stglobal.conn.engine)
        res = ss.create_table(table_name,**result_type)
        st.toast('succeed')
        #res.upload_append(**{key:"" for key in result_type})

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