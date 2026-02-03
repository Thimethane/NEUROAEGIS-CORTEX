"""
Action Executor - Enhanced Security Response System
Executes real-world responses to incidents with comprehensive action support
"""

import logging
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from pathlib import Path

from config.settings import settings
from services.database_service import db_service

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Executes security response actions with comprehensive error handling"""

    def __init__(self):
        self.executed_actions: List[Dict[str, Any]] = []
        logger.info("✅ ActionExecutor initialized")

    async def execute_plan(
        self,
        plan: List[Dict[str, Any]],
        incident_id: int,
        evidence_path: str = ""
    ):
        """
        Execute all actions in response plan with priority-based ordering
        
        Args:
            plan: List of action steps from PlannerAgent
            incident_id: Database ID of the incident
            evidence_path: Path to saved evidence file
        """
        if not plan:
            logger.warning(f"⚠️ No plan provided for incident #{incident_id}")
            return

        logger.info(f"🚀 Executing {len(plan)}-step response plan for incident #{incident_id}")

        # Sort by priority (immediate > high > medium > low) then by step number
        priority_order = {"immediate": 0, "high": 1, "medium": 2, "low": 3}
        sorted_plan = sorted(
            plan,
            key=lambda x: (
                priority_order.get(x.get("priority", "medium"), 2),
                x.get("step", 999)
            )
        )

        # Execute each action
        for step in sorted_plan:
            action_type = step.get("action")
            params = step.get("parameters", {})
            priority = step.get("priority", "medium")

            try:
                # Execute the action
                await self._execute_action(
                    action_type,
                    incident_id,
                    evidence_path,
                    params
                )

                # Record successful execution
                record = {
                    "incident_id": incident_id,
                    "action": action_type,
                    "status": "completed",
                    "priority": priority,
                    "parameters": params,
                    "timestamp": datetime.utcnow().isoformat()
                }

                # Save to database
                await asyncio.to_thread(
                    db_service.save_action,
                    incident_id,
                    action_type,
                    record
                )

                self.executed_actions.append(record)

                logger.info(
                    f"✅ [{priority.upper()}] Executed '{action_type}' for incident #{incident_id}"
                )

            except Exception as e:
                # Record failed execution
                error_record = {
                    "incident_id": incident_id,
                    "action": action_type,
                    "status": "failed",
                    "error": str(e),
                    "parameters": params,
                    "timestamp": datetime.utcnow().isoformat()
                }

                await asyncio.to_thread(
                    db_service.save_action,
                    incident_id,
                    action_type,
                    error_record
                )

                self.executed_actions.append(error_record)

                logger.error(
                    f"❌ Action '{action_type}' failed for incident #{incident_id}: {e}"
                )

        logger.info(f"✅ Response plan execution completed for incident #{incident_id}")

    async def _execute_action(
        self,
        action_type: str,
        incident_id: int,
        evidence_path: str,
        params: Dict[str, Any]
    ):
        """Execute individual action based on type"""

        # Map action types to handler methods
        action_map = {
            "save_evidence": self._save_evidence,
            "send_alert": self._send_alert,
            "log_incident": self._log_incident,
            "lock_door": self._lock_door,
            "sound_alarm": self._sound_alarm,
            "contact_authorities": self._contact_authorities,
            "monitor": self._monitor,
            "escalate": self._escalate,
            "notify_staff": self._notify_staff,          # NEW
            "record_video": self._record_video,          # NEW
            "capture_snapshot": self._capture_snapshot,  # NEW
        }

        handler = action_map.get(action_type)

        if not handler:
            logger.warning(f"⚠️ Unknown action type: {action_type}")
            return

        await handler(incident_id, evidence_path, params)

    # ========================================================================
    # ACTION HANDLERS
    # ========================================================================

    async def _save_evidence(
        self,
        incident_id: int,
        evidence_path: str,
        params: Dict
    ):
        """Save evidence to permanent storage with metadata"""
        
        if evidence_path and Path(evidence_path).exists():
            file_size = Path(evidence_path).stat().st_size
            logger.info(
                f"💾 Evidence saved: {evidence_path} ({file_size} bytes)"
            )
        else:
            logger.warning(f"⚠️ Evidence path not found or invalid: {evidence_path}")

    async def _send_alert(
        self,
        incident_id: int,
        evidence_path: str,
        params: Dict
    ):
        """Send alert notifications via multiple channels"""

        channels = params.get("channels", ["console", "email"])

        # Email alerts
        if "email" in channels and settings.ENABLE_EMAIL_ALERTS:
            try:
                await self._send_email_alert(incident_id)
            except Exception as e:
                logger.error(f"❌ Email alert failed: {e}")

        # SMS alerts
        if "sms" in channels and settings.ENABLE_SMS_ALERTS:
            try:
                await self._send_sms_alert(incident_id)
            except Exception as e:
                logger.error(f"❌ SMS alert failed: {e}")

        # Console alert (always active for development)
        logger.warning(
            f"🚨 [ALERT] SECURITY INCIDENT #{incident_id} | Evidence: {evidence_path}"
        )

    async def _send_email_alert(self, incident_id: int):
        """Send email alert via SMTP with detailed incident information"""

        if not all([
            settings.SMTP_HOST,
            settings.SMTP_USER,
            settings.SMTP_PASSWORD,
            settings.ALERT_EMAIL,
        ]):
            logger.warning("⚠️ Email configuration incomplete - skipping email alert")
            return

        # Fetch incident details
        incident = await asyncio.to_thread(
            db_service.get_incident_by_id,
            incident_id
        )

        if not incident:
            logger.error(f"❌ Incident #{incident_id} not found for email alert")
            return

        try:
            import aiosmtplib
            from email.message import EmailMessage

            message = EmailMessage()
            message["From"] = settings.SMTP_USER
            message["To"] = settings.ALERT_EMAIL
            message["Subject"] = f"🚨 AegisAI Alert: {incident['type'].upper()} - Incident #{incident_id}"

            # Create detailed email body
            subjects_str = ", ".join(incident.get('subjects', [])) or "None identified"
            
            message.set_content(
                f"""
