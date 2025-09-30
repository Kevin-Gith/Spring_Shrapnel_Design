#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
from dataclasses import dataclass
from datetime import datetime
import itertools

# -------------------- 資料結構 --------------------
@dataclass
class Quad:
    X: float
    Y: float
    SL: float
    SW: float
    ST: float
    SS: float
    G: float

    # 慣性矩 I = (SW * ST^3) / 12
    def inertia(self) -> float:
        return (self.SW * (self.ST ** 3)) / 12.0

    # 合力 F = (3 * G * I * SS) / SL^3
    def force(self) -> float:
        I = self.inertia()
        return (3.0 * self.G * I * self.SS) / (self.SL ** 3)

    # 力矩（kgf·mm）
    def moment_x(self, F: float) -> float:
        return F * self.X

    def moment_y(self, F: float) -> float:
        return F * self.Y


# -------------------- 工具函式 --------------------
def frange(start: float, stop: float, step: float):
    vals = []
    x = start
    while x <= stop + 1e-9:
        vals.append(round(x, 6))
        x += step
    return vals


def assign_stars(modified_params: set) -> str:
    """
    星級規則：
    - 只改 ST → ★★★★
    - 改 ST + 1 項 → ★★★
    - 改 ST + 2 項 → ★★
    - 改 ST + 3 項 → ★
    - 若不改 ST：
        * 改 1 項 → ★★★
        * 改 2 項 → ★★
        * 改 3 項 → ★
    """
    if not modified_params:
        return "★"

    if modified_params == {"ST"}:
        return "★★★★"
    if "ST" in modified_params:
        others = len(modified_params) - 1
        if others == 1:
            return "★★★"
        elif others == 2:
            return "★★"
        elif others == 3:
            return "★"
        return "★"
    else:
        if len(modified_params) == 1:
            return "★★★"
        elif len(modified_params) == 2:
            return "★★"
        else:
            return "★"


