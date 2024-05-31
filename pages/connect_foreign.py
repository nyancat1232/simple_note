import streamlit as st
from pre import conn,ex,sn_config_table,title
ex()


import pyplus.sql as sqlp
import pyplus.streamlit as stp
import pandas as pd
import pyplus.pandas as pdp
import pyplus.builtin as bp
from typing import Any

df_lists = sqlp.get_table_list(conn)
df_lists
schema = st.selectbox('schema',df_lists['table_schema'].unique().tolist())
table = st.selectbox('table',df_lists[df_lists['table_schema']==schema]['table_name'].unique().tolist())