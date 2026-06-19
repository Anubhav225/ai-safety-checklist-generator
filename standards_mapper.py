"""
standards_mapper.py
-------------------
Maps engineering domains to relevant safety standards and regulations.
Provides quick-reference data for ISO, OSHA, IEEE, IEC, and other standards.
"""

from typing import Optional

# Master standards database organized by domain
STANDARDS_DATABASE = {
    "Mechanical Engineering": [
        {
            "id": "ISO 12100",
            "name": "Safety of Machinery — General Principles for Design",
            "org": "ISO",
            "description": "Framework for risk assessment and risk reduction in machinery design",
            "key_clauses": ["Risk assessment methodology", "Inherently safe design", "Safeguarding"],
            "mandatory": True
        },
        {
            "id": "ISO 4413",
            "name": "Hydraulic Fluid Power — General Rules",
            "org": "ISO",
            "description": "Safety requirements for hydraulic systems",
            "key_clauses": ["Pressure relief", "Contamination control", "Fire resistance"],
            "mandatory": False
        },
        {
            "id": "ASME B31.1",
            "name": "Power Piping",
            "org": "ASME",
            "description": "Requirements for power and industrial piping systems",
            "key_clauses": ["Pressure design", "Material requirements", "Testing"],
            "mandatory": True
        },
        {
            "id": "OSHA 29 CFR 1910.217",
            "name": "Mechanical Power Presses",
            "org": "OSHA",
            "description": "Safety requirements for mechanical power press operations",
            "key_clauses": ["Point of operation guarding", "Die setting", "Training"],
            "mandatory": True
        }
    ],
    "Electrical Engineering": [
        {
            "id": "NFPA 70 (NEC)",
            "name": "National Electrical Code",
            "org": "NFPA",
            "description": "Minimum requirements for safe electrical installations",
            "key_clauses": ["Wiring methods", "Equipment grounding", "Overcurrent protection"],
            "mandatory": True
        },
        {
            "id": "NFPA 70E",
            "name": "Standard for Electrical Safety in the Workplace",
            "org": "NFPA",
            "description": "Electrical safety program requirements and arc flash hazard analysis",
            "key_clauses": ["Arc flash analysis", "PPE requirements", "LOTO"],
            "mandatory": True
        },
        {
            "id": "IEC 60364",
            "name": "Low-Voltage Electrical Installations",
            "org": "IEC",
            "description": "International standard for low-voltage electrical installation design",
            "key_clauses": ["Protection against shock", "Cable selection", "Earthing systems"],
            "mandatory": True
        },
        {
            "id": "IEEE 80",
            "name": "Guide for Safety in AC Substation Grounding",
            "org": "IEEE",
            "description": "Grounding design for outdoor AC substations",
            "key_clauses": ["Tolerable step/touch potentials", "Ground grid design", "Testing"],
            "mandatory": False
        },
        {
            "id": "OSHA 29 CFR 1910.269",
            "name": "Electric Power Generation, Transmission and Distribution",
            "org": "OSHA",
            "description": "Safety requirements for electric power industry operations",
            "key_clauses": ["Approach distances", "PPE", "Qualified worker training"],
            "mandatory": True
        }
    ],
    "Electronics Engineering": [
        {
            "id": "IEC 62368-1",
            "name": "Audio/Video, IT and Comms Technology Equipment Safety",
            "org": "IEC",
            "description": "Safety standard for electronic equipment using hazard-based approach",
            "key_clauses": ["Energy sources", "Safeguards", "Instructional safeguards"],
            "mandatory": True
        },
        {
            "id": "IEC 61000-4",
            "name": "Electromagnetic Compatibility (EMC) Testing",
            "org": "IEC",
            "description": "EMC immunity testing standards for electronic equipment",
            "key_clauses": ["ESD immunity", "Surge immunity", "Radiated immunity"],
            "mandatory": True
        },
        {
            "id": "UL 508A",
            "name": "Industrial Control Panels",
            "org": "UL",
            "description": "Safety requirements for industrial control panel assemblies",
            "key_clauses": ["Short circuit ratings", "Wiring methods", "Component marking"],
            "mandatory": True
        },
        {
            "id": "RoHS Directive 2011/65/EU",
            "name": "Restriction of Hazardous Substances",
            "org": "EU",
            "description": "Restricts use of specific hazardous materials in electronic equipment",
            "key_clauses": ["Restricted substances list", "Exemptions", "Marking requirements"],
            "mandatory": True
        }
    ],
    "Civil Engineering": [
        {
            "id": "ASCE 7",
            "name": "Minimum Design Loads and Associated Criteria for Buildings",
            "org": "ASCE",
            "description": "Structural load requirements including wind, seismic, and gravity loads",
            "key_clauses": ["Dead/live loads", "Wind loads", "Seismic design"],
            "mandatory": True
        },
        {
            "id": "ACI 318",
            "name": "Building Code Requirements for Structural Concrete",
            "org": "ACI",
            "description": "Design and construction requirements for reinforced concrete structures",
            "key_clauses": ["Strength design", "Reinforcement detailing", "Durability"],
            "mandatory": True
        },
        {
            "id": "OSHA 29 CFR 1926",
            "name": "Safety and Health Regulations for Construction",
            "org": "OSHA",
            "description": "Comprehensive construction site safety requirements",
            "key_clauses": ["Fall protection", "Excavation", "Scaffolding", "Cranes"],
            "mandatory": True
        },
        {
            "id": "IBC",
            "name": "International Building Code",
            "org": "ICC",
            "description": "Model building code for construction of new buildings",
            "key_clauses": ["Structural design", "Fire protection", "Means of egress"],
            "mandatory": True
        }
    ],
    "Software Engineering": [
        {
            "id": "IEC 62443",
            "name": "Industrial Automation and Control Systems Security",
            "org": "IEC",
            "description": "Cybersecurity standards for industrial control systems",
            "key_clauses": ["Security risk assessment", "System security requirements", "Patch management"],
            "mandatory": True
        },
        {
            "id": "ISO/IEC 27001",
            "name": "Information Security Management Systems",
            "org": "ISO/IEC",
            "description": "Requirements for establishing and maintaining an ISMS",
            "key_clauses": ["Risk treatment", "Security controls", "Incident management"],
            "mandatory": False
        },
        {
            "id": "IEC 61508",
            "name": "Functional Safety of E/E/PE Safety-Related Systems",
            "org": "IEC",
            "description": "Functional safety for software in safety-related systems",
            "key_clauses": ["SIL determination", "Software safety lifecycle", "Validation"],
            "mandatory": True
        },
        {
            "id": "DO-178C",
            "name": "Software Considerations in Airborne Systems",
            "org": "RTCA",
            "description": "Software development guidelines for airborne safety-critical systems",
            "key_clauses": ["Software levels (DAL)", "Verification", "Configuration management"],
            "mandatory": False
        },
        {
            "id": "OWASP Top 10",
            "name": "Top 10 Web Application Security Risks",
            "org": "OWASP",
            "description": "Standard awareness document for web application security risks",
            "key_clauses": ["Injection flaws", "Authentication", "Access control"],
            "mandatory": False
        }
    ],
    "Industrial Automation": [
        {
            "id": "IEC 62061",
            "name": "Safety of Machinery — Functional Safety of SCS",
            "org": "IEC",
            "description": "SIL-based functional safety for machinery control systems",
            "key_clauses": ["SILCL determination", "Hardware fault tolerance", "Software requirements"],
            "mandatory": True
        },
        {
            "id": "ISO 13849-1",
            "name": "Safety of Machinery — Safety-Related Parts of Control Systems",
            "org": "ISO",
            "description": "Performance level (PL) approach for safety control systems",
            "key_clauses": ["PL determination", "Category B-4", "Common cause failures"],
            "mandatory": True
        },
        {
            "id": "IEC 60204-1",
            "name": "Safety of Machinery — Electrical Equipment of Machines",
            "org": "IEC",
            "description": "Electrical equipment requirements for industrial machinery",
            "key_clauses": ["E-stop categories", "Control circuit voltages", "Wiring practices"],
            "mandatory": True
        },
        {
            "id": "OSHA 29 CFR 1910.147",
            "name": "Control of Hazardous Energy (Lockout/Tagout)",
            "org": "OSHA",
            "description": "Requirements for LOTO procedures during maintenance",
            "key_clauses": ["Energy isolation procedures", "Training", "Annual audits"],
            "mandatory": True
        },
        {
            "id": "ISA-18.2",
            "name": "Management of Alarm Systems for Process Industries",
            "org": "ISA",
            "description": "Design and management of process alarm systems",
            "key_clauses": ["Alarm rationalization", "Alarm prioritization", "Performance metrics"],
            "mandatory": False
        }
    ],
    "Manufacturing Systems": [
        {
            "id": "ISO 45001",
            "name": "Occupational Health and Safety Management Systems",
            "org": "ISO",
            "description": "Framework for OH&S management in manufacturing environments",
            "key_clauses": ["Hazard identification", "Legal requirements", "Incident investigation"],
            "mandatory": True
        },
        {
            "id": "OSHA 29 CFR 1910.212",
            "name": "General Requirements for All Machine Guarding",
            "org": "OSHA",
            "description": "Machine guarding requirements for manufacturing equipment",
            "key_clauses": ["Point of operation guarding", "Guarding methods", "Power transmission"],
            "mandatory": True
        },
        {
            "id": "ISO 9001",
            "name": "Quality Management Systems",
            "org": "ISO",
            "description": "Quality management requirements that support safety management",
            "key_clauses": ["Process approach", "Risk-based thinking", "Continual improvement"],
            "mandatory": False
        },
        {
            "id": "ANSI Z10",
            "name": "Occupational Health and Safety Management Systems",
            "org": "ANSI",
            "description": "US standard for OH&S management systems",
            "key_clauses": ["Management leadership", "Planning", "Evaluation"],
            "mandatory": False
        }
    ],
    "Robotics": [
        {
            "id": "ISO 10218-1/2",
            "name": "Robots and Robotic Devices — Safety Requirements for Industrial Robots",
            "org": "ISO",
            "description": "Primary safety standard for industrial robot design and installation",
            "key_clauses": ["Risk assessment", "Safeguarding requirements", "Control system safety"],
            "mandatory": True
        },
        {
            "id": "ANSI/RIA R15.06",
            "name": "Safety Requirements for Industrial Robots and Robot Systems",
            "org": "ANSI/RIA",
            "description": "US standard for industrial robot safety (adopts ISO 10218)",
            "key_clauses": ["Installation requirements", "Training", "Commissioning"],
            "mandatory": True
        },
        {
            "id": "ISO/TS 15066",
            "name": "Robots and Robotic Devices — Collaborative Robots",
            "org": "ISO",
            "description": "Safety requirements for collaborative robot operations",
            "key_clauses": ["Speed and separation monitoring", "Power/force limiting", "Hand guiding"],
            "mandatory": True
        },
        {
            "id": "IEC 62061",
            "name": "Functional Safety of Safety-Related Control Systems",
            "org": "IEC",
            "description": "SIL requirements for robot safety control functions",
            "key_clauses": ["SIL determination", "Safe torque off", "Validation"],
            "mandatory": True
        }
    ],
    "IoT Systems": [
        {
            "id": "IEC 62443",
            "name": "Industrial Automation and Control Systems Security",
            "org": "IEC",
            "description": "Cybersecurity for industrial IoT and control systems",
            "key_clauses": ["Security levels", "Zone and conduit model", "Component requirements"],
            "mandatory": True
        },
        {
            "id": "ETSI EN 303 645",
            "name": "Cybersecurity for Consumer IoT",
            "org": "ETSI",
            "description": "Baseline cybersecurity requirements for consumer IoT devices",
            "key_clauses": ["No default passwords", "Secure update mechanism", "Minimal exposure"],
            "mandatory": True
        },
        {
            "id": "FCC Part 15",
            "name": "Radio Frequency Devices",
            "org": "FCC",
            "description": "RF emissions requirements for IoT wireless devices",
            "key_clauses": ["Unintentional radiators", "Intentional radiators", "Labeling"],
            "mandatory": True
        },
        {
            "id": "ISO/IEC 27001",
            "name": "Information Security Management",
            "org": "ISO/IEC",
            "description": "Security management for IoT data and infrastructure",
            "key_clauses": ["Asset management", "Access control", "Cryptography"],
            "mandatory": False
        }
    ],
    "Construction Projects": [
        {
            "id": "OSHA 29 CFR 1926",
            "name": "Safety and Health Regulations for Construction",
            "org": "OSHA",
            "description": "Comprehensive construction safety regulations",
            "key_clauses": ["Fall protection (1926.502)", "Scaffolding", "Excavations", "Cranes"],
            "mandatory": True
        },
        {
            "id": "ANSI A10 Series",
            "name": "Safety Requirements for Construction and Demolition",
            "org": "ANSI",
            "description": "Comprehensive construction site safety standards",
            "key_clauses": ["Demolition safety", "Rigging", "Ladders", "Floor openings"],
            "mandatory": True
        },
        {
            "id": "IBC",
            "name": "International Building Code",
            "org": "ICC",
            "description": "Construction requirements for building safety",
            "key_clauses": ["Structural design loads", "Fire protection systems", "Egress"],
            "mandatory": True
        },
        {
            "id": "ISO 45001",
            "name": "Occupational Health and Safety Management",
            "org": "ISO",
            "description": "OH&S management framework applicable to construction",
            "key_clauses": ["Hazard identification", "Emergency planning", "Contractor management"],
            "mandatory": False
        }
    ]
}

