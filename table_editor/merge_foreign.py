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

"select"
foreigns = ts.get_foreign_tables()
merge = st.selectbox('merge this local foreign id',foreigns)

"rename"
def apply_check(col):
    new_col=col[col.find('.')+1:] 
    if new_col in df_expand.columns:
        return new_col+'__'+col[:col.find('.')]
    else:
        return new_col
replacer = {col:apply_check(col) for col in df_expand.columns if col.startswith(merge+'.')}
df_expand = df_expand.rename(columns= replacer)
df_expand

"filter uploader"
df_expand = df_expand[[replacer[key] for key in replacer]]
df_expand