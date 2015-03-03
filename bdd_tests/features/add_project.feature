Feature: add a new project

As a project manager
I want to be able to create a new Project
in order to isolate a set of items/milestones from other projects.

  Scenario: I am in personnel
    Given I am logged in
    When I create a new project
    Then I am on the list of personnel for the project

  Scenario: Final Release Milestone is automatically created
    Given I am logged in
    When I create a new project with final release date "2020-01-01"
    Then the project has a milestone named "Final Release"
     And the milestone has target date "2020-01-01"

  Scenario: Someday/Maybe Milestone is automatically created
    Given I am logged in
    When I create a new project
    Then the project has a milestone named "Someday/Maybe"
