from behave import when, then
import time


@when(u'I create a new project')
def i_create_a_new_project(context):
    b = context.browser
    b.get(context.browser_url("/project/create/"))
    e = b.find_element_by_xpath("//input[@name='name']")
    e.send_keys('new project')
    b.find_element_by_id("id_pub_view_0").click()
    e = b.find_element_by_xpath("//input[@name='target_date']")
    e.send_keys('2020-12-31')
    e.submit()
    context.project_url = b.current_url


@then(u'I am on the list of personnel for the project')
def i_am_on_the_personnel_for_the_project(context):
    """ expects 'project_url' and 'user' in context """
    b = context.browser
    assert b.current_url == context.project_url
    e = b.find_element_by_xpath("//a[@href='#personnel']")
    e.click()

    for a in b.find_elements_by_css_selector(
            "ul li span.personnel a"):
        if a.text == context.user.get_full_name():
            return
    else:
        # made it through without finding the user
        assert False


@then(u'the project has a milestone named "{name}"')
def the_project_has_a_milestone_named(context, name):
    """ expects 'project_url' in context """
    b = context.browser
    assert b.current_url == context.project_url
    e = b.find_element_by_xpath("//a[@href='#milestones']")
    e.click()
    time.sleep(2)  # wait for jquery fade in
    for tr in b.find_elements_by_css_selector("#milestone-table tr")[1:]:
        for link in tr.find_elements_by_tag_name("a"):
            if link.text == name:
                context.milestone_tr = tr
                return

    # didn't find our milestone
    assert False


@then(u'the milestone has target date "{date}"')
def the_milestone_has_a_target_date(context, date):
    tr = context.milestone_tr
    for td in tr.find_elements_by_tag_name('td'):
        if td.text == date:
            return

    assert False


@when(u'I create a new project with final release date "{date}"')
def i_create_a_new_project_with_date(context, date):
    b = context.browser
    b.get(context.browser_url("/project/create/"))
    e = b.find_element_by_xpath("//input[@name='name']")
    e.send_keys('new project')
    b.find_element_by_id("id_pub_view_0").click()
    e = b.find_element_by_xpath("//input[@name='target_date']")
    e.send_keys(date)
    e.submit()
    context.project_url = b.current_url
