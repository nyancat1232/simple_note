import streamlit as st
from pre import conn,ex,table_selector
ex()


import pyplus.sql as sqlp
import pyplus.streamlit as stp
import pandas as pd
import pyplus.pandas as pdp
import pyplus.builtin as bp
from typing import Any

tp=stp.TabsPlus('column','original','foreign')
with tp['original']:
    ts_left=table_selector()
    df_left=ts_left.read()
    st.dataframe(df_left)
with tp['foreign']:
    ts_right=table_selector('select a foreign table')
    df_right=ts_right.read()
    st.dataframe(df_right)
tp_mode=stp.TabsPlus('tab','new foreign','convert foreign')
with tp_mode['new foreign']:
    new_foreign_column = st.text_input('new foreign column name')
with tp_mode['convert foreign']:
    column = st.selectbox('select a column',ts_left.read().columns)