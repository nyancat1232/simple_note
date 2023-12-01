import streamlit as st
import pandas as pd
import numpy as np
from pyplus.sql.pgplus import read_from_server
import tensorflow as tf

from pyplus.streamlit.external import check_password
if not check_password():
    st.stop()

    
conn=st.connection('postgresql',type='sql')

v=read_from_server(st.secrets['study']['learn_schema'],st.secrets['study']['learn_table'],st_conn=conn)
v


xtr=np.array([ [x,x+1] for x in range(0,100,3)])
ytr=np.array([ sum(x) for x in xtr])
xtr
ytr

#model creation
inputs = tf.keras.Input(shape=(len(xtr[0])))
hidden = tf.keras.layers.Dense(units=100,activation='relu')
outputs = hidden(inputs)
model = tf.keras.Model(inputs=inputs,outputs=outputs)
model.compile(loss=tf.keras.losses.mean_squared_error)

history = model.fit(x=xtr,y=ytr)

test = model.evaluate([1,2],[3])

