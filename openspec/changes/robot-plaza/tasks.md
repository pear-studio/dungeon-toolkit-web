## 1. Backend - User Authentication

- [ ] 1.1 Extend User model if needed (add display_name, bio fields)
- [ ] 1.2 Create registration API endpoint (POST /api/auth/register/)
- [ ] 1.3 Create login API endpoint (POST /api/auth/login/)
- [ ] 1.4 Create logout API endpoint (POST /api/auth/logout/)
- [ ] 1.5 Configure DRF Token authentication
- [ ] 1.6 Write unit tests for auth endpoints

## 2. Backend - Bots App (Robot Management)

- [ ] 2.1 Create Django app `bots`
- [ ] 2.2 Create Bot model (bot_id, nickname, master_id, version, api_key, is_public, status, last_seen, created_at, updated_at)
- [ ] 2.3 Create BotSerializer
- [ ] 2.4 Create BotRegistrationView (POST /api/bots/register) - robot auto registration
- [ ] 2.5 Create BotHeartbeatView (POST /api/bots/heartbeat) - receive heartbeat
- [ ] 2.6 Create BotListView (GET /api/bots/) - public for users, authenticated for robots
- [ ] 2.7 Create BotDetailView (GET /api/bots/{id}/)
- [ ] 2.8 Create BotUpdateView (PUT /api/bots/{id}/) - owner only
- [ ] 2.9 Create BotDeleteView (DELETE /api/bots/{id}/) - owner only
- [ ] 2.10 Implement offline detection task (Celerybeat or Django management command)
- [ ] 2.11 Add API Key authentication class for robot endpoints
- [ ] 2.12 Write unit tests for Bot CRUD and API endpoints

## 3. Frontend - Auth Pages

- [ ] 3.1 Create LoginPage component
- [ ] 3.2 Create RegisterPage component
- [ ] 3.3 Update authStore to handle tokens
- [ ] 3.4 Add auth API functions to api.ts

## 4. Frontend - Robot Plaza

- [ ] 4.1 Create RobotPlazaPage component
- [ ] 4.2 Create RobotCard component
- [ ] 4.3 Implement search functionality
- [ ] 4.4 Implement status filter (online/offline)
- [ ] 4.5 Add pagination
- [ ] 4.6 Create RobotDetailPage component

## 5. Frontend - My Robots (Owner Dashboard)

- [ ] 5.1 Create MyRobotsPage component
- [ ] 5.2 Create RobotForm component (create/edit)
- [ ] 5.3 Implement create robot functionality
- [ ] 5.4 Implement edit robot functionality
- [ ] 5.5 Implement delete robot functionality

## 6. Frontend - Integration

- [ ] 6.1 Add routes for /robots, /robots/:id, /robots/my, /robots/new
- [ ] 6.2 Add navigation links
- [ ] 6.3 Add ProtectedRoute for authenticated pages
- [ ] 6.4 Update DashboardPage to include link to My Robots

## 7. Testing & Polish

- [ ] 7.1 Run backend tests
- [ ] 7.2 Run frontend build
- [ ] 7.3 Manual testing of all flows
- [ ] 7.4 Fix any issues found
