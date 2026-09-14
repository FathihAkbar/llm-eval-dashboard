import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import time

sys.path.insert(0, "src")
from evaluator import run_evaluation, DEFAULT_DATASET, DEFAULT_PROMPTS
from metrics import generate_answer, evaluate_response

st.set_page_config(
    page_title="LLM Eval Dashboard",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 LLM Evaluation Dashboard")
st.caption("Bandingkan performa berbagai prompt secara objektif menggunakan LLM-as-Judge")

# ── Sidebar ──────────────────────────────────────────────────
st.sidebar.header("⚙️ Konfigurasi")

mode = st.sidebar.radio(
    "Mode",
    ["📊 Lihat Hasil", "🚀 Jalankan Evaluasi Baru"]
)

RESULTS_PATH = "data/eval_results.csv"
os.makedirs("data", exist_ok=True)

# ── Mode: Lihat Hasil ─────────────────────────────────────────
if mode == "📊 Lihat Hasil":
    if not os.path.exists(RESULTS_PATH):
        st.warning("⚠️ Belum ada hasil evaluasi. Pilih mode 'Jalankan Evaluasi Baru' dulu.")
        st.stop()

    df = pd.read_csv(RESULTS_PATH)
    prompt_names = df["prompt_name"].unique().tolist()
    metrics = ["faithfulness", "relevancy", "completeness", "clarity", "overall"]

    st.subheader("📊 Perbandingan Prompt — Overall Score")

    # ── Summary metrics ──
    avg = df.groupby("prompt_name")[metrics].mean().round(3)
    cols = st.columns(len(prompt_names))
    for i, name in enumerate(prompt_names):
        with cols[i]:
            overall = avg.loc[name, "overall"]
            st.metric(f"🏷️ {name}", f"{overall:.3f}", "overall score")

    st.divider()

    # ── Radar chart ──
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🕸️ Radar Chart — Semua Metrik")
        metric_labels = ["faithfulness", "relevancy", "completeness", "clarity"]
        fig_radar = go.Figure()
        colors = ["#3498db", "#2ecc71", "#e74c3c", "#f39c12"]
        for i, name in enumerate(prompt_names):
            values = [avg.loc[name, m] for m in metric_labels]
            values.append(values[0])
            fig_radar.add_trace(go.Scatterpolar(
                r=values,
                theta=metric_labels + [metric_labels[0]],
                fill="toself",
                name=name,
                line_color=colors[i % len(colors)]
            ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            margin=dict(t=30, b=30)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col2:
        st.subheader("📊 Bar Chart — Per Metrik")
        avg_melted = avg[metric_labels].reset_index().melt(
            id_vars="prompt_name",
            var_name="metric",
            value_name="score"
        )
        fig_bar = px.bar(
            avg_melted,
            x="metric", y="score",
            color="prompt_name",
            barmode="group",
            color_discrete_sequence=colors
        )
        fig_bar.update_layout(
            yaxis_range=[0, 1],
            margin=dict(t=30, b=30)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.divider()

    # ── Per pertanyaan ──
    st.subheader("📋 Detail Per Pertanyaan")
    selected_metric = st.selectbox("Pilih metrik:", metrics)
    pivot = df.pivot_table(
        index="question",
        columns="prompt_name",
        values=selected_metric
    ).round(3)
    pivot["question_short"] = [q[:50] + "..." for q in pivot.index]
    fig_line = px.line(
        pivot.reset_index(),
        x="question",
        y=prompt_names,
        markers=True,
        labels={"value": selected_metric, "question": "Pertanyaan"}
    )
    fig_line.update_layout(
        xaxis_tickangle=-30,
        margin=dict(t=30, b=100)
    )
    st.plotly_chart(fig_line, use_container_width=True)

    st.divider()

    # ── Tabel detail ──
    st.subheader("🔍 Jawaban Detail")
    selected_q = st.selectbox("Pilih pertanyaan:", df["question"].unique())
    filtered = df[df["question"] == selected_q]
    for _, row in filtered.iterrows():
        with st.expander(f"📝 {row['prompt_name']} — Overall: {row['overall']:.3f}"):
            st.markdown(f"**Jawaban:**\n{row['answer']}")
            st.markdown(f"**Referensi:**\n{row['ground_truth']}")
            cols = st.columns(5)
            for i, m in enumerate(metrics):
                cols[i].metric(m, f"{row[m]:.3f}")

    st.divider()

    # ── Download ──
    st.subheader("💾 Export Hasil")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download CSV",
        csv,
        "eval_results.csv",
        "text/csv"
    )

# ── Mode: Jalankan Evaluasi Baru ─────────────────────────────
else:
    st.subheader("🚀 Jalankan Evaluasi Baru")
    st.info("Evaluasi akan memanggil Gemini API beberapa kali. Estimasi waktu: 5-10 menit.")

    # Konfigurasi prompt
    st.subheader("📝 Konfigurasi Prompt")
    use_default = st.checkbox("Pakai prompt default", value=True)

    if use_default:
        prompts = DEFAULT_PROMPTS
        st.json({k: v[:80] + "..." for k, v in prompts.items()})
    else:
        st.info("Fitur custom prompt — tambahkan prompt kamu sendiri:")
        prompts = {}
        n_prompts = st.number_input("Jumlah prompt", 2, 4, 2)
        for i in range(n_prompts):
            name = st.text_input(f"Nama prompt {i+1}", f"Prompt {i+1}")
            content = st.text_area(f"Isi prompt {i+1}", height=100)
            if name and content:
                prompts[name] = content

    # Dataset
    st.subheader("📚 Dataset Evaluasi")
    st.write(f"Menggunakan {len(DEFAULT_DATASET)} pertanyaan default tentang ML/AI")
    with st.expander("Lihat pertanyaan"):
        for i, item in enumerate(DEFAULT_DATASET, 1):
            st.write(f"{i}. {item['question']}")

    # Jalankan
    if st.button("▶️ Mulai Evaluasi", type="primary"):
        if not prompts:
            st.error("Tambahkan minimal 1 prompt dulu!")
        else:
            total = len(prompts) * len(DEFAULT_DATASET)
            st.info(f"Total: {total} evaluasi. Estimasi: {total * 15 // 60} menit {total * 15 % 60} detik")

            progress = st.progress(0)
            status = st.empty()
            results = []
            current = 0

            for prompt_name, system_prompt in prompts.items():
                for item in DEFAULT_DATASET:
                    current += 1
                    status.text(f"[{current}/{total}] {prompt_name} | {item['question'][:40]}...")

                    answer = generate_answer(item["question"], system_prompt)
                    scores = evaluate_response(item["question"], answer, item["ground_truth"])

                    results.append({
                        "prompt_name": prompt_name,
                        "question": item["question"],
                        "answer": answer,
                        "ground_truth": item["ground_truth"],
                        **scores
                    })

                    progress.progress(current / total)

                    if current < total:
                        time.sleep(65)

            df = pd.DataFrame(results)
            df.to_csv(RESULTS_PATH, index=False)

            status.success(f"✅ Evaluasi selesai! {total} jawaban dievaluasi.")
            st.balloons()