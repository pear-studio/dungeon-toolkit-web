## ADDED Requirements

### Requirement: Robot can register via API
The system SHALL allow DicePP robots to register themselves via HTTP API.

#### Scenario: Successful robot registration
- **WHEN** robot sends POST request to `/api/bots/register` with bot_id, nickname, master_id, version
- **THEN** system creates bot record
- **AND** generates and returns api_key
- **AND** returns bot_id in response

#### Scenario: Robot re-registration (update)
- **WHEN** robot sends POST request with existing bot_id
- **THEN** system updates bot information
- **AND** generates new api_key
- **AND** returns new api_key

#### Scenario: Registration with invalid data
- **WHEN** robot sends registration request with missing required fields
- **THEN** system returns 400 Bad Request with error message

### Requirement: Robot sends heartbeat
The system SHALL receive heartbeat requests from registered robots to maintain online status.

#### Scenario: Valid heartbeat
- **WHEN** registered robot sends POST request to `/api/bots/heartbeat` with valid api_key
- **THEN** system updates bot's last_seen timestamp
- **AND** marks bot as online

#### Scenario: Heartbeat with invalid api_key
- **WHEN** robot sends heartbeat with invalid or missing api_key
- **THEN** system returns 401 Unauthorized

#### Scenario: Robot offline detection
- **WHEN** bot has not sent heartbeat for more than 5 minutes
- **THEN** system marks bot as offline

### Requirement: User can manually register a robot
The system SHALL allow authenticated users to manually register their DicePP robot.

#### Scenario: Successful manual registration
- **WHEN** authenticated user submits robot name, QQ number, description
- **THEN** system creates robot record linked to the user
- **AND** returns robot details

#### Scenario: Duplicate QQ number
- **WHEN** user submits QQ number that already exists in system
- **THEN** system returns error message "This QQ number is already registered"

#### Scenario: Unauthorized edit attempt
- **WHEN** non-owner attempts to edit robot
- **THEN** system returns 403 Forbidden

#### Scenario: Unauthorized delete attempt
- **WHEN** non-owner attempts to delete robot
- **THEN** system returns 403 Forbidden
