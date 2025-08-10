Feature: Questionnaire submission
    As a candidate
    I want to submit answers to a questionnaire
    So that my answers are recorded in the database

Scenario: Submit partial answers to a questionnaire
    Given the Flask app is running
    And a valid session id "testsession" and code "supersecretadmincode" and questionnaire id "1"
    When I submit answers to some questions
        | qid      | answer   |
        | q1       | Option A |
        | q2       | Option B |
    Then the database should contain a submission for session "testsession" with those answers
