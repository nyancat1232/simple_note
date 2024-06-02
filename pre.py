import streamlit as st
import pyplus.streamlit as stp
import pyplus.sql as sqlp

def ex():
    if not stp.check_password():
        st.stop()
if 'conn' not in st.session_state:
    st.session_state['conn'] = st.connection('myaddress',type='sql')

conn = st.session_state['conn']
types=['bigint','double precision','text','timestamp with time zone','boolean','url','image_url','text_with_tag']
title = 'Simple note'
sn_config_table={'schema':'sn_config','table':'configs'}

def init_schema():
    lists=sqlp.get_table_list(conn.engine)
    return st.selectbox('select a schema',['public']+lists['table_schema'].unique().tolist())

def table_selector(label:str='select a table',conn=conn.engine)->sqlp.TableStructure:
    '''
    Show a selector for selecting schema and table.
    
    Parameters
    ----------
    label : str
        A short label explaining to the user what this select widget is for. The label can optionally contain Markdown and supports the following
        elements: Bold, Italics, Strikethroughs, Inline Code, Emojis, and Links.

        This also supports:

        Emoji shortcodes, such as and. For a list of all supported codes, see https://share.streamlit.io/streamlit/emoji-shortcodes.

        LaTeX expressions, by wrapping them in "$" or "$$" (the "$$" must be on their own lines). Supported LaTeX functions are listed at https://katex.org/docs/supported.html.

        Colored text, using the syntax :color[text to be colored], where color needs to be replaced with any of the following supported colors: blue, green, orange, red, violet, gray/grey, rainbow.

        Unsupported elements are unwrapped so only their children (text contents) render. Display unsupported elements as literal characters by backslash-escaping them. E.g. 1\. Not an ordered list.
    
    Returns
    --------
    tuple
        schema,table
    
    Examples
    --------
    
    >>> with st.sidebar:
    >>>     ts = table_selector('select a table')

    '''

    received_queries=st.query_params
    def query_to_index(query:str,ll:list):
        appender=dict()
        try:
            appender['index']=ll.index(received_queries[query])
        except:
            try:
                st.toast(f'{received_queries[query]} not in {query}')
            except:
                st.toast(f'No {query}')
        return appender

    engine = conn.engine
    df_lists=sqlp.get_table_list(engine)
    event_df = st.dataframe(df_lists,key=label,on_select='rerun',selection_mode='single-row',hide_index=True)
    selected_row = event_df['selection']['rows'][0]
    result=df_lists.to_dict('records')[selected_row]

    return sqlp.TableStructure(result['table_schema'],result['table_name'],engine)