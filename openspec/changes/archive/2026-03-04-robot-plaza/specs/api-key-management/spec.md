## ADDED Requirements

### Requirement: Owner can view API Key
The system SHALL allow robot owner to view their robot's API Key.

#### Scenario: View API Key
- **WHEN** authenticated owner requests to view robot's api_key
- **THEN** system returns the api_key

#### Scenario: Non-owner attempts to view API Key
- **WHEN** non-owner requests to view api_key
- **THEN** system returns 403 Forbidden

### Requirement: Owner can regenerate API Key
The system SHALL allow robot owner to regenerate their robot's API Key.

#### Scenario: Regenerate API Key
- **WHEN** authenticated owner requests to regenerate api_key
- **THEN** system generates new api_key
- **AND** invalidates old api_key
- **AND** returns new api_key

#### Scenario: Non-owner attempts to regenerate API Key
- **WHEN** non-owner requests to regenerate api_key
- **THEN** system returns 403 Forbidden

### Requirement: System validates API Key
The system SHALL validate API Key for robot API endpoints.

#### Scenario: Valid API Key
- **WHEN** request includes valid api_key in Authorization header
- **THEN** system authenticates the robot
- **AND** processes the request

#### Scenario: Invalid API Key
- **WHEN** request includes invalid api_key
- **THEN** system returns 401 Unauthorized

#### Scenario: Missing API Key
- **WHEN** request does not include api_key
- **THEN** system returns 401 Unauthorized
