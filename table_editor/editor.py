import streamlit as st

import pyplus.sql as sqlp
import pandas as pd
import pyplus.builtin as bp

second_ts:sqlp.TableStructure = st.session_state['selected_table']
df_with_tag = st.session_state['selected_table_dataframe']
custom_configs_ro = st.session_state['selected_table_column_config_ro']
custom_configs_rw_def = st.session_state['selected_table_column_config_rw_def']

with st.form('edit form',clear_on_submit=True):

    temp=second_ts.get_foreign_tables()

    custom_configs_rw_edit=custom_configs_rw_def.copy()
    df_edited = st.data_editor(df_with_tag,disabled=second_ts.get_identity(),column_config=custom_configs_rw_edit)

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

    if st.form_submit_button('upload'):
        for row_id in recs:
            st.toast(f'{row_id}:{recs[row_id]}')
            second_ts.upload(id_row=row_id,**recs[row_id])
        st.rerun()
