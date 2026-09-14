import pandas as pd
import time
from metrics import evaluate_response, generate_answer

# Dataset evaluasi default
DEFAULT_DATASET = [
    {
        "question": "Apa itu machine learning?",
        "ground_truth": "Machine learning adalah cabang AI yang memungkinkan komputer belajar dari data tanpa diprogram secara eksplisit."
    },
    {
        "question": "Jelaskan perbedaan supervised dan unsupervised learning.",
        "ground_truth": "Supervised learning menggunakan data berlabel untuk melatih model, sedangkan unsupervised learning menemukan pola dari data tanpa label."
    },
    {
        "question": "Apa itu overfitting dalam machine learning?",
        "ground_truth": "Overfitting terjadi ketika model terlalu menyesuaikan diri dengan data training sehingga performa buruk pada data baru."
    },
]

# Prompt yang akan dibandingkan
DEFAULT_PROMPTS = {
    "Prompt Singkat": "Jawab pertanyaan berikut dengan singkat dan jelas dalam Bahasa Indonesia.",
    "Prompt Detail": """Kamu adalah asisten AI yang ahli di bidang teknologi dan data science.
Jawab pertanyaan berikut dalam Bahasa Indonesia dengan:
- Penjelasan yang jelas dan mudah dipahami
- Contoh konkret jika relevan
- Panjang jawaban yang proporsional""",
    "Prompt ELI5": """Jelaskan seperti sedang berbicara kepada seseorang yang baru belajar.
Gunakan analogi sederhana dan hindari jargon teknis yang rumit.
Jawab dalam Bahasa Indonesia.""",
}


def run_evaluation(
    prompts: dict,
    dataset: list,
    delay: float = 15.0
) -> pd.DataFrame:
    """Jalankan evaluasi untuk semua prompt dan pertanyaan"""
    results = []

    total = len(prompts) * len(dataset)
    current = 0

    for prompt_name, system_prompt in prompts.items():
        for item in dataset:
            current += 1
            print(f"[{current}/{total}] {prompt_name} | {item['question'][:40]}...")

            # Generate jawaban
            answer = generate_answer(item["question"], system_prompt)

            # Evaluasi jawaban
            scores = evaluate_response(
                item["question"],
                answer,
                item["ground_truth"]
            )

            results.append({
                "prompt_name": prompt_name,
                "question": item["question"],
                "answer": answer,
                "ground_truth": item["ground_truth"],
                **scores
            })

            # Delay untuk hindari rate limit
            if current < total:
                print(f"   ⏳ Tunggu {delay}s...")
                time.sleep(delay)

    return pd.DataFrame(results)