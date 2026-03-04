## Context

The current web application requires mandatory login to access any functionality, creating a barrier for new users. The goal is to refactor the layout to allow anonymous users to directly access core features while providing authenticated users with additional capabilities like bot binding and management.

## Goals / Non-Goals

**Goals:**
- Remove mandatory login requirement for core functionality
- Directly display bot list on the homepage for anonymous users
- Implement login button in top right corner
- Create personal interface accessible after login
- Add bot binding functionality in personal interface
- Restructure navigation to support both anonymous and authenticated states

**Non-Goals:**
- Completely overhaul the backend API architecture
- Change existing bot functionality beyond binding
- Implement new authentication providers
- Modify data storage or database schema

## Decisions

### 1. Frontend Architecture
- **Decision**: Use client-side routing to handle anonymous vs authenticated views
- **Rationale**: Allows for seamless transitions between states without page reloads, improving user experience
- **Alternative**: Server-side rendering - rejected due to increased complexity and slower response times

### 2. Authentication Flow
- **Decision**: Implement JWT-based authentication with localStorage
- **Rationale**: Stateless authentication that works well with single-page applications
- **Alternative**: Session-based authentication - rejected due to server-side state management complexity

### 3. Layout Structure
- **Decision**: Create a responsive header with conditional elements
- **Rationale**: Provides consistent navigation while adapting to user authentication state
- **Alternative**: Separate header components - rejected due to code duplication

### 4. Bot Binding Implementation
- **Decision**: Use a modal dialog for bot binding process
- **Rationale**: Provides focused user experience without navigating away from the personal interface
- **Alternative**: Dedicated binding page - rejected due to additional navigation steps

## Risks / Trade-offs

### 1. Security Risk
- **Risk**: Anonymous access could lead to abuse of API endpoints
- **Mitigation**: Implement rate limiting and basic validation for anonymous requests

### 2. User Experience Consistency
- **Risk**: Different navigation flows for anonymous vs authenticated users
- **Mitigation**: Maintain consistent UI elements while adapting functionality based on authentication state

### 3. Backend API Changes
- **Risk**: Existing API endpoints may not support anonymous access
- **Mitigation**: Update API endpoints to handle both authenticated and anonymous requests, with appropriate permission checks

### 4. Performance Impact
- **Risk**: Additional client-side logic for authentication state management
- **Mitigation**: Optimize state management and use efficient routing strategies