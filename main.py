import streamlit as st
import pandas as pd
from pyplus.streamlit.external import check_password
from pyplus.sql.pgplus import read_from_server
from sqlutil.summary import SummaryHandler
if not check_password():
    st.stop()  # Do not continue if check_password is not True.


from datetime import datetime,timezone,timedelta
sumhandler = SummaryHandler()
sumhandler['max']=lambda df,arg1,arg2,arg3:max(df[arg1])
def func_duration(df,arg1,arg2,arg3):
    sr= df[arg1]
    recent=max(sr)
    return datetime.now(tz=timezone.utc)-recent
sumhandler['duration']=func_duration
sumhandler['min']=lambda df,arg1,arg2,arg3:min(df[arg1])
def get_weighted_mean_day(df:pd.DataFrame,arg1,arg2,arg3):
    #arg1 => date
    #arg2 => column
    #arg3 => limit
    df['_date_from_now']=datetime.now(tz=timezone.utc)-df[arg1]
    more_than_day1=df['_date_from_now']>timedelta(days=1)
    df['_weight']=1
    df['_weight'][more_than_day1]=df['_date_from_now'][more_than_day1].apply(lambda t:timedelta(days=1)/t)
    df['_weight']=df[arg2]*df['_weight']
    
    df_within_days=df[df['_date_from_now']<timedelta(days=int(arg3))]
    return sum(df_within_days['_weight'])/len(df_within_days)
sumhandler['mean_day']=get_weighted_mean_day


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
        st.write(res)
    except:
        st.write(f"{cur_row['function']} not working")
    st.divider()