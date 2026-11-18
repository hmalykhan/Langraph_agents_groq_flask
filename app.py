"""The only Flask endpoint: POST /chat."""
from flask import Flask, jsonify, request
from langchain_core.messages import HumanMessage
from graph import graph

app = Flask(__name__)


@app.post('/chat')
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get('message')
    session_id = data.get('session_id')

    if not isinstance(message, str) or not message.strip():
        return jsonify({'error': 'message must be a non-empty string'}), 400
    if not isinstance(session_id, str) or not session_id.strip():
        return jsonify({'error': 'session_id must be a non-empty string'}), 400

    # The same session_id means the same chat history.
    config = {
        'configurable': {'thread_id': session_id.strip()},
        'recursion_limit': 12,
    }

    try:
        result = graph.invoke(
            {'messages': [HumanMessage(content=message.strip())]},
            config=config,
        )
        answer = result['messages'][-1].content
        return jsonify({'session_id': session_id, 'reply': answer})
    except Exception:
        app.logger.exception('Chat request failed')
        return jsonify({'error': 'Chat failed. See server logs and check GROQ_API_KEY.'}), 502


if __name__ == '__main__':
    # No reloader: it would create a second in-memory conversation store.
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)
