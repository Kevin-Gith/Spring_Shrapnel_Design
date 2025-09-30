#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import streamlit as st
from dataclasses import dataclass
from datetime import datetime
import itertools

# -------------------- 資料結構 --------------------
@dataclass
class Quad:
    X: float   # 鎖點X座標 (mm)
    Y: float   # 鎖點Y座標 (mm)
    SL: float  # 彈片長度 (mm)
    SW: float  # 彈片寬度 (mm)
    ST: float  # 彈片厚度 (mm)
    SS: float  # 彈片行程 (mm)
    G: float   # 彈片鋼性模數 (kgf/mm²)

    # 慣性矩 I = (SW * ST^3) / 12
    def inertia(self) -> float:
        return (self.SW * (self.ST ** 3)) / 12.0

    # 合力 F = (3 * G * I * SS) / SL^3
    def force(self) -> float:
        I = self.inertia()
        return (3.0 * self.G * I * self.SS) / (self.SL ** 3)

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
    """ 星星等級：修改越少，星數越高 """
    if not modified_params:
        return "★"
    if modified_params == {"ST"}:
        return "★★★★"
    if "ST" in modified_params:
        others = len(modified_params) - 1
        return {1: "★★★", 2: "★★", 3: "★"}.get(others, "★")
    else:
        return {1: "★★★", 2: "★★", 3: "★"}.get(len(modified_params), "★")


