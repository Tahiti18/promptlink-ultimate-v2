// PromptLink Ultimate Frontend Integration
// Add this to your existing HTML file to enable revolutionary features

// Revolutionary Relay System Integration
class RevolutionaryRelay {
    constructor(baseUrl = 'https://web-production-2816f.up.railway.app') {
        this.baseUrl = baseUrl;
        this.activeSession = null;
        this.statusInterval = null;
    }

    // Start Expert Panel Mode (10 pairs working independently)
    async startExpertPanel(prompt) {
        try {
            const response = await fetch(`${this.baseUrl}/api/revolutionary-relay/start-expert-panel`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt })
            });

            const data = await response.json();
            
            if (data.status === 'started') {
                this.activeSession = data.session_id;
                this.startStatusMonitoring();
                this.updateUI('expert_panel', 'Expert Panel Mode: 10 pairs analyzing independently...');
                return data;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Expert Panel start error:', error);
            throw error;
        }
    }

    // Start Conference Chain Mode (20 agents with sticky context)
    async startConferenceChain(prompt, maxAgents = 20) {
        try {
            const response = await fetch(`${this.baseUrl}/api/revolutionary-relay/start-conference-chain`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ prompt, max_agents: maxAgents })
            });

            const data = await response.json();
            
            if (data.status === 'started') {
                this.activeSession = data.session_id;
                this.startStatusMonitoring();
                this.updateUI('conference_chain', 'Conference Chain Mode: 20 agents building with sticky context...');
                return data;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Conference Chain start error:', error);
            throw error;
        }
    }

    // Monitor session status in real-time
    startStatusMonitoring() {
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
        }

        this.statusInterval = setInterval(async () => {
            if (!this.activeSession) return;

            try {
                const response = await fetch(`${this.baseUrl}/api/revolutionary-relay/session-status/${this.activeSession}`);
                const data = await response.json();

                if (data.status === 'success') {
                    this.updateSessionStatus(data.session_data);
                    
                    if (data.session_data.status === 'completed') {
                        this.stopStatusMonitoring();
                        this.loadResults();
                    }
                }
            } catch (error) {
                console.error('Status monitoring error:', error);
            }
        }, 2000); // Update every 2 seconds
    }

    // Stop status monitoring
    stopStatusMonitoring() {
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
            this.statusInterval = null;
        }
    }

    // Update session status in UI
    updateSessionStatus(sessionData) {
        const agentAElement = document.querySelector('#agent-a-name');
        const agentBElement = document.querySelector('#agent-b-name');
        const statusElement = document.querySelector('#relay-status');

        if (sessionData.mode === 'expert_panel') {
            if (agentAElement) agentAElement.textContent = sessionData.current_agents[0] || 'Waiting...';
            if (agentBElement) agentBElement.textContent = sessionData.current_agents[1] || 'Waiting...';
            if (statusElement) statusElement.textContent = `Pair ${sessionData.current_pair}/${sessionData.total_pairs}`;
        } else if (sessionData.mode === 'conference_chain') {
            if (agentAElement) agentAElement.textContent = sessionData.current_agent_name || 'Waiting...';
            if (agentBElement) agentBElement.textContent = 'Next Agent';
            if (statusElement) statusElement.textContent = `Agent ${sessionData.current_agent}/${sessionData.total_agents}`;
        }
    }

    // Load and display results
    async loadResults() {
        if (!this.activeSession) return;

        try {
            const response = await fetch(`${this.baseUrl}/api/revolutionary-relay/session-results/${this.activeSession}`);
            const data = await response.json();

            if (data.status === 'success') {
                this.displayResults(data);
                this.generateHTMLReport();
            }
        } catch (error) {
            console.error('Results loading error:', error);
        }
    }

    // Display results in UI
    displayResults(data) {
        const resultsContainer = document.querySelector('#results-container') || document.querySelector('.live-conversation');
        
        if (!resultsContainer) return;

        let html = `<div class="revolutionary-results">
            <h3>🚀 Revolutionary Analysis Complete!</h3>
            <p><strong>Mode:</strong> ${data.mode.replace('_', ' ').toUpperCase()}</p>
            <p><strong>Total Results:</strong> ${data.total_results}</p>
            <div class="results-list">`;

        data.results.forEach((result, index) => {
            if (data.mode === 'expert_panel') {
                html += `
                    <div class="result-pair">
                        <h4>Expert Pair ${result.pair_number}</h4>
                        <div class="agent-result">
                            <strong>${result.agent_a.name}</strong> (${result.agent_a.specialty})
                            <p>${result.agent_a.response}</p>
                        </div>
                        <div class="agent-result">
                            <strong>${result.agent_b.name}</strong> (${result.agent_b.specialty})
                            <p>${result.agent_b.response}</p>
                        </div>
                    </div>`;
            } else {
                html += `
                    <div class="agent-result">
                        <strong>Agent ${result.agent_number}: ${result.agent_name}</strong> (${result.agent_specialty})
                        <p>${result.response}</p>
                    </div>`;
            }
        });

        html += `</div>
            <button onclick="revolutionaryRelay.downloadReport()" class="download-btn">
                📄 Download HTML Report
            </button>
        </div>`;

        resultsContainer.innerHTML = html;
    }

    // Generate and download HTML report
    async generateHTMLReport() {
        if (!this.activeSession) return;

        try {
            const response = await fetch(`${this.baseUrl}/api/revolutionary-relay/generate-html-report/${this.activeSession}`);
            const data = await response.json();

            if (data.status === 'success') {
                this.htmlReport = data.html_report;
            }
        } catch (error) {
            console.error('HTML report generation error:', error);
        }
    }

    // Download HTML report
    downloadReport() {
        if (!this.htmlReport) return;

        const blob = new Blob([this.htmlReport], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `promptlink-revolutionary-analysis-${new Date().toISOString().split('T')[0]}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    // Update UI with mode information
    updateUI(mode, message) {
        const statusElement = document.querySelector('#revolutionary-status');
        if (statusElement) {
            statusElement.textContent = message;
        }

        // Update agent labels
        const agentALabel = document.querySelector('#agent-a-label');
        const agentBLabel = document.querySelector('#agent-b-label');
        
        if (mode === 'expert_panel') {
            if (agentALabel) agentALabel.textContent = 'Expert A';
            if (agentBLabel) agentBLabel.textContent = 'Expert B';
        } else if (mode === 'conference_chain') {
            if (agentALabel) agentALabel.textContent = 'Current Agent';
            if (agentBLabel) agentBLabel.textContent = 'Next Agent';
        }
    }

    // Stop current session
    async stopSession() {
        if (!this.activeSession) return;

        try {
            await fetch(`${this.baseUrl}/api/revolutionary-relay/stop-session/${this.activeSession}`, {
                method: 'POST'
            });
            
            this.stopStatusMonitoring();
            this.activeSession = null;
            this.updateUI('stopped', 'Session stopped');
        } catch (error) {
            console.error('Stop session error:', error);
        }
    }
}

// Human Simulator Integration
class HumanSimulator {
    constructor(baseUrl = 'https://web-production-2816f.up.railway.app') {
        this.baseUrl = baseUrl;
        this.userId = 'default_user'; // In production, get from authentication
    }

    // Start learning session
    async startLearningSession(prompt, strategy = 'balanced', rounds = 5) {
        try {
            const response = await fetch(`${this.baseUrl}/api/human-simulator/start-session`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt,
                    strategy,
                    rounds,
                    user_id: this.userId
                })
            });

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Human Simulator start error:', error);
            throw error;
        }
    }

    // Get characteristic phrase for context
    async getCharacteristicPhrase(context = 'general') {
        try {
            const response = await fetch(`${this.baseUrl}/api/human-simulator/get-characteristic-phrase`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    context,
                    user_id: this.userId
                })
            });

            const data = await response.json();
            return data.phrase;
        } catch (error) {
            console.error('Get phrase error:', error);
            return "Let's continue with this approach";
        }
    }

    // Learn from interaction
    async learnFromInteraction(interactionType, userResponse, aiResponse, effectiveness = 0.7) {
        try {
            await fetch(`${this.baseUrl}/api/human-simulator/learn-from-interaction`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    interaction_type: interactionType,
                    user_response: userResponse,
                    ai_response: aiResponse,
                    effectiveness
                })
            });
        } catch (error) {
            console.error('Learning error:', error);
        }
    }

    // Get clone confidence
    async getCloneConfidence() {
        try {
            const response = await fetch(`${this.baseUrl}/api/human-simulator/get-clone-confidence?user_id=${this.userId}`);
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Clone confidence error:', error);
            return { clone_confidence: 0, clone_ready: false };
        }
    }
}

// Initialize revolutionary systems
const revolutionaryRelay = new RevolutionaryRelay();
const humanSimulator = new HumanSimulator();

// Enhanced button handlers for revolutionary features
function startExpertPanel() {
    const prompt = document.querySelector('#prompt-input')?.value || 
                  document.querySelector('textarea')?.value;
    
    if (!prompt) {
        alert('Please enter a prompt first');
        return;
    }

    revolutionaryRelay.startExpertPanel(prompt);
}

function startConferenceChain() {
    const prompt = document.querySelector('#prompt-input')?.value || 
                  document.querySelector('textarea')?.value;
    
    if (!prompt) {
        alert('Please enter a prompt first');
        return;
    }

    revolutionaryRelay.startConferenceChain(prompt);
}

function stopRevolutionarySession() {
    revolutionaryRelay.stopSession();
}

// Enhanced Human Simulator functions
async function startHumanSimulatorWithLearning() {
    const prompt = document.querySelector('#prompt-input')?.value || 
                  document.querySelector('textarea')?.value;
    const strategy = document.querySelector('#strategy-select')?.value || 'balanced';
    const rounds = parseInt(document.querySelector('#rounds-input')?.value || '5');

    if (!prompt) {
        alert('Please enter a prompt first');
        return;
    }

    try {
        const result = await humanSimulator.startLearningSession(prompt, strategy, rounds);
        console.log('Human Simulator started with learning:', result);
        
        // Show clone confidence
        const confidence = await humanSimulator.getCloneConfidence();
        console.log('Clone confidence:', confidence);
        
    } catch (error) {
        console.error('Human Simulator error:', error);
        alert('Error starting Human Simulator: ' + error.message);
    }
}

// Add revolutionary mode buttons to existing interface
function addRevolutionaryButtons() {
    const existingButtons = document.querySelector('.human-simulator-controls') || 
                           document.querySelector('.conversation-controls');
    
    if (existingButtons && !document.querySelector('#revolutionary-buttons')) {
        const revolutionaryHTML = `
            <div id="revolutionary-buttons" class="revolutionary-controls">
                <h4>🚀 Revolutionary AI Modes</h4>
                <button onclick="startExpertPanel()" class="revolutionary-btn expert-panel-btn">
                    👥 Expert Panel (10 Pairs)
                </button>
                <button onclick="startConferenceChain()" class="revolutionary-btn conference-chain-btn">
                    🔗 Conference Chain (20 Agents)
                </button>
                <button onclick="stopRevolutionarySession()" class="revolutionary-btn stop-btn">
                    ⏹️ Stop Session
                </button>
                <div id="revolutionary-status" class="status-display"></div>
            </div>
        `;
        
        existingButtons.insertAdjacentHTML('afterend', revolutionaryHTML);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add revolutionary buttons
    addRevolutionaryButtons();
    
    // Enhance existing Human Simulator button
    const humanSimButton = document.querySelector('button[onclick*="Human Simulator"]');
    if (humanSimButton) {
        humanSimButton.onclick = startHumanSimulatorWithLearning;
    }
    
    console.log('🚀 PromptLink Revolutionary Features Loaded!');
    console.log('✅ 20-Agent Relay System Ready');
    console.log('✅ Human Simulator with Learning Ready');
    console.log('✅ Expert Panel & Conference Chain Modes Available');
});

// CSS for revolutionary features
const revolutionaryCSS = `
<style>
.revolutionary-controls {
    margin: 20px 0;
    padding: 20px;
    background: rgba(15, 23, 42, 0.8);
    border-radius: 10px;
    border: 1px solid var(--border-color);
}

.revolutionary-btn {
    background: linear-gradient(135deg, var(--logo-primary), var(--logo-secondary));
    color: white;
    border: none;
    padding: 12px 20px;
    margin: 5px;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    transition: all 0.3s ease;
}

.revolutionary-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0, 180, 216, 0.3);
}

.status-display {
    margin-top: 15px;
    padding: 10px;
    background: rgba(0, 180, 216, 0.1);
    border-radius: 5px;
    color: var(--logo-primary);
    font-weight: bold;
}

.revolutionary-results {
    margin: 20px 0;
    padding: 20px;
    background: rgba(15, 23, 42, 0.9);
    border-radius: 10px;
    border-left: 4px solid var(--logo-primary);
}

.result-pair, .agent-result {
    margin: 15px 0;
    padding: 15px;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 8px;
}

.download-btn {
    background: var(--success);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    margin-top: 15px;
}
</style>
`;

// Inject CSS
document.head.insertAdjacentHTML('beforeend', revolutionaryCSS);