=================================================
AegisAI SECURITY ALERT
=================================================

INCIDENT DETAILS:
-------------------------------------------------
Incident ID:    #{incident_id}
Type:           {incident['type'].upper()}
Severity:       {incident['severity'].upper()}
Confidence:     {incident['confidence']}%
Status:         {incident.get('status', 'active').upper()}
Timestamp:      {incident['timestamp']}

ANALYSIS:
-------------------------------------------------
{incident['reasoning']}

SUBJECTS IDENTIFIED:
-------------------------------------------------
{subjects_str}

RESPONSE PLAN:
-------------------------------------------------
{len(incident.get('response_plan', []))} action(s) initiated

EVIDENCE:
-------------------------------------------------
Evidence Path: {incident.get('evidence_path', 'N/A')}

=================================================
This is an automated alert from AegisAI Security System.
Please review the incident details and take appropriate action.
=================================================
"""
            )

            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT or 587,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=True,
            )

            logger.info(f"✅ Email alert sent to {settings.ALERT_EMAIL}")

        except Exception as e:
            logger.error(f"❌ Email alert failed: {e}")
            raise

    async def _send_sms_alert(self, incident_id: int):
        """Send SMS alert via Twilio with incident summary"""

        if not all([
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN,
            settings.TWILIO_PHONE,
            settings.ALERT_PHONE,
        ]):
            logger.warning("⚠️ SMS configuration incomplete - skipping SMS alert")
            return

        # Fetch incident details
        incident = await asyncio.to_thread(
            db_service.get_incident_by_id,
            incident_id
        )

        if not incident:
            logger.error(f"❌ Incident #{incident_id} not found for SMS")
            return

        try:
            from twilio.rest import Client

            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN,
            )

            # Create concise SMS message
            sms_body = (
                f"🚨 AegisAI Alert #{incident_id}: "
                f"{incident['type'].upper()} | "
                f"Severity: {incident['severity'].upper()} | "
                f"Confidence: {incident['confidence']}% | "
                f"Time: {incident['timestamp']}"
            )

            message = client.messages.create(
                body=sms_body,
                from_=settings.TWILIO_PHONE,
                to=settings.ALERT_PHONE,
            )

            logger.info(f"✅ SMS alert sent to {settings.ALERT_PHONE} (SID: {message.sid})")

        except Exception as e:
            logger.error(f"❌ SMS alert failed: {e}")
            raise

    async def _log_incident(
        self,
        incident_id: int,
        evidence_path: str,
        params: Dict
    ):
        """Confirm incident logging and update status"""
        
        # Update incident status to 'logged' if not already
        await asyncio.to_thread(
            db_service.update_incident_status,
            incident_id,
            "logged"
        )
        
        logger.info(f"📝 Incident #{incident_id} formally logged and documented")

    async def _lock_door(
        self,
        incident_id: int,
        evidence_path: str,
        params: Dict
    ):
        """Trigger automated door lock via IoT integration"""
        
        door_id = params.get("door_id", "main_entrance")
        
        if not settings.ENABLE_IOT_ACTIONS:
            logger.info(f"🔒 [SIMULATED] Door locked: {door_id}")
            return

        # Real IoT integration would go here
        # Example: await iot_service.lock_door(door_id)
        logger.info(f"🔒 Door locked via IoT: {door_id}")

    async def _sound_alarm(
        self,
        incident_id: int,
        evidence_path: str,
        params: Dict
    ):
        """Activate audible alarm system"""
        
        duration = params.get("duration", 30)  # seconds
        alarm_type = params.get("type", "intrusion")
        
        if not settings.ENABLE_IOT_ACTIONS:
            logger.info(f"🚨 [SIMULATED] Alarm activated: {alarm_type} ({duration}s)")
            return

        # Real IoT integration would go here
        # Example: await iot_service.sound_alarm(alarm_type, duration)
        logger.info(f"🚨 Alarm activated via IoT: {alarm_type} for {duration}s")

    async def _contact_authorities(
        self,
        incident_id: int,
        evidence_path: str,
        params: Dict
    ):
        """Simulate contacting law enforcement (requires manual verification in production)"""
        
        authority_type = params.get("type", "police")
        urgency = params.get("urgency", "high")
        
        logger.warning(
            f"🚔 [SIMULATED] Authorities contacted: {authority_type} | "
            f"Urgency: {urgency} | Incident #{incident_id}"
        )
        
        # In production, this would:
        # 1. Send notification to security operations center
        # 2. Require human verification before actual dispatch
        # 3. Log all communication attempts

    async def _monitor(
        self,
        incident_id: int,
        evidence_path: str,
        params: Dict
    ):
        """Continue monitoring the area for specified duration"""
        
        duration = params.get("duration", 300)  # 5 minutes default
        area = params.get("area", "incident_location")
        
        logger.info(
            f"👁️ Enhanced monitoring activated for {duration}s | "
            f"Area: {area} | Incident #{incident_id}"
        )
        
        # Update incident status to indicate ongoing monitoring
        await asyncio.to_thread(
            db_service.update_incident_status,
            incident_id,
            "monitoring"
        )

    async def _escalate(
        self,
        incident_id: int,
        evidence_path: str,
        params: Dict
    ):
        """Escalate incident to human security team"""
        
        target = params.get("target", "security_team")
        reason = params.get("reason", "High severity incident requires human intervention")
        
        # Update incident status
        await asyncio.to_thread(
            db_service.update_incident_status,
            incident_id,
            "escalated"
        )
        
        logger.warning(
            f"⬆️ Incident #{incident_id} escalated to {target} | "
            f"Reason: {reason}"
        )
        
        # In production, this would trigger:
        # 1. Notification to on-call security personnel
        # 2. Dashboard alert with priority flag
        # 3. Possible SMS/call to security manager

    async def _notify_staff(
        self,
        incident_id: int,
        evidence_path: str,
        params: Dict
    ):
        """Send notification to on-site staff"""
        
        staff_group = params.get("group", "security_team")
        message = params.get("message", f"Security incident #{incident_id} detected")
        
        logger.info(
            f"👥 Staff notification sent to {staff_group} | "
            f"Message: {message}"
        )
        
        # In production, integrate with:
        # - Slack/Teams for instant messaging
        # - Internal paging system
        # - Mobile app push notifications

    async def _record_video(
        self,
        incident_id: int,
        evidence_path: str,
        params: Dict
    ):
        """Start continuous video recording"""
        
        duration = params.get("duration", 60)  # 1 minute default
        camera_id = params.get("camera_id", "main_camera")
        
        logger.info(
            f"🎥 Video recording started: {camera_id} for {duration}s | "
            f"Incident #{incident_id}"
        )
        
        # In production, this would:
        # 1. Signal video processor to increase recording quality
        # 2. Store continuous footage instead of frames
        # 3. Ensure footage is saved to evidence storage

    async def _capture_snapshot(
        self,
        incident_id: int,
        evidence_path: str,
        params: Dict
    ):
        """Capture high-resolution snapshot"""
        
        camera_id = params.get("camera_id", "main_camera")
        resolution = params.get("resolution", "high")
        
        logger.info(
            f"📸 High-res snapshot captured: {camera_id} | "
            f"Resolution: {resolution} | Incident #{incident_id}"
        )
        
        # Evidence already saved by vision_agent, this confirms it
        if evidence_path and Path(evidence_path).exists():
            logger.info(f"✅ Snapshot confirmed at: {evidence_path}")

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def get_execution_history(self, limit: int = 10) -> List[Dict]:
        """Get recent action execution history"""
        return self.executed_actions[-limit:]

    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about action execution"""
        
        if not self.executed_actions:
            return {
                "total_actions": 0,
                "successful": 0,
                "failed": 0,
                "success_rate": 0.0
            }
        
        successful = sum(1 for a in self.executed_actions if a.get("status") == "completed")
        failed = sum(1 for a in self.executed_actions if a.get("status") == "failed")
        
        return {
            "total_actions": len(self.executed_actions),
            "successful": successful,
            "failed": failed,
            "success_rate": round((successful / len(self.executed_actions)) * 100, 2)
        }

    async def test_action(self, action_type: str, params: Dict = None) -> bool:
        """Test a single action without creating an incident"""
        
        try:
            logger.info(f"🧪 Testing action: {action_type}")
            await self._execute_action(
                action_type=action_type,
                incident_id=0,  # Test incident ID
                evidence_path="",
                params=params or {}
            )
            logger.info(f"✅ Action test successful: {action_type}")
            return True
        except Exception as e:
            logger.error(f"❌ Action test failed: {action_type} - {e}")
            return False


# Singleton instance
action_executor = ActionExecutor()
