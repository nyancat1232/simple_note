import streamlit as st
import pandas as pd

import pyplus.sql as sqlp
import pyplus.streamlit as stp


def upload_button(func,label):
    if st.button(label):
        func()
        st.rerun()

ts_first:sqlp.TableStructure = st.session_state['selected_table']
read_result= st.session_state['selected_table_dataframe']
read_result

tp = stp.TabsPlus(layout='tab',titles=['append a column','change column name','change a column order'])

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