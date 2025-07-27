from flask import Blueprint, request, jsonify
import requests
import os
import json
import uuid
from datetime import datetime
import sqlite3
import threading
import time

revolutionary_relay_bp = Blueprint('revolutionary_relay', __name__)

# Session storage
active_sessions = {}

# Agent configuration (same as agents.py but organized for relay)
RELAY_AGENTS = [
    # Current working 10 agents
    {'id': 'gpt-4o', 'name': 'GPT-4o', 'model': 'openai/gpt-4o', 'specialty': 'Strategic Analysis'},
    {'id': 'chatgpt-4-turbo', 'name': 'ChatGPT 4 Turbo', 'model': 'openai/gpt-4-turbo', 'specialty': 'Business Strategy'},
    {'id': 'deepseek-r1', 'name': 'DeepSeek R1', 'model': 'deepseek/deepseek-r1', 'specialty': 'Technical Expert'},
    {'id': 'meta-llama-3.3', 'name': 'Meta Llama 3.3', 'model': 'meta-llama/llama-3.3-70b-instruct', 'specialty': 'Creative Analysis'},
    {'id': 'mistral-large', 'name': 'Mistral Large', 'model': 'mistralai/mistral-large', 'specialty': 'Analytical Processing'},
    {'id': 'gemini-2.0-flash', 'name': 'Gemini 2.0 Flash', 'model': 'google/gemini-2.0-flash-exp', 'specialty': 'Creative Synthesis'},
    {'id': 'perplexity-pro', 'name': 'Perplexity Pro', 'model': 'perplexity/llama-3.1-sonar-huge-128k-online', 'specialty': 'Research Expert'},
    {'id': 'gemini-pro-1.5', 'name': 'Gemini Pro 1.5', 'model': 'google/gemini-pro-1.5', 'specialty': 'Document Analysis'},
    {'id': 'command-r-plus', 'name': 'Command R+', 'model': 'cohere/command-r-plus', 'specialty': 'Enterprise Solutions'},
    {'id': 'qwen-2.5-72b', 'name': 'Qwen 2.5 72B', 'model': 'qwen/qwen-2.5-72b-instruct', 'specialty': 'Multilingual Expert'},
    
    # Additional 10 revolutionary agents
    {'id': 'llama-3.3-70b', 'name': 'Llama 3.3 70B', 'model': 'meta-llama/llama-3.3-70b-instruct', 'specialty': 'Logical Reasoning'},
    {'id': 'mixtral-8x22b', 'name': 'Mixtral 8x22B', 'model': 'mistralai/mixtral-8x22b-instruct', 'specialty': 'System Design'},
    {'id': 'yi-large', 'name': 'Yi Large', 'model': '01-ai/yi-large', 'specialty': 'Innovation Expert'},
    {'id': 'nous-hermes-3', 'name': 'Nous Hermes 3', 'model': 'nousresearch/hermes-3-llama-3.1-405b', 'specialty': 'Free Thinking'},
    {'id': 'wizardlm-2', 'name': 'WizardLM 2', 'model': 'microsoft/wizardlm-2-8x22b', 'specialty': 'Mathematical Reasoning'},
    {'id': 'dolphin-mixtral', 'name': 'Dolphin Mixtral', 'model': 'cognitivecomputations/dolphin-2.9-llama3-70b', 'specialty': 'Bold Synthesis'},
    {'id': 'openhermes-2.5', 'name': 'OpenHermes 2.5', 'model': 'teknium/openhermes-2.5-mistral-7b', 'specialty': 'Collaboration Expert'},
    {'id': 'starling-7b', 'name': 'Starling 7B', 'model': 'berkeley-nest/starling-lm-7b-alpha', 'specialty': 'Quick Insights'},
    {'id': 'neural-chat', 'name': 'Neural Chat', 'model': 'intel/neural-chat-7b-v3-3', 'specialty': 'Dialogue Expert'},
    {'id': 'zephyr-beta', 'name': 'Zephyr Beta', 'model': 'huggingfaceh4/zephyr-7b-beta', 'specialty': 'Final Synthesis'}
]

