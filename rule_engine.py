# rule_engine.py

class RuleNode:
    def __init__(self, type_name, value=None):
        self.type = type_name    # Can be "operator" (AND/OR) or "operand" (actual conditions)
        self.value = value       # Stores the actual value (like "AND" or "age > 30")
        self.left = None         # Left child node
        self.right = None        # Right child node

    def __str__(self):
        return f"Node(type={self.type}, value={self.value})"

class RuleParser:
    def __init__(self):
        self.operators = {'AND', 'OR'}
        self.comparisons = {'>', '<', '>=', '<=', '=', '!='}

    def parse_rule(self, rule_text):
        """Convert a text rule into our RuleNode structure"""
        # Remove extra spaces
        rule_text = ' '.join(rule_text.split())
        
        # Handle parentheses
        if rule_text.startswith('(') and rule_text.endswith(')'):
            # Remove outer parentheses
            rule_text = rule_text[1:-1]
        
        # First split by OR (lower precedence)
        or_parts = self._split_by_operator(rule_text, 'OR')
        
        if len(or_parts) > 1:
            root = RuleNode("operator", "OR")
            root.left = self.parse_rule(or_parts[0])
            root.right = self.parse_rule(or_parts[1])
            return root
            
        # Then split by AND (higher precedence)
        and_parts = self._split_by_operator(rule_text, 'AND')
        
        if len(and_parts) > 1:
            root = RuleNode("operator", "AND")
            root.left = self.parse_rule(and_parts[0])
            root.right = self.parse_rule(and_parts[1])
            return root
            
        # Base case: single condition
        return RuleNode("operand", rule_text.strip())

    def _split_by_operator(self, text, operator):
        """Split text by operator, respecting parentheses"""
        parts = []
        current_part = ""
        paren_count = 0
        
        words = text.split()
        
        for i, word in enumerate(words):
            if word == '(':
                paren_count += 1
            elif word == ')':
                paren_count -= 1
                
            if word == operator and paren_count == 0:
                if current_part:
                    parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += " " + word if current_part else word
                
        if current_part:
            parts.append(current_part.strip())
            
        return parts if len(parts) > 1 else [text]

class RuleEvaluator:
    def evaluate_rule(self, rule_node, user_data):
        """
        Evaluate if user_data matches the rule
        rule_node: Our RuleNode structure
        user_data: Dictionary with user information
        """
        # If it's an operator node (AND/OR)
        if rule_node.type == "operator":
            left_result = self.evaluate_rule(rule_node.left, user_data)
            right_result = self.evaluate_rule(rule_node.right, user_data)
            
            if rule_node.value == "AND":
                return left_result and right_result
            elif rule_node.value == "OR":
                return left_result or right_result
        
        # If it's a condition node
        elif rule_node.type == "operand":
            return self._evaluate_condition(rule_node.value, user_data)
            
        return False

    def _evaluate_condition(self, condition, user_data):
        """Evaluate a single condition like 'age > 30' or "department = 'Sales'"""
        # Split the condition into parts
        parts = condition.split()
        if len(parts) != 3:
            return False
            
        field, operator, value = parts
        
        # Check if we have this field in user data
        if field not in user_data:
            return False
            
        # Get actual value from user data
        actual_value = user_data[field]
        
        # Handle string values (remove quotes)
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]  # Remove surrounding quotes
            
        # Convert to numbers if both are numeric
        try:
            if str(actual_value).isdigit() and str(value).isdigit():
                actual_value = int(actual_value)
                value = int(value)
        except:
            pass  # Keep as strings if conversion fails
            
        # Compare based on operator
        if operator == ">":
            return actual_value > value
        elif operator == "<":
            return actual_value < value
        elif operator == ">=":
            return actual_value >= value
        elif operator == "<=":
            return actual_value <= value
        elif operator == "=":
            return str(actual_value) == str(value)  # Convert both to strings for equality
        elif operator == "!=":
            return str(actual_value) != str(value)  # Convert both to strings for inequality
            
        return False

def print_rule_tree(node, prefix=""):
    """Helper function to print the rule tree structure"""
    if not node:
        return
        
    print(f"{prefix}└─ {node}")
    
    if node.left:
        print_rule_tree(node.left, prefix + "   ")
    if node.right:
        print_rule_tree(node.right, prefix + "   ")

def test_rules():
    parser = RuleParser()
    evaluator = RuleEvaluator()
    
    # Test data
    test_users = [
        {
            "name": "Alice",
            "age": 35,
            "department": "Sales",
            "salary": 60000
        },
        {
            "name": "Bob",
            "age": 22,
            "department": "Engineering",
            "salary": 45000
        },
        {
            "name": "Charlie",
            "age": 28,
            "department": "Marketing",
            "salary": 50000
        }
    ]
    
    # Test cases
    test_rules = [
        ("Simple AND rule", "age > 30 AND department = 'Sales'"),
        ("Simple OR rule", "age < 25 OR department = 'Marketing'"),
        ("Complex rule", "(age > 25 AND salary >= 50000) OR department = 'Marketing'")
    ]
    
    # Run all test cases
    for rule_name, rule_text in test_rules:
        print(f"\nTesting {rule_name}: {rule_text}")
        rule = parser.parse_rule(rule_text)
        
        print("\nRule structure:")
        print_rule_tree(rule)
        
        print("\nResults:")
        for user in test_users:
            result = evaluator.evaluate_rule(rule, user)
            print(f"{user['name']} (Age: {user['age']}, Dept: {user['department']}, Salary: {user['salary']}): {result}")

if __name__ == "__main__":
    test_rules()