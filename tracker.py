from dataclasses import dataclass, field
from datetime import datetime
from typing import List
import json


#-------------------------------------------------------
# Events
#-------------------------------------------------------

@dataclass
class Event:
    assignee: str
    timestamp: datetime

    def to_dict(self):
        return{
            "assignee": self.assignee,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def from_json(cls, json_data):
        """Create an Event instance from JSON data"""
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        return cls(
            assignee=data["assignee"],
            timestamp=datetime.strptime(data["timestamp"], "%Y-%m-%d %H:%M:%S")
        )


@dataclass
class Status(Event):
    type: str = 'status'
    status: str

    def to_dict(self):
        data = super().to_dict()
        data['type'] = self.type
        data['status'] = self.status
        return data

    @classmethod
    def from_json(cls, json_data):
        """Create a Status instance from JSON data"""
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        # Create base Event first
        event = Event.from_json(data)
        
        return cls(
            assignee=event.assignee,
            timestamp=event.timestamp,
            status=data["status"]
        )


@dataclass
class Comment(Event):
    type: str = "comment"
    comment: str

    def to_dict(self):
        data = super().to_dict()
        data['type'] = self.type
        data['comment'] = self.comment
        return data

    @classmethod
    def from_json(cls, json_data):
        """Create a Comment instance from JSON data"""
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        # Create base Event first
        event = Event.from_json(data)
        
        return cls(
            assignee=event.assignee,
            timestamp=event.timestamp,
            comment=data["comment"]
        )


@dataclass
class Repair(Event):
    type: str = "repair"
    components: List[str] = field(default_factory=list)

    def to_dict(self):
        data = super().to_dict()
        data['type'] = self.type
        data['components'] = self.components
        return data

    @classmethod
    def from_json(cls, json_data):
        """Create a Repair instance from JSON data"""
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        # Create base Event first
        event = Event.from_json(data)
        
        return cls(
            assignee=event.assignee,
            timestamp=event.timestamp,
            components=data.get("components", [])
        )


#-------------------------------------------------------
# Units
#-------------------------------------------------------

@dataclass
class RepairUnit:
    key: str
    serial: str
    events: List[Event] = field(default_factory=list)

    def to_dict(self):
        return {
            "key": self.key,
            "serial": self.serial,
            "events": [e.to_dict() for e in self.events]
        }
    
    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data
        
        events = []
        for event_dict in data.get("events", []):
            event_type = event_dict.get("type")
            if event_type == "status":
                events.append(Status.from_json(event_dict))
            elif event_type == "comment":
                events.append(Comment.from_json(event_dict))
            elif event_type == "repair":
                events.append(Repair.from_json(event_dict))

        return cls(
            key=data["key"],
            serial=data["serial"],
            events=events
        )


@dataclass
class RepairOrder:
    key: str
    name: str
    status: str
    created: datetime
    recieved: datetime
    machines: List[RepairUnit] = field(default_factory=list)
    hashboards: List[RepairUnit] = field(default_factory=list)

    def to_dict(self):
        return {
           "key": self.key,
           "name": self.name,
           "status": self.status,
           "created": self.created.strftime("%Y-%m-%d"),
           "recieved": self.recieved.strftime("%Y-%m-%d"),
           "machines": [m.to_dict() for m in self.machines],
           "hashboards": [h.to_dict() for h in self.hashboards]                                   
        }
    
    @classmethod
    def from_json(cls, json_data):
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        machines = [RepairUnit.from_json(unit) for unit in data.get("machines", [])]
        hashboards = [RepairUnit.from_json(unit) for unit in data.get("hashboards", [])]

        return cls(
            key=data["key"],
            name=data["name"],
            status=data["status"],
            created=datetime.strptime(data["created"], "%Y-%m-%d"),
            recieved=datetime.strptime(data["recieved"], "%Y-%m-%d"),
            machines=machines,
            hashboards=hashboards
        )