import streamlit as st
import pyplus.sql as sqlp
import checkpoint as cp
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
    with st.form(key='create_table'):
        #Create table
        schema_name = st.text_input('schema name',help='schema name that is already exist.')
        table_name = st.text_input('table name')
        if st.form_submit_button(label='create table'):
                sqlp.SchemaStructure(schema_name,st.session_state['conn'].engine).create_table(table_name)

    #Select address
    all_tables= sqlp.get_table_list(st.session_state['conn'].engine).to_dict('records')
    current_address=st.selectbox('select address global',all_tables,format_func=lambda x:f"{x['table_schema']}/{x['table_name']}")

selected_table = sqlp.TableStructure(schema_name=current_address['table_schema'],table_name=current_address['table_name'],engine=st.session_state['conn'].engine)
df_with_tag:pd.DataFrame = stglobal.iter_tag_process(selected_table).filter_rows()
custom_configs_ro:dict = stglobal.iter_custom_column_configs(selected_table).readonly()
custom_configs_rw_def:dict = stglobal.iter_custom_column_configs(selected_table).edit()

st.session_state['selected_table'] = selected_table
st.session_state['selected_table_dataframe'] = df_with_tag
st.session_state['selected_table_column_config_ro'] = custom_configs_ro
st.session_state['selected_table_column_config_rw_def'] = custom_configs_rw_def

pg.run()