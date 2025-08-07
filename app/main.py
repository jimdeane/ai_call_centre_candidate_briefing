import os
import uuid
import json
import random
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus

app = Flask(__name__)
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))

os.makedirs(DATA_DIR, exist_ok=True)
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "submissions.db")
DB_URI = f"sqlite:///{DB_PATH}"

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Load all valid codes (persisted to a file)
CODE_FILE = os.path.join(DATA_DIR, "codes.log")
if not os.path.exists(CODE_FILE):
    with open(CODE_FILE, "w") as f:
        codes = [str(uuid.uuid4())[:8] for _ in range(10)]
        f.write("\n".join(codes))
else:
    with open(CODE_FILE, "r") as f:
        codes = [line.strip() for line in f.readlines()]


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    questionnaire = db.Column(db.String(64), nullable=False)
    answers = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        qid = request.form.get("qid")
        code = request.form.get("code")
        session = request.form.get("session")

        if not code or not session:
            return "Session ID and Code are required.", 400

        if code == "supersecretadmincode":
            return redirect(url_for('admin', code=code))
        else:
            return redirect(url_for('questionnaire', qid=qid, session=session, code=code))

    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Welcome to the Questionnaire Portal</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                background-color: #f8f9fa;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
            }
            .jumbotron {
                background: white;
                padding: 2rem 3rem;
                border-radius: 10px;
                box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                width: 100%;
            }
        </style>
    </head>
    <body>
        <div class="jumbotron">
            <h1 class="display-5">Questionnaire Portal</h1>
            <p class="lead">Please enter your questionnaire number, session ID, and access code to begin.</p>
            <form method="POST">
                <div class="mb-3">
                    <label class="form-label">Questionnaire ID</label>
                    <input type="text" class="form-control" name="qid" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Session ID</label>
                    <input type="text" class="form-control" name="session" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Access Code</label>
                    <input type="text" class="form-control" name="code" required>
                </div>
                <button type="submit" class="btn btn-primary">Enter</button>
            </form>
        </div>
    </body>
    </html>
    '''


@app.route("/admin", methods=["GET"])
def admin():
    admin_code = request.args.get("code")
    if not admin_code or admin_code != "supersecretadmincode":  # Replace with a secure code
        return "Unauthorized", 403

    # Load and show codes
    with open(CODE_FILE, "r") as f:
        code_list = f.read().splitlines()

    # Load submissions
    submissions = Submission.query.order_by(Submission.timestamp.desc()).all()

    html = '''
    <h1>Admin Panel</h1>
    <h2>One-Time Access Codes</h2>
    <ul>
    {% for c in codes %}
        <li>{{ c }}</li>
    {% endfor %}
    </ul>
<iframe src="https://replit.com/@jimd4/FlaskStart?embed=true" width="600" height="400"></iframe>
    <h2>Submissions</h2>
    {% for sub in submissions %}
        <div style="margin-bottom: 20px; padding: 10px; border: 1px solid #ccc;">
            <b>Time:</b> {{ sub.timestamp }}<br>
            <b>Name:</b> {{ sub.name }}<br>
            <b>Session:</b> {{ sub.session_id }}<br>
            <b>Questionnaire:</b> {{ sub.questionnaire }}<br>
            <b>Answers:</b>
            <ul>
            {% for k, v in sub.answers.items() %}
                <li><b>{{ k }}</b>: {{ v }}</li>
            {% endfor %}
            </ul>
        </div>
    {% endfor %}
    '''
    # Render with Jinja
    rendered = render_template_string(html, codes=code_list, submissions=[
        {
            "timestamp": s.timestamp,
            "name": s.name,
            "session_id": s.session_id,
            "questionnaire": s.questionnaire,
            "answers": json.loads(s.answers)
        } for s in submissions
    ])
    return rendered


@app.route("/questionnaire/<qid>", methods=["GET", "POST"])
def questionnaire(qid):
    session_id = request.args.get("session")
    code = request.args.get("code")

    if not session_id or not code or code not in codes:
        return "Invalid or missing session or code.", 403

    # Load questions
    qfile = f"questionnaire_{qid}.json"
    try:
        with open(qfile, "r") as f:
            questions = json.load(f)
    except FileNotFoundError:
        return f"No such questionnaire: {qid}", 404

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            return "Name is required.", 400

        answers = {q['id']: request.form.get(q['id'], '') for q in questions}
        db.session.add(Submission(
            session_id=session_id,
            name=name,
            questionnaire=qid,
            answers=json.dumps(answers)
        ))
        db.session.commit()
        return "<p>Thank you! Your answers have been submitted.</p>"

    form_html = '''
<!DOCTYPE html>
<html>
<head>
  <title>Questionnaire {{qid}}</title>
  <link rel="stylesheet" href="https://code.getmdl.io/1.3.0/material.indigo-pink.min.css">
  <script defer src="https://code.getmdl.io/1.3.0/material.min.js"></script>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    body {
      font-family: "Roboto", "Helvetica", "Arial", sans-serif;
      padding: 20px;
      background-color: #f5f5f5;
    }
    .container {
      max-width: 800px;
      margin: auto;
      background: white;
      padding: 30px;
      border-radius: 8px;
      box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .mdl-radio {
      display: block;
      margin: 6px 0;
    }
    h1 {
      font-size: 24px;
      margin-bottom: 20px;
    }
    .question-block {
      margin-bottom: 30px;
    }
  </style>
</head>
<body>
  <div class="container">
    <h1>Questionnaire {{qid}}</h1>
    <form method="POST">
      <div class="mdl-textfield mdl-js-textfield mdl-textfield--floating-label" style="width:100%;">
        <input class="mdl-textfield__input" type="text" id="name" name="name" required>
        <label class="mdl-textfield__label" for="name">Your Name (required)</label>
      </div>

      {% for q in questions %}
        <div class="question-block">
          <p><strong>{{loop.index}}. {{q.text}}</strong></p>
          {% for opt in q.options %}
            <label class="mdl-radio mdl-js-radio mdl-js-ripple-effect" for="{{q.id}}_{{loop.index}}">
              <input type="radio" id="{{q.id}}_{{loop.index}}" class="mdl-radio__button" name="{{q.id}}" value="{{opt}}" required>
              <span class="mdl-radio__label">{{opt}}</span>
            </label>
          {% endfor %}
        </div>
      {% endfor %}

      <button class="mdl-button mdl-js-button mdl-button--raised mdl-button--colored" type="submit">
        Submit
      </button>
    </form>
  </div>
</body>
</html>
'''

    return render_template_string(form_html, questions=questions, qid=qid)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020)
