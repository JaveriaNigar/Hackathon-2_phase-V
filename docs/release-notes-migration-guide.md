# Release Notes and Migration Guide
## Advanced Todo Features v1.0

### Release Overview
This release introduces Advanced Todo Features including recurring tasks, reminders, priorities, tags, search, filter, sort, and event-driven architecture. This document provides release notes and a migration guide for upgrading to this version.

### New Features

#### 1. Recurring Tasks
- **Feature**: Tasks can now be configured to recur based on daily, weekly, monthly, or yearly patterns
- **API Endpoint**: `POST /api/{user_id}/tasks/{id}/schedule-recurrence`
- **Implementation**: When a recurring task is completed, the system automatically creates the next occurrence with preserved metadata (title, tags, priority, due date)
- **Data Model**: Added `recurrence_pattern` and `next_occurrence` fields to the Task entity

#### 2. Reminders and Due Dates
- **Feature**: Tasks with due dates now trigger reminder notifications
- **API Endpoint**: `GET /api/{user_id}/notifications`
- **Implementation**: Notification service consumes reminder events and delivers notifications at the correct time
- **Data Model**: Added Notification entity with scheduling and delivery tracking

#### 3. Priorities, Tags, Search, Filter, Sort
- **Feature**: Enhanced task management with priorities, tags, and advanced search/filtering
- **API Endpoints**: 
  - `GET /api/{user_id}/tasks` (with filtering and sorting)
  - `GET /api/{user_id}/tasks/search`
- **Implementation**: Tasks can now have priority levels (low, medium, high) and tags for categorization
- **Search**: Full-text search across title, description, and tags
- **Filter**: Filter by priority, status, and tags
- **Sort**: Sort by due date, priority, creation date, title, and status

#### 4. Event-Driven Architecture
- **Feature**: All operations now communicate via events instead of direct API calls
- **Implementation**: Kafka topics (`task-events`, `reminders`, `task-updates`) for pub/sub messaging
- **Benefits**: Improved scalability, decoupling, and resilience
- **Events Published**: `task.created`, `task.updated`, `task.completed`, `task.deleted`

#### 5. Natural Language Communication
- **Feature**: Agent responds in human-like English or Roman Urdu
- **Implementation**: Natural language processing for human-like communication
- **Benefits**: Clear, polite, and understandable responses

### Breaking Changes

#### 1. Task Model Updates
- The Task model now includes additional fields:
  - `priority` (enum: low, medium, high)
  - `status` (enum: active, completed, archived)
  - `tags` (JSON array of strings)
  - `recurrence_pattern` (JSON object)
  - `next_occurrence` (datetime)
- Default values: `priority` defaults to "medium", `status` defaults to "active"

#### 2. API Response Changes
- Task responses now include the new fields mentioned above
- The `/tasks` endpoint now supports additional query parameters:
  - `status`, `priority`, `tag` for filtering
  - `sort`, `order` for sorting
  - `page`, `limit` for pagination

#### 3. Authentication Updates
- All endpoints now require proper JWT authentication
- User context is validated for all operations

### Migration Guide

#### 1. Database Migration
Before deploying the new version, run the database migration:

```bash
cd backend
alembic upgrade head
```

This will update your database schema to include the new fields in the Task table and create the Notification table.

#### 2. Configuration Updates
Update your environment variables to include new configuration options:

```env
# Kafka Configuration
KAFKA_BROKER=localhost:9092

# Dapr Configuration
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001

# Notification Settings
NOTIFICATION_EMAIL_HOST=smtp.gmail.com
NOTIFICATION_EMAIL_PORT=587
NOTIFICATION_EMAIL_USER=your-email@example.com
NOTIFICATION_EMAIL_PASSWORD=your-email-password

# AI Integration
GEMINI_API_KEY=your-gemini-api-key
```

#### 3. Service Dependencies
Ensure the following services are running:
- Apache Kafka (for event streaming)
- Dapr (for service mesh and component abstraction)
- PostgreSQL (for persistent data storage)

#### 4. API Migration
##### Updating Task Creation
Old code:
```javascript
const task = {
  title: "My Task",
  description: "Task description"
};
```

New code:
```javascript
const task = {
  title: "My Task",
  description: "Task description",
  priority: "medium",  // New required field
  status: "active",    // New required field
  tags: ["work", "important"],  // New optional field
  recurrence_pattern: {  // New optional field
    type: "weekly",
    interval: 1,
    end_condition: {
      type: "after_n_occurrences",
      value: 4
    }
  }
};
```

##### Updating Task Retrieval
Old code:
```javascript
fetch('/api/{user_id}/tasks')
  .then(response => response.json())
  .then(tasks => console.log(tasks));
```

New code (with filtering and sorting):
```javascript
// With filtering
fetch('/api/{user_id}/tasks?status=active&priority=high')
  .then(response => response.json())
  .then(tasks => console.log(tasks));

// With sorting
fetch('/api/{user_id}/tasks?sort=due_date&order=asc')
  .then(response => response.json())
  .then(tasks => console.log(tasks));

// With pagination
fetch('/api/{user_id}/tasks?page=0&limit=10')
  .then(response => response.json())
  .then(tasks => console.log(tasks));
```

#### 5. Event System Integration
If your application has custom integrations, ensure they are compatible with the event-driven architecture:
- Listen to Kafka topics for task events instead of polling the API
- Handle `task.created`, `task.updated`, `task.completed`, and `task.deleted` events
- Update your services to publish events to the appropriate Kafka topics

### Performance Improvements
- Added database indexes for priority, tags, and due_date fields
- Implemented caching for frequently accessed data
- Optimized queries with proper filtering and pagination
- Improved response times for search operations

### Security Enhancements
- Enhanced authentication and authorization
- Input validation and sanitization
- Protection against prompt injection attacks in AI interactions
- Secure handling of API keys and credentials

### Known Issues
- Large tag arrays may impact search performance
- Recurring tasks with complex patterns may have scheduling delays in high-load scenarios
- Notification delivery may be delayed during peak usage periods

### Upgrade Steps
1. Backup your current database
2. Update your application code to the new version
3. Run database migrations
4. Update environment configuration
5. Deploy the new services
6. Test all functionality with a subset of users
7. Monitor system performance and event flow
8. Gradually roll out to all users

### Rollback Plan
If issues arise after deployment:
1. Stop the new services
2. Revert to the previous application version
3. If needed, rollback database changes with:
   ```bash
   alembic downgrade -1
   ```
4. Restart the previous version of services

### Support
For issues with the migration or new features:
- Check the API documentation at `/docs/api-documentation.md`
- Review the system logs for error details
- Contact the development team for assistance

### Version Compatibility
- This release is compatible with Python 3.13+
- Requires FastAPI 0.115.0 or later
- Requires SQLModel 0.0.22 or later
- Requires Dapr runtime for event-driven functionality