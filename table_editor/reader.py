import streamlit as st
import pyplus.streamlit as stp
import pyplus.sql as sqlp

second_ts:sqlp.TableStructure = st.session_state['selected_table']
df_with_tag = st.session_state['selected_table_dataframe']
custom_configs_ro = st.session_state['selected_table_column_config_ro']

with st.sidebar:
    dtypes = second_ts.get_types_expanded().display_type.to_dict()
    order_nums=st.slider('size',min_value=1,max_value=len(df_with_tag.columns))
    order_selections=[st.selectbox(f'{num} selection',df_with_tag.columns) for num in range(order_nums)]
    result_list=[]
    for row in df_with_tag.to_dict('records'):
        for ind,col in enumerate(order_selections):
            match dtypes[col]:
                case 'image_url':
                    display_element = f"![image]({row[col]})"
                case 'video_url':
                    display_element = f"[video link]({row[col]})"
                case _:
                    display_element = row[col]
            result_list.append('\t'*ind+f'- {display_element}')
result_str="\n".join(result_list)
tp = stp.TabsPlus(titles=['view','code'])
with st.container():
    with tp.view:
        st.markdown(result_str)
    with tp.code:
        st.code(result_str)

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