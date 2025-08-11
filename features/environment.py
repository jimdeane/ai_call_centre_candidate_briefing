def before_all(context):
    # Called before all tests
    context.config.setup_logging()
    print("[behave] Test environment setup.")


def after_all(context):
    # Called after all tests
    print("[behave] Test environment teardown.")


def before_scenario(context, scenario):
    print(f"[behave] Starting scenario: {scenario.name}")


def after_scenario(context, scenario):
    print(f"[behave] Finished scenario: {scenario.name}")
