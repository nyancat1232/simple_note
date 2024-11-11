import streamlit as st
import pyplus.streamlit as stp
import pyplus.sql as sqlp
import pandas as pd


"load"
ts:sqlp.TableStructure = st.session_state['selected_table']
df_expand = ts.read_expand()
df_expand

"select"
event = st.dataframe(df_expand,on_select='rerun',selection_mode=['multi-column','multi-row'])
event

"remove col"
df_expand[event['selection']['columns']]
event['selection']['columns']
if st.button('delete columns'):
    for col in event['selection']['columns']:
        st.toast(col)
        ts.delete_column(col)
    st.rerun()

"remove row"
df_filtered_row=df_expand.iloc[event['selection']['rows']]
rows=df_filtered_row.index.to_list()
rows
if st.button('delete rows'):
    for row in rows:
        st.toast(row)
        ts.delete_row(row)
    st.rerun()