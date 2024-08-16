import streamlit as st
import pre as stglobal

import pyplus.sql as sqlp
import pandas as pd
import pyplus.builtin as bp

with st.sidebar:
    all_records_list= sqlp.get_table_list(st.session_state['conn'].engine).to_dict('records')
    all_table_list = [".".join([row['table_schema'],row['table_name']]) for row in all_records_list]
    current_address = st.selectbox('select address',all_table_list).split('.')
    second_ts = sqlp.TableStructure(schema_name=current_address[0],table_name=current_address[1],engine=st.session_state['conn'].engine)

st.subheader('edit mode')

df_with_tag = bp.CheckPointFunction(stglobal.iter_tag_process).filter_tag(second_ts)

temp=second_ts.get_foreign_tables()
for col in temp:
    bb=second_ts.check_selfref_table(temp[col])

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
    st.rerun()
