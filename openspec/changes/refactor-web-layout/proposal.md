## Why

The current web layout requires mandatory login to access core functionality, which creates a barrier for new users. We need to refactor the layout to allow direct access to features while maintaining user-specific capabilities through optional authentication.

## What Changes

- Remove mandatory login requirement for accessing core functionality
- Directly display features like bot list on the homepage
- Add login button in the top right corner
- Implement personal interface accessible after login
- Add bot binding functionality in the personal interface
- Restructure navigation and layout to support both anonymous and authenticated users

## Capabilities

### New Capabilities
- `anonymous-access`: Allow users to access core features without logging in
- `user-authentication`: Implement optional login system with personal interface
- `bot-management`: Enable bot binding and management in personal interface

### Modified Capabilities

## Impact

- Frontend layout and navigation structure
- Authentication flow and user session management
- Bot management functionality
- User interface components and routing
- Backend API endpoints for anonymous access