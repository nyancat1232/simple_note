from pre import conn,ex,table_selector
ex()
import streamlit as st
import pyplus.sql as sqlp
import pyplus.streamlit as stp
import pandas as pd
import pyplus.pandas as pdp
import pyplus.builtin as bp

with st.sidebar:
    schema,table=table_selector('select table')
    current_tz = st.text_input('current timezone',placeholder='like UTC',value='UTC')

first_ts = sqlp.TableStructure(schema,table,conn.engine)

def filter_new(df:pd.DataFrame,col='new')->pd.DataFrame:
    d={upper_col[0]:df[upper_col[0],col] for upper_col in df.columns}
    return pd.DataFrame(d)

def iter_custom_column_configs(ts:sqlp.TableStructure):
    column_configs = dict()

    types = ts.get_types_expanded().to_dict(orient='index')

    types_dtwithtimezone = {col for col in types if types[col]['data_type'] == 'timestamp with time zone'}
    for col in types_dtwithtimezone:
        column_configs[col] = st.column_config.DatetimeColumn(f'{col}',timezone=current_tz)
    yield 'edit', column_configs.copy()
    types_link = {col for col in types if types[col]['domain_name'] == 'url'}
    types_img = {col for col in types if types[col]['domain_name'] == 'image_url'}
    for col in types_link:
        column_configs[col] = st.column_config.LinkColumn(f'{col}')
    for col in types_img:
        column_configs[col] = st.column_config.ImageColumn(f'{col}',)
    
    yield 'readonly', column_configs.copy()

def extract_foreign_column(ts:sqlp.TableStructure)->tuple[set,set]:
    df_read = ts.read()
    df_expanded = ts.read_expand(remove_original_id=True)
    col_ex = set(df_expanded.columns.to_list())
    col_r = set(df_read.columns.to_list())
    col_non_foreign = col_ex&col_r
    col_foreign_ex = col_ex-col_non_foreign
    col_foreign_r = col_r-col_non_foreign
    return col_foreign_r,col_foreign_ex

custom_configs_rw = bp.select_yielder(iter_custom_column_configs(first_ts),'edit')
custom_configs_ro = bp.select_yielder(iter_custom_column_configs(first_ts),'readonly')
df_read = first_ts.read()
df_expanded = first_ts.read_expand()
if st.checkbox('readonly'):
    st.dataframe(df_expanded,column_config=custom_configs_ro)
    st.stop()

df_edited = st.data_editor(df_expanded,disabled=first_ts.refresh_identity(),column_config=custom_configs_rw)

st.subheader('edit mode')

df_compare2=df_edited.compare(df_expanded,keep_equal=False,result_names=('new','old'))

df_new=filter_new(df_compare2)
recs = df_new.to_dict(orient='index')

for row in recs:
    row
    recs[row]

if st.button('upload'):
    for row in recs:
        row
        recs[row]
        first_ts.upload(row,**recs[row])


st.subheader('append mode')

df_append = pdp.empty_records(df_expanded)
df_append = df_append.reset_index(drop=True)
#for col in df_read.columns:
#    df_append[col] = pd.Series([None for _ in df_append.index])


col_foreign,col_foreign_expanded = extract_foreign_column(first_ts)

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
        tab_or_col=stp.TabsPlus(connection='column',tabs=foreign_not)
        for col in foreign_not:
            with tab_or_col[col]:
                col
                ts_sub = sqlp.TableStructure(foreign_not[col]['upper_schema'],foreign_not[col]['upper_table'],conn.engine)
                df_display=ts_sub.read_expand()
                conf = bp.select_yielder(iter_custom_column_configs(ts_sub),'readonly')
                st.dataframe(df_display,column_config=conf)

df_append = st.data_editor(df_append,num_rows='dynamic',column_config=custom_configs_rw)

appends = df_append.to_dict(orient='records')
if st.button('append'):
    for append in appends:
        first_ts.upload_append(**append)