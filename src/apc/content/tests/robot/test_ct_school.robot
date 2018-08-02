# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s apc.content -t test_school.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src apc.content.testing.APC_CONTENT_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/apc/content/tests/robot/test_school.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a School
  Given a logged-in site administrator
    and an add School form
   When I type 'My School' into the title field
    and I submit the form
   Then a School with the title 'My School' has been created

Scenario: As a site administrator I can view a School
  Given a logged-in site administrator
    and a School 'My School'
   When I go to the School view
   Then I can see the School title 'My School'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add School form
  Go To  ${PLONE_URL}/++add++School

a School 'My School'
  Create content  type=School  id=my-school  title=My School

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the School view
  Go To  ${PLONE_URL}/my-school
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a School with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the School title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
