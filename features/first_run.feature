Feature: running smol for the first time
  Scenario: generate the default config
    Given there is no config directory at ~/.smol
    When I launch smol
    Then ~/.smol/config.toml has content
    """
    [files]
    
    """
    And ~/.smol/index_template.gmi exists
    And ~/.smol/posts.tsv exists
    
