import os
import uuid
import json
import random
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote_plus

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', str(uuid.uuid4()))
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))

os.makedirs(DATA_DIR, exist_ok=True)
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "submissions.sqlite")
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
    # Convert answers from JSON string to dict for each submission
    for sub in submissions:
        try:
            sub.answers = json.loads(sub.answers)
        except Exception:
            sub.answers = {}

    html = '''
    <h1>Admin Panel</h1>
    <h2>One-Time Access Codes</h2>
    <ul>
    {% for c in codes %}
        <li>{{ c }}</li>
    {% endfor %}
    </ul>
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
    <hr>
    <a href="/manage_questionnaires" class="btn btn-success">Manage Questionnaires</a>
    '''
    return render_template_string(html, codes=code_list, submissions=submissions)


# Questionnaire management page
@app.route('/manage_questionnaires', methods=['GET', 'POST'])
def manage_questionnaires():
    # List all questionnaire files
    app_dir = os.path.abspath(os.path.dirname(__file__))
    files = [f for f in os.listdir(app_dir) if f.startswith('questionnaire_') and f.endswith('.json')]
    selected = request.args.get('selected')
    message = ""
    questions = []
    validation = False
    if selected:
        qpath = os.path.join(app_dir, selected)
        try:
            with open(qpath, 'r') as f:
                data = json.load(f)
                questions = data.get('questions', []) if isinstance(data, dict) else []
                validation = data.get('validation', False) if isinstance(data, dict) else False
        except Exception as e:
            message = f"Error loading {selected}: {e}"

    if request.method == 'POST':
        action = request.form.get('action')
        qfile = request.form.get('qfile')
        if action == 'delete' and qfile:
            qpath = os.path.join(app_dir, qfile)
            try:
                os.remove(qpath)
                message = f"Deleted {qfile}"
                selected = None
            except Exception as e:
                message = f"Error deleting {qfile}: {e}"
        elif action == 'add':
            new_name = request.form.get('new_name')
            if new_name:
                fname = f"questionnaire_{new_name}.json"
                fpath = os.path.join(app_dir, fname)
                with open(fpath, 'w') as f:
                    json.dump({"questions": [], "validation": False}, f)
                message = f"Added {fname}"
                selected = fname
        elif action == 'save' and qfile:
            qpath = os.path.join(app_dir, qfile)
            try:
                questions = json.loads(request.form.get('questions_json', '[]'))
                validation = request.form.get('validation') == 'on'
                with open(qpath, 'w') as f:
                    json.dump({"questions": questions, "validation": validation}, f, indent=2)
                message = f"Saved {qfile}"
            except Exception as e:
                message = f"Error saving {qfile}: {e}"
        # After POST, reload file if selected
        if selected:
            qpath = os.path.join(app_dir, selected)
            try:
                with open(qpath, 'r') as f:
                    data = json.load(f)
                    questions = data.get('questions', []) if isinstance(data, dict) else []
                    validation = data.get('validation', False) if isinstance(data, dict) else False
            except Exception as e:
                message = f"Error loading {selected}: {e}"

    # Convert entire questionnaire JSON for textarea
    if selected:
        qpath = os.path.join(app_dir, selected)
        try:
            with open(qpath, 'r') as f:
                questions_json = f.read()
        except Exception:
            questions_json = ''
    else:
        questions_json = ''
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
      <title>Manage Questionnaires</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
      <script src="https://cdnjs.cloudflare.com/ajax/libs/ace/1.4.14/ace.js" crossorigin="anonymous"></script>
    </head>
    <body>
    <h1>Manage Questionnaires</h1>
    <form method="POST">
      <label>Add new questionnaire (number): <input type="text" name="new_name"></label>
      <button name="action" value="add" class="btn btn-primary">Add</button>
    </form>
    <hr>
    <h2>Existing Questionnaires</h2>
    <ul>
    {% for f in files %}
      <li>
        <a href="/manage_questionnaires?selected={{f}}">{{f}}</a>
        <form method="POST" style="display:inline">
          <input type="hidden" name="qfile" value="{{f}}">
          <button name="action" value="delete" class="btn btn-danger btn-sm">Delete</button>
        </form>
      </li>
    {% endfor %}
    </ul>
    {% if selected %}
    <hr>
    <h3>Editing: {{selected}}</h3>
    <form method="POST" onsubmit="document.getElementById('questions_json').value = aceEditor.getValue();">
      <input type="hidden" name="qfile" value="{{selected}}">
      <input type="hidden" id="questions_json" name="questions_json">
      <div id="editor" style="height:350px;width:100%;border:1px solid #ccc;border-radius:6px;margin-bottom:10px;"></div>
      <button name="action" value="save" class="btn btn-success">Save Changes</button>
    </form>
    <p>Edit the entire questionnaire JSON here, including <code>questions</code> and <code>validation</code>. You can add, delete, modify, and reorder questions, and change validation settings.</p>
    <script>
      document.addEventListener('DOMContentLoaded', function() {
        var aceEditor = ace.edit("editor");
        aceEditor.session.setMode("ace/mode/json");
        aceEditor.setTheme("ace/theme/github");
        aceEditor.setValue({{ questions_json|tojson }}, -1);
        aceEditor.session.setUseWrapMode(true);
        aceEditor.setOptions({
          fontSize: "14px",
          showPrintMargin: false
        });
        window.aceEditor = aceEditor;
      });
    </script>
    {% endif %}
    <p style="color:green">{{message}}</p>
    <a href="/admin" class="btn btn-secondary">Back to Admin</a>
    </body>
    </html>
    '''
    return render_template_string(html, files=files, selected=selected, questions_json=questions_json, validation=validation, message=message)


@app.route("/questionnaire/<qid>", methods=["GET", "POST"])
def questionnaire(qid):
    session_id = request.args.get("session")
    code = request.args.get("code")

    if not session_id or not code or code not in codes:
        return "Invalid or missing session or code.", 403

    # Load questions from app folder
    app_dir = os.path.abspath(os.path.dirname(__file__))
    qfile = os.path.join(app_dir, f"questionnaire_{qid}.json")
    try:
        with open(qfile, "r") as f:
            data = json.load(f)
            if isinstance(data, dict) and 'questions' in data:
                questions = data['questions']
            else:
                questions = data
    except FileNotFoundError:
        return f"No such questionnaire: {qid}", 404

    # Track which questions are correct
    # If candidate is retrying, get previous answers from session
    from flask import session as flask_session
    if 'retry_answers' not in flask_session:
        flask_session['retry_answers'] = {}

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            return "Name is required.", 400

        answers = {q['id']: request.form.get(q['id'], '') for q in questions}
        # Check answers
        results = []
        all_correct = True
        for q in questions:
            correct_idx = q.get('answer')
            user_ans = answers[q['id']]
            is_correct = False
            if correct_idx is not None:
                try:
                    is_correct = (user_ans == q['options'][correct_idx])
                except Exception:
                    is_correct = False
            results.append({'id': q['id'], 'text': q['text'], 'your_answer': user_ans, 'correct_answer': q['options'][correct_idx] if correct_idx is not None else None, 'is_correct': is_correct})
            if not is_correct:
                all_correct = False

        if all_correct:
            db.session.add(Submission(
                session_id=session_id,
                name=name,
                questionnaire=qid,
                answers=json.dumps(answers)
            ))
            db.session.commit()
            flask_session.pop('retry_answers', None)
            return redirect(url_for('instructions', qid=qid))
        else:
            # Store incorrect answers for retry
            flask_session['retry_answers'][qid] = answers
            flask_session.modified = True
            # Show results page
            results_html = '''
