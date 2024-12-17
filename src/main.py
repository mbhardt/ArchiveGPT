from flask import Flask, send_from_directory, request, jsonify, stream_with_context, Response
import os, json, sqlite3, requests, yaml
from transformers import AutoTokenizer
from emotions_classifier import load_onnx_model, classify_emotion, EMOTION_LABELS

# Load emotion model and tokenizer
print("Tokenizer and text classifier loading...")
tokenizer = AutoTokenizer.from_pretrained("SamLowe/roberta-base-go_emotions")
emotion_model = load_onnx_model("onnx/roberta_model_quantized.onnx")
print("Tokenizer and text classifier loaded.")

app = Flask(__name__)

# Load configuration
with open("config.yaml", "r", encoding="utf8") as f:
    config = yaml.safe_load(f.read())
    f.close()

API_URL = config.get("api_url")
KEY = config.get("key")
DATABASE = config.get("database", "chat_history.db")    
MAX_CONTEXT_SIZE = config.get("max_context_size", 16)
PORT = config.get("port", 80)

# Load descriptions
with open("base_description.txt", "r", encoding="utf8") as f1:
    base_description = f1.read()
    f1.close()

# Database utilities
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT
            )
        ''')

def save_message(session_id, role, content):
    with get_db() as conn:
        conn.execute('''
            INSERT INTO chats (session_id, role, content)
            VALUES (?, ?, ?)''', (str(session_id), str(role), str(content)))
        conn.commit()

def get_chat_history(session_id):
    with get_db() as conn:
        cur = conn.execute('''
            SELECT role, content FROM chats
            WHERE session_id = ?''', (session_id,))
        return cur.fetchall()

def limit_context_size(chat_history, max_size):
    return chat_history[-max_size:] if len(chat_history) > max_size else chat_history

# Routes
@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Parse request data
        data = request.get_json()
        session_id = request.cookies.get('SESS_ID')
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "No message provided."}), 400
        if not session_id or len(session_id) != 16:
            return jsonify({"error": "You may not use this service without a valid session ID."}), 400

        # Retrieve chat history
        chat_history_db = get_chat_history(session_id)
        chat_history = [{"role": row["role"], "content": row["content"]} for row in chat_history_db]
        # Append user message to chat history
        chat_history.append({"role": "user", "content": user_message})
        save_message(session_id, "user", user_message)
        # Limit context size
        limited_chat_history = limit_context_size(chat_history, MAX_CONTEXT_SIZE)
        # Add system instructions
        limited_chat_history.insert(0, {"role": "system", "content": base_description})

        # Generate response
        def generate_response():
            headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}
            payload = config.get("payload", {})
            payload["messages"] = limited_chat_history

            with requests.post(API_URL, headers=headers, json=payload, stream=True) as response:
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode('utf-8')
                        if decoded_line.startswith('data:'):
                            json_data = decoded_line[5:].strip()
                            if json_data == '[DONE]':
                                break
                            try:
                                chunk = json.loads(json_data)
                                yield chunk['choices'][0]['delta'].get('content', '')
                            except Exception as e:
                                raise Exception(f"Streaming error: {e}")

        # Stream the assistant response
        @stream_with_context
        def stream_response():
            assistant_message = ""
            for part in generate_response():
                assistant_message += part
                yield part
            save_message(session_id, "assistant", assistant_message)

        return Response(stream_response(), content_type='text/event-stream')

    except Exception as e:
        return jsonify({"error": f"Backend error: {str(e)}"}), 500

@app.route('/emotion', methods=['POST'])
def emotions():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Invalid JSON format."}), 400

        message = data.get("message", "")
        if not message:
            return jsonify({"error": "No text provided."}), 400

        # Use external classifier to predict emotion
        predicted_emotion, probabilities = classify_emotion(message, emotion_model, tokenizer)
        return jsonify({
            "predicted_emotion": predicted_emotion
        }), 200
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format."}), 400
    except Exception as e:
        print(f"Error in /emotion endpoint: {str(e)}")
        return jsonify({"error": f"Emotion classification failed: {str(e)}"}), 500

@app.route('/')
def index():
    return send_from_directory('public', "index.html")

@app.route('/<path:path>')
def send_file(path):
    return send_from_directory('public', path)

if __name__ == '__main__':
    create_table()
    app.run(host='0.0.0.0', port=PORT)