# Fallback messaging for better user experience
FALLBACK_RESPONSES = [
    "Let me approach this from a different angle...",
    "Building on what we know so far...",
    "Contributing an alternative perspective...",
    "Adding to our collective analysis...",
    "Here's my specialized insight on this topic..."
]

def get_fallback_response(agent_name):
    """Return a user-friendly fallback message when an agent fails"""
    import random
    fallback_intro = random.choice(FALLBACK_RESPONSES)
    return f"{fallback_intro} [Note: {agent_name} encountered a technical limitation, so this is a fallback response.]"

def call_openrouter_api(agent, message):
    """Call OpenRouter API for specific agent with improved error handling"""
    try:
        # Log the attempt for troubleshooting
        print(f"Calling {agent['name']} with model: {agent['model']}")
        
        response = requests.post(
            'https://openrouter.ai/api/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {os.getenv("OPENROUTER_API_KEY")}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://unitylab.ai', # Updated to new domain
                'X-Title': 'UnityLab AI Orchestration'
            },
            json={
                'model': agent['model'],
                'messages': [
                    {
                        'role': 'system',
                        'content': f'You are {agent["name"]}, specializing in {agent["specialty"]}. Provide insightful, collaborative responses that build upon previous insights when available.'
                    },
                    {
                        'role': 'user',
                        'content': message
                    }
                ],
                'max_tokens': 2000,
                'temperature': 0.7
            },
            timeout=30  # Add timeout to prevent hanging requests
        )
        
        if response.status_code == 200:
            response_data = response.json()
            return response_data['choices'][0]['message']['content']
        else:
            # Log the error but don't stop execution
            error_details = f"Error {response.status_code}: {response.text}"
            print(f"API Error with {agent['name']}: {error_details}")
            
            # Return a user-friendly message instead of error text
            return get_fallback_response(agent['name'])
            
    except requests.exceptions.Timeout:
        print(f"Timeout error with {agent['name']}")
        return get_fallback_response(agent['name'])
    except requests.exceptions.RequestException as e:
        print(f"Request error with {agent['name']}: {str(e)}")
        return get_fallback_response(agent['name'])
    except Exception as e:
        print(f"Unexpected error with {agent['name']}: {str(e)}")
        return get_fallback_response(agent['name'])

def expert_panel_worker(session_id, prompt):
    """Worker function for Expert Panel Mode (10 pairs) with improved reliability"""
    session = active_sessions[session_id]
    session['status'] = 'running'
    session['results'] = []
    
    # Create 10 pairs from 20 agents
    pairs = []
    for i in range(0, min(len(RELAY_AGENTS), 20), 2):
        if i+1 < len(RELAY_AGENTS):
            pairs.append([RELAY_AGENTS[i], RELAY_AGENTS[i+1]])
    
    session['total_pairs'] = len(pairs)
    
    for pair_index, pair in enumerate(pairs):
        if session.get('status') == 'stopped':
            break
            
        session['current_pair'] = pair_index + 1
        session['current_agents'] = [pair[0]['name'], pair[1]['name']]
        
        try:
            # Agent A responds to prompt
            agent_a_response = call_openrouter_api(pair[0], prompt)
            
            # Agent B responds to prompt (independent analysis)
            agent_b_response = call_openrouter_api(pair[1], prompt)
            
            # Store pair results
            pair_result = {
                'pair_number': pair_index + 1,
                'agent_a': {
                    'name': pair[0]['name'],
                    'specialty': pair[0]['specialty'],
                    'response': agent_a_response,
                    'success': not agent_a_response.startswith(tuple(FALLBACK_RESPONSES))
                },
                'agent_b': {
                    'name': pair[1]['name'],
                    'specialty': pair[1]['specialty'],
                    'response': agent_b_response,
                    'success': not agent_b_response.startswith(tuple(FALLBACK_RESPONSES))
                },
                'timestamp': datetime.utcnow().isoformat()
            }
            
            session['results'].append(pair_result)
        except Exception as e:
            print(f"Error processing pair {pair_index + 1}: {str(e)}")
            # Continue with next pair even if one fails
            continue
        
        # Small delay between pairs
        time.sleep(1)
    
    session['status'] = 'completed'
    session['completed_at'] = datetime.utcnow().isoformat()

