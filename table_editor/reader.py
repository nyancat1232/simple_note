import streamlit as st
import pre as stglobal

import pyplus.sql as sqlp
import pyplus.streamlit as stp
import pandas as pd
import pyplus.pandas as pdp
import pyplus.builtin as bp

with st.sidebar:
    second_ts = stglobal.table_selector('select a table')

    current_tz = st.text_input('current timezone',placeholder='like UTC',value=st.secrets['default_timezone'])

df_with_tag = bp.select_yielder(stglobal.iter_tag_process(second_ts),'filter_tag')

temp=second_ts.get_foreign_tables()
for col in temp:
    bb=second_ts.check_selfref_table(temp[col])
    bb

custom_configs_ro:dict = bp.select_yielder(stglobal.iter_custom_column_configs(second_ts),'readonly')
event=st.dataframe(df_with_tag,column_config=custom_configs_ro,on_select='rerun',selection_mode='single-row')
row = df_with_tag.iloc[event['selection']['rows']].to_dict('records')[0]
types = second_ts.get_types_expanded().to_dict(orient='index')
for col in types:
    try:
        if row[col]:
            pass
    except:
        st.toast(f'skipping column {col}')
        continue

    if row[col] is not None:
        match types[col]['display_type']:
            case 'image_url':
                st.markdown(f'#### {col}')
                st.image(row[col])
            case 'video_url':
                st.markdown(f'#### {col}')
                st.video(row[col])