# -------------------- Streamlit App --------------------
def main():
    # 頁面基本設定
    st.set_page_config(page_title="四象限彈片最佳化計算器", page_icon="🧮", layout="wide")
    st.title("🧮 四象限彈片最佳化計算器")

    param_map = {"SL": "長度", "SW": "寬度", "ST": "厚度", "SS": "行程"}
    star_rank = {"★★★★": 4, "★★★": 3, "★★": 2, "★": 1}

    # ---------- 輸入表單 ----------
    with st.form("quad_form"):
        st.subheader("📌 請輸入參數")
        cols_top = st.columns(3)
        with cols_top[0]:
            F_target = st.number_input("最大總合力 F (kgf)", min_value=0.0, value=4.50, step=0.01)
        with cols_top[1]:
            N_show = st.number_input("顯示組合數量 N (groups)", min_value=1, value=5, step=1)
        with cols_top[2]:
            default_G = st.number_input("鋼性模數預設值 (kgf/mm²)", min_value=0.0, value=18763.0, step=1.0)

        st.markdown("---")
        st.subheader("🧭 四象限參數輸入")

        def quad_inputs(label: str):
            c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
            with c1:
                X = st.number_input(f"{label} X 座標", value=0.0, step=0.01, format="%.6f")
            with c2:
                Y = st.number_input(f"{label} Y 座標", value=0.0, step=0.01, format="%.6f")
            with c3:
                SL = st.number_input(f"{label} 長度 SL (mm)", min_value=0.0, value=8.0, step=0.1)
            with c4:
                SW = st.number_input(f"{label} 寬度 SW (mm)", min_value=0.0, value=4.0, step=0.1)
            with c5:
                ST_v = st.number_input(f"{label} 厚度 ST (mm)", min_value=0.0, value=0.4, step=0.1, format="%.1f")
            with c6:
                SS = st.number_input(f"{label} 行程 SS (mm)", min_value=0.0, value=1.0, step=0.05, format="%.2f")
            with c7:
                G = st.number_input(f"{label} 鋼性模數 G", min_value=0.0, value=default_G, step=1.0)
            return Quad(X, Y, SL, SW, ST_v, SS, G)

        quadA = quad_inputs("第一象限")
        quadB = quad_inputs("第二象限")
        quadC = quad_inputs("第三象限")
        quadD = quad_inputs("第四象限")

        submitted = st.form_submit_button("🚀 開始計算")

    # ---------- 輸入確認 ----------
    if not submitted:
        st.info("請在上方輸入參數後按下「開始計算」。")
        st.markdown("---")
        st.write("最後更新時間：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return

    st.subheader("📝 輸入參數確認")
    def show_quad_table(name: str, q: Quad):
        st.markdown(
            f"- **{name}**：X={q.X:.6f} mm，Y={q.Y:.6f} mm；長度={q.SL:.2f} mm；寬度={q.SW:.2f} mm；厚度={q.ST:.2f} mm；行程={q.SS:.2f} mm；G={q.G:.0f}"
        )
    show_quad_table("第一象限", quadA)
    show_quad_table("第二象限", quadB)
    show_quad_table("第三象限", quadC)
    show_quad_table("第四象限", quadD)
    st.markdown(f"- **最大總合力目標 F**：{F_target:.2f} kgf")
    st.markdown(f"- **顯示組合數量 N**：{N_show}")

    # （📈 計算結果、🎯 中心合力、✅ 判定、🧠 最佳化搜尋邏輯同前，略）

    # ---------- 更新時間 ----------
    st.markdown("---")
    st.write("最後更新時間：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    main()

# ----------以下訊息保留 ----------
#使用者自行輸入數值(會有正值或負值)
#1.*"A1"代表彈片中心的第一象限X座標，浮點數，單位mm
#2.*"A2"代表彈片中心的第一象限Y座標，浮點數，單位mm
#3.*"B1"代表彈片中心的第二象限X座標，浮點數，單位mm
#4.*"B2"代表彈片中心的第二象限Y座標，浮點數，單位mm
#5.*"C1"代表彈片中心的第三象限X座標，浮點數，單位mm
#6.*"C2"代表彈片中心的第三象限Y座標，浮點數，單位mm
#7.*"D1"代表彈片中心的第四象限X座標，浮點數，單位mm
#8.*"D2"代表彈片中心的第四象限Y座標，浮點數，單位mm

#使用者自行輸入數值(不會有負值)
#1.*"A_SL"代表第一象限的彈片長度*，浮點數，單位mm
#2.*"A_SW"代表第一象限的彈片寬度*，浮點數，單位mm
#3.*"A_ST"代表第一象限的彈片厚度*，浮點數，單位mm
#4.*"A_SS"代表第一象限的彈片行程*，浮點數，單位mm
#5.*"A_G"代表第一象限的彈片鋼性模數*，浮點數，預設18763
#6.*"B_SL"代表第二象限的彈片長度*，浮點數，單位mm
#7.*"B_SW"代表第二象限的彈片寬度*，浮點數，單位mm
#8.*"B_ST"代表第二象限的彈片厚度*，浮點數，單位mm
#9.*"B_SS"代表第二象限的彈片行程*，浮點數，單位mm
#10.*"B_G"代表第二象限的彈片鋼性模數*，浮點數，預設18763
#11.*"C_SL"代表第三象限的彈片長度*，浮點數，單位mm
#12.*"C_SW"代表第三象限的彈片寬度*，浮點數，單位mm
#13.*"C_ST"代表第三象限的彈片厚度*，浮點數，單位mm
#14.*"C_SS"代表第三象限的彈片行程*，浮點數，單位mm
#15.*"C_G"代表第三象限的彈片鋼性模數*，浮點數，預設18763
#16.*"D_SL"代表第四象限的彈片長度*，浮點數，單位mm
#17.*"D_SW"代表第四象限的彈片寬度*，浮點數，單位mm
#18.*"D_ST"代表第四象限的彈片厚度*，浮點數，單位mm
#19.*"D_SS"代表第四象限的彈片行程*，浮點數，單位mm
#20.*"D_G"代表第四象限的彈片鋼性模數*，浮點數，預設18763
#21.*"F"代表客戶提供的最大總合力*，浮點數，單位kgf
#22.*"N"代表顯示組合數量*，整數，單位groups

#計算公式(會有正值或負值)
#1.*"A_I" = (A_SW*A_ST^3)/12 → 慣性矩 mm^4
#2.*"A_F" = (3*A_G*A_I*A_SS)/(A_SL^3) → 合力 kgf
#3.*"A_XM" = A_F*A1 → X方向力矩 kgf·mm
#4.*"A_YM" = A_F*A2 → Y方向力矩 kgf·mm
#5.*"B_I" = (B_SW*B_ST^3)/12 → 慣性矩 mm^4
#6.*"B_F" = (3*B_G*B_I*B_SS)/(B_SL^3) → 合力 kgf
#7.*"B_XM" = B_F*B1 → X方向力矩 kgf·mm
#8.*"B_YM" = B_F*B2 → Y方向力矩 kgf·mm
#9.*"C_I" = (C_SW*C_ST^3)/12 → 慣性矩 mm^4
#10.*"C_F" = (3*C_G*C_I*C_SS)/(C_SL^3) → 合力 kgf
#11.*"C_XM" = C_F*C1 → X方向力矩 kgf·mm
#12.*"C_YM" = C_F*C2 → Y方向力矩 kgf·mm
#13.*"D_I" = (D_SW*D_ST^3)/12 → 慣性矩 mm^4
#14.*"D_F" = (3*D_G*D_I*D_SS)/(D_SL^3) → 合力 kgf
#15.*"D_XM" = D_F*D1 → X方向力矩 kgf·mm
#16.*"D_YM" = D_F*D2 → Y方向力矩 kgf·mm
#17.*"ALL_X" = ALL_XM/ALL_F → 合力中心X座標 mm
#18.*"ALL_Y" = ALL_YM/ALL_F → 合力中心Y座標 mm
#19.*"ALL_XM" = A_XM+B_XM+C_XM+D_XM → 總X力矩 kgf·mm
#20.*"ALL_YM" = A_YM+B_YM+C_YM+D_YM → 總Y力矩 kgf·mm
#21.*"ALL_F" = A_F+B_F+C_F+D_F → 總合力 kgf

#結果判定
#1.ALL_F需在F±5% 內 → OK / NG
#2.ALL_X、ALL_Y需在±0.5 內 → OK / NG

#最佳化條件
#1.ST ∈ {0.3,0.4,0.5}，ABCD相同
#2.SW >3，且輸入±0.5，間隔0.1，ABCD相同
#3.SL >5，且輸入±0.5，間隔0.1，各象限可不同
#4.SS >0.3，且輸入±0.2，間隔0.05，ABCD相同