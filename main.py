import streamlit as st
import pyplus.streamlit as stp
import pyplus.sql as sqlp

page_title = 'Simple note'
page_icon='📒'
st.set_page_config(page_title=page_title,page_icon=page_icon,layout='wide')

if stp.check_password() != True:
    st.stop()

#Set global vars
if 'conn' not in st.session_state:
    st.session_state['conn'] = st.connection('myaddress',type='sql')
st.session_state['types']=['bigint','double precision','text','timestamp with time zone','boolean','url','image_url','video_url','text_with_tag']

pg = st.navigation({'main':[st.Page('table_editor/reader.py',title='reader'),
                            st.Page('table_editor/editor.py',title='editor'),
                            st.Page('table_editor/append_rows.py',title='append'),
                            st.Page('table_editor/create_table.py',title='table or column editor'),
                            st.Page('table_editor/remover_table.py',title='row or column deletion'),
                            ],
                    'foreign':[
                            st.Page('table_editor/connect_foreign.py',title='foreign connection'),
                            st.Page('table_editor/merge_foreign.py',title='merge foreign'),
                            ],
                    'initialization':[
                            st.Page('new_page/init_domain.py',title='initialization'),
                    ]
                    })
pg.run()