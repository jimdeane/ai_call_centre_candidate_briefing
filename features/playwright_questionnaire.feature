Feature: Questionnaire submission via Playwright

    Scenario: Submit correct answers to questionnaire
    Given the questionnaire page is loaded for session "session1" and code "supersecretadmincode" and questionnaire id "1"
    When I fill out the questionnaire form with name "Test User" and answers
        | qid | answer   |
        | q1  | Option A |
        | q2  | Option B |
    When I submit the questionnaire form
    Then I should be redirected to the instructions page

    Scenario: Submit incorrect answers to questionnaire
    Given the questionnaire page is loaded for session "session2" and code "supersecretadmincode" and questionnaire id "1"
    When I fill out the questionnaire form with name "Test User" and answers
        | qid | answer   |
        | q1  | Option B |
        | q2  | Option A |
    When I submit the questionnaire form
    Then I should see the results page with retry options
