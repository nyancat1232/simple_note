import streamlit as st
import pyplus.streamlit as stp
import pyplus.sql as sqlp
import pandas as pd

ts_selected:sqlp.TableStructure = st.session_state['selected_table']
df_selected:pd.DataFrame = st.session_state['selected_table_dataframe']
custom_configs_ro = st.session_state['selected_table_column_config_ro']
custom_configs_rw_def = st.session_state['selected_table_column_config_rw_def']

tp = stp.TabsPlus(titles=['cell','replace'],layout='tab')

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

def func_cell():
    with st.form('edit form',clear_on_submit=False):
        temp=ts_selected.get_foreign_tables()

        df_edited = st.data_editor(df_selected,disabled=ts_selected.get_identity(),column_config=custom_configs_rw_def)

        recs=get_comparison(df_edited,df_selected)

        if st.form_submit_button('upload'):
            st.toast(f'uploading {recs}')
            for row_id in recs:
                st.toast(f'{row_id}:{recs[row_id]}')
                ts_selected.upload(id_row=row_id,**recs[row_id])
            st.rerun()

with tp['cell']:
    func_cell()

def func_replace():
    rrr=st.dataframe(df_selected,selection_mode=['multi-column','multi-row'],on_select='rerun')
    df_replace_original=df_selected.copy()[rrr['selection']['columns']]

    inp={'from':st.text_input('from'),'to':st.text_input('to')}

    "filter"
    df_replace_after=df_replace_original.copy()
    if rrr['selection']['rows']:
        df_replace_after=df_replace_after.iloc[rrr['selection']['rows']]
    df_replace_after=df_replace_after[rrr['selection']['columns']]
    df_replace_after

    "change"
    #selected_table=selected_table.apply(lambda s:s.replace(inp['from'],inp['to']))
    df_replace_after:pd.DataFrame=df_replace_after.applymap(lambda x: x.replace(inp['from'],inp['to']) if isinstance(x, str) else x)
    df_replace_after

    "compare"
    recs=get_comparison(df_replace_after,df_replace_original)
    recs 

    if st.button('upload replace'):
        for rec in recs:
            st.toast([rec,recs[rec]])
            ts_selected.upload(rec,**recs[rec])
        st.rerun()

with tp['replace']:
    func_replace()