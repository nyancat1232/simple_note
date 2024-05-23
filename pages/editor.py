import streamlit as st
from pre import conn,ex,sn_config_table,title
ex()
st.set_page_config(page_title=title,page_icon='📒',layout='wide')

import pyplus.sql as sqlp
import pyplus.streamlit as stp
import pandas as pd
import pyplus.pandas as pdp
import pyplus.builtin as bp
from typing import Any

with st.sidebar:
    df_list=sqlp.get_table_list(conn.engine)
    received_queries=st.query_params
    def get_appender(query:str,ll:list):
        appender=dict()
        try:
            appender['index']=ll.index(received_queries[query])
        except:
            try:
                st.toast(f'{received_queries[query]} not in {query}')
            except:
                st.toast(f'No {query}')
        return appender

    li_schemas:list=df_list['table_schema'].unique().tolist()
    schema = st.selectbox(label=f'schema',options=li_schemas,**get_appender('schema',li_schemas))

    li_tables=df_list['table_name'][df_list['table_schema']==schema].tolist()
    table = st.selectbox(label=f"table",options=li_tables,**get_appender('table',li_tables))

    current_tz = st.text_input('current timezone',placeholder='like UTC',value='UTC')

tagize = sqlp.TableStructure(sn_config_table['schema'],sn_config_table['table'],conn.engine)
st.dataframe(tagize.read())

def filter_new(df:pd.DataFrame,col='new')->dict[int,dict[str,Any]]:
    d={upper_col[0]:df[upper_col[0],col] for upper_col in df.columns}
    df_d = pd.DataFrame(d)
    ret_dict=df_d.to_dict(orient='index')
    for row in ret_dict:
        ret_dict[row]={col:ret_dict[row][col] for col in ret_dict[row] if ret_dict[row][col] is not None }
    return ret_dict

def iter_custom_column_configs(ts:sqlp.TableStructure):
    column_configs = dict()

    types = ts.get_types_expanded().to_dict(orient='index')
    df_foreign = ts.get_foreign_tables_list()
    for col in df_foreign.index.tolist():
        ts_sub = sqlp.TableStructure(df_foreign.loc[col]['upper_schema'],df_foreign.loc[col]['upper_table'],conn.engine)
        ids_foreign=ts_sub.read().index.to_list()
        column_configs[col] = st.column_config.SelectboxColumn(f'{col}',options=ids_foreign,width='small')

    for col in types:
        match types[col]['data_type']:
            case 'timestamp with time zone':
                column_configs[col] = st.column_config.DatetimeColumn(f'{col}',timezone=current_tz)
            case 'date':
                column_configs[col] = st.column_config.DateColumn(f'{col}')

    for col in types:
        match types[col]['domain_name']:
            case 'url':
                column_configs[col] = st.column_config.LinkColumn(f'{col}')
            case 'image_url':
                column_configs[col] = st.column_config.LinkColumn(f'{col}')
    
    column_configs['__hidden']=st.column_config.Column(disabled=True)

    yield column_configs.copy(),'edit'

    for col in types:
        match types[col]['domain_name']:
            case 'image_url':
                column_configs[col] = st.column_config.ImageColumn(f'{col}',)

    #Hide columns
    for col in df_foreign.index.tolist():
        column_configs[col] = None

    col_expanded_tag=ts.get_types_expanded().to_dict('index')
    for col in col_expanded_tag:
        match col_expanded_tag[col]['domain_name']:
            case 'tag_string':
                column_configs[col] = None
    yield column_configs.copy(), 'readonly' 

def extract_foreign_column(ts:sqlp.TableStructure)->tuple[set,set]:
    df_read = ts.read()
    df_expanded = ts.read_expand(remove_original_id=True)
    col_ex = set(df_expanded.columns.to_list())
    col_r = set(df_read.columns.to_list())
    col_non_foreign = col_ex&col_r
    col_foreign_ex = col_ex-col_non_foreign
    col_foreign_r = col_r-col_non_foreign
    return col_foreign_r,col_foreign_ex

