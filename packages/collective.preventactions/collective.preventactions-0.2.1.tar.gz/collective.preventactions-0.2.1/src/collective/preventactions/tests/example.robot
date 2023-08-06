*** Settings ***
Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Suite Setup  Suite Setup
Suite Teardown  Close all browsers


*** Test Cases ***
Site Administrator can view homepage
    Go to homepage
    Page should contain  collective.preventactions


*** Keywords ***
Suite Setup
    Open test browser
    Enable autologin as  Site Administrator
