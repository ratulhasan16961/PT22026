import gradio as gr
import joblib
import pandas as pd

from features import FEATURE_NAMES, extract_features

try:
    model = joblib.load("models/best_model.joblib")
except FileNotFoundError:
    model = None


def predict(url: str):
    if model is None:
        return "Model not found. Run train.py first.", {}
    if not url or not url.strip():
        return "Please enter a URL.", {}
    try:
        feats = pd.DataFrame([extract_features(url)], columns=FEATURE_NAMES)
        proba = model.predict_proba(feats)[0]
        label = "Phishing" if proba[1] >= 0.5 else "Safe"
        return label, {"Safe": float(proba[0]), "Phishing": float(proba[1])}
    except Exception as e:
        return f"Error: {e}", {}


demo = gr.Interface(
    fn=predict,
    inputs=gr.Textbox(label="Enter a URL", placeholder="http://example.com/login"),
    outputs=[gr.Textbox(label="Prediction"), gr.Label(label="Confidence")],
    title="Phishing URL Detector",
    description="Paste a URL to check whether it looks like phishing.",
    examples=[
        ["https://www.wikipedia.org"],
        ["http://paypa1-secure-login.xyz/verify@account"],
    ],
)

if __name__ == "__main__":
    demo.launch()