def iter_tag_process(ts:sqlp.TableStructure):
    df=ts.read_expand()
    col_expanded_tag=ts.get_types_expanded().to_dict('index')

    for col in col_expanded_tag:
        match col_expanded_tag[col]['domain_name']:
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
                            ll = s.split(' ')
                            return ll[0]
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

        df = df[sr_contain_all]
    yield df, 'filter_tag'
    


second_ts = sqlp.TableStructure(schema,table,conn.engine)
df_with_tag = bp.select_yielder(iter_tag_process(second_ts),'filter_tag')

temp=second_ts.get_foreign_tables()
for col in temp:
    bb=second_ts.check_selfref_table(temp[col])
    bb

if st.checkbox('readonly'):
    custom_configs_ro:dict = bp.select_yielder(iter_custom_column_configs(second_ts),'readonly')
    st.dataframe(df_with_tag,column_config=custom_configs_ro)
else:
    st.subheader('edit mode')
    custom_configs_rw:dict = bp.select_yielder(iter_custom_column_configs(second_ts),'edit')
    df_edited = st.data_editor(df_with_tag,disabled=second_ts.refresh_identity(),column_config=custom_configs_rw)

    recs = filter_new(df_edited.compare(df_with_tag,keep_equal=False,result_names=('new','old')))

    tp = stp.TabsPlus('popover','type',*[f'upload of {id_row}' for id_row in recs])

    with tp['type']:
        st.write(df_edited.dtypes)

    for row in recs:
        with tp[f'upload of {row}']:
            recs[row]

    if st.button('upload'):
        for row in recs:
            st.toast(f'{row}\n{recs[row]}')
            second_ts.upload(row,**recs[row])
        st.rerun()


    st.subheader('append mode')

    df_append = pdp.empty_records(df_with_tag)
    df_append = df_append.reset_index(drop=True)

    col_foreign,col_foreign_expanded = extract_foreign_column(second_ts)

    custom_configs_rw_foreign = {}

    if len(col_foreign)>0:
        foreign_expand = st.multiselect('expand foreign column',col_foreign)
        
        df_read5 = second_ts.read()
        foreign_filter = df_read5.columns.to_list()
        for col in foreign_expand:
            orig_index = foreign_filter.index(col)
            foreign_filter.pop(orig_index)
            for col_expand in df_with_tag.columns:
                if col_expand.split('.')[0] == col:
                    foreign_filter.insert(orig_index,col_expand)
        df_append = df_append[foreign_filter]

        col_foreign_not_expanded = col_foreign-set(foreign_expand)
        if len(col_foreign_not_expanded)>0:
            df_foreign_not = second_ts.get_foreign_tables_list()
            df_foreign_not = df_foreign_not.loc[list(col_foreign_not_expanded)]
            foreign_not = df_foreign_not.to_dict(orient='index')
            tab_or_col=stp.TabsPlus('popover',*foreign_not)
            for col in foreign_not:
                ts_sub = sqlp.TableStructure(foreign_not[col]['upper_schema'],foreign_not[col]['upper_table'],conn.engine)
                df_display=ts_sub.read_expand()
                conf = bp.select_yielder(iter_custom_column_configs(ts_sub),'readonly')
                
                #display
                with tab_or_col[col]:
                    col
                    st.dataframe(df_display,column_config=conf)

    for col in df_append.columns.to_list():
        if col.startswith('_'):
            del df_append[col]
    
    if len(df_append.columns)<2:
        st.warning('Problem when column is only one. ValueError: setting an array element with a sequence')
        df_append['__hidden']=df_append.index
    df_append = st.data_editor(df_append,num_rows='dynamic',column_config={**custom_configs_rw,**custom_configs_rw_foreign})
    if len(df_append.columns)<2:
        st.warning('Problem when column is only one. ValueError: setting an array element with a sequence')
        del df_append['__hidden']

    appends = df_append.to_dict(orient='records')
    if st.button('append'):
        for append in appends:
            second_ts.upload_append(**append)
        st.toast('append')
        st.rerun()