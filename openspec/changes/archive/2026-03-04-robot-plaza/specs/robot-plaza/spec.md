## ADDED Requirements

### Requirement: User can view robot list
The system SHALL display a list of all public robots.

#### Scenario: View robot list
- **WHEN** user visits robot plaza page
- **THEN** system displays paginated list of public robots
- **AND** each robot shows name, QQ, description, online status

### Requirement: User can search robots
The system SHALL allow users to search robots by name or description.

#### Scenario: Search by name
- **WHEN** user enters search term in search box
- **THEN** system filters robots matching the search term in name or description

#### Scenario: No results
- **WHEN** search yields no matching robots
- **THEN** system displays "No robots found" message

### Requirement: User can filter robots
The system SHALL allow users to filter robots by online status.

#### Scenario: Filter by online status
- **WHEN** user selects online/offline filter
- **THEN** system shows only robots matching the selected status

### Requirement: Robot can fetch online robot list
The system SHALL provide an API endpoint for registered robots to fetch online robot list.

#### Scenario: Robot fetches online robot list
- **WHEN** registered robot sends GET request to `/api/bots/` with valid api_key
- **THEN** system returns list of all online bots
- **AND** each bot includes: nickname, bot_id, online status, version

#### Scenario: Fetch list without api_key
- **WHEN** request is made without valid api_key
- **THEN** system returns 401 Unauthorized
