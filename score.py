import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
import uuid
import os
import json
from datetime import datetime

# ログイン認証
def login():
    st.title("ログイン")
    username = st.text_input("ユーザーID")
    password = st.text_input("パスワード", type="password")
    if st.button("ログイン"):
        if username == "yokohamaz" and password == "father":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("ユーザーIDまたはパスワードが間違っています")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    login()
    st.stop()

# 項目定義
columns = [
    "名前", "サーブ打数", "サーブ決定数", "サーブ効果数", "サーブミス数",
    "サーブカットA数", "サーブカットB数", "サーブカットC数", "サーブカットミス",
    "スパイク打数", "スパイク決定数", "スパイク被ブロック数", "スパイクミス数", "ブロック決定数"
]

# 初期化
if "input_rows" not in st.session_state:
    st.session_state.input_rows = 12
if "volleyball_data" not in st.session_state:
    st.session_state.volleyball_data = pd.DataFrame(columns=columns)
if "match_info" not in st.session_state:
    st.session_state.match_info = {
        "date": "",
        "location": "",
        "opponent": "",
        "score": ""
    }

# 保存フォルダ
SAVE_DIR = "saved_matches"
os.makedirs(SAVE_DIR, exist_ok=True)

# タブ選択
tab = st.sidebar.radio("メニュー", ["入力シート", "分析シート", "保存済みシート"])

