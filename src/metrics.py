import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import json

load_dotenv()


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=os.getenv("GEMINI_API_KEY"),
    )


def evaluate_response(question: str, answer: str, ground_truth: str) -> dict:
    """Evaluasi jawaban menggunakan LLM-as-Judge"""
    llm = get_llm()

    prompt = f"""Kamu adalah evaluator AI yang objektif. Nilai jawaban berikut.

Pertanyaan: {question}
Jawaban Referensi: {ground_truth}
Jawaban yang Dinilai: {answer}

Berikan penilaian HANYA dalam format JSON ini (tanpa markdown):
{{
  "faithfulness": <0.0-1.0, seberapa akurat jawaban sesuai fakta>,
  "relevancy": <0.0-1.0, seberapa relevan jawaban dengan pertanyaan>,
  "completeness": <0.0-1.0, seberapa lengkap jawaban>,
  "clarity": <0.0-1.0, seberapa jelas dan mudah dipahami jawaban>,
  "reasoning": "<satu kalimat alasan penilaian>"
}}"""

    response = llm.invoke(prompt)
    content = response.content

    if isinstance(content, list):
        content = " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in content])

    raw = content.strip().replace("```json", "").replace("```", "").strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    raw = raw[start:end]

    scores = json.loads(raw)
    scores["overall"] = round(
        (scores["faithfulness"] + scores["relevancy"] +
         scores["completeness"] + scores["clarity"]) / 4, 3
    )
    return scores


def generate_answer(question: str, system_prompt: str) -> str:
    """Generate jawaban menggunakan system prompt tertentu"""
    llm = get_llm()
    from langchain_core.messages import HumanMessage, SystemMessage
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ]
    response = llm.invoke(messages)
    content = response.content
    if isinstance(content, list):
        content = " ".join([c.get("text", "") if isinstance(c, dict) else str(c) for c in content])
    return content