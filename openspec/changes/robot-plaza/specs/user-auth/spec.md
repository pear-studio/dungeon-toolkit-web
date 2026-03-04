## ADDED Requirements

### Requirement: User can register an account
The system SHALL allow users to register with email and password.

#### Scenario: Successful registration
- **WHEN** user submits valid email and password (min 8 chars)
- **THEN** system creates user account and returns authentication token
- **AND** user is redirected to dashboard

#### Scenario: Duplicate email
- **WHEN** user submits email that already exists
- **THEN** system returns error message "Email already registered"

#### Scenario: Weak password
- **WHEN** user submits password shorter than 8 characters
- **THEN** system returns error message "Password must be at least 8 characters"

### Requirement: User can log in
The system SHALL allow registered users to log in with email and password.

#### Scenario: Successful login
- **WHEN** user submits correct email and password
- **THEN** system returns authentication token
- **AND** user is redirected to dashboard

#### Scenario: Invalid credentials
- **WHEN** user submits wrong email or password
- **THEN** system returns error message "Invalid email or password"

### Requirement: User can log out
The system SHALL allow logged-in users to log out.

#### Scenario: Successful logout
- **WHEN** logged-in user clicks logout button
- **THEN** system clears authentication token from client
- **AND** user is redirected to login page

### Requirement: Authenticated requests
The system SHALL validate authentication token for protected endpoints.

#### Scenario: Request with valid token
- **WHEN** client includes valid Authorization header
- **THEN** system processes the request normally

#### Scenario: Request without token
- **WHEN** client makes request without Authorization header
- **THEN** system returns 401 Unauthorized

#### Scenario: Request with invalid token
- **WHEN** client includes invalid Authorization header
- **THEN** system returns 401 Unauthorized
