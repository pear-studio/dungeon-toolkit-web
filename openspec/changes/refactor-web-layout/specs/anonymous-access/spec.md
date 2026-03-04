## ADDED Requirements

### Requirement: Anonymous users can access core functionality
The system SHALL allow anonymous users to access core functionality without requiring login.

#### Scenario: Anonymous user visits homepage
- **WHEN** an anonymous user navigates to the homepage
- **THEN** the system displays the bot list without prompting for login

### Requirement: Anonymous users can view bot details
The system SHALL allow anonymous users to view bot details and basic information.

#### Scenario: Anonymous user views bot details
- **WHEN** an anonymous user clicks on a bot in the list
- **THEN** the system displays the bot's details page

### Requirement: Anonymous users see login button
The system SHALL display a login button in the top right corner for anonymous users.

#### Scenario: Anonymous user views header
- **WHEN** an anonymous user views any page
- **THEN** the system displays a login button in the top right corner