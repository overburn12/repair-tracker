"""Database service module for managing database connections and initialization."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from database import Base, Status, Assignee, RepairOrder, RepairUnit, UnitType


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

    def add_repair_order(self, order_name):
        """Add a new repair order to the database"""
        session = self.get_session()
        try:
            # Get the first status (default status)
            default_status = session.query(Status).order_by(Status.id).first()
            if not default_status:
                return {'success': False, 'message': 'No default status found. Please create a status first.'}

            # Create new repair order
            new_order = RepairOrder(
                name=order_name,
                status_id=default_status.id
            )
            session.add(new_order)
            session.commit()

            # Generate the key for the response
            order_key = self._make_key('RO', new_order.id)

            return {
                'success': True,
                'message': f"Repair order '{order_name}' added successfully with key {order_key}",
                'id': new_order.id,
                'key': order_key
            }
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f"Error adding repair order: {str(e)}"}
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

    def update_repair_order(self, order_key, **fields):
        """Update repair order fields by its key (e.g., 'RO-1')

        Accepts any combination of fields:
        - name: str
        - status_id: int
        - summary: str or None
        - received: datetime string (ISO format) or None
        - finished: datetime string (ISO format) or None
        """
        session = self.get_session()
        try:
            # Parse the key
            prefix, order_id = self._parse_key(order_key)

            if prefix != 'RO':
                return {'success': False, 'message': f"Expected RO key, got: {order_key}"}

            # Find the order
            order = session.query(RepairOrder).filter(RepairOrder.id == order_id).first()
            if not order:
                return {'success': False, 'message': f"Repair order with key '{order_key}' not found"}

            # Track what was updated
            updates = []

            # Update name if provided
            if 'name' in fields:
                order.name = fields['name']
                updates.append('name')

            # Update status if provided
            if 'status_id' in fields:
                # Verify status exists
                status = session.query(Status).filter(Status.id == fields['status_id']).first()
                if not status:
                    return {'success': False, 'message': f"Status ID {fields['status_id']} not found"}
                order.status_id = fields['status_id']
                updates.append('status')

            # Update summary if provided
            if 'summary' in fields:
                order.summary = fields['summary']
                updates.append('summary')

            # Update received date if provided
            if 'received' in fields:
                if fields['received']:
                    from datetime import datetime
                    order.received = datetime.fromisoformat(fields['received'])
                else:
                    order.received = None
                updates.append('received')

            # Update finished date if provided
            if 'finished' in fields:
                if fields['finished']:
                    from datetime import datetime
                    order.finished = datetime.fromisoformat(fields['finished'])
                else:
                    order.finished = None
                updates.append('finished')

            if not updates:
                return {'success': False, 'message': 'No fields provided to update'}

            session.commit()

            return {
                'success': True,
                'message': f"Repair order '{order_key}' updated successfully. Fields: {', '.join(updates)}"
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f"Error updating repair order: {str(e)}"}
        finally:
            session.close()

    def update_repair_unit(self, unit_key, **fields):
        """Update repair unit fields by its key (e.g., 'RU-1423')

        Accepts any combination of fields:
        - serial: str
        - type: str ('machine' or 'hashboard')
        - current_status_id: int
        - current_assignee_id: int or None
        """
        session = self.get_session()
        try:
            # Parse the key
            prefix, unit_id = self._parse_key(unit_key)

            if prefix != 'RU':
                return {'success': False, 'message': f"Expected RU key, got: {unit_key}"}

            # Find the repair unit
            unit = session.query(RepairUnit).filter(RepairUnit.id == unit_id).first()
            if not unit:
                return {'success': False, 'message': f"Repair unit with key '{unit_key}' not found"}

            # Track what was updated
            updates = []

            # Update serial if provided
            if 'serial' in fields:
                unit.serial = fields['serial']
                updates.append('serial')

            # Update type if provided
            if 'type' in fields:
                if fields['type'] not in ['machine', 'hashboard']:
                    return {'success': False, 'message': f"Invalid unit type: {fields['type']}. Must be 'machine' or 'hashboard'"}
                unit.type = UnitType(fields['type'])
                updates.append('type')

            # Update status if provided
            if 'current_status_id' in fields:
                # Verify status exists
                status = session.query(Status).filter(Status.id == fields['current_status_id']).first()
                if not status:
                    return {'success': False, 'message': f"Status ID {fields['current_status_id']} not found"}
                unit.current_status_id = fields['current_status_id']
                updates.append('status')

            # Update assignee if provided
            if 'current_assignee_id' in fields:
                if fields['current_assignee_id'] is not None:
                    # Verify assignee exists
                    assignee = session.query(Assignee).filter(Assignee.id == fields['current_assignee_id']).first()
                    if not assignee:
                        return {'success': False, 'message': f"Assignee ID {fields['current_assignee_id']} not found"}
                unit.current_assignee_id = fields['current_assignee_id']
                updates.append('assignee')

            if not updates:
                return {'success': False, 'message': 'No fields provided to update'}

            session.commit()

            return {
                'success': True,
                'message': f"Repair unit '{unit_key}' updated successfully. Fields: {', '.join(updates)}"
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f"Error updating repair unit: {str(e)}"}
        finally:
            session.close()

    def add_event_to_repair_unit(self, unit_key, event_type, assignee_key, comment=None, status_name=None, components=None):
        """Add an event to a repair unit's events_json field.

        Args:
            unit_key: The repair unit key (e.g., 'RU-1423')
            event_type: Type of event ('comment', 'status', or 'repair')
            assignee_key: The assignee key (e.g., 'AS-1')
            comment: Comment text (for 'comment' and 'repair' events)
            status_name: Status name (for 'status' events)
            components: List of component codes (for 'repair' events)

        Returns:
            dict with success status and message
        """
        import json
        from datetime import datetime

        session = self.get_session()
        try:
            # Parse the unit key
            prefix, unit_id = self._parse_key(unit_key)

            if prefix != 'RU':
                return {'success': False, 'message': f"Expected RU key, got: {unit_key}"}

            # Parse the assignee key
            assignee_prefix, assignee_id = self._parse_key(assignee_key)
            if assignee_prefix != 'AS':
                return {'success': False, 'message': f"Expected AS key for assignee, got: {assignee_key}"}

            # Find the repair unit
            unit = session.query(RepairUnit).filter(RepairUnit.id == unit_id).first()
            if not unit:
                return {'success': False, 'message': f"Repair unit with key '{unit_key}' not found"}

            # Find the assignee
            assignee = session.query(Assignee).filter(Assignee.id == assignee_id).first()
            if not assignee:
                return {'success': False, 'message': f"Assignee with key '{assignee_key}' not found"}

            # Parse existing events_json or create new structure
            if unit.events_json:
                try:
                    events_data = json.loads(unit.events_json)
                except json.JSONDecodeError:
                    events_data = {"events": []}
            else:
                events_data = {"events": []}

            # Create the new event
            timestamp = datetime.now().isoformat()
            new_event = {
                "type": event_type,
                "assignee": assignee.name,
                "timestamp": timestamp
            }

            # Add event-specific fields
            if event_type == 'comment':
                new_event['comment'] = comment or ''
            elif event_type == 'status':
                new_event['status'] = status_name or ''
            elif event_type == 'repair':
                new_event['comment'] = comment or ''
                new_event['components'] = components or []

            # Append the new event
            events_data['events'].append(new_event)

            # Update the repair unit
            unit.events_json = json.dumps(events_data)
            session.commit()

            return {
                'success': True,
                'message': f"Event added to repair unit '{unit_key}'"
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f"Error adding event: {str(e)}"}
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

    def delete_repair_order(self, order_key):
        """Delete a repair order by its key (e.g., 'RO-1')"""
        session = self.get_session()
        try:
            # Parse the key
            prefix, order_id = self._parse_key(order_key)

            if prefix != 'RO':
                return {'success': False, 'message': f"Expected RO key, got: {order_key}"}

            # Find the order
            order = session.query(RepairOrder).filter(RepairOrder.id == order_id).first()
            if not order:
                return {'success': False, 'message': f"Repair order with key '{order_key}' not found"}

            # Check if there are any repair units linked to this order
            unit_count = session.query(RepairUnit).filter(RepairUnit.repair_order_id == order_id).count()
            if unit_count > 0:
                return {
                    'success': False,
                    'message': f"Cannot delete order '{order_key}'. It has {unit_count} repair unit(s) linked to it. Please delete or reassign the units first."
                }

            # Delete the order
            order_name = order.name
            session.delete(order)
            session.commit()

            return {
                'success': True,
                'message': f"Repair order '{order_name}' deleted successfully"
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f"Error deleting repair order: {str(e)}"}
        finally:
            session.close()

    def delete_repairunit(self, unit_key):
        """Delete a repair unit by its key (e.g., 'RU-1423')"""
        session = self.get_session()
        try:
            # Parse the key
            prefix, unit_id = self._parse_key(unit_key)

            if prefix != 'RU':
                return {'success': False, 'message': f"Expected RU key, got: {unit_key}"}

            # Find the repair unit
            unit = session.query(RepairUnit).filter(RepairUnit.id == unit_id).first()
            if not unit:
                return {'success': False, 'message': f"Repair unit with key '{unit_key}' not found"}

            # Delete the repair unit
            unit_serial = unit.serial
            session.delete(unit)
            session.commit()

            return {
                'success': True,
                'message': f"Repair unit '{unit_serial}' deleted successfully"
            }
        except ValueError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f"Error deleting repair unit: {str(e)}"}
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
            result = []

            for ro in orders:
                # Count machines and hashboards for this order
                machine_count = session.query(RepairUnit).filter(
                    RepairUnit.repair_order_id == ro.id,
                    RepairUnit.type == UnitType.MACHINE
                ).count()

                hashboard_count = session.query(RepairUnit).filter(
                    RepairUnit.repair_order_id == ro.id,
                    RepairUnit.type == UnitType.HASHBOARD
                ).count()

                result.append({
                    'key': self._make_key('RO', ro.id),
                    'name': ro.name,
                    'status': ro.status.status,
                    'status_id': ro.status_id,
                    'summary': ro.summary,
                    'created': ro.created.isoformat() if ro.created else None,
                    'received': ro.received.isoformat() if ro.received else None,
                    'finished': ro.finished.isoformat() if ro.finished else None,
                    'machine_count': machine_count,
                    'hashboard_count': hashboard_count
                })

            return result
        finally:
            session.close()

    def get_repair_order_by_key(self, order_key):
        """Get a single repair order by its key (e.g., 'RO-123')"""
        session = self.get_session()
        try:
            # Parse the key
            prefix, order_id = self._parse_key(order_key)

            if prefix != 'RO':
                raise ValueError(f"Expected RO key, got: {order_key}")

            # Query the order
            order = session.query(RepairOrder).filter(RepairOrder.id == order_id).first()

            if not order:
                return None

            return {
                'key': self._make_key('RO', order.id),
                'name': order.name,
                'status': order.status.status,
                'status_id': order.status_id,
                'summary': order.summary,
                'created': order.created.isoformat() if order.created else None,
                'received': order.received.isoformat() if order.received else None,
                'finished': order.finished.isoformat() if order.finished else None
            }
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

    def get_repair_unit_by_key(self, unit_key):
        """Get a single repair unit by its key (e.g., 'RU-1423')"""
        session = self.get_session()
        try:
            # Parse the key
            prefix, unit_id = self._parse_key(unit_key)

            if prefix != 'RU':
                raise ValueError(f"Expected RU key, got: {unit_key}")

            # Query the repair unit
            unit = session.query(RepairUnit).filter(RepairUnit.id == unit_id).first()

            if not unit:
                return None

            return {
                'key': self._make_key('RU', unit.id),
                'serial': unit.serial,
                'type': unit.type.value if unit.type else None,
                'current_status': unit.current_status.status if unit.current_status else None,
                'current_status_id': unit.current_status_id,
                'current_assignee': unit.current_assignee.name if unit.current_assignee else None,
                'current_assignee_id': unit.current_assignee_id,
                'repair_order_key': self._make_key('RO', unit.repair_order_id),
                'created': unit.created.isoformat() if unit.created else None,
                'updated_at': unit.updated_at.isoformat() if unit.updated_at else None,
                'events_json': unit.events_json
            }
        finally:
            session.close()

    def add_repair_unit(self, order_key, serial, unit_type):
        """Add a new repair unit to a repair order.

        Args:
            order_key: The repair order key (e.g., 'RO-1')
            serial: Serial number of the unit
            unit_type: Type of unit ('machine' or 'hashboard')

        Returns:
            dict with success status and message
        """
        session = self.get_session()
        try:
            # Parse the order key
            prefix, order_id = self._parse_key(order_key)

            if prefix != 'RO':
                return {'success': False, 'message': f"Expected RO key, got: {order_key}"}

            # Verify the repair order exists
            order = session.query(RepairOrder).filter(RepairOrder.id == order_id).first()
            if not order:
                return {'success': False, 'message': f"Repair order '{order_key}' not found"}

            # Validate unit type
            if unit_type not in ['machine', 'hashboard']:
                return {'success': False, 'message': f"Invalid unit type: {unit_type}. Must be 'machine' or 'hashboard'"}

            # Get the first status (default status)
            default_status = session.query(Status).order_by(Status.id).first()
            if not default_status:
                return {'success': False, 'message': 'No default status found. Please create a status first.'}

            # Create new repair unit
            new_unit = RepairUnit(
                serial=serial,
                type=UnitType(unit_type),
                repair_order_id=order_id,
                current_status_id=default_status.id,
                current_assignee_id=None,
                events_json=None
            )
            session.add(new_unit)
            session.commit()

            # Generate the key for the response
            unit_key = self._make_key('RU', new_unit.id)

            return {
                'success': True,
                'message': f"Repair unit '{serial}' added successfully with key {unit_key}",
                'id': new_unit.id,
                'key': unit_key
            }
        except Exception as e:
            session.rollback()
            return {'success': False, 'message': f"Error adding repair unit: {str(e)}"}
        finally:
            session.close()


# Global instance
db_service = DatabaseService()


# Convenience function for getting sessions
def get_db_session():
    """Get a database session from the global database service."""
    return db_service.get_session()