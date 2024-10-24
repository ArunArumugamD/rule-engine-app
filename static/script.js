// static/script.js
async function loadRules() {
    try {
        const response = await fetch('/api/rules/');
        const rules = await response.json();
        
        // Update rules list
        const rulesList = document.getElementById('rulesList');
        rulesList.innerHTML = '';
        
        // Update rule select
        const ruleSelect = document.getElementById('ruleSelect');
        ruleSelect.innerHTML = '';
        
        rules.forEach(rule => {
            // Add to rules list
            const ruleDiv = document.createElement('div');
            ruleDiv.className = 'rule-card';
            ruleDiv.innerHTML = `
                <div class="rule-header">
                    <div>
                        <h3 class="rule-title">${rule.name}</h3>
                        <p class="rule-description">${rule.description}</p>
                        <pre class="rule-text">${rule.rule_text}</pre>
                    </div>
                    <button onclick="deleteRule('${rule.name}')" class="btn btn-danger">
                        Delete
                    </button>
                </div>
            `;
            rulesList.appendChild(ruleDiv);
            
            // Add to select
            const option = document.createElement('option');
            option.value = rule.name;
            option.textContent = rule.name;
            ruleSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading rules:', error);
        showNotification('Error loading rules', 'error');
    }
}

async function createRule(event) {
    event.preventDefault();
    
    const data = {
        name: document.getElementById('ruleName').value,
        description: document.getElementById('ruleDescription').value,
        rule_text: document.getElementById('ruleText').value
    };
    
    try {
        const response = await fetch('/api/rules/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            showNotification('Rule created successfully', 'success');
            loadRules();
            event.target.reset();
        } else {
            const error = await response.json();
            showNotification(`Error: ${error.detail}`, 'error');
        }
    } catch (error) {
        console.error('Error creating rule:', error);
        showNotification('Error creating rule', 'error');
    }
}

async function testRule(event) {
    event.preventDefault();
    
    try {
        const userData = JSON.parse(document.getElementById('userData').value);
        const ruleName = document.getElementById('ruleSelect').value;
        
        const response = await fetch('/api/rules/test/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                rule_name: ruleName,
                user_data: userData
            })
        });
        
        const result = await response.json();
        
        document.getElementById('testResult').innerHTML = `
            <div class="rule-card ${result.result ? 'success-result' : 'failure-result'}">
                Rule evaluation result: <strong>${result.result ? 'MATCH' : 'NO MATCH'}</strong>
            </div>
        `;
    } catch (error) {
        console.error('Error testing rule:', error);
        showNotification('Error testing rule: ' + error.message, 'error');
    }
}

async function deleteRule(ruleName) {
    if (confirm(`Are you sure you want to delete rule "${ruleName}"?`)) {
        try {
            const response = await fetch(`/api/rules/${ruleName}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                showNotification('Rule deleted successfully', 'success');
                loadRules();
            } else {
                showNotification('Error deleting rule', 'error');
            }
        } catch (error) {
            console.error('Error deleting rule:', error);
            showNotification('Error deleting rule', 'error');
        }
    }
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    loadRules();
    document.getElementById('createRuleForm').addEventListener('submit', createRule);
    document.getElementById('testRuleForm').addEventListener('submit', testRule);
});