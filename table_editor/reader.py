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

def iter_custom_column_configs(ts:sqlp.TableStructure):
    column_configs = dict()

    types = ts.get_types_expanded().to_dict(orient='index').copy()

    with st.expander('debug types of the current table.'):
        types
    for col in types:
        disable_this_col = False
        if types[col]['is_generated'] == 'ALWAYS':
            disable_this_col = True
        match types[col]['display_type']:
            case 'date':
                column_configs[col] = st.column_config.DateColumn(disabled=disable_this_col)
            case 'timestamp with time zone':
                column_configs[col] = st.column_config.DatetimeColumn(timezone=current_tz,disabled=disable_this_col)
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

def iter_tag_process(ts:sqlp.TableStructure):
    df=ts.read_expand()
    col_expanded_tag=ts.get_types_expanded().to_dict('index')

    for col in col_expanded_tag:
        match col_expanded_tag[col]['display_type']:
            case 'text_with_tag':
                df[f'_tags_{col}']=df[col].str.split('#')
                def extract_tags(cols:list):
                    try:
                        match len(cols):
                            case 1:
                                return [cols[1]]
                            case 0:
                                return [None]
                            case _:
                                return cols[1:]
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
                        spl = s.split(':')
                        return [':'.join(spl[0:1+ind]) for ind,_ in enumerate(spl)]
                    ret_pre = [apply_each(val) for val in vals]
                    ret = []
                    for l in ret_pre:
                        ret += l
                    return ret

                df[f'_tags_{col}']=df[f'_tags_{col}'].apply(extract_tags).apply(remove_spaces).apply(duplicate_super_tags)
    yield df, 'add_tag_column'
    
    col_tags = [a for a  in df.columns.to_list() if a.startswith('_tags_')]
    for col in col_tags:
        sr_tag = df[col].explode().sort_values()
        all_tags = sr_tag.unique().tolist()
        selected_tags = st.multiselect(f'select tags of {col}',all_tags,[])
        def contains_tags(ll:list,tags:list)->bool:
            left = set(ll)
            right = set(tags)
            res = right-left
            if len(res)>0:
                return False
            else:
                return True
        sr_contain_all = df[col].apply(lambda ll:contains_tags(ll,selected_tags))
        if len(df.index)>0:
            df = df[sr_contain_all]
        else:
            st.warning('empty')
    yield df, 'filter_tag'
    


df_with_tag = bp.select_yielder(iter_tag_process(second_ts),'filter_tag')

temp=second_ts.get_foreign_tables()
for col in temp:
    bb=second_ts.check_selfref_table(temp[col])
    bb

custom_configs_ro:dict = bp.select_yielder(iter_custom_column_configs(second_ts),'readonly')
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