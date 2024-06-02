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
with tp['foreign']:
    ts_right=table_selector('select a foreign table')
with tp['original']:
    df_left=ts_left.read()
    event_left = st.dataframe(df_left,on_select='rerun',selection_mode='single-column')
with tp['foreign']:
    df_right=ts_right.read()
    event_right = st.dataframe(df_right,on_select='rerun',selection_mode='single-column')

left_column = event_left['selection']['columns'][0]
right_column = event_right['selection']['columns'][0]
df_right_to_id = ts_right.get_local_val_to_id(right_column)

if left_column is None:
    raise NotImplementedError("Not None")
else:
    override = st.checkbox('override a column')
    if override:
        df_left[left_column]=df_left[left_column].apply(lambda val:df_right_to_id[val])
        df_left
        raise NotImplementedError('No override')
    else:
        local_column = st.text_input('new id column name')
        df_left[local_column]=df_left[left_column].apply(lambda val:df_right_to_id[val])
        df_left