import streamlit as st
import pandas as pd
import plotly.express as px

tab = st.sidebar.radio("メニュー", ["データ入力", "グラフ表示"])

if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "プレイヤー", "スパイク_打数", "スパイク_決定数", "スパイク_効果数", "スパイク_被ブロック", "スパイク_ミス",
        "サーブ_打数", "サーブ_決定数", "サーブ_効果数", "サーブ_被ブロック", "サーブ_ミス",
        "レシーブ_A", "レシーブ_B", "レシーブ_C", "最終スコア"
    ])

if tab == "データ入力":
    st.title("バレーボールスコア入力")

    with st.form("score_form"):
        player = st.text_input("プレイヤー名")

        st.subheader("スパイク")
        spike_attempts = st.number_input("打数（スパイク）", min_value=0, step=1)
        spike_success = st.number_input("決定数（スパイク）", min_value=0, step=1)
        spike_effective = st.number_input("効果数（スパイク）", min_value=0, step=1)
        spike_blocked = st.number_input("被ブロック（スパイク）", min_value=0, step=1)
        spike_miss = st.number_input("ミス（スパイク）", min_value=0, step=1)

        st.subheader("サーブ")
        serve_attempts = st.number_input("打数（サーブ）", min_value=0, step=1)
        serve_success = st.number_input("決定数（サーブ）", min_value=0, step=1)
        serve_effective = st.number_input("効果数（サーブ）", min_value=0, step=1)
        serve_blocked = st.number_input("被ブロック（サーブ）", min_value=0, step=1)
        serve_miss = st.number_input("ミス（サーブ）", min_value=0, step=1)

        st.subheader("サーブレシーブ")
        receive_a = st.number_input("A本数", min_value=0, step=1)
        receive_b = st.number_input("B本数", min_value=0, step=1)
        receive_c = st.number_input("C本数", min_value=0, step=1)

        final_score = st.number_input("最終スコア", min_value=0, step=1)

        submitted = st.form_submit_button("追加")

        if submitted:
            new_data = pd.DataFrame([[
                player, spike_attempts, spike_success, spike_effective, spike_blocked, spike_miss,
                serve_attempts, serve_success, serve_effective, serve_blocked, serve_miss,
                receive_a, receive_b, receive_c, final_score
            ]], columns=st.session_state.data.columns)
            st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
            st.success("データを追加しました")

    st.write("現在のデータ")
    st.dataframe(st.session_state.data)

elif tab == "グラフ表示":
    st.title("スコア分析グラフ")

    if st.session_state.data.empty:
        st.warning("データがありません。まずはデータ入力タブでデータを追加してください。")
    else:
        df = st.session_state.data

        st.subheader("プレイヤーごとの最終スコア")
        fig1 = px.bar(df, x="プレイヤー", y="最終スコア", title="最終スコア")
        st.plotly_chart(fig1)

        st.subheader("スパイク決定率")
        df["スパイク決定率"] = df["スパイク_決定数"] / df["スパイク_打数"].replace(0, pd.NA)
        fig2 = px.bar(df, x="プレイヤー", y="スパイク決定率", title="スパイク決定率")
        st.plotly_chart(fig2)

        st.subheader("サーブ効果率")
        df["サーブ効果率"] = df["サーブ_効果数"] / df["サーブ_打数"].replace(0, pd.NA)
        fig3 = px.bar(df, x="プレイヤー", y="サーブ効果率", title="サーブ効果率")
        st.plotly_chart(fig3)

        st.subheader("サーブレシーブ分布")
        receive_df = df[["プレイヤー", "レシーブ_A", "レシーブ_B", "レシーブ_C"]].melt(id_vars="プレイヤー", var_name="タイプ", value_name="本数")
        fig4 = px.bar(receive_df, x="プレイヤー", y="本数", color="タイプ", title="サーブレシーブ分布", barmode="stack")
        st.plotly_chart(fig4)
