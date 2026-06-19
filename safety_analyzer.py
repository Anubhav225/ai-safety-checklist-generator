"""
safety_analyzer.py — Core AI analysis engine using Groq API.
"""

import json
import logging
from typing import Optional
from groq import Groq

from prompts import SAFETY_ANALYSIS_SYSTEM_PROMPT, SAFETY_ANALYSIS_USER_PROMPT, CHATBOT_SYSTEM_PROMPT
from utils import parse_json_response, truncate_text, validate_analysis_structure

logger = logging.getLogger(__name__)


class SafetyAnalyzer:
    """AI safety analysis engine powered by Groq (llama-3.3-70b-versatile)."""

    MODEL = "llama-3.3-70b-versatile"

    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)

    # ------------------------------------------------------------------ #
    def analyze_project(self, project_content: str, domain: str,
                        project_name: str = "Unnamed Project") -> tuple[Optional[dict], Optional[str]]:
        """Run full safety analysis. Returns (analysis_dict, error_str)."""
        try:
            content = truncate_text(project_content, max_chars=12000)
            user_prompt = SAFETY_ANALYSIS_USER_PROMPT.format(
                project_content=content, domain=domain
            )
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": SAFETY_ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=8000,
            )
            raw = response.choices[0].message.content
            analysis = parse_json_response(raw)
            if analysis is None:
                return None, "Could not parse AI response. Please try again."

            is_valid, missing = validate_analysis_structure(analysis)
            if not is_valid:
                analysis = self._fill_missing_fields(analysis, missing)

            analysis["_metadata"] = {
                "project_name": project_name,
                "domain": domain,
                "model_used": self.MODEL,
            }
            return analysis, None

        except Exception as e:
            msg = str(e)
            if "401" in msg or "invalid_api_key" in msg.lower() or "authentication" in msg.lower():
                return None, "Invalid Groq API key. Get a free key at https://console.groq.com/keys"
            if "429" in msg or "rate_limit" in msg.lower():
                return None, "Rate limit hit. Wait a moment and try again."
            if "413" in msg or "too large" in msg.lower():
                return None, "Document too large. Please shorten the input."
            logger.error(f"Analysis error: {e}", exc_info=True)
            return None, f"Analysis error: {msg[:200]}"

    # ------------------------------------------------------------------ #
    def chat_with_analysis(self, user_message: str, analysis: dict,
                           chat_history: list) -> tuple[str, list]:
        """Chatbot for follow-up questions about the analysis."""
        try:
            summary = {
                "project_type": analysis.get("project_type", "N/A"),
                "overall_risk": analysis.get("overall_risk_assessment", "N/A"),
                "hazard_count": len(analysis.get("identified_hazards", [])),
                "top_hazards": analysis.get("identified_hazards", [])[:3],
                "standards": [s.get("standard_id") for s in analysis.get("applicable_standards", [])[:5]],
                "summary": analysis.get("summary", "N/A"),
            }
            system = CHATBOT_SYSTEM_PROMPT.format(
                analysis_context=json.dumps(summary, indent=2)
            )
            messages = [{"role": "system", "content": system}]
            for msg in chat_history[-10:]:
                messages.append({"role": msg["role"], "content": msg["content"]})
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=messages,
                temperature=0.5,
                max_tokens=1024,
            )
            reply = response.choices[0].message.content
            updated = list(chat_history)
            updated.append({"role": "user", "content": user_message})
            updated.append({"role": "assistant", "content": reply})
            return reply, updated
        except Exception as e:
            return f"Chat error: {str(e)[:150]}", chat_history

    # ------------------------------------------------------------------ #
    def _fill_missing_fields(self, analysis: dict, missing: list) -> dict:
        defaults = {
            "project_type": "Engineering Project",
            "identified_hazards": [], "risk_levels": [],
            "safety_checklist": [], "compliance_requirements": [],
            "recommended_controls": [], "overall_risk_assessment": "Medium",
            "summary": "Safety analysis completed. Review all identified items.",
            "safety_readiness_score": 50,
            "disclaimer": "AI-generated guidance only. Consult certified safety professionals.",
        }
        for f in missing:
            if f in defaults:
                analysis[f] = defaults[f]
        return analysis

    # ------------------------------------------------------------------ #
    def get_demo_analysis(self) -> dict:
        return {
            "project_type": "Industrial Robot Arm — Manufacturing Assembly System",
            "identified_hazards": [
                {"hazard_id": "H001", "category": "Mechanical", "description": "Robot arm pinch points during high-speed operation near joint actuators", "location": "Joint actuators and end-effector", "potential_consequences": "Crush injuries, fractures, or amputations", "likelihood": "Medium", "severity": "Critical", "risk_score": 15, "confidence": "High"},
                {"hazard_id": "H002", "category": "Electrical", "description": "High voltage exposure from 480V servo drive panels", "location": "Control cabinet and power distribution unit", "potential_consequences": "Electrical shock, arc flash, cardiac arrest", "likelihood": "Low", "severity": "Critical", "risk_score": 10, "confidence": "High"},
                {"hazard_id": "H003", "category": "Software", "description": "Control system failure causing unexpected motion", "location": "PLC and motion control software", "potential_consequences": "Unpredictable robot movement, collision with operators", "likelihood": "Medium", "severity": "High", "risk_score": 12, "confidence": "Medium"},
                {"hazard_id": "H004", "category": "Human Factor", "description": "Operator entering safeguarded space during maintenance without LOTO", "location": "Robot working envelope", "potential_consequences": "Struck-by injuries, fatalities", "likelihood": "Medium", "severity": "Critical", "risk_score": 15, "confidence": "High"},
                {"hazard_id": "H005", "category": "Environmental", "description": "Hydraulic fluid leak creating slip hazard and fire risk", "location": "Base and joint hydraulic connections", "potential_consequences": "Slip/fall injuries, fire hazard", "likelihood": "Medium", "severity": "Medium", "risk_score": 9, "confidence": "Medium"},
            ],
            "risk_levels": [
                {"category": "Mechanical Safety", "level": "Critical", "score": 20, "description": "High-speed moving parts pose extreme crush and strike hazards"},
                {"category": "Electrical Safety", "level": "High", "score": 16, "description": "High voltage systems require strict access controls"},
                {"category": "Software/Control Safety", "level": "High", "score": 15, "description": "Control system reliability is critical to safe operation"},
                {"category": "Human Factors", "level": "High", "score": 15, "description": "Operator-robot interaction zones need careful safeguarding"},
                {"category": "Environmental Safety", "level": "Medium", "score": 9, "description": "Fluid leaks manageable with proper containment"},
            ],
            "safety_checklist": [
                {"id": "CL001", "category": "Design Safety", "item": "Safety fence and light curtain perimeter guards installed", "description": "Physical barriers and presence-sensing devices must surround the full robot working envelope per ISO 10218-2", "priority": "Critical", "status": "Pending", "requires_expert_review": True, "applicable_standard": "ISO 10218-2"},
                {"id": "CL002", "category": "Mechanical Safety", "item": "Emergency stop buttons accessible from all operator positions", "description": "Category 0 or 1 E-Stop per IEC 60204-1 must be reachable within 1 meter of all work positions", "priority": "Critical", "status": "Pending", "requires_expert_review": False, "applicable_standard": "IEC 60204-1"},
                {"id": "CL003", "category": "Electrical Safety", "item": "Lockout/Tagout procedures established, documented and posted", "description": "Written LOTO procedures for all energy sources — electrical, pneumatic, and hydraulic", "priority": "Critical", "status": "Pending", "requires_expert_review": True, "applicable_standard": "OSHA 29 CFR 1910.147"},
                {"id": "CL004", "category": "Software Safety", "item": "Safety-rated motion controller with redundant outputs validated", "description": "PLC safety functions must meet SIL 2 or PLd minimum for this application", "priority": "High", "status": "Pending", "requires_expert_review": True, "applicable_standard": "IEC 62061"},
                {"id": "CL005", "category": "Human Factors", "item": "Operator safety training program documented and scheduled", "description": "Initial and annual refresher training on robot operation, hazard recognition, and emergency procedures", "priority": "High", "status": "Pending", "requires_expert_review": False, "applicable_standard": "ANSI/RIA R15.06"},
                {"id": "CL006", "category": "Maintenance Safety", "item": "Maintenance manual with step-by-step safety procedures for all tasks", "description": "Documented procedures with energy isolation requirements for all maintenance activities", "priority": "High", "status": "Pending", "requires_expert_review": False, "applicable_standard": "ISO 10218-1"},
            ],
            "compliance_requirements": [
                {"standard": "ISO 10218-1/2", "requirement": "Risk assessment and risk reduction for robot installations", "applicability": "Directly applicable to all industrial robot arm installations", "compliance_level": "Mandatory", "notes": "Must be performed by competent person before commissioning"},
                {"standard": "OSHA 29 CFR 1910.147", "requirement": "Lockout/Tagout program for servicing and maintenance", "applicability": "Required for all maintenance on powered equipment in the US", "compliance_level": "Mandatory", "notes": "Employer must document specific LOTO procedures for each machine"},
                {"standard": "ANSI/RIA R15.06", "requirement": "Safeguarding design, installation, and maintenance", "applicability": "US industry standard for robot safety systems", "compliance_level": "Mandatory", "notes": "Harmonized with ISO 10218 for US installations"},
            ],
            "recommended_controls": [
                {"hazard_ref": "H001", "control_type": "Engineering Control", "description": "Install safety-rated area scanners and light curtains", "implementation": "Mount safety laser scanners at 200mm height covering full robot reach envelope", "effectiveness": "High", "cost_estimate": "High", "priority": "Immediate"},
                {"hazard_ref": "H002", "control_type": "Engineering Control", "description": "Arc flash analysis and PPE labeling on all panels", "implementation": "Commission NFPA 70E arc flash study; label all panels with incident energy levels", "effectiveness": "High", "cost_estimate": "Medium", "priority": "Immediate"},
                {"hazard_ref": "H003", "control_type": "Engineering Control", "description": "Implement Safe Torque Off (STO) function in servo drives", "implementation": "Configure safety PLC with STO outputs to all servo drives; validate to SIL 2", "effectiveness": "High", "cost_estimate": "Medium", "priority": "Immediate"},
            ],
            "preventive_measures": [
                {"category": "Inspection", "measure": "Daily pre-shift safety inspection of robot and all safeguards", "frequency": "Daily", "responsible_party": "Shift supervisor", "documentation_required": True},
                {"category": "Testing", "measure": "Weekly functional test of all safety devices — E-stops, light curtains, scanners", "frequency": "Weekly", "responsible_party": "Maintenance technician", "documentation_required": True},
                {"category": "Calibration", "measure": "Annual safety system calibration, validation, and third-party audit", "frequency": "Annually", "responsible_party": "Certified safety engineer", "documentation_required": True},
            ],
            "emergency_procedures": [
                {"scenario": "Robot collision with operator", "immediate_actions": ["Activate nearest E-Stop immediately", "Do not attempt to move victim unless further immediate hazard exists", "Call emergency services (911)", "Initiate facility emergency response plan"], "notification_required": ["Emergency services", "Facility safety manager", "Plant manager", "HR department"], "equipment_needed": ["First aid kit", "AED defibrillator", "Emergency stretcher"], "recovery_steps": ["Secure scene and prevent access", "Conduct incident investigation", "Review and update safety procedures", "Notify regulatory authorities if required"]},
            ],
            "maintenance_safety": [
                {"component": "Robot arm joints and actuators", "maintenance_type": "Preventive", "safety_precautions": ["Full LOTO on all energy sources before any work begins", "Mechanically block arm in safe lowered position"], "frequency": "Every 1000 operating hours", "special_tools_ppe": ["Arc flash PPE (CAT 2 minimum)", "Mechanical arm support fixtures", "Calibrated torque wrenches"], "lockout_tagout_required": True},
            ],
            "applicable_standards": [
                {"standard_id": "ISO 10218-1/2", "name": "Robots and Robotic Devices — Safety Requirements for Industrial Robots", "organization": "ISO", "relevance": "Primary safety standard for industrial robot design and installation", "key_requirements": ["Risk assessment methodology", "Safeguarding requirements", "Control system safety"], "url_reference": "iso.org"},
                {"standard_id": "IEC 62061", "name": "Safety of Machinery — Functional Safety of Safety-Related Control Systems", "organization": "IEC", "relevance": "Defines SIL requirements for robot safety control functions", "key_requirements": ["SIL determination", "Control system architecture", "Validation testing"], "url_reference": "iec.ch"},
                {"standard_id": "ANSI/RIA R15.06", "name": "Safety Requirements for Industrial Robots and Robot Systems", "organization": "RIA/ANSI", "relevance": "US-specific robot safety installation requirements", "key_requirements": ["Safeguarding installation", "Operator training", "Commissioning checklist"], "url_reference": "ria.org"},
            ],
            "safety_training_recommendations": [
                {"training_topic": "Robot Safety Awareness", "target_audience": "All personnel working near robot cell", "frequency": "Initial + Annual", "method": "Classroom + Hands-on", "duration_hours": 4},
                {"training_topic": "Lockout/Tagout Procedures", "target_audience": "Maintenance technicians and engineers", "frequency": "Initial + Annual", "method": "Hands-on practical", "duration_hours": 8},
                {"training_topic": "Emergency Response Procedures", "target_audience": "All site personnel", "frequency": "Initial + Annual drill", "method": "Classroom + Drill", "duration_hours": 2},
            ],
            "overall_risk_assessment": "High",
            "safety_readiness_score": 35,
            "summary": "This industrial robot arm installation presents HIGH overall risk requiring immediate attention before commissioning. Five primary hazards identified — three rated Critical risk — centered on mechanical pinch points, high-voltage electrical systems, and operator entry into the working envelope. Priority actions are: install safety-rated perimeter guarding, complete formal ISO 10218 risk assessment by a competent person, establish LOTO procedures, and validate control system safety functions to SIL 2 / PLd. Current safety readiness score of 35/100 indicates significant work is required.",
            "disclaimer": "This safety assessment is AI-generated guidance only and does not constitute certified professional engineering review. All recommendations must be validated by qualified safety professionals before implementation.",
            "areas_requiring_expert_validation": [
                "SIL/PLd determination and verification calculations for control system safety functions",
                "Arc flash incident energy calculations per NFPA 70E",
                "Formal ISO 10218-1/2 risk assessment by a competent person",
                "Structural loading analysis for robot base mounting",
            ],
            "_metadata": {"project_name": "Demo — Robot Arm", "domain": "Robotics", "model_used": "Demo Mode"},
        }
