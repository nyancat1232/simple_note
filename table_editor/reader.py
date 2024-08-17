import streamlit as st
import pre as stglobal

import pyplus.sql as sqlp
import pandas as pd
import pyplus.pandas as pdp
import pyplus.builtin as bp

second_ts = sqlp.TableStructure(schema_name=st.session_state['current_address'][0][0],table_name=st.session_state['current_address'][0][1],engine=st.session_state['conn'].engine)

df_with_tag:pd.DataFrame = bp.select_yielder(stglobal.iter_tag_process(second_ts),'filter_tag')

temp=second_ts.get_foreign_tables()
for col in temp:
    bb=second_ts.check_selfref_table(temp[col])

order_nums=st.slider('size',min_value=1,max_value=len(df_with_tag.columns))
order_selections=[st.selectbox(f'{num} selection',df_with_tag.columns) for num in range(order_nums)]
result_list=[]
for row in df_with_tag.to_dict('records'):
    for ind,col in enumerate(order_selections):
        result_list.append('\t'*ind+f'- {row[col]}')
result_str="\n".join(result_list)
st.code(result_str)

custom_configs_ro:dict = bp.select_yielder(stglobal.iter_custom_column_configs(second_ts),'readonly')
event=st.dataframe(df_with_tag,column_config=custom_configs_ro,on_select='rerun',selection_mode='single-row')
row = df_with_tag.iloc[event['selection']['rows']].to_dict('records')[0]
types = second_ts.get_types_expanded().to_dict(orient='index')
for col in types:
    try:
        if row[col]:
            pass
    except:
        st.toast(f'skipping column {col}')
        continue

    if row[col] is not None:
        match types[col]['display_type']:
            case 'image_url':
                st.markdown(f'#### {col}')
                st.image(row[col])
            case 'video_url':
                st.markdown(f'#### {col}')
                st.video(row[col])