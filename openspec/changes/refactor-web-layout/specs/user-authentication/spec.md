## ADDED Requirements

### Requirement: Users can log in
The system SHALL allow users to log in using their credentials.

#### Scenario: User logs in successfully
- **WHEN** a user enters valid credentials and clicks login
- **THEN** the system authenticates the user and redirects to the homepage

### Requirement: Users can log out
The system SHALL allow authenticated users to log out.

#### Scenario: User logs out
- **WHEN** an authenticated user clicks the logout button
- **THEN** the system clears the user's session and redirects to the homepage

### Requirement: Authenticated users see personal interface
The system SHALL display a personal interface link for authenticated users.

#### Scenario: Authenticated user views header
- **WHEN** an authenticated user views any page
- **THEN** the system displays a personal interface link in the top right corner instead of the login button

### Requirement: Users can access personal interface
The system SHALL allow authenticated users to access their personal interface.

#### Scenario: User accesses personal interface
- **WHEN** an authenticated user clicks the personal interface link
- **THEN** the system displays the user's personal interface page