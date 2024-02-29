Feature: Running the application for the first time generates default configuration
  Scenario: Generate the default config
    Given the current directory does not contain the directory .smol
    When the application is started
    Then the file .smol/config.ini exists
