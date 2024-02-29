Feature: Posting from email
  Scenario: View the list of available emails
    Given the email inbox contains emails from the author
    And the application is at the main menu
    When the site administrator chooses "new post from email"
    Then the emails from the author are displayed

#  Scenario: Select an email to use as a new post
#    Given the application is at the email selection menu
#    When the site administrator chooses an email
#    And the site administrator enters a publication date
#    And the site administrator chooses tags
#    Then the new post is created
