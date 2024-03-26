import streamlit as st
import pandas as pd

from pre import ex,conn
ex()


from simple_note_funcs.summary import *



cur_sch=st.secrets['summary']['schema']
cur_tab=st.secrets['summary']['table']

summaries=read_from_server(cur_sch,cur_tab,conn)
summaries
for summary_idx in summaries.index:
    cur_row = summaries.loc[summary_idx]
    cur_tab = read_from_server(cur_row['schema_name'],cur_row['table_name'],conn)
    
    try:
        res = sumhandler[cur_row['function']](cur_tab,*cur_row['function_args'])
        st.subheader(f"{cur_row['schema_name']}.{cur_row['table_name']} {cur_row['function_args']}")
        res
        st.slider(**res,disabled=True)
    except:
        st.write(f"{cur_row['function']} not working")
    st.divider()