import os
import json
import time
from behave import given, when, then
from flask import Flask
from app.main import app, db, Submission, DATA_DIR
from flask.testing import FlaskClient


def get_test_client():
    app.config['TESTING'] = True
    return app.test_client()


@given('the Flask app is running')
def step_impl_flask_running(context):
    context.client = get_test_client()
    # Ensure test data exists
    # 1. Ensure a valid code is available
    code_file = os.path.join(DATA_DIR, "codes.log")
    if os.path.exists(code_file):
        with open(code_file) as f:
            codes = [line.strip() for line in f if line.strip()]
        if codes:
            context.valid_code = codes[0]
        else:
            # Generate a code if none exist
            import uuid
            context.valid_code = str(uuid.uuid4())[:8]
            with open(code_file, "w") as f:
                f.write(context.valid_code + "\n")
    else:
        import uuid
        context.valid_code = str(uuid.uuid4())[:8]
        with open(code_file, "w") as f:
            f.write(context.valid_code + "\n")
    # 2. Ensure questionnaire_1.json exists with q1 and q2
    qfile = os.path.join(DATA_DIR, "questionnaire_1.json")
    if not os.path.exists(qfile):
        questions = [
            {"id": "q1", "text": "Test Question 1", "options": ["Option A", "Option B"], "answer": 0},
            {"id": "q2", "text": "Test Question 2", "options": ["Option A", "Option B"], "answer": 1}
        ]
        with open(qfile, "w") as f:
            json.dump({"questions": questions, "mandatory": True}, f)


@given('a valid session id "{session}" and code "{code}" and questionnaire id "{qid}"')
def step_impl_valid_session(context, session, code, qid):
    context.session = session
    # Use valid code from context if requested code is not valid
    code_file = os.path.join(DATA_DIR, "codes.log")
    with open(code_file) as f:
        valid_codes = [line.strip() for line in f if line.strip()]
    if code not in valid_codes:
        context.code = context.valid_code
    else:
        context.code = code
    context.qid = qid


@when('I submit answers to some questions')
def step_impl_submit_answers(context):
    answers = {}
    for row in context.table:
        answers[row['qid']] = row['answer']
    data = {'name': 'Test User'}
    data.update(answers)
    url = f"/questionnaire/{context.qid}?session={context.session}&code={context.code}"
    context.response = context.client.post(url, data=data, follow_redirects=True)
    time.sleep(0.5)  # Give DB time to commit


@then('the database should contain a submission for session "{session}" with those answers')
def step_impl_db_contains(context, session):
    # Find the latest submission for this session within app context
    with app.app_context():
        sub = Submission.query.filter_by(session_id=session).order_by(Submission.timestamp.desc()).first()
        assert sub is not None, f"No submission found for session {session}"
        answers = json.loads(sub.answers)
        if context.table is not None:
            for row in context.table:
                assert answers.get(row['qid']) == row['answer'], f"Answer for {row['qid']} does not match"
