# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s apc.content -t test_course.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src apc.content.testing.APC_CONTENT_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot src/plonetraining/testing/tests/robot/test_course.robot
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

Scenario: As a site administrator I can add a Course
  Given a logged-in site administrator
    and an add Course form
   When I type 'My Course' into the title field
    and I submit the form
   Then a Course with the title 'My Course' has been created

Scenario: As a site administrator I can view a Course
  Given a logged-in site administrator
    and a Course 'My Course'
   When I go to the Course view
   Then I can see the Course title 'My Course'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Course form
  Go To  ${PLONE_URL}/++add++Course

a Course 'My Course'
  Create content  type=Course  id=my-course  title=My Course


# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form-widgets-IBasic-title  ${title}

I submit the form
  Click Button  Save

I go to the Course view
  Go To  ${PLONE_URL}/my-course
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Course with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Course title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
