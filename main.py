import streamlit as st
import pandas as pd
from pyplus.streamlit.external import check_password
from pyplus.sql.pgplus import read_from_server
from sqlutil.sql_util import table_selection
if not check_password():
    st.stop()  # Do not continue if check_password is not True.


cur_sch=st.secrets['summary']['schema']
cur_tab=st.secrets['summary']['table']
conn = st.connection(name='postgresql',type='sql')
summaries=read_from_server(cur_sch,cur_tab,conn)
summaries
for summary_idx in summaries.index:
    cur_row = summaries.loc[summary_idx]
    cur_tab = read_from_server(cur_row['schema_name'],cur_row['table_name'],conn)

    di_func={
        'max':max,
        'min':min
    }

    res = di_func[cur_row['function']](cur_tab[cur_row['column_name']])
    res