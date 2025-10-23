# Repair Tracker

A web-based application for tracking and managing repair orders for machines and hashboards. This system provides a comprehensive workflow for managing repair statuses, assignments, and timelines.

## Features

- **Repair Order Management**: Create and track repair orders with multiple repair units
- **Unit Tracking**: Monitor individual machines and hashboards through their repair lifecycle
- **Status Management**: Configurable status workflow for tracking repair progress
- **Assignee Management**: Assign repairs to team members and track responsibility
- **Timeline Visualization**: View repair history and events with Chart.js visualizations
- **RESTful API**: JSON API for all operations
- **Dark Theme UI**: Modern, responsive dark-themed interface

## Tech Stack

- **Backend**: Python Flask
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Frontend**: HTML, JavaScript, Chart.js
- **Templating**: Jinja2

## Project Structure

```
repair-tracker/
├── app.py              # Flask application and routes
├── service.py          # Business logic and database service layer
├── database.py         # SQLAlchemy models and schema definitions
├── templates/          # HTML templates
│   ├── base.html       # Base template with common layout
│   ├── index.html      # Main page listing all repair orders
│   ├── order.html      # Individual repair order details
│   ├── repair.html     # Individual repair unit details
│   └── settings.html   # Settings for statuses and assignees
├── files/
│   └── timeline.js     # Timeline formatting for Chart.js
└── static/             # Static assets (CSS, images, etc.)
```

## Database Schema

### Tables

- **repair_orders**: Tracks repair orders with name, status, dates (created, received, finished)
- **repair_units**: Individual machines or hashboards with serial numbers, status, assignee, and event history
- **statuses**: Configurable repair status options
- **assignees**: Team members who can be assigned repair work

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd repair-tracker
```

2. Install Python dependencies:
```bash
pip install flask sqlalchemy psycopg2-binary
```

3. Set up PostgreSQL database and configure connection in `service.py`

4. Initialize the database schema:
```python
python -c "from database import Base; from sqlalchemy import create_engine; engine = create_engine('your-db-url'); Base.metadata.create_all(engine)"
```

5. Run the application:
```bash
python app.py
```

## API Endpoints

### Repair Orders
- `GET /api/repair-orders` - List all repair orders
- `POST /api/add-repair-order` - Create new repair order
- `GET /api/repair-order/<key>` - Get order details
- `PUT /api/update-order/<key>` - Update order information
- `DELETE /api/delete-order/<key>` - Delete order

### Repair Units
- `GET /api/repair-units/<order_key>` - List units for an order
- `POST /api/add-unit/<order_key>` - Add unit to order
- `GET /api/repair-unit/<unit_key>` - Get unit details
- `PUT /api/update-unit/<unit_key>` - Update unit information
- `DELETE /api/delete-unit/<unit_key>` - Delete unit

### Configuration
- `GET /api/statuses` - List all statuses
- `POST /api/add-status` - Create new status
- `PUT /api/update-status/<key>` - Update status
- `DELETE /api/delete-status/<key>` - Delete status
- `GET /api/assignees` - List all assignees
- `POST /api/add-assignee` - Create new assignee
- `PUT /api/update-assignee/<key>` - Update assignee
- `DELETE /api/delete-assignee/<key>` - Delete assignee

## Usage

1. **Configure Settings**: Add statuses and assignees in the settings page
2. **Create Repair Order**: Add a new repair order from the main page
3. **Add Units**: Add machines or hashboards to the repair order
4. **Track Progress**: Update unit status and assignee as repairs progress
5. **View Timeline**: Monitor repair events and history on unit pages

## Key Components

### formatTimelineForChartjs (files/timeline.js:311)
Formats repair unit event data for Chart.js timeline visualization, converting event history into chart-compatible format.

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
