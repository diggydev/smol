Feature: running smol for the first time
  Scenario: generate the default config
    Given there is no config directory at .smol
    When I launch smol
    Then the file .smol/config.toml exists
#    """
#    [files]
#
#    """
#    And ~/.smol/index_template.gmi exists
#    And ~/.smol/posts.tsv exists
#
