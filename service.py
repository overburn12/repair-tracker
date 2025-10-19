"""Database service module for managing database connections and initialization."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database import Base, Status, Assignee, RepairOrder, RepairUnit


class DatabaseService:
    def __init__(self, db_path='files/repair.db'):
        self.db_path = db_path
        self.engine = None
        self.Session = None

    def initialize(self):
        """Initialize database connection and create tables if needed"""
        # Ensure the files directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Check if database exists
        db_exists = os.path.exists(self.db_path)
        
        # Create engine
        self.engine = create_engine(f'sqlite:///{self.db_path}', echo=False)
        
        # Create session factory
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        
        # Create tables if database is new
        if not db_exists:
            self._create_tables()
            self._populate_initial_data()

    def _create_tables(self):
        """Create all tables defined in the database models"""
        Base.metadata.create_all(self.engine)
        print("Database tables created successfully")

    def _populate_initial_data(self):
        """Populate initial required data"""
        session = self.Session()
        try:
            # Add default status
            default_status = Status(status='Backlog')
            session.add(default_status)
            session.commit()
            print("Initial data populated: Default status 'Backlog' created")
        except Exception as e:
            session.rollback()
            print(f"Error populating initial data: {e}")
            raise
        finally:
            session.close()

    def get_session(self):
        """Get a new database session"""
        if self.Session is None:
            raise RuntimeError("Database not initialized. Call initialize() first")
        return self.Session()

    def close(self):
        """Close database connections"""
        if self.Session:
            self.Session.remove()
        if self.engine:
            self.engine.dispose()

    # ============================================================
    # KEY TRANSLATION UTILITIES
    # ============================================================
    
    @staticmethod
    def _parse_key(key):
        """Parse a JIRA-style key like 'RO-123' into prefix and ID"""
        parts = key.split('-')
        if len(parts) != 2:
            raise ValueError(f"Invalid key format: {key}")
        prefix, id_str = parts
        try:
            id_num = int(id_str)
        except ValueError:
            raise ValueError(f"Invalid key format: {key}")
        return prefix, id_num

    @staticmethod
    def _make_key(prefix, id_num):
        """Create a JIRA-style key from prefix and ID"""
        return f"{prefix}-{id_num}"

    # ============================================================
    # CREATE FUNCTIONS
    # ============================================================

    def add_status(self, status_name):
        """Add a new status to the database"""
        session = self.get_session()
        try:
            # Check if status already exists
            existing = session.query(Status).filter(Status.status == status_name).first()
            if existing:
                return {'success': False, 'message': f"Status '{status_name}' already exists"}

            # Create new status
            new_status = Status(status=status_name)
            session.add(new_status)
            session.commit()

            return {
                'success': True,
                'message': f"Status '{status_name}' added successfully",
                'id': new_status.id
            }
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f"Error adding status: {str(e)}"}
        finally:
            session.close()

    def add_assignee(self, assignee_name):
        """Add a new assignee to the database"""
        session = self.get_session()
        try:
            # Check if assignee already exists
            existing = session.query(Assignee).filter(Assignee.name == assignee_name).first()
            if existing:
                return {'success': False, 'message': f"Assignee '{assignee_name}' already exists"}

            # Create new assignee
            new_assignee = Assignee(name=assignee_name)
            session.add(new_assignee)
            session.commit()

            return {
                'success': True,
                'message': f"Assignee '{assignee_name}' added successfully",
                'id': new_assignee.id
            }
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f"Error adding assignee: {str(e)}"}
        finally:
            session.close()

    # ============================================================
    # UPDATE FUNCTIONS
    # ============================================================

    def update_status(self, status_key, new_name):
        """Update a status name by its key (e.g., 'ST-1')"""
        session = self.get_session()
        try:
            # Parse the key
            prefix, status_id = self._parse_key(status_key)

            if prefix != 'ST':
                return {'success': False, 'message': f"Expected ST key, got: {status_key}"}

            # Find the status
            status = session.query(Status).filter(Status.id == status_id).first()
            if not status:
                return {'success': False, 'message': f"Status with key '{status_key}' not found"}

            # Check if new name already exists
            existing = session.query(Status).filter(
                Status.status == new_name,
                Status.id != status_id
            ).first()
            if existing:
                return {'success': False, 'message': f"Status '{new_name}' already exists"}

            # Update the status
            old_name = status.status
            status.status = new_name
            session.commit()

            return {
                'success': True,
                'message': f"Status updated from '{old_name}' to '{new_name}'"
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f"Error updating status: {str(e)}"}
        finally:
            session.close()

    def update_assignee(self, assignee_key, new_name):
        """Update an assignee name by its key (e.g., 'AS-1')"""
        session = self.get_session()
        try:
            # Parse the key
            prefix, assignee_id = self._parse_key(assignee_key)

            if prefix != 'AS':
                return {'success': False, 'message': f"Expected AS key, got: {assignee_key}"}

            # Find the assignee
            assignee = session.query(Assignee).filter(Assignee.id == assignee_id).first()
            if not assignee:
                return {'success': False, 'message': f"Assignee with key '{assignee_key}' not found"}

            # Check if new name already exists
            existing = session.query(Assignee).filter(
                Assignee.name == new_name,
                Assignee.id != assignee_id
            ).first()
            if existing:
                return {'success': False, 'message': f"Assignee '{new_name}' already exists"}

            # Update the assignee
            old_name = assignee.name
            assignee.name = new_name
            session.commit()

            return {
                'success': True,
                'message': f"Assignee updated from '{old_name}' to '{new_name}'"
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f"Error updating assignee: {str(e)}"}
        finally:
            session.close()

    # ============================================================
    # DELETE FUNCTIONS
    # ============================================================

    def delete_status(self, status_key):
        """Delete a status by its key (e.g., 'ST-1')"""
        session = self.get_session()
        try:
            # Parse the key
            prefix, status_id = self._parse_key(status_key)

            if prefix != 'ST':
                return {'success': False, 'message': f"Expected ST key, got: {status_key}"}

            # Find the status
            status = session.query(Status).filter(Status.id == status_id).first()
            if not status:
                return {'success': False, 'message': f"Status with key '{status_key}' not found"}

            # Delete the status
            session.delete(status)
            session.commit()

            return {
                'success': True,
                'message': f"Status '{status.status}' deleted successfully"
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f"Error deleting status: {str(e)}"}
        finally:
            session.close()

    def delete_assignee(self, assignee_key):
        """Delete an assignee by its key (e.g., 'AS-1')"""
        session = self.get_session()
        try:
            # Parse the key
            prefix, assignee_id = self._parse_key(assignee_key)

            if prefix != 'AS':
                return {'success': False, 'message': f"Expected AS key, got: {assignee_key}"}

            # Find the assignee
            assignee = session.query(Assignee).filter(Assignee.id == assignee_id).first()
            if not assignee:
                return {'success': False, 'message': f"Assignee with key '{assignee_key}' not found"}

            # Delete the assignee
            session.delete(assignee)
            session.commit()

            return {
                'success': True,
                'message': f"Assignee '{assignee.name}' deleted successfully"
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f"Error deleting assignee: {str(e)}"}
        finally:
            session.close()

    # ============================================================
    # BULK READ FUNCTIONS
    # ============================================================

    def get_all_statuses(self):
        """Get all statuses as a list of dicts"""
        session = self.get_session()
        try:
            statuses = session.query(Status).all()
            return [
                {
                    'id': s.id,
                    'key': self._make_key('ST', s.id),
                    'status': s.status
                }
                for s in statuses
            ]
        finally:
            session.close()

    def get_all_assignees(self):
        """Get all assignees as a list of dicts"""
        session = self.get_session()
        try:
            assignees = session.query(Assignee).all()
            return [
                {
                    'id': a.id,
                    'key': self._make_key('AS', a.id),
                    'name': a.name
                }
                for a in assignees
            ]
        finally:
            session.close()

    def get_all_repair_orders(self):
        """Get all repair orders as a list of dicts with JIRA-style keys"""
        session = self.get_session()
        try:
            orders = session.query(RepairOrder).all()
            return [
                {
                    'key': self._make_key('RO', ro.id),
                    'name': ro.name,
                    'status': ro.status.status,
                    'status_id': ro.status_id,
                    'created': ro.created.isoformat() if ro.created else None,
                    'received': ro.received.isoformat() if ro.received else None,
                    'finished': ro.finished.isoformat() if ro.finished else None
                }
                for ro in orders
            ]
        finally:
            session.close()

    def get_repair_units_by_order(self, order_key):
        """Get all repair units for a given repair order key (e.g., 'RO-123')"""
        # Parse the order key
        prefix, order_id = self._parse_key(order_key)
        
        if prefix != 'RO':
            raise ValueError(f"Expected RO key, got: {order_key}")
        
        session = self.get_session()
        try:
            # Query all units for this order
            units = session.query(RepairUnit).filter(
                RepairUnit.repair_order_id == order_id
            ).all()
            
            return [
                {
                    'key': self._make_key('RU', ru.id),
                    'serial': ru.serial,
                    'type': ru.type.value if ru.type else None,
                    'current_status': ru.current_status.status if ru.current_status else None,
                    'current_status_id': ru.current_status_id,
                    'current_assignee': ru.current_assignee.name if ru.current_assignee else None,
                    'current_assignee_id': ru.current_assignee_id,
                    'repair_order_key': self._make_key('RO', ru.repair_order_id),
                    'created': ru.created.isoformat() if ru.created else None,
                    'updated_at': ru.updated_at.isoformat() if ru.updated_at else None,
                    'events_json': ru.events_json
                }
                for ru in units
            ]
        finally:
            session.close()


# Global instance
db_service = DatabaseService()


# Convenience function for getting sessions
def get_db_session():
    """Get a database session from the global database service."""
    return db_service.get_session()