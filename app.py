# app.py
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uvicorn
import os

# Import our previous code
from rule_engine import RuleParser, RuleEvaluator
from rule_database import RuleDatabase

# Create directories if they don't exist
os.makedirs('static', exist_ok=True)

app = FastAPI(title="Rule Engine")
rule_db = RuleDatabase('rules.db')
parser = RuleParser()
evaluator = RuleEvaluator()

# Pydantic models for request/response
class RuleCreate(BaseModel):
    name: str
    description: str
    rule_text: str

class RuleTest(BaseModel):
    rule_name: str
    user_data: Dict[str, Any]

# API Routes
@app.post("/api/rules/", response_model=dict)
async def create_rule(rule: RuleCreate):
    try:
        # Validate rule by parsing it
        parser.parse_rule(rule.rule_text)
        
        # Save to database
        rule_id = rule_db.save_rule(rule.name, rule.rule_text, rule.description)
        if rule_id:
            return {"message": "Rule created successfully", "id": rule_id}
        raise HTTPException(status_code=400, detail="Failed to create rule")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/rules/", response_model=List[dict])
async def get_rules():
    return rule_db.get_all_rules()

@app.post("/api/rules/test/", response_model=dict)
async def test_rule(test_data: RuleTest):
    try:
        # Get rule from database
        rule = rule_db.get_rule(test_data.rule_name)
        if not rule:
            raise HTTPException(status_code=404, detail="Rule not found")
            
        # Parse and evaluate rule
        rule_ast = parser.parse_rule(rule['rule_text'])
        result = evaluator.evaluate_rule(rule_ast, test_data.user_data)
        
        return {
            "rule_name": test_data.rule_name,
            "user_data": test_data.user_data,
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/rules/{rule_name}")
async def delete_rule(rule_name: str):
    if rule_db.delete_rule(rule_name):
        return {"message": "Rule deleted successfully"}
    raise HTTPException(status_code=404, detail="Rule not found")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# HTML route
@app.get("/")
async def get_index():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rule Engine</title>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    </head>
    <body class="bg-gray-100">
        <div class="container mx-auto px-4 py-8">
            <h1 class="text-3xl font-bold mb-8">Rule Engine</h1>
            
            <!-- Create Rule Form -->
            <div class="bg-white p-6 rounded-lg shadow-md mb-8">
                <h2 class="text-xl font-semibold mb-4">Create New Rule</h2>
                <form id="createRuleForm" class="space-y-4">
                    <div>
                        <label class="block mb-1">Name:</label>
                        <input type="text" id="ruleName" class="w-full p-2 border rounded">
                    </div>
                    <div>
                        <label class="block mb-1">Description:</label>
                        <input type="text" id="ruleDescription" class="w-full p-2 border rounded">
                    </div>
                    <div>
                        <label class="block mb-1">Rule Text:</label>
                        <input type="text" id="ruleText" class="w-full p-2 border rounded">
                        <p class="text-sm text-gray-500 mt-1">
                            Example: age > 30 AND department = 'Sales'
                        </p>
                    </div>
                    <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                        Create Rule
                    </button>
                </form>
            </div>
            
            <!-- Test Rule Form -->
            <div class="bg-white p-6 rounded-lg shadow-md mb-8">
                <h2 class="text-xl font-semibold mb-4">Test Rule</h2>
                <form id="testRuleForm" class="space-y-4">
                    <div>
                        <label class="block mb-1">Select Rule:</label>
                        <select id="ruleSelect" class="w-full p-2 border rounded"></select>
                    </div>
                    <div>
                        <label class="block mb-1">User Data (JSON):</label>
                        <textarea id="userData" class="w-full p-2 border rounded" rows="4"></textarea>
                        <p class="text-sm text-gray-500 mt-1">
                            Example: {"age": 35, "department": "Sales", "salary": 60000}
                        </p>
                    </div>
                    <button type="submit" class="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
                        Test Rule
                    </button>
                </form>
                <div id="testResult" class="mt-4"></div>
            </div>
            
            <!-- Rules List -->
            <div class="bg-white p-6 rounded-lg shadow-md">
                <h2 class="text-xl font-semibold mb-4">Existing Rules</h2>
                <div id="rulesList" class="space-y-4"></div>
            </div>
        </div>

        <script>
            // Load rules on page load
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
                        ruleDiv.className = 'p-4 border rounded';
                        ruleDiv.innerHTML = `
                            <div class="flex justify-between items-start">
                                <div>
                                    <h3 class="font-semibold">${rule.name}</h3>
                                    <p class="text-gray-600">${rule.description}</p>
                                    <p class="text-sm font-mono bg-gray-100 p-2 mt-2 rounded">${rule.rule_text}</p>
                                </div>
                                <button onclick="deleteRule('${rule.name}')" class="text-red-500 hover:text-red-700">
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
                    alert('Error loading rules');
                }
            }

            // Create rule
            document.getElementById('createRuleForm').onsubmit = async (e) => {
                e.preventDefault();
                
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
                        alert('Rule created successfully');
                        loadRules();
                        e.target.reset();
                    } else {
                        const error = await response.json();
                        alert(`Error: ${error.detail}`);
                    }
                } catch (error) {
                    console.error('Error creating rule:', error);
                    alert('Error creating rule');
                }
            };

            // Test rule
            document.getElementById('testRuleForm').onsubmit = async (e) => {
                e.preventDefault();
                
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
                        <div class="p-4 ${result.result ? 'bg-green-100' : 'bg-red-100'} rounded">
                            Rule evaluation result: <strong>${result.result ? 'MATCH' : 'NO MATCH'}</strong>
                        </div>
                    `;
                } catch (error) {
                    console.error('Error testing rule:', error);
                    alert('Error testing rule: ' + error.message);
                }
            };

            // Delete rule
            async function deleteRule(ruleName) {
                if (confirm(`Are you sure you want to delete rule "${ruleName}"?`)) {
                    try {
                        const response = await fetch(`/api/rules/${ruleName}`, {
                            method: 'DELETE'
                        });
                        
                        if (response.ok) {
                            alert('Rule deleted successfully');
                            loadRules();
                        } else {
                            alert('Error deleting rule');
                        }
                    } catch (error) {
                        console.error('Error deleting rule:', error);
                        alert('Error deleting rule');
                    }
                }
            }

            // Load rules on page load
            loadRules();
        </script>
    </body>
    </html>
    """)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)