# Robot Detail

## Purpose

This spec defines the robot detail viewing functionality.

## Requirements

### Requirement: User can view robot details
The system SHALL display detailed information about a robot.

#### Scenario: View robot details
- **WHEN** user clicks on a robot in the plaza
- **THEN** system displays robot detail page
- **AND** shows name, QQ, description, owner, online status, registration date

### Requirement: User can view robot owner profile
The system SHALL allow users to view the robot owner's profile.

#### Scenario: View owner profile
- **WHEN** user clicks on owner name in robot detail
- **THEN** system displays owner's public profile
- **AND** shows list of all robots owned by this user