# Universal standards that apply across all domains
UNIVERSAL_STANDARDS = [
    {
        "id": "ISO 45001",
        "name": "Occupational Health and Safety Management Systems",
        "org": "ISO",
        "description": "Universal OH&S management framework",
        "key_clauses": ["Hazard identification", "Risk assessment", "Incident investigation"],
        "mandatory": False
    },
    {
        "id": "ISO 31000",
        "name": "Risk Management — Guidelines",
        "org": "ISO",
        "description": "Principles and guidelines for risk management across all domains",
        "key_clauses": ["Risk assessment process", "Risk treatment", "Monitoring and review"],
        "mandatory": False
    }
]


class StandardsMapper:
    """
    Maps engineering domains to applicable safety standards and provides
    quick-reference information for compliance requirements.
    """

    def get_domain_standards(self, domain: str) -> list:
        """Return list of applicable standards for a given domain."""
        domain_stds = STANDARDS_DATABASE.get(domain, [])
        # Include universal standards
        return domain_stds + UNIVERSAL_STANDARDS

    def get_all_domains(self) -> list:
        """Return list of all supported engineering domains."""
        return list(STANDARDS_DATABASE.keys())

    def get_mandatory_standards(self, domain: str) -> list:
        """Return only mandatory standards for a domain."""
        all_stds = self.get_domain_standards(domain)
        return [s for s in all_stds if s.get('mandatory', False)]

    def search_standards(self, query: str) -> list:
        """Search standards by keyword across all domains."""
        query_lower = query.lower()
        results = []
        seen_ids = set()

        for domain, standards in STANDARDS_DATABASE.items():
            for std in standards:
                if std['id'] in seen_ids:
                    continue
                if (query_lower in std['id'].lower() or
                        query_lower in std['name'].lower() or
                        query_lower in std.get('description', '').lower()):
                    results.append({**std, 'domain': domain})
                    seen_ids.add(std['id'])

        return results

    def get_standard_by_id(self, standard_id: str) -> Optional[dict]:
        """Find a standard by its ID."""
        for standards in STANDARDS_DATABASE.values():
            for std in standards:
                if std['id'] == standard_id:
                    return std
        return None

    def get_standards_summary_table(self, domain: str) -> list:
        """Return a simplified table of standards for display."""
        standards = self.get_domain_standards(domain)
        return [
            {
                'Standard ID': s['id'],
                'Name': s['name'],
                'Organization': s['org'],
                'Mandatory': '✅ Yes' if s.get('mandatory') else '⭕ Recommended',
                'Description': s['description']
            }
            for s in standards
        ]
