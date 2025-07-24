from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime

# Import all route blueprints
from routes.agents import agents_bp
from routes.human_simulator import human_simulator_bp
from routes.revolutionary_relay import revolutionary_relay_bp
from routes.payments import payments_bp

app = Flask(__name__)

# Configure CORS
CORS(app, origins=["https://thepromptlink.netlify.app", "http://localhost:3000"])

# Register all blueprints
app.register_blueprint(agents_bp, url_prefix='/api/agents')
app.register_blueprint(human_simulator_bp, url_prefix='/api/human-simulator')
app.register_blueprint(revolutionary_relay_bp, url_prefix='/api/revolutionary-relay')
app.register_blueprint(payments_bp, url_prefix='/api/payments')

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'PromptLink Ultimate Backend',
        'version': '2.0.0',
        'features': {
            'agents': '20 AI agents available',
            'human_simulator': 'Persistent learning enabled',
            'revolutionary_relay': 'Expert Panel + Conference Chain modes',
            'payments': 'Stripe integration active'
        },
        'timestamp': datetime.utcnow().isoformat()
    })

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'PromptLink Ultimate Backend API',
        'version': '2.0.0',
        'endpoints': {
            '/api/agents': 'AI agent management and chat',
            '/api/human-simulator': 'Persistent learning and clone functionality',
            '/api/revolutionary-relay': 'Revolutionary 20-agent relay system',
            '/api/payments': 'Stripe subscription management'
        },
        'revolutionary_features': [
            '20 AI agents with sequential processing',
            'Expert Panel Mode (10 independent pairs)',
            'Conference Chain Mode (sticky context building)',
            'Human Simulator with persistent learning',
            'Personal AI clone development',
            'Beautiful HTML report generation'
        ]
    })

# Legacy chat endpoint for backward compatibility
@app.route('/api/chat', methods=['POST'])
def legacy_chat():
    """Legacy chat endpoint - redirects to agents API"""
    try:
        data = request.get_json()
        agent_id = data.get('agent', 'gpt-4o')  # Default to GPT-4o
        message = data.get('message')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Forward to agents API
        from routes.agents import chat_with_agent
        return chat_with_agent()
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Legacy relay endpoint for backward compatibility
@app.route('/api/relay', methods=['POST'])
def legacy_relay():
    """Legacy relay endpoint - basic 2-agent relay"""
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        agent_a = data.get('agent_a', 'gpt-4o')
        agent_b = data.get('agent_b', 'chatgpt-4-turbo')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Simple 2-agent relay for backward compatibility
        from routes.agents import AGENTS, call_openrouter_api
        
        # Agent A responds
        agent_a_config = AGENTS.get(agent_a)
        if not agent_a_config:
            return jsonify({'error': f'Invalid agent: {agent_a}'}), 400
        
        # This is a simplified version - full implementation would use the agents route
        return jsonify({
            'status': 'success',
            'message': 'Legacy relay - use /api/revolutionary-relay for full features',
            'agent_a': agent_a,
            'agent_b': agent_b
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Serve static files (if needed)
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/api/agents',
            '/api/human-simulator', 
            '/api/revolutionary-relay',
            '/api/payments',
            '/health'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Please check logs for details'
    }), 500

# Environment variables check
@app.before_first_request
def check_environment():
    """Check required environment variables"""
    required_vars = [
        'OPENROUTER_API_KEY',
        'STRIPE_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"WARNING: Missing environment variables: {', '.join(missing_vars)}")
        print("Some features may not work properly.")
    else:
        print("✅ All required environment variables are set")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    print("🚀 Starting PromptLink Ultimate Backend...")
    print(f"🌟 Features: 20 AI agents, Revolutionary relay, Human Simulator, Payments")
    print(f"🔗 Port: {port}")
    print(f"🐛 Debug: {debug}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

