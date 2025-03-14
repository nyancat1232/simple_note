import streamlit as st
import pyplus.streamlit as stp
import pyplus.sql as sqlp
import pandas as pd
from typing import Dict,Any,Callable

ts:sqlp.TableStructure = st.session_state['global_selected_table']
df:pd.DataFrame = st.session_state['global_selected_table_dataframe']
custom_configs_rw_def = st.session_state['global_selected_table_column_config_rw_def']

identity = ts.get_identity()

def get_comparison(df_new,df_old)->Dict[int,Dict[str,Any]]:
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

def set_progress(upload_pendings:Dict|str,func:Callable,display_process:str):
    @st.dialog(f'dialog {display_process}')
    def commit():
        prog = st.progress(0.,f'Progression {display_process}')
        for ind,key in enumerate(upload_pendings):
            if type(upload_pendings[key]) == dict:
                func(key,**upload_pendings[key])
            elif type(upload_pendings[key]) == str:
                func(key,upload_pendings[key])
            else:
                raise NotImplementedError('Exceptional type')
            prog.progress(float(ind)/len(upload_pendings),f"{key}:{upload_pendings[key]}")
    commit()
    st.rerun()

@st.fragment
def func_cell(df:pd.DataFrame,ts:sqlp.TableStructure):
    df_edited = st.data_editor(df,disabled=identity,column_config=custom_configs_rw_def)

    upload_pendings=get_comparison(df_edited,df)
    upload_pendings 

    if st.button('upload'):
        set_progress(upload_pendings=upload_pendings,
                     func=ts.upload,
                     display_process='cell')

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
    df_replace_after=df_replace_after.map(lambda x: x.replace(inp['from'],inp['to']) if isinstance(x, str) else x)
    df_replace_after

    "compare"
    upload_pendings=get_comparison(df_replace_after,df_replace_original)
    upload_pendings 

    if st.button('upload replace'):
        set_progress(upload_pendings=upload_pendings,
                     func=ts.upload,
                     display_process='replacement')

@st.fragment
def func_default(df:pd.DataFrame,ts:sqlp.Table):
    ser_default_value = ts.get_default_value()
    ser_edited=st.data_editor(ser_default_value,disabled=['column_name'])
    upload_pendings=(ser_default_value.compare(ser_edited)['other']
                          .to_dict()
    )
    upload_pendings

    if st.button('upload default'):
        set_progress(upload_pendings=upload_pendings,
                     func=ts.set_default_value,
                     display_process='default')

@st.fragment
def func_cell_rename(df:pd.DataFrame,ts:sqlp.Table):
    pending = {key:key for key in df.columns.to_list()}
    pending = st.data_editor(pending)
    pending = {key:pending[key] for key in pending if key != pending[key]}
    pending

    if st.button('upload column rename'):
        set_progress(upload_pendings=pending,
                     func=ts.change_column_name,
                     display_process='column rename')

@st.fragment
def func_col_to_tag(df:pd.DataFrame,ts:sqlp.Table):
    new_name = st.text_input('name of column')
    delete_existing = st.checkbox('delete existing columns')
    space_to_valid_tag = lambda s:str(s).replace(' ','_').replace('.','_').replace('/','_').replace('\n','_')
    selection = st.dataframe(df,selection_mode=['multi-column'],on_select='rerun')
    ser = (
        df[selection['selection']['columns']]
        .apply(lambda ser:ser.apply(lambda v:f"#{ser.name}/{space_to_valid_tag(v)}"))
        .rename(columns=lambda s:f"#{s}")
        .aggregate('sum',axis=1)
    )
    df = (
        df
        .assign(**{new_name:ser})
        [[new_name]]
    )
    df
    if st.button('upload column to tag'):
        ts.append_column(**{new_name:'text'})
        ts.upload_dataframe(df)
        if delete_existing:
            ts.delete_columns(*selection['selection']['columns'])
        st.rerun()


tp = stp.TabsPlus(titles=['cell','replace','default','rename','col_to_tag'],layout='tab')
with tp.cell:
    func_cell(df,ts)
with tp.replace:
    func_replace(df,ts)
with tp.default:
    func_default(df,ts)
with tp.rename:
    func_cell_rename(df,ts)
with tp.col_to_tag:
    func_col_to_tag(df,ts)