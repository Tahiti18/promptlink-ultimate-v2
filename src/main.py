import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from datetime import datetime

# Import all route blueprints (unified system)
from routes.agents import agents_bp
from routes.human_simulator import human_simulator_bp
from routes.revolutionary_relay import revolutionary_relay_bp
from routes.payments import payments_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'promptlink-ultimate-orchestration-engine-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for frontend integration
CORS(app, origins=[
    'http://localhost:3000',
    'https://lucky-kheer-f8d0d3.netlify.app',
    'https://thepromptlink.com',
    'https://thepromptlink.netlify.app',
    'https://singular-bunny-82fc57.netlify.app',
    'https://dancing-meerkat-41c610.netlify.app'
], allow_headers=['Content-Type', 'Authorization', 'x-user-id'])

# Register all blueprints (ULTIMATE SYSTEM)
app.register_blueprint(agents_bp, url_prefix='/api')
app.register_blueprint(human_simulator_bp, url_prefix='/api/human-simulator')
app.register_blueprint(revolutionary_relay_bp, url_prefix='/api/revolutionary-relay')
app.register_blueprint(payments_bp, url_prefix='/api/payments')

# Legacy endpoints for backward compatibility
@app.route('/api/chat', methods=['POST'])
def legacy_chat():
    """Legacy chat endpoint - redirects to agents API"""
    from flask import request
    try:
        data = request.get_json()
        agent_id = data.get('agent', 'gpt-4o')  # Default to GPT-4o
        message = data.get('message')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Forward to unified agents API
        import requests
        response = requests.post(
            f"{request.host_url}api/agents/chat",
            json={'agent_id': agent_id, 'message': message}
        )
        return response.json()
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/relay', methods=['POST'])
def legacy_relay():
    """Legacy relay endpoint - basic 2-agent relay"""
    from flask import request
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        agent_a = data.get('agent_a', 'gpt-4o')
        agent_b = data.get('agent_b', 'chatgpt-4-turbo')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Simple 2-agent relay for backward compatibility
        from routes.agents import AGENTS
        import requests
        import os
        
        # Agent A responds
        agent_a_config = AGENTS.get(agent_a)
        if not agent_a_config:
            return jsonify({'error': f'Invalid agent: {agent_a}'}), 400
        
        # Call OpenRouter for Agent A
        openrouter_response_a = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {os.getenv("OPENROUTER_API_KEY")}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://thepromptlink.netlify.app',
                'X-Title': 'PromptLink AI Collaboration'
            },
            json={
                'model': agent_a_config['model'],
                'messages': [
                    {
                        'role': 'system',
                        'content': f'You are {agent_a_config["name"]}, specializing in {agent_a_config["specialty"]}. Provide insightful responses.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 2000,
                'temperature': 0.7
            }
        )
        
        if openrouter_response_a.status_code != 200:
            return jsonify({'error': 'Agent A API error'}), 500
        
        agent_a_response = openrouter_response_a.json()['choices'][0]['message']['content']
        
        # Agent B responds to Agent A's response
        agent_b_config = AGENTS.get(agent_b)
        if not agent_b_config:
            return jsonify({'error': f'Invalid agent: {agent_b}'}), 400
        
        openrouter_response_b = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {os.getenv("OPENROUTER_API_KEY")}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://thepromptlink.netlify.app',
                'X-Title': 'PromptLink AI Collaboration'
            },
            json={
                'model': agent_b_config['model'],
                'messages': [
                    {
                        'role': 'system',
                        'content': f'You are {agent_b_config["name"]}, specializing in {agent_b_config["specialty"]}. Respond to and build upon the previous agent\'s insights.'
                    },
                    {
                        'role': 'user',
                        'content': f"Original prompt: {prompt}\n\nPrevious response from {agent_a_config['name']}:\n{agent_a_response}\n\nPlease provide your perspective and build upon this insight:"
                    }
                ],
                'max_tokens': 2000,
                'temperature': 0.7
            }
        )
        
        if openrouter_response_b.status_code != 200:
            return jsonify({'error': 'Agent B API error'}), 500
        
        agent_b_response = openrouter_response_b.json()['choices'][0]['message']['content']
        
        return jsonify({
            'status': 'success',
            'agent_a': {
                'name': agent_a_config['name'],
                'response': agent_a_response
            },
            'agent_b': {
                'name': agent_b_config['name'],
                'response': agent_b_response
            },
            'legacy_mode': True
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/workflows', methods=['GET', 'POST'])
def legacy_workflows():
    """Legacy workflows endpoint"""
    from flask import request
    if request.method == 'GET':
        return jsonify({
            'status': 'success',
            'workflows': [
                {'id': 'basic', 'name': 'Basic Collaboration'},
                {'id': 'expert_panel', 'name': 'Expert Panel (Revolutionary)'},
                {'id': 'conference_chain', 'name': 'Conference Chain (Revolutionary)'}
            ]
        })
    else:
        return jsonify({'status': 'success', 'message': 'Workflow endpoint - use revolutionary relay for advanced features'})

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'PromptLink Ultimate Backend',
        'version': '3.0.0',
        'features': {
            'agents': '20 AI agents available (10 current + 10 revolutionary)',
            'human_simulator': 'Persistent learning and clone functionality',
            'revolutionary_relay': 'Expert Panel + Conference Chain modes',
            'payments': 'Stripe integration with 4 tiers ($0, $19, $99, $499)',
            'legacy_compatibility': 'Full backward compatibility maintained'
        },
        'revolutionary_features': [
            'Expert Panel Mode: 10 independent agent pairs',
            'Conference Chain Mode: 20 agents with sticky context',
            'Human Simulator with persistent learning',
            'Personal AI clone development',
            'Beautiful HTML report generation',
            'Sequential processing (zero resource overhead)'
        ],
        'timestamp': datetime.utcnow().isoformat()
    })

