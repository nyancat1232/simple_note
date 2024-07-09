import streamlit as st
from pre import ex
ex()

import json 
from typing import List
import pyplus.streamlit as stp
from collections import Counter


fe = stp.FileExecutor()
fe.append_behavior('[A-Za-z0-9]*.json',json.load)
dfs = fe.execute_file_descriptions(label='jsons')


all_selection = []
def selection(op,all_selection:List,_depth=0):
    if _depth>5:
        return
    if type(op) != type(dict()):
        return
    
    op_op = op


    st.divider()
    try:
        check_terminate = st.checkbox(label=f'terminate{_depth}')
        filtered_op = filter(lambda key:type(op_op[key]) == dict,op_op)
        res = st.radio(label=f'test{_depth}',options=filtered_op)
        all_selection.append(res)
        if not check_terminate:
            selection(op_op[res],all_selection=all_selection,_depth=_depth+1)
    except:
        st.write('no')
        return

selection(dfs,all_selection)

#st.write(all_selection)

i=-1
correct_answers=dfs
while (i:=i+1) < len(all_selection):
    correct_answers=correct_answers[all_selection[i]]

with st.expander('expand result'):
    st.json(correct_answers,expanded=False)

input_mems=st.text_input(label='memorize_test').split(" ")
st.subheader(f'answer counter is {len(correct_answers)}')
st.write(f'you wrote {len(input_mems)} answer{"s" if len(input_mems)>1 else ""}')
cols=st.columns(3)

for input_mem in input_mems:
    with cols[0]:
        st.write('match')
        input_mem in correct_answers
    with cols[1]:
        co_inp = Counter(input_mem)

        l_res=[]
        for res in correct_answers:
            co_res = Counter(res)
            #co_res
            co_error_left_right=len(co_inp-co_res)
            co_error_right_left=len(co_res-co_inp)
            l_res.append(co_error_left_right+co_error_right_left)
        
        st.write('error of character count')
        st.write(min(l_res))

