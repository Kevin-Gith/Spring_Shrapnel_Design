import streamlit as st
import math
from datetime import datetime
from zoneinfo import ZoneInfo

# ---------- 固定參數 ----------
G = 8000  # kgf/mm^2 （彈簧鋼性模數的預設值）

# ---------- 自訂浮點範圍產生器 ----------
def frange(start, stop, step):
    """模擬 Python 的 range，但支援小數"""
    while start <= stop:
        yield round(start, 2)
        start += step

# ---------- 星星得分 ----------
def score_to_stars(score):
    """將評分 (0~4) 轉換成 ★/☆ 顯示"""
    return '★' * score + '☆' * (4 - score)

# ---------- 主程式 ----------
def main():
    """壓縮彈簧組合計算器主程式（Streamlit 入口）"""

    # 頁面基本設定
    st.set_page_config(page_title="壓縮彈簧組合計算器", page_icon="🧮")
    st.title("🧮 壓縮彈簧組合計算器")

    # ---------- 輸入表單 ----------
    with st.form("spring_form"):
        st.subheader("📌 請輸入參數")
        L = st.number_input("CPU長度 (mm)", min_value=1.0, value=25.0)
        W = st.number_input("CPU寬度 (mm)", min_value=1.0, value=25.0)
        G = st.number_input("彈簧鋼性模數 (kgf/mm²)", min_value=1.0, value=8000.0)
        SS = st.number_input("螺絲行程 (mm)", min_value=0.1, value=0.3)
        SRU = st.number_input("Spring Room Unlock (mm)", min_value=0.1, value=2.5)
        SSD = st.number_input("螺絲桿徑 (mm)", min_value=0.1, value=1.2, step=0.1)
        SHD = st.number_input("螺絲頭徑 (mm)", min_value=0.1, value=2.4, step=0.1)
        CPSI = st.number_input("晶片承受最大負載 (lbf/in²)", min_value=1.0, value=40.0)
        SNN = st.number_input("螺絲數量 (pcs)", min_value=1, step=1, value=4)
        N = st.number_input("顯示組合數量", min_value=1, step=1, value=5)
        submitted = st.form_submit_button("🚀 開始計算")

    # ---------- 計算 ----------
    if submitted:
        st.subheader("📝 輸入參數確認")
        st.markdown(f"""
        - CPU長度：{L} mm  
        - CPU寬度：{W} mm  
        - 彈簧鋼性模數：{G} kgf/mm²  
        - 螺絲行程：{SS} mm  
        - Spring Room Unlock：{SRU} mm  
        - 螺絲桿徑：{SSD} mm  
        - 螺絲頭徑：{SHD} mm  
        - 晶片最大負載：{CPSI} lbf/in²  
        - 螺絲數量：{SNN} pcs  
        - 顯示組合數量：{N} 組  
        """)

        # 晶片負載允許範圍 (±10%)
        PSI_lower = CPSI * 0.9
        PSI_upper = CPSI * 1.1
        valid_combinations = []

        # ---------- 計算所有組合 ----------
        for WD in frange(0.2, 1.0, 0.1):  # 線徑
            ID_min = SSD + 0.01
            ID_max = SHD - 0.01
            for ID in frange(ID_min, ID_max, 0.1):  # 內徑
                for SN in frange(3, 20, 1):  # 總圈數
                    NC = SN - 2  # 有效圈數
                    if NC <= 0:
                        continue
                    OD = round(ID + 2*WD, 2)  # 外徑
                    MD = round(ID + WD, 2)    # 中徑
                    SK = round((G * WD**4) / (8 * MD**3 * NC), 2)  # 彈簧常數
                    SL = round((SN + 1) * WD, 2)  # 密實高度

                    FL_min = SL + 0.1
                    FL_max = SRU + SL
                    for FL in frange(FL_min, FL_max, 0.5):  # 自由長度
                        SP = round(FL - SRU, 2)  # 預壓
                        if SP <= 0:
                            continue
                        SPP = round(FL / SN, 2)  # 節距
                        ST = round(SP + SS, 2)   # 行程
                        SCC = round(ST + SL, 2)  # 壓縮確認
                        if SCC > FL:
                            continue
                        DF = round(ST * SK, 2)   # 行程壓力
                        TFK = round(DF * SNN, 2) # 模組總壓力 (kgf)
                        TFL = round(TFK * 2.2046, 2) # 模組總壓力 (lbf)
                        PSI = round((TFK / (L * W)) * 1421.0573, 2) # 晶片負載

                        # ---------- 條件檢查 ----------
                        cond1 = PSI_lower <= PSI <= PSI_upper  # 晶片負載允許
                        cond2 = SP > 0                         # 預壓必須 > 0
                        cond3 = SPP < 2.5                      # 節距不宜過大
                        cond4 = SL >= FL*0.75                  # 壓縮比例合理
                        score = sum([cond1, cond2, cond3, cond4])

                        # 紀錄不符合原因
                        notes = []
                        if not cond1: notes.append(f"PSI超出範圍 → {PSI} lbf/in²")
                        if not cond2: notes.append(f"預壓不足 → {SP} mm")
                        if not cond3: notes.append(f"節距過大 → {SPP} mm")
                        if not cond4: notes.append(f"壓縮不足 → 自由長度：{FL} mm, 密實高度：{SL} mm")

                        # 符合條件才加入清單
                        if score >= 2:
                            valid_combinations.append({
                                "線徑": WD, "內徑": ID, "外徑": OD, "中心徑": MD,
                                "總圈數": SN, "有效圈數": NC, "自由長度": FL, "密實高度": SL,
                                "預壓": SP, "節距": SPP, "Spring Room Locked": SRU - SS,
                                "行程": ST, "壓縮確認": SCC, "行程壓力": DF,
                                "模組總壓力(kgf)": TFK, "模組總壓力(lbf)": TFL,
                                "晶片負載": PSI, "評分": score, "不符合原因": notes
                            })

        # ---------- 顯示結果 ----------
        st.subheader("💻最佳化組合")
        
        if not valid_combinations:
            st.warning("❌ 沒有符合條件的組合，請嘗試調整參數。")
        else:
            valid_combinations.sort(key=lambda x: -x['評分'])
            available = len(valid_combinations)
            st.success(f"✅ 找到 {available} 組符合條件的組合。顯示前 {min(N, available)} 組：")
            for i, combo in enumerate(valid_combinations[:N]):
                stars_display = score_to_stars(combo['評分'])
                with st.expander(f"第 {i+1} 組（滿足條件：{stars_display}）", expanded=True):
                    for k, v in combo.items():
                        if k != "不符合原因" and k != "評分":
                            st.write(f"{k}: {v}")
                    if combo["不符合原因"]:
                        st.markdown(
                            f"<div style='background-color:#fff3cd; padding:8px; border-radius:5px;'>⚠ 不符合條件：</div>",
                            unsafe_allow_html=True
                        )
                        for note in combo["不符合原因"]:
                            st.write(note)
                    else:
                        st.markdown(
                            f"<div style='background-color:#d1ecf1; padding:8px; border-radius:5px;'>⚠ 不符合條件： 無</div>",
                            unsafe_allow_html=True
                        )

    # ---------- 顯示最後更新時間（台灣時間） ----------
    st.write("最後更新時間（台灣）：", datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d %H:%M:%S"))

# 允許直接執行 Spring.py，也能被 app.py 匯入
if __name__ == "__main__":
    main()

#----------以下訊息保留 ----------
#使用者自行輸入數值(不會有負值)
#1.*"L"代表CPU長度*，浮點數，單位mm
#2.*"W"代表CPU寬度*，浮點數，單位mm
#3.*"G"代表彈簧鋼性模數*，浮點數
#4.*"SS"代表螺絲行程*，浮點數，單位mm
#5.*"SRU"代表Spring Room Unlock*，浮點數，單位mm
#6.*"SSD"螺絲桿徑*，浮點數，單位mm
#7.*"SHD"螺絲頭徑*，浮點數，單位mm
#8.*"CPSI"代表客戶要求晶片承受最大負載*，浮點數，單位lbf/in^2
#9.*"SNN"代表螺絲數量*，整數，單位pcs
#10.*"N"代表顯示組合數量*，整數，單位groups

#範圍變數(不會有負值，透過python計算出最佳化參數，不會由使用者輸入)
#1.*"WD"代表線徑*，浮點數(顯示小數點後二位)，範圍1>=WD>=0.2，間隔0.1，單位mm
#2.*"ID"代表內徑*，浮點數(顯示小數點後二位)，範圍SHD>ID>SSD，單位mm
#3.*"SN"代表彈簧總圈數*，浮點數(顯示小數點後一位)，範圍SN>0，單位laps
#4.*"FL"代表彈簧自由長度*，浮點數(顯示小數點後二位)，單位mm

#計算公式(不會有負值)
#1.*"OD"代表彈簧外徑*，浮點數(顯示小數點後二位)，ID+2*WD，單位mm
#2.*"MD"代表彈簧中心徑*，浮點數(顯示小數點後二位)，WD+ID，單位mm
#3.*"NC"代表彈簧有效圈數*，浮點數(顯示小數點後一位)，SN-2，單位laps
#4.*"SK"代表彈簧常數*，浮點數(顯示小數點後二位)(G*WD^4)/(8*MD^3*NC)，單位kgf/mm
#5.*"SL"代表彈簧密實高度*，浮點數(顯示小數點後二位)，(SN+1)*WD，單位mm
#6.*"SP"代表彈簧預壓*，浮點數(顯示小數點後二位)，FL-SRU，單位mm
#7.*"SPP"代表彈簧節距*，浮點數(顯示小數點後二位)，FL/SN，單位mm
#8.*"SRL"代表Spring Room Locked*，浮點數(顯示小數點後二位)，SRU-SS，單位mm
#9.*"ST"代表彈簧行程(含預壓行程)*，浮點數(顯示小數點後二位)，SP+SS，單位mm
#10.*"SCC"代表彈簧壓縮確認*，浮點數(顯示小數點後二位)，ST+SL，單位mm
#11.*"DF"代表行程壓力*，浮點數(顯示小數點後二位)，ST*SK，單位kg
#12.*"TFK"代表模組上的彈簧總壓力*，浮點數(顯示小數點後二位)，DF*SNN，單位kgf
#13.*"TFL"代表模組上的彈簧總壓力*，浮點數(顯示小數點後二位)，TFK*2.2046，單位lbf
#14.*"PSI"代表晶片承受最大負載*，浮點數(顯示小數點後二位)，TFK/(L*W)*1421.0573，單位lbf/in^2

#最佳化目標(不會有負值)
#1.CPSI+(CPSI*10%)>PSI>CPSI-(CPSI*10%)，*要滿足晶片承受最大負載的+/-10%*
#2.SP>0，*彈簧要有預壓*
#3.SPP<2.5，*彈簧節距要小於2.5*
#4.FL>SL>FL*75%，*密實彈簧壓縮後不能低於自由長度75%*
#5.最好情況是1.2.3.4點都滿足，否則至少要滿足1.2點，其餘參數則為不符合要求
#6.輸出的組合請從最佳開始排列

#額外條件
#1.使用者自行輸入數值時，必須是SHD>SSD，如果不符合上述要求時，顯示"螺絲桿徑需小於螺絲頭徑"，並且重新從第6點開始輸入
#2.當計算結果SCC>FL時，代表錯誤，直接排除該組合，不顯示在結果
#3.當輸入的N(顯示組合數量)，無法滿足時，請提供最大的建議值，並直接請使用者再次輸入組合數量
#4.當使用者沒有輸入數值時，顯示"請重新輸入數值"，並再次跳出該欄位
#5.當使用者輸入完所有條件時，再出現結果前，會先顯示當前輸入的數值列表，才會在顯示結果
#6.輸出的結果不顯示代號，但都要有單位顯示
#7.最好的情況能滿足第1.2.3.4點，但無法達成時，請至少滿足其中任2點和顯示哪一點無法達到(需顯示當前計算數值)，並且達成N點時，會用星星符號表示(滿足4點則會有4顆星星)
#8.**內的文字註明在程式內，以便確認程式內容