# Root endpoint
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        'message': 'PromptLink Ultimate Backend API - Revolutionary AI Orchestration',
        'version': '3.0.0',
        'endpoints': {
            '/api/agents': 'AI agent management and chat (20 agents)',
            '/api/human-simulator': 'Persistent learning and clone functionality',
            '/api/revolutionary-relay': 'Revolutionary 20-agent relay system',
            '/api/payments': 'Stripe subscription management (4 tiers)',
            '/api/chat': 'Legacy chat endpoint (backward compatible)',
            '/api/relay': 'Legacy relay endpoint (backward compatible)',
            '/api/workflows': 'Legacy workflows endpoint (backward compatible)'
        },
        'revolutionary_power': {
            'total_agents': 20,
            'expert_panel_pairs': 10,
            'conference_chain_agents': 20,
            'human_simulator_learning': True,
            'persistent_clone_development': True,
            'subscription_tiers': 4,
            'backward_compatibility': True
        }
    })

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

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
            '/api/chat (legacy)',
            '/api/relay (legacy)',
            '/api/workflows (legacy)',
            '/health'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'Internal server error',
        'message': 'Please check logs for details'
    }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Check environment variables
    required_vars = [
        'OPENROUTER_API_KEY',
        'STRIPE_SECRET_KEY'
    ]
    
    optional_vars = [
        'STRIPE_BASIC_PRICE_ID',
        'STRIPE_PRO_PRICE_ID', 
        'STRIPE_EXPERT_PRICE_ID',
        'STRIPE_WEBHOOK_SECRET'
    ]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_required:
        print(f"❌ CRITICAL: Missing required environment variables: {', '.join(missing_required)}")
        print("System may not function properly.")
    else:
        print("✅ All required environment variables are set")
    
    if missing_optional:
        print(f"⚠️  Optional environment variables not set: {', '.join(missing_optional)}")
        print("Some payment features may not work.")
    
    print("🚀 PromptLink Ultimate Backend - Revolutionary AI Orchestration System")
    print("🌟 Features: 20 AI agents, Expert Panel, Conference Chain, Human Simulator, Payments")
    
    print("🚀 Starting PromptLink Ultimate Backend...")
    print(f"🌟 Revolutionary Features: Expert Panel + Conference Chain + Human Simulator")
    print(f"🤖 Total AI Agents: 20 (10 current + 10 revolutionary)")
    print(f"🧠 Human Simulator: Persistent learning enabled")
    print(f"💳 Payment Tiers: Free ($0), Basic ($19), Pro ($99), Expert ($499)")
    print(f"🔗 Port: {port}")
    print(f"🐛 Debug: {debug}")
    print("🏆 READY TO DOMINATE THE AI WORLD!")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
