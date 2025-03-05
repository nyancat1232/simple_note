import streamlit as st
from streamlit import column_config as stcc
import pyplus.sql as sqlp
import pyplus.streamlit as stp
import checkpoint as cp
import pandas as pd
import os
from sqlalchemy import create_engine
import pytz
import main_filter as mf

debug = True if 'SN_DEBUG' in os.environ  else False

@cp.CheckPointFunctionDecoration
def iter_custom_column_configs(ts:sqlp.TableStructure,mytz:str):
    column_configs = dict()

    types = (ts.get_types_expanded()
               .to_dict(orient='index')
               .copy()
    )
    for col in types:
        disable_this_col = False
        if types[col]['is_generated'] == 'ALWAYS':
            disable_this_col = True
        match types[col]['display_type']:
            case 'date':
                column_configs[col] = stcc.DateColumn(disabled=disable_this_col)
            case 'timestamp with time zone':
                column_configs[col] = stcc.DatetimeColumn(timezone=mytz,
                                                          disabled=disable_this_col)
            case 'url':
                column_configs[col] = stcc.LinkColumn(disabled=disable_this_col)
            case 'image_url':
                column_configs[col] = stcc.LinkColumn(disabled=disable_this_col)
            case 'video_url':
                column_configs[col] = stcc.LinkColumn(disabled=disable_this_col)
            case _:
                column_configs[col] = stcc.Column(disabled=disable_this_col)
    
    tss_foreign = ts.get_foreign_tables()
    for col in tss_foreign:
        ids_foreign=(tss_foreign[col].read()
                                     .index.to_list()
        )
        column_configs[col] = stcc.SelectboxColumn(f'{col}',
                                                   options=ids_foreign,
                                                   width='small'
                                                   )

    yield column_configs.copy(),'edit'

    for col in types:
        match types[col]['display_type']:
            case 'image_url':
                column_configs[col] = stcc.ImageColumn(f'{col}',)

    #Hide columns
    for col in tss_foreign:
        column_configs[col] = None

    col_expanded_tag=(ts.get_types_expanded()
                        .to_dict('index')
    )
    for col in col_expanded_tag:
        match col_expanded_tag[col]['display_type']:
            case 'tag_string':
                column_configs[col] = None
    yield column_configs.copy(), 'readonly' 

def column_process(ts:sqlp.TableStructure):
    df=ts.read_expand()
    dfs_foreign_tables=ts.get_foreign_tables()
    col_expanded_tag=ts.get_types_expanded().to_dict('index')
    col_type = {col:col_expanded_tag[col]['display_type'] for col in col_expanded_tag}
    for col_foreign in dfs_foreign_tables:
        col_type[col_foreign] = 'sn_foreign'
    
    tp = stp.TabsPlus(titles=col_expanded_tag,layout='tab')
    filt_rows=[]
    for col in col_expanded_tag:
        with tp[col]:
            match col_type[col]:
                case 'sn_foreign':
                    filt_rows.append(mf.filter_rows_sn_foreign(df,dfs_foreign_tables,col))
                case 'text'|'text_with_tag':
                    filt_rows.append(mf.filter_rows_text(df,col))
    try:
        return df[pd.concat(filt_rows,axis=1).all(axis=1)]
    except:
        return df


page_title = 'Simple note'
page_icon='📒'
st.set_page_config(page_title=page_title,page_icon=page_icon,layout='wide')

#Set global vars
if 'global_conn' not in st.session_state:
    st.session_state['global_conn'] = create_engine(os.environ['SN_ADDRESS'])

st.session_state['global_supported_types']=['bigint',
                           'double precision',
                           'text',
                           'date',
                           'timestamp',
                           'timestamp with time zone',
                           'boolean',
                           'url',
                           'image_url',
                           'video_url',
                           'text_with_tag'
                          ]

pg = st.navigation({'main':[st.Page('table_editor/reader.py',title='reader'),
                            st.Page('table_editor/editor.py',title='editor'),
                            st.Page('table_editor/append_rows.py',title='append'),
                            st.Page('table_editor/remover_table.py',title='row or column deletion'),
                            ],
                    'foreign':[
                            st.Page('table_editor/connect_foreign.py',title='foreign connection'),
                            st.Page('table_editor/merge_foreign.py',title='merge foreign'),
                            ],
                    'experiment':[
                            st.Page('experiment/reader_pivot.py',title='Read with pivot table')
                            ],
                    'initialization':[
                            st.Page('new_page/init_domain.py',title='initialization'),
                    ]
                    })

with st.sidebar:
    with st.form(key='global_create_table'):
        #Create table
        schema_name = st.selectbox('schema name',
                                   sqlp.get_schema_list(st.session_state['global_conn'].engine)
                                   )
        table_name = st.text_input('table name')
        if st.form_submit_button(label='create table'):
                (sqlp.SchemaStructure(schema_name,st.session_state['global_conn'].engine)
                     .create_table(table_name)
                )

    # Select address
    all_tables= (sqlp.get_table_list(st.session_state['global_conn'].engine)
                     .to_dict('records')
    )
    ## Accept query parameters
    default_index=0
    if ('table_schema' in st.query_params) and ('table_name' in st.query_params):
        default_index = all_tables.index({'table_schema':st.query_params.table_schema,'table_name':st.query_params.table_name})
    current_address=st.selectbox('select address global',
                                 all_tables,
                                 index=default_index,
                                 format_func=lambda x:f"{x['table_schema']}.{x['table_name']}"
                                )
    
    @st.fragment
    def copy_url():
        if st.button('copy url'):
            url = f"{st.context.headers['Origin']}/{pg.url_path}?table_schema={current_address['table_schema']}&table_name={current_address['table_name']}"
            st.write(url)
    copy_url()
    
    #add timezone selection
    all_timezones = pytz.all_timezones
    default_timezone = all_timezones.index(st.context.timezone)
    mytimezone = st.selectbox('Timezone setting',index=default_timezone,options=all_timezones)

selected_table = sqlp.TableStructure(schema_name=current_address['table_schema'],
                                     table_name=current_address['table_name'],
                                     engine=st.session_state['global_conn'].engine
                                    )

st.session_state['global_selected_table'] = selected_table
st.session_state['global_selected_table_dataframe']= column_process(selected_table)
st.session_state['global_selected_table_column_config_ro']= iter_custom_column_configs(selected_table,mytimezone).readonly()
st.session_state['global_selected_table_column_config_rw_def']= iter_custom_column_configs(selected_table,mytimezone).edit()

if debug == True:
    if 'count' not in st.session_state:
        st.session_state.count = 0
    else:
        st.session_state.count += 1

    st.json(st.session_state,expanded=False)

    if 'tester' in st.query_params:
        st.json(st.query_params['tester'])

pg.run()