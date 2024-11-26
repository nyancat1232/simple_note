import streamlit as st
import pyplus.sql as sqlp
import pyplus.streamlit as stp
import pandas as pd
import pyplus.pandas as pdp

second_ts:sqlp.TableStructure = st.session_state['selected_table']
df_with_tag = st.session_state['selected_table_dataframe']
custom_configs_ro = st.session_state['selected_table_column_config_ro']
custom_configs_rw_def = st.session_state['selected_table_column_config_rw_def']

st.dataframe(df_with_tag,column_config=custom_configs_ro)

df_append = pdp.empty_records(second_ts.read())
df_append = df_append.reset_index(drop=True)

tss_foreign = second_ts.get_foreign_tables()

tabs_axis_selection = stp.TabsPlus(titles=['row','column'],layout='tab')

with tabs_axis_selection['row']:
    "Select a column"
    tab_or_col=stp.TabsPlus(layout='column',titles=tss_foreign,hide_titles=False)
    with st.form('append form',clear_on_submit=False):
        selected_col_convert=dict()
        for col_local_foreign in tss_foreign:
            ts_sub = tss_foreign[col_local_foreign]
            df_display=ts_sub.read_expand()
            
            #display
            with tab_or_col[col_local_foreign]:
                selected_col_convert[col_local_foreign]=st.dataframe(df_display,selection_mode='single-column',on_select='rerun',key=f'convert_of_{col_local_foreign}')['selection']['columns']
                if len(selected_col_convert[col_local_foreign])>0:
                    selected_col_convert[col_local_foreign]=selected_col_convert[col_local_foreign][0]
                    selections=df_display[selected_col_convert[col_local_foreign]].unique().dropna().tolist()
                    custom_configs_rw_def[col_local_foreign+'__conversion']=st.column_config.SelectboxColumn(f'{col_local_foreign}(conversion from {selected_col_convert[col_local_foreign]})',options=selections)
                    df_append[col_local_foreign+'__conversion']=pd.Series()
                    del df_append[col_local_foreign]

        for col in df_append.columns.to_list():
            if col.startswith('_'):
                del df_append[col]
        cond_satisfies_warning = len(df_append.columns)<2
        if cond_satisfies_warning:
            st.warning('Problem when column is only one. ValueError: setting an array element with a sequence')
            df_append['__hidden']=df_append.index
        df_append = st.data_editor(df_append,num_rows='dynamic',column_config=custom_configs_rw_def)
        if cond_satisfies_warning:
            st.warning('Problem when column is only one. ValueError: setting an array element with a sequence')
            del df_append['__hidden']

        "Conversion to ids"
        for col in [col for col in df_append.columns.to_list() if col.endswith('__conversion')]:
            original_col=col[:col.find('__conversion')]
            df_append[original_col]=df_append[col].apply(lambda val:tss_foreign[original_col].get_local_val_to_id(selected_col_convert[original_col])[val])
            del df_append[col]


        if st.form_submit_button('append'):
            appends = df_append.to_dict(orient='records')
            second_ts.upload_appends(*appends)
            st.toast(f'append {appends}')
            st.rerun()

with tabs_axis_selection['column']:
    df = pd.DataFrame({'name':pd.Series(dtype=pd.StringDtype),'type':pd.Series(dtype=pd.StringDtype)})
    sttype = {'name':st.column_config.TextColumn('name'),'type':st.column_config.SelectboxColumn('type',options=st.session_state['types'])}
    result = st.data_editor(df,num_rows='dynamic',column_config=sttype)
    result = {rec['name']:rec['type'] for rec in result.to_dict(orient='records')}
    result

    def append_columns():
        second_ts.append_column(**result)

    if st.button('append columns'):
        append_columns()
        st.rerun()