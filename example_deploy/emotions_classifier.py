import onnxruntime as ort
import numpy as np
from transformers import AutoTokenizer

# Emotion labels
EMOTION_LABELS = [
    "admiration", "amusement", "anger", "annoyance", "approval", "caring", "confusion",
    "curiosity", "desire", "disappointment", "disapproval", "disgust", "embarrassment",
    "excitement", "fear", "gratitude", "grief", "joy", "love", "nervousness", "optimism",
    "pride", "realization", "relief", "remorse", "sadness", "surprise", "neutral"
]

# Load the ONNX model
def load_onnx_model(model_path="onnx/roberta_model_quantized.onnx"):
    return ort.InferenceSession(model_path)

# Classify emotion function
def classify_emotion(text, ort_session, tokenizer):
    # Tokenize the input
    inputs = tokenizer(text, return_tensors="np", truncation=True)
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]
    # Prepare inputs for ONNX model
    onnx_inputs = {
        "input_ids": input_ids,
        "attention_mask": attention_mask
    }
    # Run inference
    outputs = ort_session.run(None, onnx_inputs)
    # Extract logits
    logits = outputs[0]
    # Apply softmax to convert logits to probabilities
    probabilities = np.exp(logits) / np.sum(np.exp(logits), axis=-1, keepdims=True)
    # Get the predicted label
    predicted_label_index = np.argmax(probabilities, axis=-1)
    predicted_label = EMOTION_LABELS[predicted_label_index[0]]
    return predicted_label, probabilities[0]

# Main execution block for standalone usage
if __name__ == "__main__":
    # Initialize model and tokenizer
    print("Model and tokenizer loading...")
    #tokenizer = AutoTokenizer.from_pretrained("Cohee/distilbert-base-uncased-go-emotions-onnx")
    tokenizer = AutoTokenizer.from_pretrained("SamLowe/roberta-base-go_emotions")
    ort_session = load_onnx_model()
    print("Model and tokenizer loaded.")
    
    # Input loop
    while True:
        text = input("Enter text: ")
        if not text.strip():
            break
        
        # Get predicted emotion and probabilities
        predicted_emotion, probabilities = classify_emotion(text, ort_session, tokenizer)
        
        # Print results
        print(f"Text: {text}")
        print(f"Predicted Emotion: {predicted_emotion}")
        print(f"Probabilities: {dict(zip(EMOTION_LABELS, probabilities))}")