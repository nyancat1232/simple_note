import streamlit as st
import pyplus.sql as sqlp
import pyplus.streamlit as stp
import pandas as pd
from typing import Literal
import altair as alt

def skip_if_error(val,func):
    try:
        return func(val)
    except:
        pass

def filter_rows_sn_foreign(df:pd.DataFrame,dfs_foreign_tables:dict[str,sqlp.Table],col_name:str):
    "If not select, select all."
    "If select, only show you selected"
    rows=st.dataframe(dfs_foreign_tables[col_name].read_expand(),selection_mode='multi-row',on_select='rerun',key=f'filter_rows_{col_name}')['selection']['rows']
    if len(rows)>0:
        filt_foreign_id=(
            dfs_foreign_tables[col_name]
            .read_expand()
            .iloc[rows]
            .index
            .to_list()
        )
        return df[col_name].apply(lambda val: val in filt_foreign_id)
def filter_rows_text(df:pd.DataFrame,col_name:str,hashtag_init_symbol:str='#'):
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
    sr_tags_original=(
        df[col_name]
        .str.split(hashtag_init_symbol)
        .apply(extract_tags)
        .apply(remove_spaces)
    )
    #Statistic
    tp_statistic = stp.TabsPlus(titles=['count','tag_preview'],layout='column',hide_titles=False)
    with tp_statistic.count:
        @st.fragment
        def statistic_counts():
            max_depth = (
                sr_tags_original
                .apply(lambda l:len(l))
                .max()
            )
            sr_explode = sr_tags_original
            if max_depth>1:
                depth_apply = st.slider(f'depth of {col_name}',1,max_depth)
                filter_depth = lambda l:set(
                    ['/'.join(v.split('/')[:depth_apply]) for v in l]
                )
                sr_explode = (
                    sr_explode
                    .apply(skip_if_error,args=(filter_depth,))
                )
            ser_agg_count = (
                sr_explode
                .explode()
                .dropna()
                .value_counts(ascending=True)
            )

            if ser_agg_count.max()>1:
                exclude_counts= st.slider(f'exclude if the count of {col_name} is over',
                                        min_value=1,
                                        max_value=ser_agg_count.max(),
                                        value=ser_agg_count.max()
                                        )
                ser_agg_count=ser_agg_count[ser_agg_count<=exclude_counts]

                df_count_tags = (
                    pd.DataFrame({'num_of_tags':ser_agg_count})
                    .reset_index()
                )
                base = (alt.Chart(df_count_tags)
                        .mark_arc()
                        .encode(
                            alt.Color(field=col_name,type='nominal'),
                            alt.Theta(field='num_of_tags',type='quantitative')
                        )
                )
                st.altair_chart(base)
        statistic_counts()
    with tp_statistic.tag_preview:
        @st.fragment
        def tag_preview():
            pass
        tag_preview()

    logic = 'and' if st.checkbox(
                                f'{col_name} : Subtract rows that is not selected(True), Show row that is selected(False)',
                                True
                                ) else 'or'

    sr_tags_extracted=sr_tags_original.apply(duplicate_super_tags)
    all_tags_list = (
        sr_tags_extracted
        .explode()
        .dropna()
        .sort_values()
        .unique()
        .tolist()
    ) #find_all_tags

    selected_tags = []
    if len(all_tags_list)>0:
        selected_tags = st.multiselect(
            f'select tags of {col_name}',
            all_tags_list
        )
    return sr_tags_extracted.apply(contains_tags,
                                    args=(selected_tags,logic)
                                    )