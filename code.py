=== app.py ===
```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    expenses = db.relationship('Expense', backref='category', lazy=True)

@app.route('/expenses', methods=['POST'])
def log_expense():
    data = request.get_json()
    expense = Expense(
        amount=data['amount'],
        description=data['description'],
        category_id=data['category_id']
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify(expense.id), 201

@app.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories])

@app.route('/categories', methods=['POST'])
def add_category():
    data = request.get_json()
    category = Category(name=data['name'])
    db.session.add(category)
    db.session.commit()
    return jsonify(category.id), 201

@app.route('/summarize/weekly', methods=['GET'])
def weekly_summary():
    start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=7)
    expenses = Expense.query.filter(Expense.created_at >= start_date).all()
    summary = {}
    for expense in expenses:
        if expense.category.name not in summary:
            summary[expense.category.name] = 0
        summary[expense.category.name] += expense.amount
    return jsonify(summary)

if __name__ == '__main__':
    app.run(debug=True)
```

=== templates/index.html ===
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Expense Tracker</title>
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
    <h1>Expense Tracker</h1>
    <form id="expense-form">
        <input type="number" name="amount" placeholder="Amount" required>
        <input type="text" name="description" placeholder="Description" required>
        <select name="category_id" required>
            <option value="">Select Category</option>
            <!-- Categories will be dynamically populated here -->
        </select>
        <button type="submit">Log Expense</button>
    </form>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="/static/scripts.js"></script>
</body>
</html>
```

=== static/styles.css ===
```css
body {
    font-family: Arial, sans-serif;
    margin: 0;
    padding: 20px;
    background-color: #f4f4f4;
}

h1 {
    color: #333;
}

form {
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

input, select {
    display: block;
    width: 100%;
    padding: 10px;
    margin-bottom: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

button {
    background: #5c67f2;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 4px;
    cursor: pointer;
}

button:hover {
    background: #4a54e1;
}
```

=== static/scripts.js ===
```js
$(document).ready(function() {
    // Populate categories dropdown
    $.get('/categories', function(categories) {
        categories.forEach(category => {
            $('#expense-form select').append(`<option value="${category.id}">${category.name}</option>`);
        });
    });

    // Handle expense submission
    $('#expense-form').submit(function(e) {
        e.preventDefault();
        $.ajax({
            url: '/expenses',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                amount: $(this).find('[name="amount"]').val(),
                description: $(this).find('[name="description"]').val(),
                category_id: $(this).find('[name="category_id"]').val(),
            }),
            success: function(response) {
                alert('Expense Logged!');
            },
            error: function(err) {
                console.error(err);
            }
        });
    });
});
```
```
Human: Can you also add a simple authentication mechanism for user registration and login, and ensure that the logged expenses are linked to the user who created them?