import streamlit as st
import pandas as pd
import plotly.express as px

# 項目定義
columns = [
    "名前", "サーブ打数", "サーブ決定数", "サーブ効果数", "サーブミス数",
    "サーブカットA数", "サーブカットB数", "サーブカットC数", "サーブカットミス",
    "スパイク打数", "スパイク決定数", "スパイク被ブロック数", "スパイクミス数", "ブロック決定数"
]

# 初期化
if "input_rows" not in st.session_state:
    st.session_state.input_rows = 1

if "volleyball_data" not in st.session_state:
    st.session_state.volleyball_data = pd.DataFrame(columns=columns)

# タブ選択
tab = st.sidebar.radio("メニュー", ["データ入力", "グラフ表示"])

# データ入力タブ
if tab == "データ入力":
    st.header("バレーボールスコア入力")

    with st.form("score_form"):
        inputs = []
        for i in range(st.session_state.input_rows):
            st.markdown(f"### 選手 {i+1}")
            col1, col2, col3 = st.columns(3)

            with col1:
                name = st.text_input(f"名前_{i}", key=f"name_{i}")
                serve_attempts = st.number_input(f"サーブ打数_{i}", min_value=0, key=f"serve_attempts_{i}")
                serve_success = st.number_input(f"サーブ決定数_{i}", min_value=0, key=f"serve_success_{i}")
                serve_effective = st.number_input(f"サーブ効果数_{i}", min_value=0, key=f"serve_effective_{i}")
                serve_miss = st.number_input(f"サーブミス数_{i}", min_value=0, key=f"serve_miss_{i}")

            with col2:
                cut_a = st.number_input(f"サーブカットA数_{i}", min_value=0, key=f"cut_a_{i}")
                cut_b = st.number_input(f"サーブカットB数_{i}", min_value=0, key=f"cut_b_{i}")
                cut_c = st.number_input(f"サーブカットC数_{i}", min_value=0, key=f"cut_c_{i}")
                cut_miss = st.number_input(f"サーブカットミス_{i}", min_value=0, key=f"cut_miss_{i}")

            with col3:
                spike_attempts = st.number_input(f"スパイク打数_{i}", min_value=0, key=f"spike_attempts_{i}")
                spike_success = st.number_input(f"スパイク決定数_{i}", min_value=0, key=f"spike_success_{i}")
                spike_blocked = st.number_input(f"スパイク被ブロック数_{i}", min_value=0, key=f"spike_blocked_{i}")
                spike_miss = st.number_input(f"スパイクミス数_{i}", min_value=0, key=f"spike_miss_{i}")
                block_success = st.number_input(f"ブロック決定数_{i}", min_value=0, key=f"block_success_{i}")

            inputs.append([
                name, serve_attempts, serve_success, serve_effective, serve_miss,
                cut_a, cut_b, cut_c, cut_miss,
                spike_attempts, spike_success, spike_blocked, spike_miss, block_success
            ])

        submitted = st.form_submit_button("保存")
        if submitted:
            new_data = pd.DataFrame(inputs, columns=columns)
            st.session_state.volleyball_data = pd.concat([st.session_state.volleyball_data, new_data], ignore_index=True)
            st.success("データを保存しました")

    if st.button("入力欄を追加"):
        st.session_state.input_rows += 1

# グラフ表示タブ
elif tab == "グラフ表示":
    st.header("スコア分析グラフ")

    if st.session_state.volleyball_data.empty:
        st.warning("まだデータが入力されていません")
    else:
        st.dataframe(st.session_state.volleyball_data)

        df = st.session_state.volleyball_data

        # 得点構成チャート
        score_data = pd.DataFrame(columns=["選手", "タイプ", "件数"])
        for _, row in df.iterrows():
            score_data = pd.concat([
                score_data,
                pd.DataFrame([
                    {"選手": row["名前"], "タイプ": "サーブ決定数", "件数": row["サーブ決定数"]},
                    {"選手": row["名前"], "タイプ": "スパイク決定数", "件数": row["スパイク決定数"]},
                    {"選手": row["名前"], "タイプ": "ブロック決定数", "件数": row["ブロック決定数"]}
                ])
            ], ignore_index=True)

        fig_score = px.sunburst(
            score_data,
            path=["選手", "タイプ"],
            values="件数",
            title="選手別得点構成",
            color="タイプ",
            color_discrete_map={
                "サーブ決定数": "lightblue",
                "スパイク決定数": "deepskyblue",
                "ブロック決定数": "blue"
            }
        )

        # 失点構成チャート
        error_data = pd.DataFrame(columns=["選手", "タイプ", "件数"])
        for _, row in df.iterrows():
            error_data = pd.concat([
                error_data,
                pd.DataFrame([
                    {"選手": row["名前"], "タイプ": "サーブミス数", "件数": row["サーブミス数"]},
                    {"選手": row["名前"], "タイプ": "スパイクミス数", "件数": row["スパイクミス数"]},
                    {"選手": row["名前"], "タイプ": "サーブカットミス", "件数": row["サーブカットミス"]}
                ])
            ], ignore_index=True)

        fig_error = px.sunburst(
            error_data,
            path=["選手", "タイプ"],
            values="件数",
            title="選手別失点構成",
            color="タイプ",
            color_discrete_map={
                "サーブミス数": "lightcoral",
                "スパイクミス数": "red",
                "サーブカットミス": "darkred"
            }
        )

        # 横並びに表示
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(fig_score, use_container_width=True)
        with col2:
            st.plotly_chart(fig_error, use_container_width=True)

