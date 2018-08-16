# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s apc.content -t test_prepare.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src apc.content.testing.APC_CONTENT_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot src/plonetraining/testing/tests/robot/test_prepare.robot
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

Scenario: As a site administrator I can add a Prepare
  Given a logged-in site administrator
    and an add Prepare form
   When I type 'My Prepare' into the title field
    and I submit the form
   Then a Prepare with the title 'My Prepare' has been created

Scenario: As a site administrator I can view a Prepare
  Given a logged-in site administrator
    and a Prepare 'My Prepare'
   When I go to the Prepare view
   Then I can see the Prepare title 'My Prepare'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Prepare form
  Go To  ${PLONE_URL}/++add++Prepare

a Prepare 'My Prepare'
  Create content  type=Prepare  id=my-prepare  title=My Prepare


# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form-widgets-IBasic-title  ${title}

I submit the form
  Click Button  Save

I go to the Prepare view
  Go To  ${PLONE_URL}/my-prepare
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Prepare with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Prepare title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
