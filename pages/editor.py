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
    df_foreign = ts.get_foreign_table()
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

def add_tag_column():
    ts=first_ts
    df=df_expanded

    col_expanded_tag=ts.get_types_expanded().to_dict('index')
    for col in col_expanded_tag:
        match col_expanded_tag[col]['domain_name']:
            case 'text_with_tag':
                df[f'_tags_{col}']=df[col].str.split('#')
                def try_tag(cols:list):
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
                df[f'_tags_{col}']=df[f'_tags_{col}'].apply(lambda cols:try_tag(cols))

first_ts = sqlp.TableStructure(schema,table,conn.engine)
custom_configs_rw:dict = bp.select_yielder(iter_custom_column_configs(first_ts),'edit')
custom_configs_ro:dict = bp.select_yielder(iter_custom_column_configs(first_ts),'readonly')
df_read = first_ts.read()
df_expanded = first_ts.read_expand()

add_tag_column()

if st.checkbox('readonly'):
    st.dataframe(df_expanded,column_config=custom_configs_ro)
    st.stop()

df_edited = st.data_editor(df_expanded,disabled=first_ts.refresh_identity(),column_config=custom_configs_rw)

st.subheader('edit mode')

df_compare2=df_edited.compare(df_expanded,keep_equal=False,result_names=('new','old'))

recs = filter_new(df_compare2)

tp = stp.TabsPlus('popover','type',*[f'upload of {id_row}' for id_row in recs])

with tp['type']:
    st.write(df_edited.dtypes)

for row in recs:
    with tp[f'upload of {row}']:
        recs[row]

if st.button('upload'):
    for row in recs:
        row
        recs[row]
        first_ts.upload(row,**recs[row])


st.subheader('append mode')

df_append = pdp.empty_records(df_expanded)
df_append = df_append.reset_index(drop=True)

col_foreign,col_foreign_expanded = extract_foreign_column(first_ts)

custom_configs_rw_foreign = {}

if len(col_foreign)>0:
    foreign_expand = st.multiselect('expand foreign column',col_foreign)

    foreign_filter = df_read.columns.to_list()
    for col in foreign_expand:
        orig_index = foreign_filter.index(col)
        foreign_filter.pop(orig_index)
        for col_expand in df_expanded.columns:
            if col_expand.split('.')[0] == col:
                foreign_filter.insert(orig_index,col_expand)
    df_append = df_append[foreign_filter]

    col_foreign_not_expanded = col_foreign-set(foreign_expand)
    if len(col_foreign_not_expanded)>0:
        df_foreign_not = first_ts.get_foreign_table()
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

df_append = st.data_editor(df_append,num_rows='dynamic',column_config={**custom_configs_rw,**custom_configs_rw_foreign})

appends = df_append.to_dict(orient='records')
if st.button('append'):
    for append in appends:
        first_ts.upload_append(**append)