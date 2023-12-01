import streamlit as st
import pandas as pd
import numpy as np
from typing import List
from pyplus.sql.pgplus import read_from_server
import cv2

from pyplus.streamlit.external import check_password
if not check_password():
    st.stop()

    
conn=st.connection('postgresql',type='sql')

import streamlit as st
import pandas as pd
import numpy as np
from typing import List
from pyplus.sql.pgplus import read_from_server
import qrcode 
from pyplus.streamlit.external import check_password
if not check_password():
    st.stop()

    
conn=st.connection('postgresql',type='sql')


image=st.camera_input(label='cam')

ttt = st.text_input('test')
im = qrcode.make(ttt)
st.write(im)
if im is not None:
    st.image(im.get_image())
    

image
# Get the image that contains the QR code
if image is not None:
    bytes_data = image.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    detector = cv2.QRCodeDetector()

    data, bbox, straight_qrcode = detector.detectAndDecode(cv2_img)

    st.write("Here!")
    st.write(data)