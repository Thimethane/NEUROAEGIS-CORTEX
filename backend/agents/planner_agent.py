"""
Planner Agent - Tactical Response Planning
Enhanced with robust validation and frontend integration
"""

from typing import Dict, List, Any
from google.genai.types import GenerateContentConfig, Content, Part
from agents.base_agent import BaseAgent
from config.settings import settings, PLANNER_AGENT_PROMPT


class PlannerAgent(BaseAgent):
    """Converts detected threats into tactical response plans.
    
    Key improvements:
    - Comprehensive action validation
    - Automatic fallback plans for API failures
    - Severity-based plan generation
    - Integration with frontend action executor
    """

    # Valid actions that can be executed by the system
    VALID_ACTIONS = {
        'save_evidence',
        'send_alert', 
        'log_incident',
        'lock_door',
        'sound_alarm',
        'contact_authorities',
        'monitor',
        'escalate',
        'notify_staff',
        'record_video',
        'capture_snapshot'
    }

    async def process(self, incident: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generates a list of actionable response steps.

        Args:
            incident: Threat metadata from the VisionAgent. Should contain:
                - type: Incident type (theft, intrusion, etc.)
                - severity: Severity level (low, medium, high, critical)
                - reasoning: Analysis explanation
                - confidence: Confidence score (0-100)

        Returns:
            List[Dict]: A sequence of steps with action, priority, and reasoning.
        """
        try:
            # Format the prompt with incident details
            query = PLANNER_AGENT_PROMPT.format(
                incident_type=incident.get("type", "unknown"),
                severity=incident.get("severity", "low"),
                reasoning=incident.get("reasoning", "No reasoning provided"),
                confidence=incident.get("confidence", 0),
            )

            # Call Gemini to generate plan
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[Content(role="user", parts=[Part.from_text(text=query)])],
                config=GenerateContentConfig(
                    temperature=settings.TEMPERATURE,
                    response_mime_type="application/json"
                ),
            )

            # Parse and validate response
            plan = self._parse_json_response(response.text)
            
            if plan and isinstance(plan, list) and len(plan) > 0:
                validated_plan = self._validate_plan(plan)
                self.logger.info(f"✅ Generated {len(validated_plan)}-step plan")
                return validated_plan
            else:
                self.logger.warning("Plan parsing failed or empty, using fallback")
                return self._create_fallback_plan(incident)
                
        except Exception as e:
            self.logger.error(f"Plan generation failed: {e}")
            return self._create_fallback_plan(incident)

    def _validate_plan(self, plan: List[Dict]) -> List[Dict]:
        """Ensures all actions are within the approved security protocol.
        
        Args:
            plan: Raw plan from Gemini API
            
        Returns:
            List[Dict]: Validated plan with normalized fields
        """
        validated = []
        
        for i, step in enumerate(plan):
            action = step.get("action", "log_incident")
            
            # Normalize action name (remove spaces, lowercase)
            action = action.lower().replace(" ", "_")
            
            # Replace invalid actions with safe default
            if action not in self.VALID_ACTIONS:
                self.logger.warning(f"Invalid action '{action}' replaced with 'log_incident'")
                action = "log_incident"
            
            # Normalize priority
            priority = step.get("priority", "medium").lower()
            if priority not in ["immediate", "high", "medium", "low"]:
                priority = "medium"
            
            # Ensure parameters is a dict
            parameters = step.get("parameters", {})
            if not isinstance(parameters, dict):
                parameters = {}
                
            validated.append({
                "step": step.get("step", i + 1),
                "action": action,
                "priority": priority,
                "parameters": parameters,
                "reasoning": step.get("reasoning", "Standard security procedure")
            })
            
        self.logger.debug(f"Validated {len(validated)} actions: {[s['action'] for s in validated]}")
        return validated

    def _create_fallback_plan(self, incident: Dict) -> List[Dict]:
        """Provides a safe default response if the LLM fails.
        
        Creates severity-appropriate plans automatically:
        - Low/Medium: Evidence + Logging
        - High/Critical: Evidence + Alert + Logging + optional escalation
        
        Args:
            incident: The incident metadata dictionary.

        Returns:
            List[Dict]: A validated action plan with at least 2-3 steps.
        """
        severity = str(incident.get("severity", "low")).lower()
        incident_type = incident.get("type", "unknown")
        confidence = incident.get("confidence", 0)
        
        self.logger.info(f"Creating fallback plan for {severity} severity incident")
        
        plan = []
        step_num = 1
        
        # Step 1: Always preserve evidence first
        plan.append({
            "step": step_num,
            "action": "save_evidence",
            "priority": "immediate" if severity in ["high", "critical"] else "high",
            "parameters": {
                "incident_type": incident_type,
                "confidence": confidence
            },
            "reasoning": "Preserve forensic evidence for investigation"
        })
        step_num += 1
        
        # Step 2: High/Critical incidents need immediate alerts
        if severity in ["high", "critical"]:
            plan.append({
                "step": step_num,
                "action": "send_alert",
                "priority": "immediate",
                "parameters": {
                    "severity": severity,
                    "incident_type": incident_type
                },
                "reasoning": "Immediate notification required for high-severity threat"
            })
            step_num += 1
        
        # Step 3: Always log the incident
        plan.append({
            "step": step_num,
            "action": "log_incident",
            "priority": "high" if severity in ["high", "critical"] else "medium",
            "parameters": {
                "severity": severity,
                "incident_type": incident_type,
                "confidence": confidence
            },
            "reasoning": "Document incident in security log for audit trail"
        })
        step_num += 1
        
        # Step 4: Critical incidents may need escalation
        if severity == "critical":
            plan.append({
                "step": step_num,
                "action": "escalate",
                "priority": "immediate",
                "parameters": {
                    "target": "security_team",
                    "incident_type": incident_type
                },
                "reasoning": "Critical threat requires immediate human intervention"
            })
            step_num += 1
        
        # Step 5: Physical threats need monitoring
        if incident_type in ["intrusion", "theft", "violence", "vandalism"]:
            plan.append({
                "step": step_num,
                "action": "monitor",
                "priority": "high",
                "parameters": {
                    "duration": 300,  # 5 minutes
                    "incident_type": incident_type
                },
                "reasoning": "Continue monitoring for threat escalation or resolution"
            })
        
        self.logger.info(f"✅ Fallback plan created with {len(plan)} steps")
        return plan

    def get_action_description(self, action: str) -> str:
        """Returns a human-readable description of an action.
        
        Useful for frontend display and logging.
        
        Args:
            action: Action identifier
            
        Returns:
            str: Human-readable description
        """
        descriptions = {
            'save_evidence': 'Save frame snapshot to evidence database',
            'send_alert': 'Send email/SMS alert to security personnel',
            'log_incident': 'Record incident details in system log',
            'lock_door': 'Trigger automated door lock',
            'sound_alarm': 'Activate audible alarm system',
            'contact_authorities': 'Notify law enforcement automatically',
            'monitor': 'Continue active monitoring of area',
            'escalate': 'Escalate to human security team',
            'notify_staff': 'Send notification to on-site staff',
            'record_video': 'Start continuous video recording',
            'capture_snapshot': 'Capture high-resolution snapshot'
        }
        return descriptions.get(action, f'Execute {action}')
