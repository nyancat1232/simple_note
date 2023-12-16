import streamlit as st
import pandas as pd
from pyplus.streamlit.external import check_password
from pyplus.sql.pgplus import read_from_server
if not check_password():
    st.stop()  # Do not continue if check_password is not True.


from simple_note_funcs.summary import *



cur_sch=st.secrets['summary']['schema']
cur_tab=st.secrets['summary']['table']
conn = st.connection(name='postgresql',type='sql')
summaries=read_from_server(cur_sch,cur_tab,conn)
summaries
for summary_idx in summaries.index:
    cur_row = summaries.loc[summary_idx]
    cur_tab = read_from_server(cur_row['schema_name'],cur_row['table_name'],conn)
    
    try:
        res = sumhandler[cur_row['function']](cur_tab,cur_row['function_arg1'],cur_row['function_arg2'],cur_row['function_arg3'])
        st.subheader(f"{cur_row['schema_name']}.{cur_row['table_name']} {cur_row['function_arg1']} {cur_row['function_arg2']}")
        res
        st.slider(**res,disabled=True)
    except:
        st.write(f"{cur_row['function']} not working")
    st.divider()