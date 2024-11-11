import streamlit as st
import pyplus.sql as sqlp
import pyplus.streamlit as stp
import pandas as pd
import pyplus.pandas as pdp
import pyplus.builtin as bp

second_ts:sqlp.TableStructure = st.session_state['selected_table']
df_with_tag = st.session_state['selected_table_dataframe']
custom_configs_ro = st.session_state['selected_table_column_config_ro']
custom_configs_rw_def = st.session_state['selected_table_column_config_rw_def']

temp=second_ts.get_foreign_tables()

st.dataframe(df_with_tag,column_config=custom_configs_rw_def)

st.subheader('append mode')
custom_configs_rw_append=custom_configs_rw_def.copy()

df_append = pdp.empty_records(second_ts.read())
df_append = df_append.reset_index(drop=True)

tss_foreign = second_ts.get_foreign_tables()

selected_col_convert=dict()
"Select a column"
tab_or_col=stp.TabsPlus(layout='column',titles=tss_foreign,hide_titles=False)
with st.form('append form',clear_on_submit=True):
    for col_local_foreign in tss_foreign:
        ts_sub = tss_foreign[col_local_foreign]
        df_display=ts_sub.read_expand()
        conf = custom_configs_ro.copy()
        
        #display
        with tab_or_col[col_local_foreign]:
            selected_col_convert[col_local_foreign]=st.dataframe(df_display,column_config=conf,selection_mode='single-column',on_select='rerun',key=f'convert_of_{col_local_foreign}')['selection']['columns']
            if len(selected_col_convert[col_local_foreign])>0:
                selected_col_convert[col_local_foreign]=selected_col_convert[col_local_foreign][0]
                selections=df_display[selected_col_convert[col_local_foreign]].unique().dropna().tolist()
                custom_configs_rw_append[col_local_foreign+'__conversion']=st.column_config.SelectboxColumn(f'{col_local_foreign}(conversion from {selected_col_convert[col_local_foreign]})',options=selections)
                df_append[col_local_foreign+'__conversion']=pd.Series()
                del df_append[col_local_foreign]

    for col in df_append.columns.to_list():
        if col.startswith('_'):
            del df_append[col]
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

    appends = df_append.to_dict(orient='records')

    if st.form_submit_button('append'):
        second_ts.upload_appends(*appends)
        st.toast('append')
        st.rerun()