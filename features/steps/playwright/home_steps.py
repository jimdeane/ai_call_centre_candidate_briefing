from behave import given, then
from playwright.sync_api import sync_playwright


@given('the home page is loaded')
def step_impl_home_loaded(context):
    p = sync_playwright().start()
    context.browser = p.chromium.launch()
    context.page = context.browser.new_page()
    context.page.goto("http://localhost:5020/")


@then('the home form should be visible')
def step_impl_home_form_visible(context):
    assert context.page.locator("form").is_visible()
    assert context.page.locator("input[name='qid']").is_visible()
    assert context.page.locator("input[name='session']").is_visible()
    assert context.page.locator("input[name='code']").is_visible()
    context.browser.close()