<!DOCTYPE html>
<html>
<head>
  <title>Results for Questionnaire {{qid}}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
  <div class="container">
    <h1>Results for Questionnaire {{qid}}</h1>
    <form method="POST">
      <input type="hidden" name="name" value="{{name}}">
      {% for r in results %}
        <div class="mb-3">
          <strong>{{loop.index}}. {{r.text}}</strong><br>
          <span>Your answer: <b>{{r.your_answer}}</b></span><br>
          <span>Correct answer: <b>{{r.correct_answer}}</b></span><br>
          {% if r.is_correct %}
            <span style="color:green">Correct</span>
          {% else %}
            <span style="color:red">Incorrect</span><br>
            <label>Try again:
              <select name="{{r.id}}" class="form-select">
                {% for opt in questions[loop.index0].options %}
                  <option value="{{opt}}" {% if r.your_answer == opt %}selected{% endif %}>{{opt}}</option>
                {% endfor %}
              </select>
            </label>
          {% endif %}
        </div>
      {% endfor %}
      <button class="btn btn-primary" type="submit">Resubmit Incorrect Answers</button>
    </form>
  </div>
</body>
</html>
'''
            return render_template_string(results_html, results=results, questions=questions, qid=qid, name=name)

    # If GET or first load, show form
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


@app.route('/instructions')
def instructions():
    qid = request.args.get("qid", "1")
    instructions_path = os.path.join(DATA_DIR, f"instructions_{qid}.txt")
    try:
        with open(instructions_path, "r") as f:
            instructions_text = f.read()
    except FileNotFoundError:
        instructions_text = "Instructions not found."

    page = f'''
    <!DOCTYPE html>
    <html>
    <head>
      <title>Next Steps</title>
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
      <style>
        html, body {{
          height: 100%;
          margin: 0;
          padding: 0;
        }}
        body {{ background:#f5f5f5; min-height:100vh; display:flex; flex-direction:column; }}
        .container {{ flex: 1 1 auto; display: flex; flex-direction: column; height: 100vh; }}
        .panel {{
          background:#fff;
          padding:20px;
          border-radius:8px;
          box-shadow:0 2px 6px rgba(0,0,0,0.1);
          margin-bottom:0;
          height:300px;
          overflow:auto;
        }}
        .iframe-wrapper {{
          flex: 1 1 auto;
          display: flex;
        }}
        iframe {{
          width: 100%;
          height: 100%;
          border:1px solid #ccc;
          border-radius:8px;
          min-height:0;
        }}
      </style>
    </head>
    <body>
      <div class="container">
        <h1 class="mb-4">Instructions & Environment</h1>
        <div class="panel">
          <h4>Instructions</h4>
          <p>{instructions_text}</p>
        </div>
        <div class="iframe-wrapper">
          <iframe src="https://replit.com/@jimd4/FlaskStart?embed=true"></iframe>
        </div>
      </div>
    </body>
    </html>
    '''
    return page


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5020)
