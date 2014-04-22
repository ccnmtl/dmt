Feature: Index Page

Just some simple sanity checks on the index page of the application
This also serves as a good test that the behave
stuff is all hooked up properly and running.

    Scenario: Index Page Load
        Given I am not logged in
        When I access the url "/"
        Then I see the navbar
