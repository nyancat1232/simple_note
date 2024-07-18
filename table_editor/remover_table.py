import streamlit as st
import pyplus.streamlit as stp
import pyplus.sql as sqlp
import pandas as pd


df_list = sqlp.get_table_list(st.session_state['conn'])
event = st.dataframe(df_list,on_select='rerun',selection_mode='single-row')
row = event['selection']['rows']
address=df_list.loc[row].to_dict('records')[0]
address

"load"
ts = sqlp.TableStructure(address['table_schema'],address['table_name'],st.session_state['conn'].engine)
df_expand = ts.read_expand()
df_expand