# rule_database.py
import sqlite3
import json
from datetime import datetime

class RuleDatabase:
    def __init__(self, db_name='rules.db'):
        self.db_name = db_name
        self.setup_database()

    def setup_database(self):
        """Create the rules table if it doesn't exist"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    rule_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()

    def save_rule(self, name: str, rule_text: str, description: str = None):
        """Save a new rule or update existing one"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO rules (name, rule_text, description)
                    VALUES (?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                        rule_text = excluded.rule_text,
                        description = excluded.description,
                        updated_at = CURRENT_TIMESTAMP
                ''', (name, rule_text, description))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.Error as e:
                print(f"Error saving rule: {e}")
                return None

    def get_rule(self, name: str):
        """Retrieve a rule by name"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM rules WHERE name = ?', (name,))
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'description': result[2],
                    'rule_text': result[3],
                    'created_at': result[4],
                    'updated_at': result[5]
                }
            return None

    def get_all_rules(self):
        """Retrieve all rules"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM rules')
            results = cursor.fetchall()
            return [{
                'id': r[0],
                'name': r[1],
                'description': r[2],
                'rule_text': r[3],
                'created_at': r[4],
                'updated_at': r[5]
            } for r in results]

    def delete_rule(self, name: str):
        """Delete a rule by name"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM rules WHERE name = ?', (name,))
            conn.commit()
            return cursor.rowcount > 0

# Test the database functionality
def test_database():
    # Create database instance
    db = RuleDatabase('test_rules.db')
    
    # Test rules to save
    test_rules = [
        {
            'name': 'Senior Sales Rule',
            'description': 'Identifies senior sales staff',
            'rule_text': 'age > 30 AND department = \'Sales\''
        },
        {
            'name': 'Junior or Marketing Rule',
            'description': 'Identifies junior staff or marketing department',
            'rule_text': 'age < 25 OR department = \'Marketing\''
        },
        {
            'name': 'Complex Eligibility',
            'description': 'Complex rule for bonus eligibility',
            'rule_text': '(age > 25 AND salary >= 50000) OR department = \'Marketing\''
        }
    ]
    
    print("Saving rules to database...")
    for rule in test_rules:
        db.save_rule(rule['name'], rule['rule_text'], rule['description'])
    
    print("\nRetrieving all rules:")
    all_rules = db.get_all_rules()
    for rule in all_rules:
        print(f"\nRule: {rule['name']}")
        print(f"Description: {rule['description']}")
        print(f"Rule text: {rule['rule_text']}")
        print(f"Created at: {rule['created_at']}")
        print(f"Updated at: {rule['updated_at']}")
    
    print("\nTesting rule retrieval by name:")
    rule = db.get_rule('Senior Sales Rule')
    if rule:
        print(f"Found rule: {rule['name']}")
        print(f"Rule text: {rule['rule_text']}")
    
    print("\nTesting rule deletion:")
    deleted = db.delete_rule('Junior or Marketing Rule')
    print(f"Rule deleted: {deleted}")
    
    print("\nRemaining rules:")
    remaining_rules = db.get_all_rules()
    for rule in remaining_rules:
        print(f"- {rule['name']}: {rule['rule_text']}")

if __name__ == "__main__":
    test_database()