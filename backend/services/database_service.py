"""
Database Service - Enhanced SQLite Operations
Thread-safe incident tracking with comprehensive querying and analytics
"""

import sqlite3
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager

from config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseService:
    """Thread-safe database operations for incident tracking with advanced querying"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DB_PATH
        self._ensure_database()
        logger.info(f"✅ Database service initialized: {self.db_path}")
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def _ensure_database(self):
        """Create database and tables if they don't exist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Incidents table with enhanced fields
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    incident_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    reasoning TEXT NOT NULL,
                    subjects TEXT,
                    recommended_actions TEXT,
                    evidence_path TEXT,
                    response_plan TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Actions table with execution details
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS actions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id INTEGER,
                    action_type TEXT NOT NULL,
                    action_data TEXT,
                    priority TEXT DEFAULT 'medium',
                    status TEXT DEFAULT 'pending',
                    executed_at TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
                )
            """)
            
            # System stats table for performance tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    component TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    value REAL NOT NULL,
                    metadata TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Evidence metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evidence_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id INTEGER,
                    file_path TEXT NOT NULL,
                    file_type TEXT,
                    file_size INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (incident_id) REFERENCES incidents(id) ON DELETE CASCADE
                )
            """)
            
            # Performance indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_incidents_created 
                ON incidents(created_at DESC)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_incidents_severity 
                ON incidents(severity)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_incidents_status 
                ON incidents(status)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_actions_incident 
                ON actions(incident_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_system_stats_component 
                ON system_stats(component, timestamp DESC)
            """)
            
            conn.commit()
            logger.info("✅ Database schema initialized")
    
    # ========================================================================
    # INCIDENT OPERATIONS
    # ========================================================================
    
    def save_incident(self, incident_data: Dict[str, Any]) -> int:
        """
        Save incident to database with comprehensive error handling
        
        Args:
            incident_data: Incident details including type, severity, etc.
            
        Returns:
            Incident ID or -1 on failure
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO incidents (
                        timestamp, incident_type, severity, confidence,
                        reasoning, subjects, recommended_actions, 
                        evidence_path, response_plan, status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    incident_data.get('timestamp', datetime.now().isoformat()),
                    incident_data.get('type', 'unknown'),
                    incident_data.get('severity', 'low'),
                    incident_data.get('confidence', 0),
                    incident_data.get('reasoning', ''),
                    json.dumps(incident_data.get('subjects', [])),
                    json.dumps(incident_data.get('recommended_actions', [])),
                    incident_data.get('evidence_path', ''),
                    json.dumps(incident_data.get('response_plan', [])),
                    incident_data.get('status', 'active'),
                    incident_data.get('created_at', datetime.now().isoformat())
                ))
                
                incident_id = cursor.lastrowid
                conn.commit()
                
                logger.info(f"✅ Saved incident #{incident_id}: {incident_data.get('type', 'unknown')}")
                return incident_id
                
            except Exception as e:
                logger.error(f"❌ Failed to save incident: {e}")
                conn.rollback()
                return -1
    
    def get_recent_incidents(
        self, 
        limit: int = 50,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        incident_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Retrieve recent incidents with optional filtering
        
        Args:
            limit: Maximum number of incidents to return
            severity: Filter by severity (low/medium/high/critical)
            status: Filter by status (active/resolved/escalated)
            incident_type: Filter by incident type
            
        Returns:
            List of incident dictionaries
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                query = """
                    SELECT 
                        id, timestamp, incident_type, severity, confidence,
                        reasoning, subjects, recommended_actions, 
                        evidence_path, status, created_at
                    FROM incidents
                    WHERE 1=1
                """
                
                params = []
                
                if severity:
                    query += " AND severity = ?"
                    params.append(severity)
                
                if status:
                    query += " AND status = ?"
                    params.append(status)
                
                if incident_type:
                    query += " AND incident_type = ?"
                    params.append(incident_type)
                
                query += " ORDER BY created_at DESC LIMIT ?"
                params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                incidents = []
                for row in rows:
                    incidents.append({
                        'id': row['id'],
                        'timestamp': row['timestamp'],
                        'type': row['incident_type'],
                        'severity': row['severity'],
                        'confidence': row['confidence'],
                        'reasoning': row['reasoning'],
                        'subjects': json.loads(row['subjects']) if row['subjects'] else [],
                        'recommended_actions': json.loads(row['recommended_actions']) if row['recommended_actions'] else [],
                        'evidence_path': row['evidence_path'],
                        'status': row['status'],
                        'created_at': row['created_at']
                    })
                
                return incidents
                
            except Exception as e:
                logger.error(f"❌ Failed to retrieve incidents: {e}")
                return []
    
    def get_incident_by_id(self, incident_id: int) -> Optional[Dict]:
        """Get single incident by ID with all details"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT * FROM incidents WHERE id = ?
                """, (incident_id,))
                
                row = cursor.fetchone()
                
                if row:
                    return {
                        'id': row['id'],
                        'timestamp': row['timestamp'],
                        'type': row['incident_type'],
                        'severity': row['severity'],
                        'confidence': row['confidence'],
                        'reasoning': row['reasoning'],
                        'subjects': json.loads(row['subjects']) if row['subjects'] else [],
                        'recommended_actions': json.loads(row['recommended_actions']) if row['recommended_actions'] else [],
                        'evidence_path': row['evidence_path'],
                        'response_plan': json.loads(row['response_plan']) if row['response_plan'] else [],
                        'status': row['status'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    }
                
                return None
                
            except Exception as e:
                logger.error(f"❌ Failed to get incident #{incident_id}: {e}")
                return None
    
    def update_incident_status(self, incident_id: int, status: str) -> bool:
        """Update incident status and set updated_at timestamp"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    UPDATE incidents 
                    SET status = ?, updated_at = ? 
                    WHERE id = ?
                """, (status, datetime.now().isoformat(), incident_id))
                
                conn.commit()
                success = cursor.rowcount > 0
                
                if success:
                    logger.info(f"✅ Updated incident #{incident_id} status to: {status}")
                
                return success
                
            except Exception as e:
                logger.error(f"❌ Failed to update incident #{incident_id}: {e}")
                conn.rollback()
                return False
    
    # ========================================================================
    # ACTION OPERATIONS
    # ========================================================================
    
    def save_action(
        self, 
        incident_id: int, 
        action_type: str, 
        action_data: Dict[str, Any]
    ) -> int:
        """Save executed action with details"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    INSERT INTO actions (
                        incident_id, action_type, action_data, 
                        priority, status, executed_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    incident_id,
                    action_type,
                    json.dumps(action_data),
                    action_data.get('priority', 'medium'),
                    action_data.get('status', 'completed'),
                    datetime.now().isoformat()
                ))
                
                action_id = cursor.lastrowid
                conn.commit()
                
                return action_id
                
            except Exception as e:
                logger.error(f"❌ Failed to save action: {e}")
                conn.rollback()
                return -1
    
    def get_actions_for_incident(self, incident_id: int) -> List[Dict]:
        """Get all actions associated with an incident"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT * FROM actions 
                    WHERE incident_id = ? 
                    ORDER BY executed_at ASC
                """, (incident_id,))
                
                rows = cursor.fetchall()
                
                actions = []
                for row in rows:
                    actions.append({
                        'id': row['id'],
                        'incident_id': row['incident_id'],
                        'action_type': row['action_type'],
                        'action_data': json.loads(row['action_data']) if row['action_data'] else {},
                        'priority': row['priority'],
                        'status': row['status'],
                        'executed_at': row['executed_at'],
                        'created_at': row['created_at']
                    })
                
                return actions
                
            except Exception as e:
                logger.error(f"❌ Failed to get actions for incident #{incident_id}: {e}")
                return []
    
    # ========================================================================
    # STATISTICS & ANALYTICS
    # ========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                stats = {}
                
                # Total incidents
                cursor.execute("SELECT COUNT(*) as count FROM incidents")
                stats['total_incidents'] = cursor.fetchone()['count']
                
                # Active incidents
                cursor.execute("SELECT COUNT(*) as count FROM incidents WHERE status = 'active'")
                stats['active_incidents'] = cursor.fetchone()['count']
                
                # Severity breakdown
                cursor.execute("""
                    SELECT severity, COUNT(*) as count
                    FROM incidents 
                    GROUP BY severity
                """)
                stats['severity_breakdown'] = {
                    row['severity']: row['count'] 
                    for row in cursor.fetchall()
                }
                
                # Recent incidents (last 24h)
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM incidents 
                    WHERE datetime(created_at) > datetime('now', '-1 day')
                """)
                stats['recent_24h'] = cursor.fetchone()['count']
                
                # Incident type breakdown
                cursor.execute("""
                    SELECT incident_type, COUNT(*) as count
                    FROM incidents 
                    GROUP BY incident_type
                    ORDER BY count DESC
                    LIMIT 5
                """)
                stats['top_incident_types'] = {
                    row['incident_type']: row['count']
                    for row in cursor.fetchall()
                }
                
                # Average confidence score
                cursor.execute("""
                    SELECT AVG(confidence) as avg_confidence
                    FROM incidents
                """)
                result = cursor.fetchone()
                stats['avg_confidence'] = round(result['avg_confidence'], 2) if result['avg_confidence'] else 0
                
                # Total actions executed
                cursor.execute("SELECT COUNT(*) as count FROM actions")
                stats['total_actions'] = cursor.fetchone()['count']
                
                # Action success rate
                cursor.execute("""
                    SELECT 
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as successful,
                        COUNT(*) as total
                    FROM actions
                """)
                result = cursor.fetchone()
                if result['total'] > 0:
                    stats['action_success_rate'] = round(
                        (result['successful'] / result['total']) * 100, 2
                    )
                else:
                    stats['action_success_rate'] = 0
                
                return stats
                
            except Exception as e:
                logger.error(f"❌ Failed to get statistics: {e}")
                return {}
    
    def get_hourly_incident_trend(self, hours: int = 24) -> List[Dict]:
        """Get incident count per hour for the specified time period"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT 
                        strftime('%Y-%m-%d %H:00:00', created_at) as hour,
                        COUNT(*) as count,
                        AVG(confidence) as avg_confidence
                    FROM incidents
                    WHERE datetime(created_at) > datetime('now', ? || ' hours')
                    GROUP BY hour
                    ORDER BY hour DESC
                """, (f'-{hours}',))
                
                return [
                    {
                        'hour': row['hour'],
                        'count': row['count'],
                        'avg_confidence': round(row['avg_confidence'], 2)
                    }
                    for row in cursor.fetchall()
                ]
                
            except Exception as e:
                logger.error(f"❌ Failed to get hourly trend: {e}")
                return []
    
    def get_severity_trends(self, days: int = 7) -> Dict[str, List[int]]:
        """Get severity distribution over time"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT 
                        date(created_at) as date,
                        severity,
                        COUNT(*) as count
                    FROM incidents
                    WHERE datetime(created_at) > datetime('now', ? || ' days')
                    GROUP BY date, severity
                    ORDER BY date DESC
                """, (f'-{days}',))
                
                # Organize by severity
                trends = {'low': [], 'medium': [], 'high': [], 'critical': []}
                current_date = None
                
                for row in cursor.fetchall():
                    if current_date != row['date']:
                        current_date = row['date']
                    
                    severity = row['severity']
                    if severity in trends:
                        trends[severity].append({
                            'date': row['date'],
                            'count': row['count']
                        })
                
                return trends
                
            except Exception as e:
                logger.error(f"❌ Failed to get severity trends: {e}")
                return {}
    
    # ========================================================================
    # MAINTENANCE OPERATIONS
    # ========================================================================
    
    def cleanup_old_incidents(self, days: int = 30) -> int:
        """Delete incidents older than specified days"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            try:
                cutoff_date = datetime.now() - timedelta(days=days)
                cursor.execute("""
                    DELETE FROM incidents 
                    WHERE datetime(created_at) < ?
                """, (cutoff_date.isoformat(),))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"🧹 Cleaned up {deleted_count} incidents older than {days} days")
                return deleted_count
                
            except Exception as e:
                logger.error(f"❌ Cleanup failed: {e}")
                conn.rollback()
                return 0
    
    def vacuum_database(self):
        """Optimize database by reclaiming space"""
        with self._get_connection() as conn:
            try:
                conn.execute("VACUUM")
                logger.info("✅ Database vacuumed successfully")
            except Exception as e:
                logger.error(f"❌ Database vacuum failed: {e}")
    
    def backup_database(self, backup_path: Path) -> bool:
        """Create a backup of the database"""
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"✅ Database backed up to: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Database backup failed: {e}")
            return False


# Singleton instance
db_service = DatabaseService()
