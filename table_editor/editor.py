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

st.subheader('edit mode')
custom_configs_rw:dict = bp.select_yielder(stglobal.iter_custom_column_configs(second_ts),'edit')
df_edited = st.data_editor(df_with_tag,disabled=second_ts.column_identity,column_config=custom_configs_rw)

idname_df_edited = df_edited.index.name
def func_melt(df:pd.DataFrame):
    df_reset = df.copy().reset_index()
    return df_reset.melt(id_vars='id',value_name='_sn_value')
df_edited_melt=func_melt(df_edited)
df_with_tag_melt=func_melt(df_with_tag)
df_compared = df_edited_melt.compare(df_with_tag_melt)
changed=df_compared.index.to_list()
df_temp = df_edited_melt.loc[changed]
recs=dict()
for temp in df_temp.to_dict('records'):
    if temp['id'] not in recs:
        recs[temp['id']] = {}
    recs[temp['id']][temp['variable']] = temp['_sn_value']

if st.button('upload'):
    for row_id in recs:
        st.toast(f'{row_id}:{recs[row_id]}')
        second_ts.upload(id_row=row_id,**recs[row_id])
    st.rerun()


st.subheader('append mode')

df_append = pdp.empty_records(second_ts.read())
df_append = df_append.reset_index(drop=True)

tss_foreign = second_ts.get_foreign_tables()

tab_or_col=stp.TabsPlus(layout='column',titles=tss_foreign,hide_titles=False)
for col_local_foreign in tss_foreign:
    ts_sub = tss_foreign[col_local_foreign]
    df_display=ts_sub.read_expand()
    conf = bp.select_yielder(stglobal.iter_custom_column_configs(ts_sub),'readonly')
    
    #display
    with tab_or_col[col_local_foreign]:
        st.dataframe(df_display,column_config=conf)

for col in df_append.columns.to_list():
    if col.startswith('_'):
        del df_append[col]
cond_satisfies_warning = len(df_append.columns)<2
if cond_satisfies_warning:
    st.warning('Problem when column is only one. ValueError: setting an array element with a sequence')
    df_append['__hidden']=df_append.index
df_append = st.data_editor(df_append,num_rows='dynamic',column_config=custom_configs_rw)
if cond_satisfies_warning:
    st.warning('Problem when column is only one. ValueError: setting an array element with a sequence')
    del df_append['__hidden']

appends = df_append.to_dict(orient='records')

if st.button('append'):
    second_ts.upload_appends(*appends)
    st.toast('append')
    st.rerun()