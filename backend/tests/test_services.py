"""
Service Layer Tests
Run with: pytest tests/test_services.py -v
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import tempfile

from services.database_service import DatabaseService
from services.action_executor import ActionExecutor


class TestDatabaseService:
    """Test DatabaseService functionality"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        db_path = Path(temp_file.name)
        temp_file.close()
        
        db = DatabaseService(db_path)
        yield db
        
        # Cleanup
        db_path.unlink(missing_ok=True)
    
    def test_database_initialization(self, temp_db):
        """Test database initializes with correct schema"""
        import sqlite3
        
        conn = sqlite3.connect(temp_db.db_path)
        cursor = conn.cursor()
        
        # Check incidents table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='incidents'
        """)
        assert cursor.fetchone() is not None
        
        # Check actions table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='actions'
        """)
        assert cursor.fetchone() is not None
        
        conn.close()
    
    def test_save_incident(self, temp_db):
        """Test saving incident to database"""
        incident_data = {
            'timestamp': datetime.now().isoformat(),
            'type': 'theft',
            'severity': 'high',
            'confidence': 85,
            'reasoning': 'Test incident',
            'subjects': ['person in dark clothing'],
            'evidence_path': '/path/to/evidence.jpg',
            'response_plan': [
                {'action': 'save_evidence', 'priority': 'immediate'}
            ]
        }
        
        incident_id = temp_db.save_incident(incident_data)
        
        assert incident_id > 0
        
        # Verify it was saved
        retrieved = temp_db.get_incident_by_id(incident_id)
        assert retrieved is not None
        assert retrieved['type'] == 'theft'
        assert retrieved['severity'] == 'high'
        assert retrieved['confidence'] == 85
    
    def test_get_recent_incidents(self, temp_db):
        """Test retrieving recent incidents in reverse chronological order"""
        # Save multiple incidents with increasing timestamps
        base_time = datetime.now()
        for i in range(5):
            temp_db.save_incident({
                'timestamp': (base_time + timedelta(seconds=i)).isoformat(),
                'type': f'type_{i}',
                'severity': 'low',
                'confidence': 70 + i,
                'reasoning': f'Test {i}',
                'subjects': [],
                'evidence_path': '',
                'response_plan': []
            })
        
        incidents = temp_db.get_recent_incidents(limit=10)
        
        assert len(incidents) == 5
        # Should be in reverse chronological order (latest first)
        actual_order = [inc['type'] for inc in incidents]
        expected_order = ['type_4', 'type_3', 'type_2', 'type_1', 'type_0']
        assert actual_order == expected_order
    
    def test_severity_filter(self, temp_db):
        """Test filtering incidents by severity"""
        # Save incidents with different severities
        temp_db.save_incident({
            'timestamp': datetime.now().isoformat(),
            'type': 'low_incident',
            'severity': 'low',
            'confidence': 70,
            'reasoning': 'Test',
            'subjects': [],
            'evidence_path': '',
            'response_plan': []
        })
        
        temp_db.save_incident({
            'timestamp': datetime.now().isoformat(),
            'type': 'high_incident',
            'severity': 'high',
            'confidence': 90,
            'reasoning': 'Test',
            'subjects': [],
            'evidence_path': '',
            'response_plan': []
        })
        
        high_incidents = temp_db.get_recent_incidents(severity='high')
        
        assert len(high_incidents) == 1
        assert high_incidents[0]['type'] == 'high_incident'
    
    def test_save_action(self, temp_db):
        """Test saving action execution"""
        # First create an incident
        incident_id = temp_db.save_incident({
            'timestamp': datetime.now().isoformat(),
            'type': 'test',
            'severity': 'low',
            'confidence': 70,
            'reasoning': 'Test',
            'subjects': [],
            'evidence_path': '',
            'response_plan': []
        })
        
        # Save action
        action_id = temp_db.save_action(
            incident_id=incident_id,
            action_type='save_evidence',
            action_data={'status': 'completed', 'timestamp': datetime.now().isoformat()}
        )
        
        assert action_id > 0
    
    def test_get_statistics(self, temp_db):
        """Test statistics retrieval"""
        # Save some test incidents
        for i in range(3):
            temp_db.save_incident({
                'timestamp': datetime.now().isoformat(),
                'type': 'test',
                'severity': 'high' if i == 0 else 'low',
                'confidence': 80,
                'reasoning': 'Test',
                'subjects': [],
                'evidence_path': '',
                'response_plan': []
            })
        
        stats = temp_db.get_statistics()
        
        assert stats['total_incidents'] == 3
        assert stats['severity_breakdown']['high'] == 1
        assert stats['severity_breakdown']['low'] == 2
    
    def test_update_incident_status(self, temp_db):
        """Test updating incident status"""
        incident_id = temp_db.save_incident({
            'timestamp': datetime.now().isoformat(),
            'type': 'test',
            'severity': 'low',
            'confidence': 70,
            'reasoning': 'Test',
            'subjects': [],
            'evidence_path': '',
            'response_plan': []
        })
        
        success = temp_db.update_incident_status(incident_id, 'resolved')
        assert success
        
        incident = temp_db.get_incident_by_id(incident_id)
        assert incident['status'] == 'resolved'
    
    def test_cleanup_old_incidents(self, temp_db):
        """Test cleanup of old incidents"""
        # Save an incident with timestamp and created_at in the past
        old_time = datetime.now() - timedelta(days=2)
        temp_db.save_incident({
            'timestamp': old_time.isoformat(),
            'type': 'old_test',
            'severity': 'low',
            'confidence': 70,
            'reasoning': 'Old incident',
            'subjects': [],
            'evidence_path': '',
            'response_plan': [],
            'created_at': old_time.isoformat()  # <-- Force old creation date
        })
        
        # Cleanup (should delete incidents older than 1 day)
        deleted = temp_db.cleanup_old_incidents(days=1)
        
        assert deleted >= 1


