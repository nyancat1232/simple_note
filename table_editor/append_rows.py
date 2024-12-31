import streamlit as st
import pyplus.sql as sqlp
import pyplus.streamlit as stp
import pandas as pd
import pyplus.pandas as pdp

ts:sqlp.TableStructure = st.session_state['selected_table']
df = st.session_state['selected_table_dataframe']
custom_configs_ro = st.session_state['selected_table_column_config_ro']
custom_configs_rw_def = st.session_state['selected_table_column_config_rw_def']

st.dataframe(df,column_config=custom_configs_ro)

df_append = pdp.empty_records(ts.read())
df_append = df_append.reset_index(drop=True)

tss_foreign = ts.get_foreign_tables()
dfs_foreign:dict[pd.DataFrame] = {}
for col_local_foreign in tss_foreign:
    ts_sub = tss_foreign[col_local_foreign]
    dfs_foreign[col_local_foreign]=ts_sub.read_expand()

dfs_foreign

@st.fragment
def append_rows(df_append:pd.DataFrame):
    df_append = df_append.copy()
    "Select a column"
    tab_or_col=stp.TabsPlus(layout='column',titles=tss_foreign,hide_titles=False)

    selected_col_convert=dict()

    for col_local_foreign in tss_foreign:
        #display
        with tab_or_col[col_local_foreign]:
            try:
                selected_col_convert[col_local_foreign]=st.dataframe(dfs_foreign[col_local_foreign],
                                                                    selection_mode='single-column',
                                                                    on_select='rerun',
                                                                    key=f'convert_of_{col_local_foreign}'
                                                                    )['selection']['columns'][0]
                selections=(dfs_foreign[col_local_foreign][selected_col_convert[col_local_foreign]].unique()
                                                                                                   .dropna()
                                                                                                   .tolist()
                )
                new_column=col_local_foreign+'__conversion'
                custom_configs_rw_def[new_column]=st.column_config.SelectboxColumn(f'{col_local_foreign}(conversion from {selected_col_convert[col_local_foreign]})',
                                                                                                            options=selections)
                df_append[new_column]=pd.Series()
                del df_append[col_local_foreign]
            except:
                pass

    for col in df_append.columns.to_list():
        if col.startswith('_'):
            del df_append[col]
    df_append = st.data_editor(df_append,num_rows='dynamic',column_config=custom_configs_rw_def)

    "Conversion to ids"
    for col in [col for col in df_append.columns.to_list() if col.endswith('__conversion')]:
        original_col=col[:col.find('__conversion')]
        df_append[original_col]=df_append[col].apply(lambda val:tss_foreign[original_col].get_local_val_to_id(selected_col_convert[original_col])[val])
        del df_append[col]


    if st.button('append'):
        appends = df_append.to_dict(orient='records')
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
    append_rows(df_append)
with tabs_axis_selection.column:
    append_columns()
with tabs_axis_selection.foreign_column:
    append_foreign_column()