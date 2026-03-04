## 1. Backend - User Authentication

- [x] 1.1 Extend User model if needed (add display_name, bio fields)
- [x] 1.2 Create registration API endpoint (POST /api/auth/register/)
- [x] 1.3 Create login API endpoint (POST /api/auth/login/)
- [x] 1.4 Create logout API endpoint (POST /api/auth/logout/)
- [x] 1.5 Configure DRF Token authentication
- [x] 1.6 Write unit tests for auth endpoints

## 2. Backend - Bots App

- [x] 2.1 Create Django app `bots`
- [x] 2.2 Create Bot model (bot_id, nickname, master_id, version, api_key, owner, is_public, status, last_seen, created_at, updated_at)
- [x] 2.3 Create BotSerializer
- [x] 2.4 Create RobotRegistrationView (POST /api/bots/register/) - robot auto registration
- [x] 2.5 Create BotHeartbeatView (POST /api/bots/heartbeat/) - receive heartbeat
- [x] 2.6 Create BotListView (GET /api/bots/) - public for users
- [x] 2.7 Create BotDetailView (GET /api/bots/{id}/)
- [x] 2.8 Create BotUpdateView (PUT /api/bots/{id}/update/) - owner only
- [x] 2.9 Create BotDeleteView (DELETE /api/bots/{id}/delete/) - owner only
- [ ] 2.10 Implement offline detection task
- [ ] 2.11 Add API Key authentication class for robot endpoints
- [ ] 2.12 Write unit tests for Bot CRUD and API endpoints

## 3. Frontend - Auth Pages

- [x] 3.1 Create LoginPage component (existing)
- [x] 3.2 Create RegisterPage component (existing)
- [x] 3.3 Update authStore to handle tokens
- [x] 3.4 Add auth API functions to api.ts

## 4. Frontend - Robot Plaza

- [x] 4.1 Create RobotPlazaPage component
- [x] 4.2 Create RobotCard component
- [x] 4.3 Implement search functionality
- [x] 4.4 Implement status filter (online/offline)
- [x] 4.5 Add pagination
- [x] 4.6 Create RobotDetailPage component

## 5. Frontend - My Robots (Owner Dashboard)

- [x] 5.1 Create MyRobotsPage component
- [x] 5.2 Create RobotFormPage component (create/edit)
- [x] 5.3 Implement create robot functionality
- [x] 5.4 Implement edit robot functionality
- [x] 5.5 Implement delete robot functionality

## 6. Frontend - Integration

- [x] 6.1 Add routes for /robots, /robots/:id, /robots/my, /robots/my/new, /robots/my/edit/:id
- [x] 6.2 Add navigation links
- [x] 6.3 Add ProtectedRoute for authenticated pages
- [x] 6.4 Update DashboardPage to include link to My Robots

## 7. Testing & Polish

- [x] 7.1 Run backend tests
- [x] 7.2 Run frontend build
- [x] 7.3 Manual testing of all flows
- [ ] 7.4 Fix any issues found
