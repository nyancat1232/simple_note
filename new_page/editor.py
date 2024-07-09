import streamlit as st
from pre import table_selector

import pyplus.sql as sqlp
import pyplus.streamlit as stp
import pandas as pd
import pyplus.pandas as pdp
import pyplus.builtin as bp

with st.sidebar:
    second_ts = table_selector('select a table')

    current_tz = st.text_input('current timezone',placeholder='like UTC',value=st.secrets['default_timezone'])
    b_readonly = st.checkbox('readonly')

def iter_custom_column_configs(ts:sqlp.TableStructure):
    column_configs = dict()

    types = ts.get_types_expanded().to_dict(orient='index').copy()
    tss_foreign = ts.get_foreign_tables()
    for col in tss_foreign:
        ids_foreign=tss_foreign[col].read().index.to_list()
        column_configs[col] = st.column_config.SelectboxColumn(f'{col}',options=ids_foreign,width='small')

    with st.expander('debug types of the current table.'):
        types
    for col in types:
        disable_this_col = False
        if types[col]['is_generated'] == 'ALWAYS':
            disable_this_col = True
        match types[col]['display_type']:
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

def extract_foreign_column(ts:sqlp.TableStructure)->tuple[set,set]:
    tss_foreign = ts.get_foreign_tables()
    col_foreign_r = set((local_foreign_col for local_foreign_col in tss_foreign))
    col_foreign_ex = set()
    for col_local_foreign in tss_foreign:
        foreign_columns = tss_foreign[col_local_foreign].read_expand().columns.to_list()
        foreign_columns = set((f'{col_local_foreign}.{col}' for col in foreign_columns))
        col_foreign_ex = col_foreign_ex|foreign_columns
    
    return col_foreign_r,col_foreign_ex

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

if b_readonly:
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
else:
    st.subheader('edit mode')
    custom_configs_rw:dict = bp.select_yielder(iter_custom_column_configs(second_ts),'edit')
    with st.expander('column config'):
        custom_configs_rw
    df_edited = st.data_editor(df_with_tag,disabled=second_ts.column_identity,column_config=custom_configs_rw)

    idname_df_edited = df_edited.index.name
    def func_melt(df:pd.DataFrame):
        df_reset = df.copy().reset_index()
        return df_reset.melt(id_vars='id',value_name='_sn_value')
    df_edited_melt=func_melt(df_edited)
    df_with_tag_melt=func_melt(df_with_tag)
    with st.expander('debug'):
        tp_debug = stp.TabsPlus(layout='column',titles=['before','after'])
        with tp_debug['before']:
            df_edited_melt
        with tp_debug['after']:
            df_with_tag_melt
        df_compared = df_edited_melt.compare(df_with_tag_melt)
        changed=df_compared.index.to_list()
        df_temp = df_edited_melt.loc[changed]
        df_temp
        recs=dict()
        for temp in df_temp.to_dict('records'):
            if temp['id'] not in recs:
                recs[temp['id']] = {}
            recs[temp['id']][temp['variable']] = temp['_sn_value']
        recs
    if st.button('upload'):
        for row_id in recs:
            st.toast(f'{row_id}:{recs[row_id]}')
            second_ts.upload(id_row=row_id,**recs[row_id])
        st.rerun()


    st.subheader('append mode')

    df_append = pdp.empty_records(df_with_tag)
    df_append = df_append.reset_index(drop=True)

    col_foreign,col_foreign_expanded = extract_foreign_column(second_ts)

    custom_configs_rw_foreign = {}

    if len(col_foreign)>0:
        tss_foreign = second_ts.get_foreign_tables()
        
        tab_or_col=stp.TabsPlus(layout='column',titles=tss_foreign,hide_titles=False)
        for col_local_foreign in tss_foreign:
            ts_sub = tss_foreign[col_local_foreign]
            df_display=ts_sub.read_expand()
            conf = bp.select_yielder(iter_custom_column_configs(ts_sub),'readonly')
            
            #display
            with tab_or_col[col_local_foreign]:
                st.dataframe(df_display,column_config=conf)

    for col in df_append.columns.to_list():
        if col.startswith('_'):
            del df_append[col]
    
    cond_satisfies_warning = len(df_append.columns)<3
    if cond_satisfies_warning:
        st.warning('Problem when column is only one. ValueError: setting an array element with a sequence')
        df_append['__hidden']=df_append.index
    df_append = st.data_editor(df_append,num_rows='dynamic',column_config={**custom_configs_rw,**custom_configs_rw_foreign})
    if cond_satisfies_warning:
        st.warning('Problem when column is only one. ValueError: setting an array element with a sequence')
        del df_append['__hidden']
    
    appends = df_append.to_dict(orient='records')
    with st.expander('upload preview'):
        appends
    if st.button('append'):
        second_ts.upload_appends(*appends)
        st.toast('append')
        st.rerun()