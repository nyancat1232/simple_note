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
    st.dataframe(ts_left.read())
with tp['foreign']:
    ts_right=table_selector('select a foreign table')
    st.dataframe(ts_right.read())
tp_mode=stp.TabsPlus('tab','new foreign','convert foreign')
with tp_mode['new foreign']:
    new_foreign_column = st.text_input('new foreign column name')
with tp_mode['convert foreign']:
    column = st.selectbox('select a column',ts_left.read().columns)