def conference_chain_worker(session_id, prompt, max_agents=20):
    """Worker function for Conference Chain Mode (sticky context) with improved reliability"""
    session = active_sessions[session_id]
    session['status'] = 'running'
    session['results'] = []
    session['sticky_context'] = prompt
    
    session['total_agents'] = min(max_agents, len(RELAY_AGENTS))
    
    for agent_index in range(session['total_agents']):
        if session.get('status') == 'stopped':
            break
            
        agent = RELAY_AGENTS[agent_index]
        session['current_agent'] = agent_index + 1
        session['current_agent_name'] = agent['name']
        
        try:
            # Create message with sticky context
            if agent_index == 0:
                # First agent gets original prompt
                message = prompt
            else:
                # Subsequent agents get original prompt + latest response
                latest_response = session['results'][-1]['response']
                message = f"ORIGINAL PROMPT: {prompt}\n\nPREVIOUS INSIGHT: {latest_response}\n\nBuild upon this insight with your expertise:"
            
            # Get agent response
            agent_response = call_openrouter_api(agent, message)
            
            # Store result
            result = {
                'agent_number': agent_index + 1,
                'agent_name': agent['name'],
                'agent_specialty': agent['specialty'],
                'response': agent_response,
                'sticky_context_used': agent_index > 0,
                'success': not agent_response.startswith(tuple(FALLBACK_RESPONSES)),
                'timestamp': datetime.utcnow().isoformat()
            }
            
            session['results'].append(result)
        except Exception as e:
            print(f"Error processing agent {agent_index + 1}: {str(e)}")
            # Use fallback to maintain chain continuity
            fallback_response = get_fallback_response(agent['name'])
            result = {
                'agent_number': agent_index + 1,
                'agent_name': agent['name'],
                'agent_specialty': agent['specialty'],
                'response': fallback_response,
                'sticky_context_used': agent_index > 0,
                'success': False,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
            session['results'].append(result)
        
        # Small delay between agents
        time.sleep(1)
    
    session['status'] = 'completed'
    session['completed_at'] = datetime.utcnow().isoformat()

@revolutionary_relay_bp.route('/start-expert-panel', methods=['POST'])
def start_expert_panel():
    """Start Expert Panel Mode (10 pairs working independently)"""
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        
        if not prompt:
            return jsonify({'status': 'error', 'message': 'Prompt is required'}), 400
        
        session_id = str(uuid.uuid4())
        
        # Initialize session
        active_sessions[session_id] = {
            'mode': 'expert_panel',
            'prompt': prompt,
            'status': 'starting',
            'created_at': datetime.utcnow().isoformat(),
            'current_pair': 0,
            'total_pairs': 10,
            'current_agents': ['Initializing...', 'Waiting...']
        }
        
        # Start worker thread
        worker_thread = threading.Thread(
            target=expert_panel_worker,
            args=(session_id, prompt)
        )
        worker_thread.daemon = True
        worker_thread.start()
        
        return jsonify({
            'status': 'started',
            'session_id': session_id,
            'mode': 'expert_panel',
            'total_pairs': 10,
            'message': 'Expert Panel Mode started - 10 pairs analyzing independently'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@revolutionary_relay_bp.route('/start-conference-chain', methods=['POST'])
def start_conference_chain():
    """Start Conference Chain Mode (20 agents with sticky context)"""
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        max_agents = data.get('max_agents', 20)
        
        if not prompt:
            return jsonify({'status': 'error', 'message': 'Prompt is required'}), 400
        
        session_id = str(uuid.uuid4())
        
        # Initialize session
        active_sessions[session_id] = {
            'mode': 'conference_chain',
            'prompt': prompt,
            'status': 'starting',
            'created_at': datetime.utcnow().isoformat(),
            'current_agent': 0,
            'total_agents': max_agents,
            'current_agent_name': 'Initializing...'
        }
        
        # Start worker thread
        worker_thread = threading.Thread(
            target=conference_chain_worker,
            args=(session_id, prompt, max_agents)
        )
        worker_thread.daemon = True
        worker_thread.start()
        
        return jsonify({
            'status': 'started',
            'session_id': session_id,
            'mode': 'conference_chain',
            'total_agents': max_agents,
            'message': 'Conference Chain Mode started - agents building with sticky context'
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@revolutionary_relay_bp.route('/stop-session/', methods=['POST'])
def stop_session(session_id):
    """Stop a running session"""
    try:
        if session_id not in active_sessions:
            return jsonify({'status': 'error', 'message': 'Session not found'}), 404
        
        session = active_sessions[session_id]
        session['status'] = 'stopped'
        
        return jsonify({
            'status': 'success',
            'message': f"{session['mode']} session stopped",
            'session_id': session_id
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@revolutionary_relay_bp.route('/get-session-status/', methods=['GET'])
def get_session_status(session_id):
    """Get status of a running session"""
    try:
        if session_id not in active_sessions:
            return jsonify({'status': 'error', 'message': 'Session not found'}), 404
        
        session = active_sessions[session_id]
        
        # Create response based on session type
        response = {
            'status': session['status'],
            'mode': session['mode'],
            'created_at': session['created_at']
        }
        
        if session['mode'] == 'expert_panel':
            response.update({
                'current_pair': session['current_pair'],
                'total_pairs': session['total_pairs'],
                'current_agents': session['current_agents']
            })
        else:  # conference_chain
            response.update({
                'current_agent': session['current_agent'],
                'total_agents': session['total_agents'],
                'current_agent_name': session['current_agent_name']
            })
        
        if session['status'] == 'completed':
            response['completed_at'] = session.get('completed_at')
            
        # Include partial results if available
        if len(session.get('results', [])) > 0:
            response['partial_results'] = len(session['results'])
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@revolutionary_relay_bp.route('/get-session-results/', methods=['GET'])
def get_session_results(session_id):
    """Get results of a completed session"""
    try:
        if session_id not in active_sessions:
            return jsonify({'status': 'error', 'message': 'Session not found'}), 404
        
        session = active_sessions[session_id]
        
        if session['status'] not in ['completed', 'stopped']:
            return jsonify({
                'status': 'pending',
                'message': f"Session is still {session['status']}",
                'progress': f"{len(session.get('results', []))} responses so far"
            })
        
        # Return complete results
        return jsonify({
            'completed': True,
            'completed_at': session.get('completed_at'),
            'created_at': session['created_at'],
            'mode': session['mode'],
            'prompt': session['prompt'],
            'results': session.get('results', [])
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@revolutionary_relay_bp.route('/generate-html-report/', methods=['GET'])
def generate_html_report(session_id):
    """Generate HTML report from session results"""
    try:
        if session_id not in active_sessions:
            return jsonify({'status': 'error', 'message': 'Session not found'}), 404
        
        session = active_sessions[session_id]
        
        if session['status'] not in ['completed', 'stopped']:
            return jsonify({
                'status': 'pending',
                'message': f"Session is still {session['status']}. HTML report not available yet."
            }), 400
        
        # Generate HTML based on session mode
        if session['mode'] == 'expert_panel':
            html = generate_expert_panel_html(session)
        else:  # conference_chain
            html = generate_conference_chain_html(session)
        
        return jsonify({
            'status': 'success',
            'html': html,
            'mode': session['mode']
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def generate_expert_panel_html(session):
    """Generate HTML for Expert Panel results"""
    prompt = session['prompt']
    results = session.get('results', [])
    
    html = f"""
    
    
    
        Expert Panel Analysis
        
            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .prompt {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .pair {{ margin-bottom: 30px; border: 1px solid #ddd; border-radius: 5px; overflow: hidden; }}
            .pair-header {{ background-color: #2c3e50; color: white; padding: 10px 15px; display: flex; justify-content: space-between; }}
            .agent {{ padding: 15px; }}
            .agent:first-child {{ border-bottom: 1px solid #ddd; }}
            .agent-name {{ font-weight: bold; color: #2980b9; margin-bottom: 5px; }}
            .agent-specialty {{ font-style: italic; color: #7f8c8d; margin-bottom: 10px; }}
            .response {{ white-space: pre-wrap; }}
            .footer {{ text-align: center; margin-top: 30px; font-size: 0.8em; color: #7f8c8d; }}
        
    
    
        
            
                Expert Panel Analysis
                Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
            
            
            
                Prompt:
                {prompt}
            
            
            Expert Analysis (10 Pairs)
    """
    
    for pair_result in results:
        agent_a = pair_result['agent_a']
        agent_b = pair_result['agent_b']
        
        html += f"""
            
                
                    Pair {pair_result['pair_number']}
                    {pair_result['timestamp']}
                
                
                
                    {agent_a['name']}
                    Specialty: {agent_a['specialty']}
                    {agent_a['response']}
                
                
                
                    {agent_b['name']}
                    Specialty: {agent_b['specialty']}
                    {agent_b['response']}
                
            
        """
    
    html += """
            
                Generated by UnityLab AI Orchestration Platform
            
        
    

    
    """
    
    return html

def generate_conference_chain_html(session):
    """Generate HTML for Conference Chain results"""
    prompt = session['prompt']
    results = session.get('results', [])
    
    html = f"""
    
    
    
        Conference Chain Analysis
        
            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .prompt {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            .agent {{ margin-bottom: 20px; border: 1px solid #ddd; border-radius: 5px; overflow: hidden; }}
            .agent-header {{ background-color: #27ae60; color: white; padding: 10px 15px; display: flex; justify-content: space-between; }}
            .agent-content {{ padding: 15px; }}
            .agent-name {{ font-weight: bold; color: #2980b9; margin-bottom: 5px; }}
            .agent-specialty {{ font-style: italic; color: #7f8c8d; margin-bottom: 10px; }}
            .response {{ white-space: pre-wrap; }}
            .footer {{ text-align: center; margin-top: 30px; font-size: 0.8em; color: #7f8c8d; }}
            .sticky-context {{ background-color: #fef9e7; padding: 10px; border-left: 3px solid #f39c12; margin-top: 10px; font-size: 0.9em; }}
        
    
    
        
            
                Conference Chain Analysis
                Generated on {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
            
            
            
                Prompt:
                {prompt}
            
            
            Sequential Expert Analysis
    """
    
    for result in results:
        html += f"""
            
                
                    Agent {result['agent_number']}
                    {result['timestamp']}
                
                
                
                    {result['agent_name']}
                    Specialty: {result['agent_specialty']}
                    {result['response']}
                    
                    {f'Building on previous insights' if result.get('sticky_context_used') else ''}
                
            
        """
    
    html += """
            
                Generated by UnityLab AI Orchestration Platform
            
        
    
    
    """
    
    return html

@revolutionary_relay_bp.route('/cleanup-old-sessions', methods=['POST'])
def cleanup_old_sessions():
    """Clean up old sessions to prevent memory leaks"""
    try:
        # Remove sessions older than 24 hours
        current_time = datetime.utcnow()
        session_ids_to_remove = []
        
        for session_id, session in active_sessions.items():
            created_at = datetime.fromisoformat(session['created_at'])
            age_hours = (current_time - created_at).total_seconds() / 3600
            
            if age_hours > 24:
                session_ids_to_remove.append(session_id)
        
        for session_id in session_ids_to_remove:
            del active_sessions[session_id]
        
        return jsonify({
            'status': 'success',
            'sessions_removed': len(session_ids_to_remove),
            'remaining_sessions': len(active_sessions)
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