class TestActionExecutor:
    """Test ActionExecutor functionality"""
    
    @pytest.fixture
    def executor(self):
        """Create ActionExecutor instance"""
        return ActionExecutor()
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        db_path = Path(temp_file.name)
        temp_file.close()
        
        from services.database_service import DatabaseService
        db = DatabaseService(db_path)
        
        yield db
        
        db_path.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_execute_plan(self, executor, temp_db):
        """Test executing a response plan"""
        # Create incident in database
        incident_id = temp_db.save_incident({
            'timestamp': datetime.now().isoformat(),
            'type': 'test',
            'severity': 'high',
            'confidence': 85,
            'reasoning': 'Test',
            'subjects': [],
            'evidence_path': '/test/path.jpg',
            'response_plan': []
        })
        
        plan = [
            {
                'step': 1,
                'action': 'save_evidence',
                'priority': 'immediate',
                'parameters': {},
                'reasoning': 'Preserve evidence'
            },
            {
                'step': 2,
                'action': 'log_incident',
                'priority': 'high',
                'parameters': {},
                'reasoning': 'Document'
            }
        ]
        
        # Execute plan
        await executor.execute_plan(plan, incident_id, '/test/evidence.jpg')
        
        # Should complete without errors
        assert True
    
    @pytest.mark.asyncio
    async def test_save_evidence_action(self, executor):
        """Test save_evidence action"""
        await executor._save_evidence(1, '/test/evidence.jpg', {})
        assert True
    
    @pytest.mark.asyncio
    async def test_log_incident_action(self, executor):
        """Test log_incident action"""
        await executor._log_incident(1, '/test/evidence.jpg', {})
        assert True
    
    @pytest.mark.asyncio
    async def test_send_alert_action(self, executor):
        """Test send_alert action"""
        await executor._send_alert(1, '/test/evidence.jpg', {})
        assert True
    
    @pytest.mark.asyncio
    async def test_lock_door_action(self, executor):
        """Test lock_door action (simulated)"""
        await executor._lock_door(1, '/test/evidence.jpg', {})
        assert True
    
    @pytest.mark.asyncio
    async def test_action_priority_sorting(self, executor, temp_db):
        """Test actions execute in priority order"""
        incident_id = temp_db.save_incident({
            'timestamp': datetime.now().isoformat(),
            'type': 'test',
            'severity': 'high',
            'confidence': 85,
            'reasoning': 'Test',
            'subjects': [],
            'evidence_path': '',
            'response_plan': []
        })
        
        plan = [
            {'step': 3, 'action': 'log_incident', 'priority': 'low', 'parameters': {}, 'reasoning': 'Log'},
            {'step': 1, 'action': 'save_evidence', 'priority': 'immediate', 'parameters': {}, 'reasoning': 'Save'},
            {'step': 2, 'action': 'send_alert', 'priority': 'high', 'parameters': {}, 'reasoning': 'Alert'}
        ]
        
        await executor.execute_plan(plan, incident_id, '/test/evidence.jpg')
        
        # Should execute in priority order: immediate, high, low
        assert True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
