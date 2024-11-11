import streamlit as st
import pandas as pd

import pre as stglobal

import pyplus.sql as sqlp
import pyplus.streamlit as stp


def upload_button(func,label):
    if st.button(label):
        func()
        st.rerun()

with st.sidebar:
    all_records_list= sqlp.get_table_list(st.session_state['conn'].engine).to_dict('records')
    all_table_list = [None]+[".".join([row['table_schema'],row['table_name']]) for row in all_records_list]
    current_address = st.selectbox('select address',all_table_list)
    if current_address is not None:
        current_address = current_address.split('.')
        ts_first = sqlp.TableStructure(schema_name=current_address[0],table_name=current_address[1],engine=st.session_state['conn'].engine)
    else:
        ts_first = None

if ts_first is not None:
    read_result = ts_first.read()
    read_result

    tp = stp.TabsPlus(layout='tab',titles=['append a column','change column name','change a column order'])

    with tp['append a column']:
        df = pd.DataFrame({'name':pd.Series(dtype=pd.StringDtype),'type':pd.Series(dtype=pd.StringDtype)})
        sttype = {'name':st.column_config.TextColumn('name'),'type':st.column_config.SelectboxColumn('type',options=st.session_state['types'])}
        result = st.data_editor(df,num_rows='dynamic',column_config=sttype)
        result = {rec['name']:rec['type'] for rec in result.to_dict(orient='records')}
        result

        def append_columns():
            ts_first.append_column(**result)
        upload_button(append_columns,'append columns')

    with tp['change column name']:
        df_change = pd.DataFrame({'before':read_result.columns,'after':read_result.columns})
        df_change = st.data_editor(df_change,column_config={'before':st.column_config.Column(disabled=True)})
        df_change['changed'] = df_change['before'] != df_change['after']
        df_change
        df_change = df_change[df_change['changed']]
        del df_change['changed']
        df_change

        arg={row['before']: row['after'] for row in df_change.to_dict('records')}
        arg
        def change_names():
            ts_first.change_column_name(**arg)
        upload_button(change_names,'change column names')

    with tp['change a column order']:
        columns=read_result.columns
        df_order = pd.DataFrame({'name':columns,'order':range(len(columns))})
        tp_order = stp.TabsPlus(layout='column',titles=['before','after'])
        with tp_order['before']:
            df_order = st.data_editor(df_order,column_config={'name':st.column_config.Column(disabled=True)})
        with tp_order['after']:
            columns_after = [df_order['name'][ind] for ind in df_order['order']]
            df_order_after = pd.DataFrame({'name':columns_after}) 
            df_order_after
else:
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
