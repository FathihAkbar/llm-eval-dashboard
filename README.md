# 🔬 LLM Evaluation Dashboard

Dashboard interaktif untuk **membandingkan performa berbagai prompt** secara objektif menggunakan metode **LLM-as-Judge**. Visualisasikan faithfulness, relevancy, completeness, dan clarity dari setiap prompt dalam satu dashboard.

---

## 🖥️ Demo

<img width="1663" height="845" alt="image" src="https://github.com/user-attachments/assets/a34d30db-189e-4f5d-909c-b7eb52371eeb" />


---

## 📊 Hasil Evaluasi

| Prompt | Faithfulness | Relevancy | Completeness | Clarity | Overall |
|--------|-------------|-----------|--------------|---------|---------|
| Prompt Detail | 0.88 | 0.87 | 0.86 | 0.88 | **0.866** |
| Prompt ELI5 | 0.80 | 0.79 | 0.78 | 0.80 | **0.793** |
| Prompt Singkat | 0.71 | 0.72 | 0.70 | 0.71 | **0.711** |

> **Kesimpulan:** Prompt Detail unggul di semua metrik — memberikan jawaban yang lebih lengkap, akurat, dan jelas dibanding prompt singkat maupun ELI5.

---

## 🏗️ Arsitektur

```
Dataset (pertanyaan + ground truth)
           │
           ▼
  [Generate Answer]     ← Gemini + System Prompt
           │
           ▼
  [LLM-as-Judge]        ← Gemini menilai jawaban
           │
           ▼
  [Scoring]             ← faithfulness, relevancy,
                           completeness, clarity
           │
           ▼
  [Streamlit Dashboard] ← visualisasi interaktif
```

---

## 📈 Metrik Evaluasi

| Metrik | Deskripsi |
|--------|-----------|
| **Faithfulness** | Seberapa akurat jawaban sesuai fakta (tidak hallusinasi) |
| **Relevancy** | Seberapa relevan jawaban dengan pertanyaan |
| **Completeness** | Seberapa lengkap jawaban mencakup semua aspek |
| **Clarity** | Seberapa jelas dan mudah dipahami jawaban |
| **Overall** | Rata-rata keempat metrik di atas |

---

## ✨ Fitur Dashboard

- **📊 Overall Score** — perbandingan skor tiap prompt sekilas
- **🕸️ Radar Chart** — visualisasi semua metrik sekaligus
- **📊 Bar Chart** — breakdown skor per metrik per prompt
- **📈 Line Chart** — trend performa per pertanyaan
- **🔍 Jawaban Detail** — lihat jawaban lengkap + skor per prompt
- **💾 Export CSV** — download hasil evaluasi

---

## ⚙️ Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| LLM | Google Gemini 3.6 Flash |
| Evaluasi | LLM-as-Judge (Gemini) |
| Dashboard | Streamlit |
| Visualisasi | Plotly |
| Data Processing | Pandas |

---

## 🚀 Cara Menjalankan

### 1. Clone & Install
```bash
git clone https://github.com/USERNAME/llm-eval-dashboard.git
cd llm-eval-dashboard
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Setup API Key
Buat file `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

### 3. Jalankan Dashboard
```bash
streamlit run app.py
```

Buka `http://localhost:8501`

---

## 📁 Struktur Project

```
llm-eval-dashboard/
├── src/
│   ├── evaluator.py    # Evaluation pipeline
│   └── metrics.py      # LLM-as-Judge scoring
├── data/
│   └── eval_results.csv  # Hasil evaluasi
├── app.py              # Streamlit dashboard
├── .env
└── requirements.txt
```

---

## 💡 Cara Pakai

### Mode Lihat Hasil
Langsung lihat hasil evaluasi yang sudah ada dalam bentuk chart interaktif.

### Mode Evaluasi Baru
1. Pilih prompt default atau buat prompt sendiri
2. Klik **Mulai Evaluasi**
3. Tunggu proses selesai (~10 menit)
4. Pindah ke mode **Lihat Hasil**

---

## 🔮 Pengembangan Selanjutnya

- [ ] Support multiple model (GPT-4, Claude, Gemini)
- [ ] Custom dataset upload
- [ ] A/B testing statistik (t-test, confidence interval)
- [ ] Scheduled evaluation otomatis
- [ ] Export laporan ke PDF
