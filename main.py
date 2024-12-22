import streamlit as st
import pyplus.sql as sqlp
import checkpoint as cp
import pandas as pd
import os
from sqlalchemy import create_engine

@cp.CheckPointFunctionDecoration
def iter_custom_column_configs(ts:sqlp.TableStructure):
    column_configs = dict()

    types = ts.get_types_expanded().to_dict(orient='index').copy()

    for col in types:
        disable_this_col = False
        if types[col]['is_generated'] == 'ALWAYS':
            disable_this_col = True
        match types[col]['display_type']:
            case 'date':
                column_configs[col] = st.column_config.DateColumn(disabled=disable_this_col)
            case 'timestamp with time zone':
                column_configs[col] = st.column_config.DatetimeColumn(timezone=os.environ['SN_DEFAULT_TIMEZONE'],disabled=disable_this_col)
            case 'url':
                column_configs[col] = st.column_config.LinkColumn(disabled=disable_this_col)
            case 'image_url':
                column_configs[col] = st.column_config.LinkColumn(disabled=disable_this_col)
            case 'video_url':
                column_configs[col] = st.column_config.LinkColumn(disabled=disable_this_col)
            case _:
                column_configs[col] = st.column_config.Column(disabled=disable_this_col)
    
    tss_foreign = ts.get_foreign_tables()
    for col in tss_foreign:
        ids_foreign=tss_foreign[col].read().index.to_list()
        column_configs[col] = st.column_config.SelectboxColumn(f'{col}',options=ids_foreign,width='small')

    column_configs['__hidden']=st.column_config.Column(disabled=True)

    yield column_configs.copy(),'edit'

    for col in types:
        match types[col]['display_type']:
            case 'image_url':
                column_configs[col] = st.column_config.ImageColumn(f'{col}',)

    #Hide columns
    for col in tss_foreign:
        column_configs[col] = None

    col_expanded_tag=ts.get_types_expanded().to_dict('index')
    for col in col_expanded_tag:
        match col_expanded_tag[col]['display_type']:
            case 'tag_string':
                column_configs[col] = None
    yield column_configs.copy(), 'readonly' 

@cp.CheckPointFunctionDecoration
def iter_tag_process(ts:sqlp.TableStructure,hashtag_init_symbol:str='#',hashtag_sub_symbol:str='/'):
    df=ts.read_expand()
    col_expanded_tag=ts.get_types_expanded().to_dict('index')

    def filter_rows(col_3:str):
        match col_expanded_tag[col_3]['display_type']:
            case 'text'|'text_with_tag':
                def extract_tags(vals:list):
                    try:
                        match len(vals):
                            case 1:
                                return [vals[1]]
                            case 0:
                                return [None]
                            case _:
                                return vals[1:]
                    except:
                        return [None]
                def remove_spaces(vals:list):
                    def apply_each(s:str):
                        try:
                            ret = s
                            for ch in ' \n':
                                ll = ret.split(ch)
                                ret = ll[0]
                            return ret
                        except:
                            return s
                    return [apply_each(val) for val in vals]
                def duplicate_super_tags(vals:list):
                    def apply_each(s:str):
                        if s is None:
                            return [s]
                        spl = s.split(hashtag_sub_symbol)
                        return [hashtag_sub_symbol.join(spl[0:1+ind]) for ind,_ in enumerate(spl)]
                    ret_pre = [apply_each(val) for val in vals]
                    ret = []
                    for l in ret_pre:
                        ret += l
                    return ret
                def find_all_tags(sr_tag:pd.Series):
                    return sr_tag.explode().sort_values()\
                                .unique().tolist()
                def contains_tags(ll:list,tags:list)->bool:
                    left = set(ll)
                    right = set(tags)
                    res = right-left
                    if len(res)>0:
                        return False
                    else:
                        return True
                
                sr_tags_extracted=df[col_3].str.split(hashtag_init_symbol)\
                .apply(extract_tags).apply(remove_spaces).apply(duplicate_super_tags)
                all_tags_list = find_all_tags(sr_tags_extracted)
                selected_tags = st.multiselect(f'select tags of {col_3}',all_tags_list,[])
                return sr_tags_extracted.apply(lambda ll:contains_tags(ll,selected_tags))
                
    filt_rows={col:filter_rows(col) for col in col_expanded_tag}
    df_bool_filter = pd.concat(filt_rows,axis=1)
    sr_total_filter = df_bool_filter.all(axis=1)
    df_res = df[sr_total_filter]
    yield df_res, 'filter_rows'


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
        schema_name = st.selectbox('schema name',sqlp.get_schema_list(st.session_state['conn'].engine))
        table_name = st.text_input('table name')
        if st.form_submit_button(label='create table'):
                sqlp.SchemaStructure(schema_name,st.session_state['conn'].engine).create_table(table_name)

    #Select address
    all_tables= sqlp.get_table_list(st.session_state['conn'].engine).to_dict('records')
    current_address=st.selectbox('select address global',all_tables,format_func=lambda x:f"{x['table_schema']}/{x['table_name']}")

selected_table = sqlp.TableStructure(schema_name=current_address['table_schema'],table_name=current_address['table_name'],engine=st.session_state['conn'].engine)
df_with_tag:pd.DataFrame = iter_tag_process(selected_table).filter_rows()
custom_configs_ro:dict = iter_custom_column_configs(selected_table).readonly()
custom_configs_rw_def:dict = iter_custom_column_configs(selected_table).edit()

st.session_state['selected_table'] = selected_table
st.session_state['selected_table_dataframe'] = df_with_tag
st.session_state['selected_table_column_config_ro'] = custom_configs_ro
st.session_state['selected_table_column_config_rw_def'] = custom_configs_rw_def

pg.run()