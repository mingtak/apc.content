# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s apc.content -t test_live_class.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src apc.content.testing.APC_CONTENT_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/apc/content/tests/robot/test_live_class.robot
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

Scenario: As a site administrator I can add a LiveClass
  Given a logged-in site administrator
    and an add Folder form
   When I type 'My LiveClass' into the title field
    and I submit the form
   Then a LiveClass with the title 'My LiveClass' has been created

Scenario: As a site administrator I can view a LiveClass
  Given a logged-in site administrator
    and a LiveClass 'My LiveClass'
   When I go to the LiveClass view
   Then I can see the LiveClass title 'My LiveClass'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Folder form
  Go To  ${PLONE_URL}/++add++Folder

a LiveClass 'My LiveClass'
  Create content  type=Folder  id=my-live_class  title=My LiveClass

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the LiveClass view
  Go To  ${PLONE_URL}/my-live_class
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a LiveClass with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the LiveClass title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