# 入力シート
if tab == "入力シート":
    st.header("試合情報入力")
    col1, col2, col3 = st.columns(3)
    st.session_state.match_info["date"] = col1.date_input("日付")
    st.session_state.match_info["location"] = col2.text_input("場所")
    st.session_state.match_info["opponent"] = col3.text_input("対戦相手")
    st.session_state.match_info["score"] = st.text_input("最終スコア（例: 21 - 19）")

    input_method = st.radio("入力方法を選択", ["手入力", "Excelアップロード"])
    if input_method == "手入力":
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
                st.session_state.volleyball_data = pd.DataFrame(inputs, columns=columns)
                st.success("データを保存しました")
    else:
        uploaded_file = st.file_uploader("Excelファイルをアップロードしてください", type=["xlsx"])
        if uploaded_file:
            try:
                df_uploaded = pd.read_excel(uploaded_file, engine="openpyxl")
                if all(col in df_uploaded.columns for col in columns):
                    st.session_state.volleyball_data = df_uploaded[columns]
                    st.success("Excelデータを読み込みました")
                else:
                    st.error("Excelファイルの列名が正しくありません。")
            except Exception as e:
                st.error(f"読み込みエラー: {e}")

    # 保存ボタン
    if st.button("この試合データを保存する"):
        date_str = st.session_state.match_info["date"].strftime("%Y%m%d") if st.session_state.match_info["date"] else "未設定"
        location = st.session_state.match_info["location"].replace(" ", "_")
        opponent = st.session_state.match_info["opponent"].replace(" ", "_")
        match_id = f"{date_str}_{location}_{opponent}"
        save_data = {
            "match_info": {
                "date": st.session_state.match_info["date"].strftime("%Y-%m-%d") if st.session_state.match_info["date"] else "",
                "location": st.session_state.match_info["location"],
                "opponent": st.session_state.match_info["opponent"],
                "score": st.session_state.match_info["score"]
            },
            "volleyball_data": st.session_state.volleyball_data.to_dict(orient="records")
        }
        with open(os.path.join(SAVE_DIR, f"{match_id}.json"), "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
        st.success("試合データを保存しました")

# 保存済みシート
elif tab == "保存済みシート":
    st.header("保存済み試合一覧")
    saved_files = [f for f in os.listdir(SAVE_DIR) if f.endswith(".json")]
    if saved_files:
        selected_file = st.selectbox("表示する試合を選択", saved_files)
        if st.button("この試合を読み込む"):
            with open(os.path.join(SAVE_DIR, selected_file), "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
                st.session_state.match_info = {
                    "date": datetime.strptime(loaded_data["match_info"]["date"], "%Y-%m-%d").date(),
                    "location": loaded_data["match_info"]["location"],
                    "opponent": loaded_data["match_info"]["opponent"],
                    "score": loaded_data["match_info"]["score"]
                }
                st.session_state.volleyball_data = pd.DataFrame(loaded_data["volleyball_data"])
                st.success("試合データを読み込みました。左の「分析シート」タブで確認できます。")
    else:
        st.info("保存された試合データはまだありません。")

# 分析シート
elif tab == "分析シート":
    st.header("試合情報")
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"**日付**: {st.session_state.match_info['date']}")
    col2.markdown(f"**場所**: {st.session_state.match_info['location']}")
    col3.markdown(f"**対戦相手**: {st.session_state.match_info['opponent']}")
    st.markdown(f"<h2 style='font-size:2em;'>最終スコア: {st.session_state.match_info['score']}</h2>", unsafe_allow_html=True)

    df = st.session_state.volleyball_data
    df = df[df["名前"].notna() & (df["名前"] != "")]

    if df.empty:
        st.warning("まだデータが入力されていません")
    else:
        st.subheader("選手データ")
        st.dataframe(df)

        # 色マップ
        player_names = df["名前"].tolist()
        color_palette = px.colors.qualitative.Set3
        color_map = {name: color_palette[i % len(color_palette)] for i, name in enumerate(player_names)}

        # サーブ構成
        serve_df = df[["名前", "サーブ打数", "サーブ決定数", "サーブ効果数", "サーブミス数"]][::-1]
        serve_fig = px.bar(serve_df, y="名前", x=serve_df.columns[1:], orientation="h", title="サーブ構成", color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(serve_fig)

        # スパイク構成
        spike_df = df[["名前", "スパイク打数", "スパイク決定数", "スパイク被ブロック数", "スパイクミス数"]][::-1]
        spike_fig = px.bar(spike_df, y="名前", x=spike_df.columns[1:], orientation="h", title="スパイク構成", color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(spike_fig)

        # サーブカット構成
        cut_df = df[["名前", "サーブカットA数", "サーブカットB数", "サーブカットC数", "サーブカットミス"]][::-1]
        cut_fig = px.bar(cut_df, y="名前", x=cut_df.columns[1:], orientation="h", title="サーブカット構成", color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(cut_fig)

        # 得点構成チャート
        score_data = pd.DataFrame([
            {"選手": row["名前"], "タイプ": t, "件数": row[t]}
            for _, row in df.iterrows()
            for t in ["サーブ決定数", "スパイク決定数", "ブロック決定数"]
        ])
        fig_score = px.sunburst(score_data, path=["選手", "タイプ"], values="件数", title="選手別得点構成", color="選手", color_discrete_map=color_map)
        fig_score.update_traces(marker=dict(colorscale="Blues"))
        st.plotly_chart(fig_score)

        # 失点構成チャート
        error_data = pd.DataFrame([
            {"選手": row["名前"], "タイプ": t, "件数": row[t]}
            for _, row in df.iterrows()
            for t in ["サーブミス数", "スパイクミス数", "サーブカットミス"]
        ])
        fig_error = px.sunburst(error_data, path=["選手", "タイプ"], values="件数", title="選手別失点構成", color="選手", color_discrete_map=color_map)
        fig_error.update_traces(marker=dict(colorscale="Reds"))
        st.plotly_chart(fig_error)

        # ファイル名生成
        date_str = st.session_state.match_info["date"].strftime("%Y%m%d") if st.session_state.match_info["date"] else "未設定"
        location = st.session_state.match_info["location"].replace(" ", "_")
        opponent = st.session_state.match_info["opponent"].replace(" ", "_")
        download_filename = f"{date_str}_{location}_{opponent}.html"

        # HTMLダウンロードボタン
        html_id = str(uuid.uuid4())
        html_path = f"volleyball_charts_{html_id}.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write("<html><head><meta charset='utf-8'><title>分析シート</title></head><body>")
            f.write(f"<h2>日付: {st.session_state.match_info['date']}　場所: {st.session_state.match_info['location']}　対戦相手: {st.session_state.match_info['opponent']}</h2>")
            f.write(f"<h1>最終スコア: {st.session_state.match_info['score']}</h1>")
            f.write("<h2>選手データ</h2>")
            f.write(df.to_html(index=False))
            f.write("<h2>サーブ構成</h2>")
            f.write(pio.to_html(serve_fig, include_plotlyjs='cdn', full_html=False))
            f.write("<h2>スパイク構成</h2>")
            f.write(pio.to_html(spike_fig, include_plotlyjs='cdn', full_html=False))
            f.write("<h2>サーブカット構成</h2>")
            f.write(pio.to_html(cut_fig, include_plotlyjs='cdn', full_html=False))
            f.write("<h2>得点構成チャート</h2>")
            f.write(pio.to_html(fig_score, include_plotlyjs='cdn', full_html=False))
            f.write("<h2>失点構成チャート</h2>")
            f.write(pio.to_html(fig_error, include_plotlyjs='cdn', full_html=False))
            f.write("</body></html>")
        with open(html_path, "rb") as f:
            st.download_button("分析シートをHTMLでダウンロード", f, file_name=download_filename, mime="text/html")
        os.remove(html_path)

