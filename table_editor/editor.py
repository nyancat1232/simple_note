import streamlit as st
import pre as stglobal

import pyplus.sql as sqlp
import pyplus.streamlit as stp
import pandas as pd
import pyplus.pandas as pdp
import pyplus.builtin as bp
from contextlib import contextmanager

with st.sidebar:
    second_ts = stglobal.table_selector('select a table')

df_with_tag = bp.CheckPointFunction(stglobal.iter_tag_process).filter_tag(second_ts)

temp=second_ts.get_foreign_tables()
for col in temp:
    bb=second_ts.check_selfref_table(temp[col])
del col

st.subheader('edit mode')
custom_configs_rw_def:dict = bp.CheckPointFunction(stglobal.iter_custom_column_configs).edit(second_ts)
custom_configs_rw_edit=custom_configs_rw_def.copy()
df_edited = st.data_editor(df_with_tag,disabled=second_ts.column_identity,column_config=custom_configs_rw_edit)

def get_comparison(df_new,df_old):
    def func_melt(df:pd.DataFrame):
        df_reset = df.copy().reset_index()
        return df_reset.melt(id_vars='id',value_name='_sn_value')
    df_new_melt=func_melt(df_new)
    df_old_melt=func_melt(df_old)
    df_compared = df_new_melt.compare(df_old_melt)
    changed=df_compared.index.to_list()
    df_temp = df_new_melt.loc[changed]
    recs=dict()
    for temp in df_temp.to_dict('records'):
        if temp['id'] not in recs:
            recs[temp['id']] = {}
        recs[temp['id']][temp['variable']] = temp['_sn_value']
    return recs

recs=get_comparison(df_edited,df_with_tag)

if st.button('upload'):
    for row_id in recs:
        st.toast(f'{row_id}:{recs[row_id]}')
        second_ts.upload(id_row=row_id,**recs[row_id])
    del row_id
    st.rerun()


st.subheader('append mode')
custom_configs_rw_append=custom_configs_rw_def.copy()

df_append = pdp.empty_records(second_ts.read())
df_append = df_append.reset_index(drop=True)

tss_foreign = second_ts.get_foreign_tables()

selected_col_convert=dict()
"Select a column"
tab_or_col=stp.TabsPlus(layout='column',titles=tss_foreign,hide_titles=False)
for col_local_foreign in tss_foreign:
    ts_sub = tss_foreign[col_local_foreign]
    df_display=ts_sub.read_expand()
    conf = bp.CheckPointFunction(stglobal.iter_custom_column_configs).readonly(ts_sub)
    
    #display
    with tab_or_col[col_local_foreign]:
        selected_col_convert[col_local_foreign]=st.dataframe(df_display,column_config=conf,selection_mode='single-column',on_select='rerun',key=f'convert_of_{col_local_foreign}')['selection']['columns']
        if len(selected_col_convert[col_local_foreign])>0:
            selected_col_convert[col_local_foreign]=selected_col_convert[col_local_foreign][0]
            selections=df_display[selected_col_convert[col_local_foreign]].unique().dropna().tolist()
            custom_configs_rw_append[col_local_foreign+'__conversion']=st.column_config.SelectboxColumn(f'{col_local_foreign}(conversion from {selected_col_convert[col_local_foreign]})',options=selections)
            df_append[col_local_foreign+'__conversion']=pd.Series()
            del df_append[col_local_foreign]
del col_local_foreign

for col in df_append.columns.to_list():
    if col.startswith('_'):
        del df_append[col]
del col

cond_satisfies_warning = len(df_append.columns)<2
if cond_satisfies_warning:
    st.warning('Problem when column is only one. ValueError: setting an array element with a sequence')
    df_append['__hidden']=df_append.index
df_append = st.data_editor(df_append,num_rows='dynamic',column_config=custom_configs_rw_append)
if cond_satisfies_warning:
    st.warning('Problem when column is only one. ValueError: setting an array element with a sequence')
    del df_append['__hidden']

"Conversion to ids"
for col in [col for col in df_append.columns.to_list() if col.endswith('__conversion')]:
    original_col=col[:col.find('__conversion')]
    df_append[original_col]=df_append[col].apply(lambda val:tss_foreign[original_col].get_local_val_to_id(selected_col_convert[original_col])[val])
    del df_append[col]
df_append

appends = df_append.to_dict(orient='records')

if st.button('append'):
    second_ts.upload_appends(*appends)
    st.toast('append')
    st.rerun()