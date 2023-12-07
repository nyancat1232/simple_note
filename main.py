import streamlit as st
import pandas as pd
from pyplus.streamlit.external import check_password
from pyplus.sql.pgplus import read_from_server
from sqlutil.summary import SummaryHandler
if not check_password():
    st.stop()  # Do not continue if check_password is not True.


sumhandler = SummaryHandler()
sumhandler['max']=max
def func_duration(sr):
    from datetime import datetime,timezone
    recent=max(sr)
    return datetime.now(tz=timezone.utc)-recent
sumhandler['duration']=func_duration
sumhandler['min']=min



cur_sch=st.secrets['summary']['schema']
cur_tab=st.secrets['summary']['table']
conn = st.connection(name='postgresql',type='sql')
summaries=read_from_server(cur_sch,cur_tab,conn)
summaries
for summary_idx in summaries.index:
    cur_row = summaries.loc[summary_idx]
    cur_tab = read_from_server(cur_row['schema_name'],cur_row['table_name'],conn)
    
    sr_column = cur_tab[cur_row['column_name']]
    
    res = sumhandler[cur_row['function']](sr_column)
    res