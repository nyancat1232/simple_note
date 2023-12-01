import streamlit as st
import pandas as pd
import numpy as np
from typing import List
import json 
from pyplus.streamlit.streamlit_plus_utility import FileExecutor,FileDescription

from pyplus.streamlit.external import check_password
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
        res = st.radio(label=f'test{_depth}',options=op)
        all_selection.append(res)
        if not st.checkbox(label=f'terminate{_depth}'):
            selection(op[res],all_selection=all_selection,_depth=_depth+1)
    except:
        st.write('no')
        return

selection(dfs,all_selection)


i=-1
ss=dfs
while (i:=i+1) < len(all_selection):
    ss=ss[all_selection[i]]

with st.expander('expand result'):
    ss