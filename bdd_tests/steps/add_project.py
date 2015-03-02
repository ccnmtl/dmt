from behave import when, then


@when(u'I create a new project')
def i_create_a_new_project(context):
    context.browser.visit(context.browser_url("/project/create/"))
    context.browser.fill('name', 'new project')
    context.browser.choose('pub_view', 'true')
    context.browser.fill('target_date', '2020-12-31')
    context.browser.find_by_value('Save project').first.click()
    context.project_url = context.browser.url


@then(u'I am on the list of personnel for the project')
def i_am_on_the_personnel_for_the_project(context):
    """ expects 'project_url' and 'user' in context """
    context.browser.visit(context.project_url)
    context.browser.find_link_by_text("Personnel").first.click()
    for a in context.browser.find_by_css("ul li span.personnel a"):
        if a.text == context.user.get_full_name():
            return
    else:
        # made it through without finding the user
        assert False


@then(u'the project has a milestone named "{name}"')
def the_project_has_a_milestone_named(context, name):
    """ expects 'project_url' in context """
    context.browser.visit(context.project_url)
    context.browser.find_link_by_text("Milestones").first.click()
    for tr in context.browser.find_by_css("#milestone-table tr"):
        for link in tr.find_by_tag('a'):
            if link.html == name or link.text == name:
                context.milestone_tr = tr
                return
    # didn't find our milestone
    assert False


@then(u'the milestone has target date "{date}"')
def the_milestone_has_a_target_date(context, date):
    tr = context.milestone_tr
    assert "<td>" + date + "</td>" in tr.html


@when(u'I create a new project with final release date "{date}"')
def i_create_a_new_project_with_date(context, date):
    context.browser.visit(context.browser_url("/project/create/"))
    context.browser.fill('name', 'new project')
    context.browser.choose('pub_view', 'true')
    context.browser.fill('target_date', date)
    context.browser.find_by_value('Save project').first.click()
    context.project_url = context.browser.url
