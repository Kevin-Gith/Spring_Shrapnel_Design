# app.py
import streamlit as st
import Spring
import Shrapnel

def main():
    st.set_page_config(page_title="彈簧彈片計算工具", page_icon="🏗️", layout="wide")
    st.title("🏗️ 彈簧彈片計算工具")

    if "page" not in st.session_state:
        st.session_state.page = None

    # --- 首頁選單 ---
    if st.session_state.page is None:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔩 壓縮彈簧計算器"):
                st.session_state.page = "spring"
        with col2:
            if st.button("⚙️ 彈片彈簧計算器"):
                st.session_state.page = "shrapnel"
        with col3:
            if st.button("📖 設計參數說明"):
                st.session_state.page = "docs"

    # --- 壓縮彈簧 ---
    if st.session_state.page == "spring":
        if st.button("⬅️ 返回主選單"):
            st.session_state.page = None
            st.experimental_rerun()
        Spring.main()

    # --- 彈片彈簧 ---
    elif st.session_state.page == "shrapnel":
        if st.button("⬅️ 返回主選單"):
            st.session_state.page = None
            st.experimental_rerun()
        Shrapnel.main()

    # --- 設計參數說明 ---
    elif st.session_state.page == "docs":
        if st.button("⬅️ 返回主選單"):
            st.session_state.page = None
            st.experimental_rerun()

        st.header("📖 設計參數說明")

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🔩 壓縮彈簧參數")
            st.image("Spring.PNG", caption="壓縮彈簧", use_container_width=True)

        with col2:
            st.subheader("⚙️ 彈片彈簧參數")
            st.image("Shrapnel.PNG", caption="彈片彈簧", use_container_width=True)

if __name__ == "__main__":
    main()