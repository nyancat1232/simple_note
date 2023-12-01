import streamlit as st
import json 
from typing import List
from pyplus.streamlit.streamlit_plus_utility import FileExecutor,FileDescription

from pyplus.streamlit.external import check_password
from collections import Counter
if not check_password():
    st.stop()


fe = FileExecutor()
fe.behaviors.append(FileDescription('[A-Za-z0-9]*.json',json.load))
dfs = fe.execute_file_descriptions(label='jsons')


all_selection = []
def selection(op,all_selection:List,_depth=0):
    if _depth>5:
        return
    if type(op) != type(dict()):
        return


    st.divider()
    try:
        check_terminate = st.checkbox(label=f'terminate{_depth}')
        res = st.radio(label=f'test{_depth}',options=op)
        all_selection.append(res)
        if not check_terminate:
            selection(op[res],all_selection=all_selection,_depth=_depth+1)
    except:
        st.write('no')
        return

selection(dfs,all_selection)


i=-1
correct_answers=dfs
while (i:=i+1) < len(all_selection):
    correct_answers=correct_answers[all_selection[i]]

with st.expander('expand result'):
    correct_answers

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

