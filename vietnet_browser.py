# Streamlit
import streamlit as st

# Components
from components.utils_wn import *
from components.utils_search import *
from components.utils_display import *
# from components.class_Node import *
from components.utils_search import *
from components.class_NodeFamily import *
import streamlit.components.v1 as components

# WordNet
# from nltk.corpus import wordnet as wn
import wn
# from wn_editor.editor import LexiconEditor

# Resolve save thread of wn library
import os
import sqlite3

# ------------- UI ------------- #
st.set_page_config(layout="wide")
st.title("🌐 Trình tra cứu VietNet")
st.markdown("""
    Đây là công trình nghiên cứu của nhóm nghiên cứu thuộc Trung tâm Ngôn ngữ học Tính toán (CLC)
    - PGS. TS. Đinh Điền
    - NCS. Phan Thị Mỹ Trang
    - Phan Văn Bá Hải
    - Đỗ Quốc Trí
""")

# Tạo 3 cột cho ba input hàng ngang
col1, col2, col3, col4 = st.columns([1.5, 1, 1.5, 2])
with col1:
    relationship_type = st.selectbox("🔗 Loại quan hệ:", ['hypernym', 'hyponym', 'meronym', 'holonym'])
with col2:
    max_recursive = st.slider("📏 Độ sâu đệ quy:", min_value=1, max_value=10, value=3)
with col3:
    view_mode = st.radio("👁️ Chế độ hiển thị:", ['Dạng chữ', 'Dạng đồ thị'], horizontal=True)
with col4:
    database_version = st.radio("Phiên bản dữ liệu:", ['Version 1 - Không có bước đánh giá', 'Version 2 - Đánh giá 4 mức'], horizontal=True)

# Thanh nhập từ
word = st.text_input("🔍 Nhập từ cần tìm:")
folder_path = ''

if word:
    if database_version == 'Version 1 - Không có bước đánh giá':
        folder_path = 'data/vietnet_data_v1'
    elif database_version == 'Version 2 - Đánh giá 4 mức':
        folder_path = 'data/vietnet_data_v2'


    lexicon = wn.Wordnet('oewn:2024')
    # synsets = lexicon.synsets(word, pos='n')
    synsets, search_message = search_function(word, lexicon, folder_path)

    # if not synsets:
        # st.text('Từ bạn tìm không tồn tại !!!')
    if search_message:
        st.text(search_message)
        pass

    else:
        families = NodeFamily(synsets, relationship_type, folder_path, max_recursive)
        
        if view_mode == 'Dạng chữ':
            st.subheader("🌲 Dạng chữ (Tree View)")
            st.markdown(get_tree_view_css(), unsafe_allow_html=True)
            html = render_details_tree(families.nodes)
            st.markdown(html, unsafe_allow_html=True)

        else:
            st.subheader("📊 Dạng biểu đồ (Graph View)")
            elements = nodefamily_to_cytoscape_elements(families.nodes)
            render_cytoscape(elements)
            
