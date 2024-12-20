import streamlit as st
import pyplus.streamlit as stp
import pandas as pd
import pyplus.sql as sqlp

"Need to implement second table selection"
conn = st.session_state['conn']
ts:sqlp.TableStructure = st.session_state['selected_table']
df:pd.DataFrame = st.session_state['selected_table_dataframe']

selected_column_left = st.dataframe(df,on_select='rerun',selection_mode='single-column')['selection']['columns']
if not selected_column_left:
    selected_column_left = st.text_input('New column name')
    override = False
else:
    selected_column_left = selected_column_left[0]
    override = True

all_tables= sqlp.get_table_list(st.session_state['conn'].engine).to_dict('records')
address_right=st.selectbox('select a second table',all_tables,format_func=lambda x:f"{x['table_schema']}/{x['table_name']}")

ts_right = sqlp.TableStructure(schema_name=address_right['table_schema'],table_name=address_right['table_name'],engine=st.session_state['conn'].engine)
df_right = ts_right.read()
if override:
    selected_column_right = st.dataframe(df_right,on_select='rerun',selection_mode='single-column')['selection']['columns']

    if not selected_column_right:
        selected_column_right = ts_right.get_identity()[0]
    df_merged = df.merge(df_right.reset_index(),left_on=selected_column_left,right_on=selected_column_right,how='left')
    df_merged
else:
    df_right
    if st.button('upload'):
        st.toast('uploading')
        ts.append_column(**{selected_column_left:'bigint'})
        ts.connect_foreign_column(ts_right,selected_column_left)
        st.rerun()