# -------------------- Streamlit App --------------------
def main():
    st.set_page_config(page_title="彈片彈簧計算器", page_icon="⚙️", layout="wide")
    st.title("⚙️ 彈片彈簧計算器")

    param_map = {"SL": "長度", "SW": "寬度", "ST": "厚度", "SS": "行程"}
    star_rank = {"★★★★": 4, "★★★": 3, "★★": 2, "★": 1}

    with st.form("form"):
        st.subheader("📌 目標與顯示")
        col1, col2 = st.columns(2)
        with col1:
            F_target = st.number_input("客戶提供的最大總合力 (kgf)", min_value=0.1, value=50.0)
        with col2:
            N_show = st.number_input("顯示組合數量 N (groups)", min_value=1, value=5, step=1)

        st.markdown("---")
        st.subheader("📌 彈片參數輸入")

        def quad_inputs(label: str, defaultX=0.0, defaultY=0.0):
            with st.expander(f"{label}的彈片參數", expanded=True):
                X = st.number_input("鎖點X座標", value=defaultX, step=0.01, format="%.2f")
                Y = st.number_input("鎖點Y座標", value=defaultY, step=0.01, format="%.2f")
                SL = st.number_input("彈片長度 (mm)", min_value=0.1, value=20.0, step=0.1)
                SW = st.number_input("彈片寬度 (mm)", min_value=0.1, value=5.0, step=0.1)
                ST_v = st.number_input("彈片厚度 (mm)", min_value=0.1, value=0.3, step=0.1)
                SS = st.number_input("彈片行程 (mm)", min_value=0.1, value=0.5, step=0.05)
                G = st.number_input("彈片鋼性模數 (kgf/mm²)", min_value=0.0, value=18763.0, step=1.0)
            return Quad(X, Y, SL, SW, ST_v, SS, G)


        quadA = quad_inputs("第一象限", 10.0, 10.0)
        quadB = quad_inputs("第二象限", -10.0, 10.0)
        quadC = quad_inputs("第三象限", -10.0, -10.0)
        quadD = quad_inputs("第四象限", 10.0, -10.0)

        submitted = st.form_submit_button("🚀 開始計算 / 最佳化")

    if not submitted:
        st.info("請在上方輸入參數後按下「開始計算 / 最佳化」。")
        st.write("最後更新時間：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return

    # --------- 計算單象限結果 ---------
    st.subheader("📈 四象限計算結果")
    quads = {"第一": quadA, "第二": quadB, "第三": quadC, "第四": quadD}

    total_F = total_XM = total_YM = 0.0
    cols_res = st.columns(4)
    for idx, name in enumerate(["第一", "第二", "第三", "第四"]):
        q = quads[name]
        I = round(q.inertia(), 6)   # *I
        F = round(q.force(), 6)     # *F
        XM = round(q.moment_x(F), 6)  # *XM
        YM = round(q.moment_y(F), 6)  # *YM

        total_F += F
        total_XM += XM
        total_YM += YM

        with cols_res[idx]:
            st.markdown(f"**{name}象限**")
            st.write(f"慣性矩 I (mm⁴)：{I:.4f}")
            st.write(f"X方向力矩（kgf·mm）：{XM:.2f}")
            st.write(f"Y方向力矩（kgf·mm）：{YM:.2f}")
            st.write(f"合力 F（kgf）：{F:.2f}")

    ALL_X = (total_XM / total_F) if total_F != 0 else 0.0
    ALL_Y = (total_YM / total_F) if total_F != 0 else 0.0

    st.subheader("🎯 中心合力結果")
    st.write(f"合力中心 X 座標：{ALL_X:.2f}")
    st.write(f"合力中心 Y 座標：{ALL_Y:.2f}")
    st.write(f"合力中心 X 總力矩（kgf·mm）：{total_XM:.2f}")
    st.write(f"合力中心 Y 總力矩（kgf·mm）：{total_YM:.2f}")
    st.write(f"總合力 F（kgf）：{total_F:.2f}")

    # --------- 結果判定 ---------
    st.subheader("✅ 結果判定")
    lower_bound = F_target * 0.95
    upper_bound = F_target * 1.05
    X_status = "OK" if -0.5 <= ALL_X <= 0.5 else "NG"
    Y_status = "OK" if -0.5 <= ALL_Y <= 0.5 else "NG"
    F_status = "OK" if lower_bound <= total_F <= upper_bound else "NG"

    st.write(f"合力中心 X 座標 (範圍 -0.5 ~ +0.5)：**{X_status}**")
    st.write(f"合力中心 Y 座標 (範圍 -0.5 ~ +0.5)：**{Y_status}**")
    st.write(f"總合力 F (範圍 {lower_bound:.2f} ~ {upper_bound:.2f})：**{F_status}**")

    # -------------------- 最佳化搜尋 --------------------
    st.subheader("🧠 最佳化搜尋（滿足 F±5%、X/Y 在 ±0.5）")

    ST_candidates = [0.3, 0.4, 0.5]
    base_SW = quadA.SW
    SW_candidates = frange(max(3.0, base_SW - 0.5), base_SW + 0.5, 0.1)
    base_SS = quadA.SS
    SS_candidates = frange(max(0.3, base_SS - 0.2), base_SS + 0.2, 0.05)
    SL_bases = [quadA.SL, quadB.SL, quadC.SL, quadD.SL]
    SL_ranges = [frange(max(5.0, base - 0.5), base + 0.5, 0.1) for base in SL_bases]

    results = []
    for ST_val in ST_candidates:
        for SW_val in SW_candidates:
            for SS_val in SS_candidates:
                for SL_combo in itertools.product(*SL_ranges):
                    opt = {
                        "第一": Quad(quadA.X, quadA.Y, SL_combo[0], SW_val, ST_val, SS_val, quadA.G),
                        "第二": Quad(quadB.X, quadB.Y, SL_combo[1], SW_val, ST_val, SS_val, quadB.G),
                        "第三": Quad(quadC.X, quadC.Y, SL_combo[2], SW_val, ST_val, SS_val, quadC.G),
                        "第四": Quad(quadD.X, quadD.Y, SL_combo[3], SW_val, ST_val, SS_val, quadD.G),
                    }
                    totF = totXM = totYM = 0.0
                    for nm in ["第一", "第二", "第三", "第四"]:
                        Fi = opt[nm].force()
                        Xi = opt[nm].moment_x(Fi)
                        Yi = opt[nm].moment_y(Fi)
                        totF += Fi
                        totXM += Xi
                        totYM += Yi
                    allX = (totXM / totF) if totF != 0 else 0.0
                    allY = (totYM / totF) if totF != 0 else 0.0
                    if not (lower_bound <= totF <= upper_bound): continue
                    if not (-0.5 <= allX <= 0.5 and -0.5 <= allY <= 0.5): continue
                    modified = set()
                    if round(ST_val - quadA.ST, 6) != 0: modified.add("ST")
                    if round(SW_val - quadA.SW, 6) != 0: modified.add("SW")
                    if any(round(SL_combo[i] - SL_bases[i], 6) != 0 for i in range(4)): modified.add("SL")
                    if round(SS_val - quadA.SS, 6) != 0: modified.add("SS")
                    stars = assign_stars(modified)
                    results.append((ST_val, SW_val, SL_combo, SS_val, totF, allX, allY, stars, modified))

    if not results:
        st.warning("❌ 找不到符合條件的最佳化組合，請調整輸入條件或範圍。")
    else:
        results.sort(key=lambda x: (-star_rank.get(x[7], 1), abs(x[4] - F_target)))
        st.success(f"✅ 找到 {len(results)} 組符合條件的最佳化結果，顯示前 {min(N_show, len(results))} 組：")
        for idx, (STv, SWv, SLs, SSv, totF, allX, allY, stars, modified) in enumerate(results[:N_show], 1):
            with st.expander(f"組合 {idx}（{stars}）", expanded=(idx == 1)):
                for i, nm in enumerate(["第一", "第二", "第三", "第四"]):
                    st.write(f"{nm}象限 → 長度={SLs[i]:.2f} mm / 寬度={SWv:.2f} mm / 厚度={STv:.2f} mm / 行程={SSv:.2f} mm")
                modified_cn = [param_map[p] for p in sorted(modified)]
                st.write(f"🔧 修改參數：{('、'.join(modified_cn)) if modified_cn else '無'}")
                st.write(f"合力中心 X：{allX:.2f}，Y：{allY:.2f}，總合力 F：{totF:.2f} kgf")

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