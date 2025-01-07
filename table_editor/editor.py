import streamlit as st
import pyplus.streamlit as stp
import pyplus.sql as sqlp
import pandas as pd

ts:sqlp.TableStructure = st.session_state['selected_table']
df:pd.DataFrame = st.session_state['selected_table_dataframe']
custom_configs_rw_def = st.session_state['selected_table_column_config_rw_def']

identity = ts.get_identity()

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

@st.fragment
def func_cell(df:pd.DataFrame,ts:sqlp.TableStructure):
    df_edited = st.data_editor(df,disabled=identity,column_config=custom_configs_rw_def)

    recs=get_comparison(df_edited,df)

    if st.button('upload'):
        st.toast(f'uploading {recs}')
        for row_id in recs:
            st.toast(f'{row_id}:{recs[row_id]}')
            ts.upload(id_row=row_id,**recs[row_id])
        st.rerun()

@st.fragment
def func_replace(df:pd.DataFrame,ts:sqlp.TableStructure):
    rrr=st.dataframe(df,selection_mode=['multi-column','multi-row'],on_select='rerun')
    df_replace_original=df.copy()[rrr['selection']['columns']]

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
        prog = st.progress(0.,'Upload replace')
        for ind,rec in enumerate(recs):
            ts.upload(rec,**recs[rec])
            prog.progress(float(ind)/len(recs),f"{rec}:{recs[rec]}")
        st.rerun()

@st.fragment
def func_default(df:pd.DataFrame,ts:sqlp.Table):
    ser_default_value = ts.get_default_value()
    ser_edited=st.data_editor(ser_default_value,disabled=['column_name'])
    upload_default=(ser_default_value.compare(ser_edited)['other']
                          .to_dict()
    )
    upload_default
    if st.button('upload default'):
        prog = st.progress(0,'Uploading default')
        for ind,key in enumerate(upload_default):
            ts.set_default_value(key,upload_default[key])
            prog.progress(float(ind)/len(upload_default),f"{key}:{upload_default[key]}")
        st.rerun()


tp = stp.TabsPlus(titles=['cell','replace','default'],layout='tab')
with tp.cell:
    func_cell(df,ts)
with tp.replace:
    func_replace(df,ts)
with tp.default:
    func_default(df,ts)