from behave import given, when, then
from playwright.sync_api import sync_playwright


@given('the questionnaire page is loaded for session "{session}" and code "{code}" and questionnaire id "{qid}"')
def step_impl_questionnaire_loaded(context, session, code, qid):
    p = sync_playwright().start()
    context.browser = p.chromium.launch()
    context.page = context.browser.new_page()
    context.page.goto(f"http://localhost:5020/questionnaire/{qid}?session={session}&code={code}")


@when('I fill out the questionnaire form with name "{name}" and answers')
def step_impl_fill_questionnaire(context, name):
    context.page.fill('input[name="name"]', name)
    for row in context.table:
        context.page.check(f"input[name='{row['qid']}'][value='{row['answer']}']")


@when('I submit the questionnaire form')
def step_impl_submit_questionnaire(context):
    context.page.click('button[type="submit"]')


@then('I should be redirected to the instructions page')
def step_impl_redirect_instructions(context):
    assert 'instructions' in context.page.url
    context.browser.close()


@then('I should see the results page with retry options')
def step_impl_results_page(context):
    assert context.page.locator('form').is_visible()
    assert context.page.locator('form').inner_text().find('Resubmit Incorrect Answers') != -1
    context.browser.close()
