import streamlit as st
import pyplus.sql as sqlp
import pyplus.builtin as bp
import pre as stglobal
import pandas as pd
import os
from sqlalchemy import create_engine

page_title = 'Simple note'
page_icon='📒'
st.set_page_config(page_title=page_title,page_icon=page_icon,layout='wide')

#Set global vars
if 'conn' not in st.session_state:
    st.session_state['conn'] = create_engine(os.environ['SN_ADDRESS'])

st.session_state['types']=['bigint','double precision','text','timestamp with time zone','boolean','url','image_url','video_url','text_with_tag']

pg = st.navigation({'main':[st.Page('table_editor/reader.py',title='reader'),
                            st.Page('table_editor/editor.py',title='editor'),
                            st.Page('table_editor/append_rows.py',title='append'),
                            st.Page('table_editor/table_editor.py',title='table or column editor'),
                            st.Page('table_editor/remover_table.py',title='row or column deletion'),
                            ],
                    'foreign':[
                            st.Page('table_editor/connect_foreign.py',title='foreign connection'),
                            st.Page('table_editor/merge_foreign.py',title='merge foreign'),
                            ],
                    'initialization':[
                            st.Page('new_page/init_domain.py',title='initialization'),
                    ]
                    })

with st.sidebar:
    all_records_list= sqlp.get_table_list(st.session_state['conn'].engine).to_dict('records')
    all_table_list = [".".join([row['table_schema'],row['table_name']]) for row in all_records_list]
    current_address=[st.selectbox('select address global',all_table_list).split('.')]

selected_table = sqlp.TableStructure(schema_name=current_address[0][0],table_name=current_address[0][1],engine=st.session_state['conn'].engine)

with st.sidebar:
    df_with_tag:pd.DataFrame = bp.CheckPointFunction(stglobal.iter_tag_process)(selected_table).filter_tag()
custom_configs_ro:dict = bp.CheckPointFunction(stglobal.iter_custom_column_configs)(selected_table).readonly()
custom_configs_rw_def:dict = bp.CheckPointFunction(stglobal.iter_custom_column_configs)(selected_table).edit()

st.session_state['selected_table'] = selected_table
st.session_state['selected_table_dataframe'] = df_with_tag
st.session_state['selected_table_column_config_ro'] = custom_configs_ro
st.session_state['selected_table_column_config_rw_def'] = custom_configs_rw_def

pg.run()