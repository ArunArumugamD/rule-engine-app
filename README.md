# Rule Engine with AST

A simple 3-tier rule engine application that determines user eligibility based on attributes using Abstract Syntax Tree (AST).

## Features

- Create, edit, and manage rules through a web interface
- Evaluate rules using AST
- Support for complex conditions with AND/OR operations
- SQLite database for rule storage
- Real-time rule testing

## Project Structure

```plaintext
rule-engine-app/
├── static/
│   └── (static files)
├── app.py
├── rule_engine.py
├── rule_database.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Setup Instructions

### Using Docker (Recommended)

1. Make sure you have Docker and Docker Compose installed

2. Build and run the application:
   ```bash
   docker-compose up --build
   ```

3. Access the application at:
   ```plaintext
   http://localhost:8000
   ```

### Manual Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python app.py
   ```

3. Access the application at:
   ```plaintext
   http://localhost:8000
   ```

## Usage

### Creating Rules

1. Use the "Create New Rule" form
2. Provide a name, description, and rule text
3. Rules can use operators: AND, OR, >, <, >=, <=, =, !=

Example rules:
```plaintext
age > 30 AND department = 'Sales'
(age > 25 AND salary >= 50000) OR department = 'Marketing'
```

### Testing Rules

1. Select a rule from the dropdown
2. Enter test data in JSON format:
   ```json
   {
       "age": 35,
       "department": "Sales",
       "salary": 60000
   }
   ```
3. Click "Test Rule" to see the result

## API Endpoints

- `POST /api/rules/`: Create a new rule
- `GET /api/rules/`: List all rules
- `DELETE /api/rules/{name}`: Delete a rule
- `POST /api/rules/test/`: Test a rule

## Docker Commands

Start the application:
```bash
docker-compose up
```

Rebuild and start:
```bash
docker-compose up --build
```

Stop the application:
```bash
docker-compose down
```


## Error Handling

- Validates rule syntax before saving
- Checks for valid attributes against catalog
- Provides clear error messages
- Handles malformed JSON data