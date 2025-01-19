import streamlit as st
import pyplus.sql as sqlp
import pyplus.streamlit as stp
import pandas as pd
import pyplus.pandas as pdp

ts:sqlp.TableStructure = st.session_state['selected_table']
df = st.session_state['selected_table_dataframe']
custom_configs_ro = st.session_state['selected_table_column_config_ro']
custom_configs_rw_def_pre = st.session_state['selected_table_column_config_rw_def']

st.dataframe(df,column_config=custom_configs_ro)

df_append_pre = pdp.empty_records(ts.read())
df_append_pre = df_append_pre.reset_index(drop=True)

tss_foreign = ts.get_foreign_tables()
dfs_foreign:dict[str,pd.DataFrame] = {}
for col_local_foreign in tss_foreign:
    dfs_foreign[col_local_foreign]=tss_foreign[col_local_foreign].read_expand()

def inverse_dict(di:dict)->dict:
    return {di[key]:key for key in di}

@st.fragment
def append_rows(df_append:pd.DataFrame,custom_configs_rw_def:dict):
    df_append = df_append.copy()
    custom_configs_rw_def = custom_configs_rw_def.copy()
    "Select a column"
    tab_or_col=stp.TabsPlus(layout='column',titles=dfs_foreign,hide_titles=False)

    selected_col_convert_result={}
    for col_local_foreign in dfs_foreign:
        #display
        with tab_or_col[col_local_foreign]:
            try:
                col_selected_foreign=st.dataframe(dfs_foreign[col_local_foreign],
                                                  selection_mode='single-column',
                                                  on_select='rerun',
                                                  key=f'convert_of_{col_local_foreign}'
                                                  )['selection']['columns'][0]
                ser_convert = dfs_foreign[col_local_foreign][col_selected_foreign]
                selected_col_convert_result[col_local_foreign]= inverse_dict(ser_convert.to_dict())
                selected_col_convert_result[col_local_foreign][None]=None
                selections=(ser_convert.unique()
                                       .dropna()
                                       .tolist()
                )
                custom_configs_rw_def[col_local_foreign]=st.column_config.SelectboxColumn(f'{col_local_foreign}(conversion from {col_selected_foreign})',
                                                                                                            options=selections)
                del df_append[col_local_foreign]
                df_append[col_local_foreign]=pd.Series()
            except:
                pass

    df_append = st.data_editor(df_append,num_rows='dynamic',column_config=custom_configs_rw_def)

    "Conversion to ids"
    conv={col:df_append[col].apply(lambda val:selected_col_convert_result[col][val]) 
          for col in selected_col_convert_result}
    df_append = df_append.assign(**conv)
    df_append

    "Remove blank"
    dict_remove_blank = (
        df_append
        .reset_index()
        .melt(id_vars='index')
        .dropna(subset='value')
        .to_dict(orient='records')
    )
    appends={}
    for rec in dict_remove_blank:
        if rec['index'] in appends:
            appends[rec['index']][rec['variable']]=rec['value']
        else:
            appends[rec['index']]={rec['variable']:rec['value']}
    appends = [appends[key] for key in appends]
    appends

    if st.button('append'):
        if not appends:
            st.error('No appends')
        else:
            ts.upload_appends(*appends)
            st.toast(f'append {appends}')
            st.rerun()

@st.fragment
def append_columns():
    df = pd.DataFrame({'name':pd.Series(dtype=pd.StringDtype),'type':pd.Series(dtype=pd.StringDtype)})
    sttype = {'name':st.column_config.TextColumn('name'),'type':st.column_config.SelectboxColumn('type',options=st.session_state['types'])}
    result = st.data_editor(df,num_rows='dynamic',column_config=sttype)
    result = {rec['name']:rec['type'] for rec in result.to_dict(orient='records')}
    result

    if st.button('append columns'):
        ts.append_column(**result)
        st.rerun()

@st.fragment
def append_foreign_column():
    all_tables= sqlp.get_table_list(st.session_state['conn'].engine).to_dict('records')
    address_right=st.selectbox('select a second table',all_tables,format_func=lambda x:f"{x['table_schema']}/{x['table_name']}")
    new_column_name = st.text_input('New column name')

    ts_right = sqlp.TableStructure(schema_name=address_right['table_schema'],table_name=address_right['table_name'],engine=st.session_state['conn'].engine)
    df_right = ts_right.read()
    df_right

    if st.button('upload'):
        st.toast('uploading')
        ts.append_column(**{new_column_name:'bigint'})
        ts.connect_foreign_column(ts_right,new_column_name)
        st.rerun()

tabs_axis_selection = stp.TabsPlus(titles=['row','column','foreign_column'],layout='tab')
with tabs_axis_selection.row:
    append_rows(df_append_pre,custom_configs_rw_def_pre)
with tabs_axis_selection.column:
    append_columns()
with tabs_axis_selection.foreign_column:
    append_foreign_column()