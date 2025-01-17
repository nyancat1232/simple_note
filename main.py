import streamlit as st
from streamlit import column_config as stcc
import pyplus.sql as sqlp
import pyplus.streamlit as stp
import checkpoint as cp
import pandas as pd
import os
from sqlalchemy import create_engine
from typing import Literal
import altair as alt

debug = True

@cp.CheckPointFunctionDecoration
def iter_custom_column_configs(ts:sqlp.TableStructure):
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
                column_configs[col] = stcc.DatetimeColumn(timezone=os.environ['SN_DEFAULT_TIMEZONE'],
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

    column_configs['__hidden']=stcc.Column(disabled=True)

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

def extract_tags(vals:list):
    try:
        match len(vals):
            case 1:
                return [vals[1]]
            case 0:
                return [None]
            case _:
                return vals[1:]
    except:
        return [None]
def remove_spaces(vals:list):
    def apply_each(s:str):
        try:
            ret = s
            for ch in ' \n':
                ll = ret.split(ch)
                ret = ll[0]
            return ret
        except:
            return s
    return [apply_each(val) for val in vals]
def duplicate_super_tags(vals:list,hashtag_sub_symbol:str='/'):
    def apply_each(s:str):
        if s is None:
            return [s]
        spl = s.split(hashtag_sub_symbol)
        return [hashtag_sub_symbol.join(spl[0:1+ind]) for ind,_ in enumerate(spl)]
    ret_pre = [apply_each(val) for val in vals]
    ret = []
    for l in ret_pre:
        ret += l
    return ret
def contains_tags(ll:list,tags:list,logic:Literal['and','or'])->bool:
    left = set(ll)
    right = set(tags)
    match logic:
        case 'and':
            res = right-left
            if len(res)>0:
                return False
            else:
                return True
        case 'or':
            res = left-right
            if res == left:
                return False
            else:
                return True
        case _:
            raise NotImplementedError('This logic is not implemented')
def skip_if_error(val,func):
    try:
        return func(val)
    except:
        pass
def column_process(ts:sqlp.TableStructure,hashtag_init_symbol:str='#'):
    df=ts.read_expand()
    col_expanded_tag=ts.get_types_expanded().to_dict('index')

    def filter_rows(col_3:str):
        match col_expanded_tag[col_3]['display_type']:
            case 'text'|'text_with_tag':
                sr_tags_original=(df[col_3].str.split(hashtag_init_symbol)
                                           .apply(extract_tags)
                                           .apply(remove_spaces)
                )
                sr_tags_extracted=sr_tags_original.apply(duplicate_super_tags)
                all_tags_list = (sr_tags_extracted.explode()
                                                  .dropna()
                                                  .sort_values()
                                                  .unique()
                                                  .tolist()
                ) #find_all_tags

                #Statistic
                tp_statistic = stp.TabsPlus(titles=['count'])
                with tp_statistic.count:
                    @st.fragment
                    def statistic_counts():
                        max_depth = (sr_tags_original.apply(lambda l:len(l))
                                                    .max()
                        )
                        sr_explode = sr_tags_original
                        if max_depth>1:
                            depth_apply = st.slider(f'depth of {col_3}',1,max_depth)
                            filter_depth = lambda l:set(
                                ['/'.join(v.split('/')[:depth_apply]) for v in l]
                            )
                            sr_explode = sr_explode.apply(skip_if_error,
                                                        args=(filter_depth,)
                                                        )
                        ser_agg_count = (sr_explode.explode()
                                                .dropna()
                                                .value_counts(ascending=True)
                        )

                        if ser_agg_count.max()>1:
                            exclude_counts= st.slider(f'exclude if the count of {col_3} is over',
                                                    min_value=1,
                                                    max_value=ser_agg_count.max(),
                                                    value=ser_agg_count.max()
                                                    )
                            ser_agg_count=ser_agg_count[ser_agg_count<=exclude_counts]

                            df_count_tags = pd.DataFrame({'num_of_tags':ser_agg_count}).reset_index()
                            base = (alt.Chart(df_count_tags)
                                    .mark_arc()
                                    .encode(
                                        alt.Color(field=col_3,type='nominal'),
                                        alt.Theta(field='num_of_tags',type='quantitative')
                                    )
                            )
                            st.altair_chart(base)
                    statistic_counts()

                logic = 'and' if st.checkbox(
                                            f'{col_3} : Subtract rows that is not selected(True), Show row that is selected(False)',
                                            True
                                            ) else 'or'
                if len(all_tags_list)>0:
                    selected_tags = st.multiselect(
                        f'select tags of {col_3}',
                        all_tags_list
                    )
                    return sr_tags_extracted.apply(contains_tags,
                                                    args=(selected_tags,logic)
                                                  )
                else:
                    return sr_tags_extracted.apply(contains_tags,
                                                    args=([],logic)
                                                  )
                
    tp = stp.TabsPlus(titles=col_expanded_tag,layout='tab')
    filt_rows={}
    for col in col_expanded_tag:
        with tp[col]:
            filt_rows[col]=filter_rows(col)
    try:
        return df[pd.concat(filt_rows,axis=1).all(axis=1)]
    except:
        return df


page_title = 'Simple note'
page_icon='📒'
st.set_page_config(page_title=page_title,page_icon=page_icon,layout='wide')

#Set global vars
if 'conn' not in st.session_state:
    st.session_state['conn'] = create_engine(os.environ['SN_ADDRESS'])

st.session_state['types']=['bigint',
                           'double precision',
                           'text',
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
                    'initialization':[
                            st.Page('new_page/init_domain.py',title='initialization'),
                    ]
                    })

with st.sidebar:
    with st.form(key='create_table'):
        #Create table
        schema_name = st.selectbox('schema name',
                                   sqlp.get_schema_list(st.session_state['conn'].engine)
                                   )
        table_name = st.text_input('table name')
        if st.form_submit_button(label='create table'):
                (sqlp.SchemaStructure(schema_name,st.session_state['conn'].engine)
                     .create_table(table_name)
                )

    #Select address
    all_tables= (sqlp.get_table_list(st.session_state['conn'].engine)
                     .to_dict('records')
    )
    current_address=st.selectbox('select address global',
                                 all_tables,
                                 format_func=lambda x:f"{x['table_schema']}.{x['table_name']}"
                                )

selected_table = sqlp.TableStructure(schema_name=current_address['table_schema'],
                                     table_name=current_address['table_name'],
                                     engine=st.session_state['conn'].engine
                                    )

st.session_state['selected_table'] = selected_table
st.session_state['selected_table_dataframe']= column_process(selected_table)
st.session_state['selected_table_column_config_ro']= iter_custom_column_configs(selected_table).readonly()
st.session_state['selected_table_column_config_rw_def']= iter_custom_column_configs(selected_table).edit()

if debug == True:
    if 'count' not in st.session_state:
        st.session_state.count = 0
    else:
        st.session_state.count += 1

    if 'pending_upload' not in st.session_state:
        st.session_state.pending_upload = []

    st.json(st.session_state,expanded=False)

pg.run()