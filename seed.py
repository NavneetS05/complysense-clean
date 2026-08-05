#!/usr/bin/env python3
"""
ComplySense — Database Seed Script
====================================
Usage:
    python seed.py

Dependencies:
    pip install psycopg2-binary bcrypt python-dotenv

Behaviour:
    Clears all previously seeded data (except the 9 roles from schema.sql),
    then inserts fresh data. Safe to run multiple times.

Password for all seeded users: Comply@2025
MongoDB control IDs used here are the canonical IDs —
use the same strings as _id / control_id in your MongoDB control_library collection.
"""

import json
import logging
import os
import sys
import traceback
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import bcrypt
import psycopg2
from dotenv import load_dotenv

# ── reproducibility ──────────────────────────────────────────────────────────
random.seed(42)

# ── env ──────────────────────────────────────────────────────────────────────
# Look for .env in the same directory as this script first, then cwd
_script_dir = Path(__file__).resolve().parent
load_dotenv(_script_dir / ".env")
load_dotenv(".env")  # fallback: also try cwd

_raw_url = os.environ.get("DATABASE_URL", "")
if not _raw_url:
    raise SystemExit("DATABASE_URL not found in .env")
DATABASE_URL = _raw_url.replace("postgresql+asyncpg://", "postgresql://")

# ── password ─────────────────────────────────────────────────────────────────
_PWD = "Comply@2025"
PASSWORD_HASH = bcrypt.hashpw(_PWD.encode(), bcrypt.gensalt(rounds=12)).decode()
print(f"[seed] Password hash generated for '{_PWD}'")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

PERMISSION_DEFS = [
    # Roles & Institutions
    ("view_roles",              "View platform roles"),
    ("manage_institutions",     "Create and manage institution tenants"),
    # Audit
    ("view_audit_trail",        "View audit trail logs"),
    # Users
    ("manage_users",            "Create, edit, and deactivate users"),
    # Departments
    ("manage_departments",      "Create and manage departments"),
    # Calendar
    ("view_calendar",           "View compliance calendar events"),
    ("manage_calendar",         "Create and manage compliance calendar events"),
    # Controls
    ("view_controls",           "View control assignments and status"),
    ("manage_controls",         "Manage control assignments"),
    # Assessments
    ("view_assessments",        "View assessments"),
    ("manage_assessments",      "Create and manage assessments"),
    # Gaps
    ("view_gaps",               "View compliance gaps"),
    ("manage_gaps",             "Manage compliance gaps"),
    # Tasks
    ("view_tasks",              "View mitigation tasks"),
    ("manage_tasks",            "Create and manage mitigation tasks"),
    # Evidence
    ("upload_evidence",         "Upload evidence documents"),
    ("review_evidence",         "Review and approve/reject evidence"),
    ("view_evidence",           "View uploaded evidence documents"),
    # Incidents
    ("manage_incidents",        "Create and manage security incidents"),
    ("view_incidents",          "View security incidents"),
    # Vendors
    ("manage_vendors",          "Create and manage vendor records"),
    ("view_vendors",            "View vendor register"),
    # Policies
    ("draft_policies",          "Draft and edit compliance policies"),
    ("approve_policies",        "Approve or reject policy drafts"),
    ("view_policies",           "View policy documents"),
    # Audit observations & reports
    ("add_audit_observations",  "Add audit observations"),
    ("generate_audit_reports",  "Generate compliance and audit reports"),
    ("view_audit_reports",      "View audit and compliance reports"),
    # Notifications
    ("view_notifications",      "View system notifications"),
    # Assessor AI chat
    ("use_assessor_chat",       "Use the AI assessor chat"),
    # Role assumption
    ("use_role_assumption",     "Temporarily assume another role"),
]

ROLE_PERMISSION_MAP = {
    "Super Admin": [p[0] for p in PERMISSION_DEFS],  # all permissions
    "Institution Admin": [
        "view_roles", "manage_institutions",
        "view_audit_trail",
        "manage_users",
        "manage_departments",
        "view_calendar", "manage_calendar",
        "view_controls",
        "view_assessments",
        "view_gaps",
        "view_tasks",
        "view_evidence",
        "view_incidents",
        "view_vendors",
        "view_policies",
        "view_audit_reports", "generate_audit_reports",
        "view_notifications",
        "use_role_assumption",
    ],
    "Compliance Officer": [
        "view_audit_trail",
        "view_calendar", "manage_calendar",
        "view_controls", "manage_controls",
        "view_assessments", "manage_assessments",
        "view_gaps", "manage_gaps",
        "view_tasks", "manage_tasks",
        "upload_evidence", "review_evidence", "view_evidence",
        "view_incidents",
        "view_vendors",
        "draft_policies", "view_policies",
        "add_audit_observations", "generate_audit_reports", "view_audit_reports",
        "view_notifications",
        "use_assessor_chat",
        "use_role_assumption",
    ],
    "IT Security Officer": [
        "view_calendar",
        "view_controls", "manage_controls",
        "view_assessments",
        "view_gaps",
        "view_tasks", "manage_tasks",
        "upload_evidence", "view_evidence",
        "manage_incidents", "view_incidents",
        "view_vendors",
        "view_policies",
        "view_audit_reports",
        "view_notifications",
    ],
    "Auditor": [
        "view_audit_trail",
        "view_calendar",
        "view_controls",
        "view_assessments",
        "view_gaps",
        "view_tasks",
        "view_evidence",
        "view_incidents",
        "view_vendors",
        "view_policies",
        "add_audit_observations", "generate_audit_reports", "view_audit_reports",
        "view_notifications",
    ],
    "Department Reviewer": [
        "view_calendar",
        "view_controls",
        "view_assessments", "manage_assessments",
        "view_gaps",
        "view_tasks", "manage_tasks",
        "upload_evidence", "view_evidence",
        "view_notifications",
    ],
    "Vendor Reviewer": [
        "view_calendar",
        "manage_vendors", "view_vendors",
        "view_policies",
        "view_notifications",
    ],
    "Policy Approver": [
        "view_audit_trail",
        "view_calendar",
        "approve_policies", "view_policies",
        "view_audit_reports",
        "view_notifications",
    ],
    "Read-Only Assessor": [
        "view_calendar",
        "view_controls",
        "view_assessments",
        "view_gaps",
        "view_incidents",
        "view_policies",
        "view_audit_reports",
        "view_notifications",
        "use_assessor_chat",
    ],
}

# 4 institutions (3 regular + 1 platform for Super Admin)
INSTITUTIONS = [
    {
        "short":        "BIT",
        "name":         "Bharat Institute of Technology",
        "type":         "University",
        "email":        "admin@bit.edu.in",
        "phone":        "0141-2345678",
        "address":      "NH-48, Sitapura Industrial Area",
        "city":         "Jaipur",
        "state":        "Rajasthan",
        "staff_count":  1200,
        "is_platform":  False,
    },
    {
        "short":        "SEC",
        "name":         "Sunrise Engineering College",
        "type":         "College",
        "email":        "admin@sec.edu.in",
        "phone":        "020-98765432",
        "address":      "Baner Road, Balewadi",
        "city":         "Pune",
        "state":        "Maharashtra",
        "staff_count":  640,
        "is_platform":  False,
    },
    {
        "short":        "NMTI",
        "name":         "National Medical & Technical Institute",
        "type":         "Institute",
        "email":        "admin@nmti.edu.in",
        "phone":        "040-23456789",
        "address":      "Gachibowli, Cyberabad",
        "city":         "Hyderabad",
        "state":        "Telangana",
        "staff_count":  870,
        "is_platform":  False,
    },
    {
        "short":        "PLATFORM",
        "name":         "ComplySense Platform",
        "type":         "Platform",
        "email":        "platform@complysense.io",
        "phone":        "0141-0000000",
        "address":      "ComplySense HQ",
        "city":         "Jaipur",
        "state":        "Rajasthan",
        "staff_count":  10,
        "is_platform":  True,
    },
]

# Users per regular institution (index 0-12 per inst).
# Platform institution gets only Super Admin.
USER_TEMPLATES = {
    "BIT": [
        ("Institution Admin",   "Amit",     "Kumar",     "amit.kumar",      "Vice Chancellor"),
        ("Compliance Officer",  "Priya",    "Sharma",    "priya.sharma",    "Data Protection Officer"),
        ("IT Security Officer", "Rajesh",   "Singh",     "rajesh.singh",    "IT Security Manager"),
        ("Auditor",             "Neha",     "Gupta",     "neha.gupta",      "Internal Auditor"),
        ("Department Reviewer", "Vikram",   "Patel",     "vikram.patel",    "HOD Computer Science"),
        ("Department Reviewer", "Sunita",   "Joshi",     "sunita.joshi",    "HOD Electronics"),
        ("Department Reviewer", "Arjun",    "Reddy",     "arjun.reddy",     "HOD Mechanical"),
        ("Department Reviewer", "Kavita",   "Nair",      "kavita.nair",     "Administrative Head"),
        ("Department Reviewer", "Manish",   "Tiwari",    "manish.tiwari",   "IT Services Manager"),
        ("Vendor Reviewer",     "Deepak",   "Mehta",     "deepak.mehta",    "Procurement Officer"),
        ("Policy Approver",     "Ananya",   "Das",       "ananya.das",      "General Counsel"),
        ("Read-Only Assessor",  "Suresh",   "Rao",       "suresh.rao",      "Board Member"),
        ("Read-Only Assessor",  "Meena",    "Pillai",    "meena.pillai",    "NAAC Coordinator"),
    ],
    "SEC": [
        ("Institution Admin",   "Rahul",    "Verma",     "rahul.verma",     "Principal"),
        ("Compliance Officer",  "Pooja",    "Agarwal",   "pooja.agarwal",   "Compliance Manager"),
        ("IT Security Officer", "Kiran",    "Bhat",      "kiran.bhat",      "Network Security Lead"),
        ("Auditor",             "Sanjay",   "Kumar",     "sanjay.kumar",    "External Auditor"),
        ("Department Reviewer", "Ravi",     "Shankar",   "ravi.shankar",    "HOD Computer Science"),
        ("Department Reviewer", "Divya",    "Menon",     "divya.menon",     "HOD Electronics"),
        ("Department Reviewer", "Anil",     "Pandey",    "anil.pandey",     "HOD Mechanical"),
        ("Department Reviewer", "Lakshmi",  "Iyer",      "lakshmi.iyer",    "Administrative Officer"),
        ("Department Reviewer", "Vijay",    "Malhotra",  "vijay.malhotra",  "IT Manager"),
        ("Vendor Reviewer",     "Preeti",   "Saxena",    "preeti.saxena",   "Vendor Relations Manager"),
        ("Policy Approver",     "Rohit",    "Chandra",   "rohit.chandra",   "VP Academics"),
        ("Read-Only Assessor",  "Geeta",    "Krishnan",  "geeta.krishnan",  "Governing Board Member"),
        ("Read-Only Assessor",  "Naresh",   "Yadav",     "naresh.yadav",    "State Regulator Rep"),
    ],
    "NMTI": [
        ("Institution Admin",   "Sushma",   "Reddy",     "sushma.reddy",    "Director"),
        ("Compliance Officer",  "Arun",     "Nair",      "arun.nair",       "Compliance Lead"),
        ("IT Security Officer", "Bhavna",   "Desai",     "bhavna.desai",    "Cybersecurity Officer"),
        ("Auditor",             "Gopal",    "Mishra",    "gopal.mishra",    "Audit Committee Head"),
        ("Department Reviewer", "Harish",   "Patil",     "harish.patil",    "HOD Computer Science"),
        ("Department Reviewer", "Indira",   "Rao",       "indira.rao",      "HOD Electronics"),
        ("Department Reviewer", "Jagdish",  "Shah",      "jagdish.shah",    "HOD Mechanical"),
        ("Department Reviewer", "Kamla",    "Devi",      "kamla.devi",      "Admin Manager"),
        ("Department Reviewer", "Lokesh",   "Gupta",     "lokesh.gupta",    "IT Infrastructure Lead"),
        ("Vendor Reviewer",     "Madhuri",  "Patil",     "madhuri.patil",   "Third Party Risk Officer"),
        ("Policy Approver",     "Navin",    "Kumar",     "navin.kumar",     "Registrar"),
        ("Read-Only Assessor",  "Ojas",     "Mehta",     "ojas.mehta",      "Board of Governors Member"),
        ("Read-Only Assessor",  "Padma",    "Subramaniam","padma.subramaniam","AICTE Inspector"),
    ],
}

DEPARTMENTS = [
    ("CSE",   "Computer Science & Engineering"),
    ("ECE",   "Electronics & Communication Engineering"),
    ("MECH",  "Mechanical Engineering"),
    ("ADMIN", "Administration"),
    ("IT",    "IT Services"),
]

# ── Control pool ─────────────────────────────────────────────────────────────
# These IDs are canonical — MongoDB control_library._id must match exactly.
CONTROL_POOL = {
    "DPDP Act 2023": [f"DPDP-{i:03d}" for i in range(1, 26)],
    "ISO 27001:2022": (
        [f"ISO-A5-{i:03d}" for i in range(1, 11)] +
        [f"ISO-A8-{i:03d}" for i in range(1, 11)] +
        [f"ISO-A9-{i:03d}" for i in range(1, 11)]
    ),
    "NIST CSF 2.0": [
        "NIST-GV-001", "NIST-GV-002", "NIST-ID-001", "NIST-ID-002",
        "NIST-PR-001", "NIST-PR-002", "NIST-DE-001", "NIST-RS-001", "NIST-RC-001",
    ],
    "CERT-In 2022":        [f"CERTIN-{i:03d}" for i in range(1, 13)],
    "UGC Guidelines":      [f"UGC-{i:03d}" for i in range(1, 16)],
    "NAAC Criteria 4 & 6": (
        [f"NAAC-C4-{i:03d}" for i in range(1, 8)] +
        [f"NAAC-C6-{i:03d}" for i in range(1, 8)]
    ),
}
ALL_CONTROLS = [(fw, cid) for fw, ids in CONTROL_POOL.items() for cid in ids]  # 105 total

VENDOR_DATA = {
    "BIT": [
        {"name": "Google Workspace",           "product": "G Suite for Education",    "category": "cloud",         "location": "US",     "dpa": True,  "model_train": False, "expiry_days": 180},
        {"name": "Amazon Web Services",         "product": "AWS Cloud Infrastructure", "category": "cloud",         "location": "India",  "dpa": True,  "model_train": False, "expiry_days": 365},
        {"name": "Zoom Video Communications",   "product": "Zoom for Education",       "category": "communication", "location": "US",     "dpa": False, "model_train": False, "expiry_days": 25},
        {"name": "Tally Solutions Pvt Ltd",     "product": "TallyPrime ERP",           "category": "erp",           "location": "India",  "dpa": False, "model_train": False, "expiry_days": 90},
    ],
    "SEC": [
        {"name": "Microsoft Corporation",       "product": "Microsoft 365 Education",  "category": "cloud",         "location": "US",     "dpa": True,  "model_train": False, "expiry_days": 290},
        {"name": "Oracle India Pvt Ltd",        "product": "Oracle ERP Cloud",         "category": "erp",           "location": "India",  "dpa": True,  "model_train": False, "expiry_days": 400},
        {"name": "Cisco Systems India",         "product": "Cisco Networking Suite",   "category": "security",      "location": "India",  "dpa": False, "model_train": False, "expiry_days": 15},
        {"name": "Trellix (formerly McAfee)",   "product": "Trellix Endpoint Security","category": "security",      "location": "US",     "dpa": True,  "model_train": False, "expiry_days": 60},
    ],
    "NMTI": [
        {"name": "Google Workspace",            "product": "Google Workspace EDU",     "category": "cloud",         "location": "US",     "dpa": True,  "model_train": False, "expiry_days": 200},
        {"name": "Moodle HQ",                   "product": "Moodle LMS Hosting",       "category": "edtech",        "location": "EU",     "dpa": True,  "model_train": False, "expiry_days": 340},
        {"name": "Adobe Systems India",         "product": "Adobe Creative Cloud EDU", "category": "other",         "location": "India",  "dpa": False, "model_train": True,  "expiry_days": 120},
        {"name": "NPTEL e-Learning Platform",   "product": "NPTEL Course Access",      "category": "edtech",        "location": "India",  "dpa": False, "model_train": False, "expiry_days": 500},
    ],
}

POLICY_TEMPLATES = [
    "Data Protection and Privacy Policy",
    "Information Security and Access Control Policy",
    "IT Incident Response and CERT-In Compliance Policy",
    "Research Data Retention and Archival Policy",
]

INCIDENT_TEMPLATES = [
    {
        "title": "Ransomware Detected on Lab Network Server",
        "type":  "ransomware",   "severity": "critical",
        "status": "investigating",
        "cert_reported": False,
        "dpdp_required": True,
        "systems": "Lab-Server-01, Lab-Server-02, NAS-Storage-01",
        "data": "Student assignment data, faculty research files",
    },
    {
        "title": "Phishing Campaign Targeting Faculty Accounts",
        "type":  "phishing",     "severity": "high",
        "status": "contained",
        "cert_reported": True,
        "dpdp_required": False,
        "systems": "Faculty email accounts (approximately 23 accounts)",
        "data": "Faculty email credentials",
    },
    {
        "title": "Unauthorized Access to Student Records Database",
        "type":  "unauthorized_access", "severity": "critical",
        "status": "resolved",
        "cert_reported": True,
        "dpdp_required": True,
        "systems": "Student Information System, PostgreSQL DB Server",
        "data": "Student PII including Aadhaar references, grades, contact details",
    },
]

NOTE_SAMPLES = [
    json.dumps([{"author": "System", "text": "Initial assignment created during assessment.", "timestamp": str(datetime.now())}]),
    json.dumps([{"author": "System", "text": "Assigned to department reviewer for evidence collection.", "timestamp": str(datetime.now())}]),
    json.dumps([{"author": "System", "text": "Control flagged as priority during gap analysis.", "timestamp": str(datetime.now())}]),
    None,
]

AI_CONVERSATION_SAMPLES = [
    {
        "agent_type": "assessor_qa",
        "messages": [
            {"role": "user",      "content": "What is our current DPDP Act 2023 compliance status?",      "timestamp": str(datetime.now() - timedelta(days=2))},
            {"role": "assistant", "content": "Based on your latest DPDP assessment, your institution is currently 72% compliant. The main gaps are in data subject rights handling (Section 11) and breach notification procedures (Section 8). You have 3 critical gaps and 7 high-severity gaps pending remediation.", "timestamp": str(datetime.now() - timedelta(days=2))},
        ],
    },
    {
        "agent_type": "assessor_qa",
        "messages": [
            {"role": "user",      "content": "Why did our ISO 27001 compliance score drop last month?",   "timestamp": str(datetime.now() - timedelta(days=5))},
            {"role": "assistant", "content": "Your ISO 27001 score decreased by 4% primarily because 6 controls in Annex A.9 (Access Control) moved from compliant to non-compliant status after the quarterly review. Additionally, 2 evidence documents for Annex A.5 controls were rejected by the Compliance Officer and have not yet been resubmitted.", "timestamp": str(datetime.now() - timedelta(days=5))},
        ],
    },
    {
        "agent_type": "compliance_triage",
        "messages": [
            {"role": "user",      "content": "Run triage on today's control alerts.",                     "timestamp": str(datetime.now() - timedelta(hours=3))},
            {"role": "assistant", "content": "Triage complete. Top priority: 1. DPDP-011 (Data Subject Rights) — overdue by 5 days, no evidence uploaded. 2. ISO-A9-003 (User Access Management) — submitted evidence was rejected 3 days ago, needs resubmission. 3. CERTIN-006 (Incident Reporting Procedure) — assigned to IT Security with deadline in 2 days.", "timestamp": str(datetime.now() - timedelta(hours=3))},
        ],
    },
]

AUDIT_LOG_ACTION_TYPES = [
    "user_login", "user_logout", "user_created", "user_deactivated",
    "control_status_updated", "control_assigned",
    "evidence_uploaded", "evidence_approved", "evidence_rejected",
    "incident_created", "incident_status_updated", "incident_timeline_added",
    "policy_created", "policy_submitted", "policy_approved", "policy_rejected",
    "task_created", "task_completed", "task_status_updated",
    "vendor_created", "vendor_risk_assessed",
    "assessment_started", "assessment_response_saved", "assessment_completed",
    "gap_created", "gap_remediation_updated",
    "report_generated", "calendar_event_created",
]


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def uid() -> str:
    return str(uuid.uuid4())

def now() -> datetime:
    return datetime.now()

def days_from_now(n: int) -> datetime:
    return datetime.now() + timedelta(days=n)

def days_ago(n: int) -> datetime:
    return datetime.now() - timedelta(days=n)

def rnd_past(max_days: int = 90) -> datetime:
    return datetime.now() - timedelta(days=random.randint(1, max_days))

def pick(lst: list):
    return random.choice(lst)

def pick_n(lst: list, n: int) -> list:
    return random.sample(lst, min(n, len(lst)))

def weighted_status(statuses: list, weights: list) -> str:
    return random.choices(statuses, weights=weights, k=1)[0]


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — CLEANUP
# ═══════════════════════════════════════════════════════════════════════════════

CLEANUP_ORDER = [
    "ai_conversations",
    "audit_logs",
    "notifications",
    "compliance_calendar",
    "audit_reports",
    "audit_observations",
    "generated_policies",
    "vendor_risk_assessments",
    "vendors",
    "incident_timeline",
    "incidents",
    "evidence_documents",
    "mitigation_tasks",
    "compliance_gaps",
    "compliance_results",
    "assessment_responses",
    "assessments",
    "control_assignments",
    "allowed_role_transitions",
    "role_assumption_sessions",
    "user_sessions",
    "password_reset_tokens",
    "departments",
    "users",
    "role_permissions",
    "permissions",
    "institutions",
    "roles",  # now also cleared — seed.py re-inserts all 9 roles
]

def cleanup(cur):
    print("[seed] Cleaning previous seed data...")
    for table in CLEANUP_ORDER:
        cur.execute(f"DELETE FROM {table}")
        print(f"  cleared {table}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — SEED FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

# ── 4.1 Roles ────────────────────────────────────────────────────────────────
# Previously only fetched roles seeded by schema.sql.
# Now inserts all 9 roles directly so the script is fully self-contained.

ROLE_DEFS = [
    ("Super Admin",         "Platform-level developer administrator. God mode."),
    ("Institution Admin",   "Institution-wide administrative authority. Manages users, departments, calendar."),
    ("Compliance Officer",  "Primary daily operator. Manages controls, evidence, gap assessments, report building."),
    ("IT Security Officer", "Technical controls, incident management, CERT-In reporting, vulnerability tracking."),
    ("Auditor",             "Read and comment only. Reviews evidence, adds observations, generates audit reports."),
    ("Department Reviewer", "Dept-level tasks. Fills self-assessments and uploads evidence for their department."),
    ("Vendor Reviewer",     "Manages vendor register, conducts vendor risk assessments."),
    ("Policy Approver",     "Approves or rejects drafted policies. Sees version diffs."),
    ("Read-Only Assessor",  "Pure observer. Can view dashboards, control status, and reports. No edits."),
]


def seed_roles(cur) -> dict:
    """
    Inserts all 9 platform roles and returns role_map: {role_name: role_id}.
    """
    role_map = {}
    rows = []
    for role_name, description in ROLE_DEFS:
        rid = uid()
        role_map[role_name] = rid
        rows.append((rid, role_name, description))
    cur.executemany(
        "INSERT INTO roles (role_id, role_name, description) VALUES (%s, %s, %s)",
        rows,
    )
    print(f"[seed] Roles inserted: {len(role_map)}")
    return role_map


# ── 4.2 Permissions ──────────────────────────────────────────────────────────
def seed_permissions(cur) -> dict:
    perm_map = {}
    rows = []
    for key, desc in PERMISSION_DEFS:
        pid = uid()
        perm_map[key] = pid
        rows.append((pid, key, desc))
    cur.executemany(
        "INSERT INTO permissions (permission_id, permission_key, description) VALUES (%s, %s, %s)",
        rows,
    )
    print(f"[seed] Permissions: {len(rows)}")
    return perm_map


# ── 4.3 Role Permissions ─────────────────────────────────────────────────────
def seed_role_permissions(cur, role_map: dict, perm_map: dict):
    rows = []
    for role_name, perm_keys in ROLE_PERMISSION_MAP.items():
        role_id = role_map[role_name]
        for key in perm_keys:
            rows.append((uid(), role_id, perm_map[key]))
    cur.executemany(
        "INSERT INTO role_permissions (role_permission_id, role_id, permission_id) VALUES (%s, %s, %s)",
        rows,
    )
    print(f"[seed] Role permissions: {len(rows)}")


# ── 4.4 Institutions ─────────────────────────────────────────────────────────
def seed_institutions(cur) -> dict:
    inst_map = {}
    for i in INSTITUTIONS:
        iid = uid()
        inst_map[i["short"]] = iid
        cur.execute(
            """INSERT INTO institutions
               (institution_id, institution_name, institution_type, email, phone,
                address, city, state, country, staff_count, is_active)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (iid, i["name"], i["type"], i["email"], i["phone"],
             i["address"], i["city"], i["state"], "India", i["staff_count"], True),
        )
    print(f"[seed] Institutions: {len(inst_map)}")
    return inst_map


# ── 4.5 Users ────────────────────────────────────────────────────────────────
def seed_users(cur, inst_map: dict, role_map: dict) -> dict:
    """
    Returns user_map: {email: {id, role_name, inst_short, inst_id, full_name}}
    """
    user_map = {}

    # Super Admin on platform institution
    platform_id = inst_map["PLATFORM"]
    sa_id = uid()
    sa_email = "admin@complysense.io"
    cur.execute(
        """INSERT INTO users
           (user_id, institution_id, role_id, full_name, email, password_hash,
            phone, designation, is_active)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (sa_id, platform_id, role_map["Super Admin"],
         "Platform Admin", sa_email, PASSWORD_HASH,
         "0141-0000001", "Platform Administrator", True),
    )
    user_map[sa_email] = {
        "id": sa_id, "role_name": "Super Admin",
        "inst_short": "PLATFORM", "inst_id": platform_id, "full_name": "Platform Admin",
    }

    # Regular institution users
    for inst_short, templates in USER_TEMPLATES.items():
        inst_id = inst_map[inst_short]
        domain = inst_short.lower() + ".edu.in"
        for role_name, first, last, prefix, designation in templates:
            uid_ = uid()
            email = f"{prefix}@{domain}"
            full_name = f"{first} {last}"
            cur.execute(
                """INSERT INTO users
                   (user_id, institution_id, role_id, full_name, email, password_hash,
                    phone, designation, is_active)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (uid_, inst_id, role_map[role_name],
                 full_name, email, PASSWORD_HASH,
                 f"9{random.randint(100000000, 999999999)}", designation, True),
            )
            user_map[email] = {
                "id": uid_, "role_name": role_name,
                "inst_short": inst_short, "inst_id": inst_id, "full_name": full_name,
            }

    print(f"[seed] Users: {len(user_map)}")
    return user_map


# ── 4.6 Departments ──────────────────────────────────────────────────────────
def seed_departments(cur, inst_map: dict, user_map: dict) -> dict:
    """
    Returns dept_map: {(inst_short, dept_code): dept_id}
    Assigns one Dept Reviewer per department.
    """
    dept_map = {}
    for inst_short in ("BIT", "SEC", "NMTI"):
        inst_id = inst_map[inst_short]
        domain = inst_short.lower() + ".edu.in"
        # Get all Dept Reviewer user IDs for this institution (in order of DEPARTMENTS)
        reviewers = [
            u["id"] for email, u in user_map.items()
            if u["inst_short"] == inst_short and u["role_name"] == "Department Reviewer"
        ]
        for idx, (code, name) in enumerate(DEPARTMENTS):
            did = uid()
            reviewer_id = reviewers[idx] if idx < len(reviewers) else None
            cur.execute(
                """INSERT INTO departments
                   (department_id, institution_id, department_name, department_code,
                    hod_name, reviewer_user_id, is_active)
                   VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                (did, inst_id, name, code, f"Prof. HOD {name}", reviewer_id, True),
            )
            dept_map[(inst_short, code)] = did
    print(f"[seed] Departments: {len(dept_map)}")
    return dept_map


# ── 4.7 Allowed Role Transitions ─────────────────────────────────────────────
def seed_allowed_transitions(cur, role_map: dict):
    transitions = [
        ("Institution Admin",   "Compliance Officer"),
        ("Institution Admin",   "IT Security Officer"),
        ("Institution Admin",   "Auditor"),
        ("Institution Admin",   "Department Reviewer"),
        ("Institution Admin",   "Vendor Reviewer"),
        ("Institution Admin",   "Read-Only Assessor"),
        ("Compliance Officer",  "Department Reviewer"),
        ("Compliance Officer",  "Read-Only Assessor"),
    ]
    rows = [(uid(), role_map[f], role_map[t]) for f, t in transitions]
    cur.executemany(
        "INSERT INTO allowed_role_transitions (transition_id, from_role_id, to_role_id) VALUES (%s,%s,%s)",
        rows,
    )
    print(f"[seed] Allowed role transitions: {len(rows)}")


# ── 4.8 Control Assignments ──────────────────────────────────────────────────
def seed_control_assignments(cur, inst_map: dict, user_map: dict, dept_map: dict) -> dict:
    """
    60 controls per institution, 180 total.
    Returns assignment_map: {(inst_short, control_id): assignment_id}
    """
    assignment_map = {}
    status_pool = (
        ["not_started"] * 30 +
        ["in_progress"]  * 18 +
        ["submitted"]    * 9  +
        ["compliant"]    * 3
    )  # exactly 60, matches 50/30/15/5 %

    for inst_short in ("BIT", "SEC", "NMTI"):
        inst_id = inst_map[inst_short]
        sampled = pick_n(ALL_CONTROLS, 60)
        statuses = status_pool[:]
        random.shuffle(statuses)

        # build lookups
        co_id = next(u["id"] for e, u in user_map.items()
                     if u["inst_short"] == inst_short and u["role_name"] == "Compliance Officer")
        its_id = next(u["id"] for e, u in user_map.items()
                      if u["inst_short"] == inst_short and u["role_name"] == "IT Security Officer")
        dept_reviewers = [
            (u["id"], dept_map.get((inst_short, code)))
            for e, u in user_map.items()
            for code, _ in DEPARTMENTS
            if u["inst_short"] == inst_short and u["role_name"] == "Department Reviewer"
        ]

        rows = []
        for (fw, ctrl_id), status in zip(sampled, statuses):
            aid = uid()
            assignment_map[(inst_short, ctrl_id)] = aid

            # choose assignee — IT controls → IT Security, others → Dept Reviewer or CO
            if fw in ("NIST CSF 2.0", "CERT-In 2022"):
                assignee_id = its_id
                dept_id = None
            elif dept_reviewers:
                dr_id, dept_id = pick(dept_reviewers)
                assignee_id = dr_id
            else:
                assignee_id = co_id
                dept_id = None

            due = days_from_now(random.randint(-10, 60))
            completed_at = days_ago(random.randint(1, 20)) if status == "compliant" else None

            rows.append((
                aid, inst_id, ctrl_id, fw, assignee_id, dept_id,
                status, due, completed_at, co_id,
                pick(NOTE_SAMPLES),
            ))

        cur.executemany(
            """INSERT INTO control_assignments
               (assignment_id, institution_id, control_id, framework_name, assigned_to,
                department_id, status, due_date, completed_at, assigned_by, notes)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            rows,
        )
        print(f"  {inst_short}: {len(rows)} control assignments")

    print(f"[seed] Control assignments: {len(assignment_map)}")
    return assignment_map


# ── 4.9 Assessments ──────────────────────────────────────────────────────────
def seed_assessments(cur, inst_map: dict, user_map: dict) -> dict:
    """
    3 assessments per institution (DPDP completed, ISO in_progress, NIST draft).
    Returns assessment_map: {(inst_short, framework_short): assessment_id}
    """
    assessment_map = {}
    configs = [
        ("DPDP Act 2023",   "DPDP Readiness Assessment 2025",  "completed",   -30),
        ("ISO 27001:2022",  "ISO 27001 Gap Assessment Q3 2025", "in_progress", -10),
        ("NIST CSF 2.0",    "NIST CSF Baseline Assessment",     "draft",         0),
    ]
    for inst_short in ("BIT", "SEC", "NMTI"):
        inst_id = inst_map[inst_short]
        co_id = next(u["id"] for e, u in user_map.items()
                     if u["inst_short"] == inst_short and u["role_name"] == "Compliance Officer")
        for fw, name, status, started_offset in configs:
            aid = uid()
            key = (inst_short, fw.split()[0])
            assessment_map[key] = aid
            started = days_ago(abs(started_offset)) if started_offset < 0 else now()
            completed = days_ago(1) if status == "completed" else None
            cur.execute(
                """INSERT INTO assessments
                   (assessment_id, institution_id, assessment_name, framework_name,
                    assessment_status, started_by, started_at, completed_at)
                   VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                (aid, inst_id, name, fw, status, co_id, started, completed),
            )
    print(f"[seed] Assessments: {len(assessment_map)}")
    return assessment_map


# ── 4.10 Assessment Responses ────────────────────────────────────────────────
def seed_assessment_responses(cur, assessment_map: dict, user_map: dict):
    """
    Completed assessments get all framework controls answered.
    In-progress get 50%. Draft get 0.
    """
    response_values = ["Yes", "No", "Partial", "Not Applicable"]
    score_map = {"Yes": 1.0, "No": 0.0, "Partial": 0.5, "Not Applicable": None}
    rows = []

    for inst_short in ("BIT", "SEC", "NMTI"):
        co_id = next(u["id"] for e, u in user_map.items()
                     if u["inst_short"] == inst_short and u["role_name"] == "Compliance Officer")
        for fw_short, framework_name in [("DPDP", "DPDP Act 2023"), ("ISO", "ISO 27001:2022"), ("NIST", "NIST CSF 2.0")]:
            key = (inst_short, fw_short)
            if key not in assessment_map:
                continue
            assessment_id = assessment_map[key]
            controls = CONTROL_POOL.get(framework_name, [])
            # Determine how many to answer
            status = "completed" if fw_short == "DPDP" else ("in_progress" if fw_short == "ISO" else "draft")
            if status == "draft":
                continue
            n = len(controls) if status == "completed" else len(controls) // 2
            for ctrl_id in controls[:n]:
                val = weighted_status(response_values, [50, 20, 20, 10])
                rows.append((
                    uid(), assessment_id,
                    f"Q-{ctrl_id}", ctrl_id,
                    val, score_map[val], co_id,
                ))

    cur.executemany(
        """INSERT INTO assessment_responses
           (response_id, assessment_id, question_id, control_id,
            response_value, score_value, answered_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        rows,
    )
    print(f"[seed] Assessment responses: {len(rows)}")


# ── 4.11 Compliance Results ───────────────────────────────────────────────────
def seed_compliance_results(cur, assessment_map: dict, inst_map: dict):
    scores = {
        "BIT":  {"DPDP": (72, 18, 4, 3, 2), "ISO": (65, 19, 6, 5, 4)},
        "SEC":  {"DPDP": (80, 20, 3, 2, 1), "ISO": (70, 21, 5, 4, 3)},
        "NMTI": {"DPDP": (68, 17, 5, 3, 3), "ISO": (60, 18, 7, 5, 5)},
    }
    rows = []
    for inst_short, fw_scores in scores.items():
        inst_id = inst_map[inst_short]
        for fw_short, (pct, comp, partial, noncomp, crit) in fw_scores.items():
            framework_name = "DPDP Act 2023" if fw_short == "DPDP" else "ISO 27001:2022"
            key = (inst_short, fw_short)
            if key not in assessment_map:
                continue
            rows.append((
                uid(), assessment_map[key], inst_id, framework_name,
                pct, comp, partial, noncomp, crit,
            ))
    cur.executemany(
        """INSERT INTO compliance_results
           (result_id, assessment_id, institution_id, framework_name,
            compliance_percentage, compliant_controls, partial_controls,
            non_compliant_controls, critical_gap_count)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        rows,
    )
    print(f"[seed] Compliance results: {len(rows)}")


# ── 4.12 Compliance Gaps ─────────────────────────────────────────────────────
def seed_compliance_gaps(cur, assessment_map: dict, inst_map: dict) -> dict:
    """
    20 gaps per institution (60 total). Severity: 20% critical, 30% high, 30% medium, 20% low.
    Returns gap_map: {(inst_short, n): gap_id}
    """
    severities = (
        ["critical"] * 4 + ["high"] * 6 + ["medium"] * 6 + ["low"] * 4
    )  # 20

    gap_titles = [
        "Data subject rights mechanism not implemented",
        "Breach notification SOP missing",
        "Access control policy not documented",
        "MFA not enforced for admin accounts",
        "Vendor DPA not executed",
        "Incident response plan not tested",
        "Data retention schedule not defined",
        "Security awareness training not conducted",
        "Audit log review not performed regularly",
        "Network segmentation not implemented",
        "Backup and recovery process not tested",
        "Asset inventory incomplete",
        "Change management process not followed",
        "Password policy not enforced",
        "Physical access controls inadequate",
        "Third-party risk assessment not completed",
        "Encryption not applied to sensitive data at rest",
        "Vulnerability scanning not scheduled",
        "NAAC self-study report data governance gap",
        "UGC data sovereignty clause missing in cloud contracts",
    ]

    gap_map = {}
    rows = []
    frameworks = ["DPDP Act 2023", "ISO 27001:2022", "NIST CSF 2.0",
                  "CERT-In 2022", "UGC Guidelines", "NAAC Criteria 4 & 6"]
    controls_flat = [cid for ids in CONTROL_POOL.values() for cid in ids]

    for inst_short in ("BIT", "SEC", "NMTI"):
        inst_id = inst_map[inst_short]
        # use DPDP assessment as primary assessment link
        assessment_id = assessment_map.get((inst_short, "DPDP"))
        sev_pool = severities[:]
        random.shuffle(sev_pool)
        for n, (sev, title) in enumerate(zip(sev_pool, gap_titles)):
            gid = uid()
            gap_map[(inst_short, n)] = gid
            status = weighted_status(
                ["open", "in_progress", "resolved", "accepted_risk"],
                [50, 30, 15, 5],
            )
            rows.append((
                gid, assessment_id, inst_id,
                pick(controls_flat), pick(frameworks),
                sev, title,
                f"The institution has not fully implemented controls related to: {title.lower()}. "
                "Immediate remediation is required to meet regulatory obligations.",
                status,
            ))

    cur.executemany(
        """INSERT INTO compliance_gaps
           (gap_id, assessment_id, institution_id, control_id, framework_name,
            severity, title, description, remediation_status)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        rows,
    )
    print(f"[seed] Compliance gaps: {len(rows)}")
    return gap_map


# ── 4.13 Mitigation Tasks ────────────────────────────────────────────────────
def seed_mitigation_tasks(cur, gap_map: dict, assignment_map: dict,
                           user_map: dict, dept_map: dict, inst_map: dict):
    rows = []
    priorities = ["critical", "high", "medium", "low"]

    for inst_short in ("BIT", "SEC", "NMTI"):
        inst_id = inst_map[inst_short]
        co_id = next(u["id"] for e, u in user_map.items()
                     if u["inst_short"] == inst_short and u["role_name"] == "Compliance Officer")
        dept_reviewer_ids = [
            u["id"] for e, u in user_map.items()
            if u["inst_short"] == inst_short and u["role_name"] == "Department Reviewer"
        ]
        dept_ids = [dept_map[(inst_short, code)] for code, _ in DEPARTMENTS
                    if (inst_short, code) in dept_map]

        # 2 tasks per gap (20 gaps × 2 = 40 per inst, ~120 total)
        for n in range(20):
            gap_id = gap_map.get((inst_short, n))
            if not gap_id:
                continue
            for t in range(2):
                tid = uid()
                assignee = pick(dept_reviewer_ids) if dept_reviewer_ids else co_id
                dept_id = pick(dept_ids) if dept_ids else None
                status = weighted_status(
                    ["open", "in_progress", "completed", "overdue"],
                    [40, 30, 20, 10],
                )
                completed_at = days_ago(random.randint(1, 10)) if status == "completed" else None
                rows.append((
                    tid, inst_id, gap_id, None,
                    assignee, dept_id,
                    f"Remediation Task {t+1}: Address gap in compliance area",
                    "Review current controls, gather evidence, and implement required changes to close this compliance gap.",
                    pick(priorities), status,
                    days_from_now(random.randint(-5, 30)),
                    completed_at, co_id,
                ))

    cur.executemany(
        """INSERT INTO mitigation_tasks
           (task_id, institution_id, gap_id, assignment_id, assigned_to, department_id,
            task_title, task_description, priority, task_status, due_date,
            completed_at, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        rows,
    )
    print(f"[seed] Mitigation tasks: {len(rows)}")


# ── 4.14 Evidence Documents ───────────────────────────────────────────────────
def seed_evidence_documents(cur, assignment_map: dict, dept_map: dict,
                             user_map: dict, inst_map: dict):
    ext_mime = {
        "pdf":  "application/pdf",
        "png":  "image/png",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    ext_weights = [60, 25, 10, 5]
    ext_list = list(ext_mime.keys())

    rows = []
    counter = 1
    for inst_short in ("BIT", "SEC", "NMTI"):
        inst_id = inst_map[inst_short]
        dept_reviewers = {
            u["id"]: dept_map.get((inst_short, code))
            for e, u in user_map.items()
            for code, _ in DEPARTMENTS
            if u["inst_short"] == inst_short and u["role_name"] == "Department Reviewer"
        }
        co_id = next(u["id"] for e, u in user_map.items()
                     if u["inst_short"] == inst_short and u["role_name"] == "Compliance Officer")

        # 100 evidence docs per institution
        inst_assignments = [(ctrl_id, aid) for (s, ctrl_id), aid in assignment_map.items()
                            if s == inst_short]
        random.shuffle(inst_assignments)
        sample = inst_assignments[:100]

        for ctrl_id, assignment_id in sample:
            ext = random.choices(ext_list, weights=ext_weights, k=1)[0]
            filename = f"evidence_{counter:04d}.{ext}"
            uploader_id = pick(list(dept_reviewers.keys())) if dept_reviewers else co_id
            dept_id = dept_reviewers.get(uploader_id)
            approval_status = weighted_status(
                ["pending", "approved", "rejected"], [30, 55, 15]
            )
            approved_by = co_id if approval_status in ("approved", "rejected") else None
            approved_at = days_ago(random.randint(1, 15)) if approval_status in ("approved", "rejected") else None
            rejection_reason = (
                "Evidence does not clearly demonstrate the required control. "
                "Please resubmit with a clearer screenshot showing the date and system name."
                if approval_status == "rejected" else None
            )
            rows.append((
                uid(), inst_id, ctrl_id, assignment_id, dept_id,
                filename,
                f"evidence-documents/{inst_id}/{assignment_id}/{filename}",
                ext_mime[ext],
                random.randint(50, 2500),
                f"Evidence for {ctrl_id}",
                uploader_id, approval_status, approved_by, approved_at, rejection_reason,
                days_ago(random.randint(1, 60)),
            ))
            counter += 1

    cur.executemany(
        """INSERT INTO evidence_documents
           (evidence_id, institution_id, control_id, assignment_id, department_id,
            file_name, file_path, mime_type, file_size_kb, description,
            uploaded_by, approval_status, approved_by, approved_at, rejection_reason,
            uploaded_at)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        rows,
    )
    print(f"[seed] Evidence documents: {len(rows)}")


# ── 4.15 Incidents ────────────────────────────────────────────────────────────
def seed_incidents(cur, inst_map: dict, user_map: dict) -> dict:
    """
    3 incidents per institution. Returns incident_map: {(inst_short, n): incident_id}
    """
    incident_map = {}
    rows = []
    for inst_short in ("BIT", "SEC", "NMTI"):
        inst_id = inst_map[inst_short]
        its_id = next(u["id"] for e, u in user_map.items()
                      if u["inst_short"] == inst_short and u["role_name"] == "IT Security Officer")
        for n, tmpl in enumerate(INCIDENT_TEMPLATES):
            iid = uid()
            incident_map[(inst_short, n)] = iid
            detected = days_ago(random.randint(1, 45))
            cert_deadline = detected + timedelta(hours=6)
            cert_reported_at = detected + timedelta(hours=5, minutes=30) if tmpl["cert_reported"] else None
            resolved_at = days_ago(random.randint(1, 20)) if tmpl["status"] == "resolved" else None
            rows.append((
                iid, inst_id, tmpl["title"],
                f"Incident detected on institution network. Initial investigation ongoing. "
                f"Security team has been notified and is responding per incident response plan.",
                tmpl["type"], tmpl["severity"], tmpl["status"],
                detected - timedelta(hours=random.randint(1, 3)),
                detected, cert_deadline,
                tmpl["cert_reported"], cert_reported_at,
                tmpl["dpdp_required"],
                detected + timedelta(hours=4) if tmpl["dpdp_required"] and tmpl["cert_reported"] else None,
                tmpl["systems"], tmpl["data"],
                its_id, its_id, resolved_at,
                "Incident contained. Affected systems have been isolated and restored from clean backups. "
                "Post-incident review scheduled." if resolved_at else None,
            ))

    cur.executemany(
        """INSERT INTO incidents
           (incident_id, institution_id, title, description, incident_type, severity,
            status, occurred_at, detected_at, cert_in_deadline, cert_in_reported,
            cert_in_reported_at, dpdp_notification_required, dpdp_notified_at,
            affected_systems, affected_data_categories, reported_by, assigned_to,
            resolved_at, resolution_notes)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        rows,
    )
    print(f"[seed] Incidents: {len(rows)}")
    return incident_map


# ── 4.16 Incident Timeline ────────────────────────────────────────────────────
def seed_incident_timeline(cur, incident_map: dict, user_map: dict):
    timeline_entries = [
        "Incident detected. Initial triage initiated. Security team notified.",
        "Affected systems identified and isolated from main network.",
        "Forensic analysis initiated. Evidence preservation in progress.",
        "CERT-In notification drafted and reviewed by compliance team.",
        "CERT-In report submitted via official portal. Reference number obtained.",
        "Containment measures verified. Systems undergoing clean restore.",
        "Post-incident review meeting scheduled with all stakeholders.",
    ]
    rows = []
    for (inst_short, n), incident_id in incident_map.items():
        its_id = next(u["id"] for e, u in user_map.items()
                      if u["inst_short"] == inst_short and u["role_name"] == "IT Security Officer")
        base_time = days_ago(random.randint(5, 40))
        for i, action in enumerate(pick_n(timeline_entries, 5)):
            rows.append((
                uid(), incident_id, action, its_id,
                base_time + timedelta(hours=i * 2),
            ))
    cur.executemany(
        "INSERT INTO incident_timeline (timeline_id, incident_id, action_taken, action_by, action_at) VALUES (%s,%s,%s,%s,%s)",
        rows,
    )
    print(f"[seed] Incident timeline entries: {len(rows)}")


# ── 4.17 Vendors ─────────────────────────────────────────────────────────────
def seed_vendors(cur, inst_map: dict, user_map: dict) -> dict:
    vendor_map = {}
    rows = []
    for inst_short, vendors in VENDOR_DATA.items():
        inst_id = inst_map[inst_short]
        vr_id = next(u["id"] for e, u in user_map.items()
                     if u["inst_short"] == inst_short and u["role_name"] == "Vendor Reviewer")
        for v in vendors:
            vid = uid()
            vendor_map[(inst_short, v["name"])] = vid
            expiry = days_from_now(v["expiry_days"]).date()
            rows.append((
                vid, inst_id, v["name"], v["product"], v["category"],
                v["location"], v["dpa"], v["model_train"], expiry,
                f"vendor@{v['name'].lower().replace(' ', '')}.com", vr_id,
            ))
    cur.executemany(
        """INSERT INTO vendors
           (vendor_id, institution_id, vendor_name, product_name, vendor_category,
            processing_location, dpa_available, model_training_allowed,
            contract_expiry_date, contact_email, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        rows,
    )
    print(f"[seed] Vendors: {len(rows)}")
    return vendor_map


# ── 4.18 Vendor Risk Assessments ─────────────────────────────────────────────
def seed_vendor_risk_assessments(cur, vendor_map: dict, user_map: dict, inst_map: dict):
    risk_levels = {
        "US":     "high",
        "EU":     "medium",
        "India":  "low",
        "Other":  "critical",
    }
    rows = []
    for (inst_short, vendor_name), vendor_id in vendor_map.items():
        inst_id = inst_map[inst_short]
        vr_id = next(u["id"] for e, u in user_map.items()
                     if u["inst_short"] == inst_short and u["role_name"] == "Vendor Reviewer")
        # find vendor location from VENDOR_DATA
        v_data = next((v for v in VENDOR_DATA[inst_short] if v["name"] == vendor_name), None)
        if not v_data:
            continue
        risk = risk_levels.get(v_data["location"], "medium")
        dpdp_ok = v_data["dpa"] and not v_data["model_train"]
        rows.append((
            uid(), vendor_id, inst_id, risk,
            f"Vendor risk assessment completed. Data processing location: {v_data['location']}. "
            f"DPA available: {'Yes' if v_data['dpa'] else 'No'}. "
            f"Model training on data: {'Allowed — HIGH RISK' if v_data['model_train'] else 'Not allowed'}.",
            "Obtain DPA if not available. Verify data localization compliance. "
            "Review contract terms for DPDP Section 7 processor obligations.",
            dpdp_ok, vr_id,
        ))
    cur.executemany(
        """INSERT INTO vendor_risk_assessments
           (vendor_risk_id, vendor_id, institution_id, risk_level, assessment_summary,
            recommendations, dpdp_compliant, assessed_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        rows,
    )
    print(f"[seed] Vendor risk assessments: {len(rows)}")


# ── 4.19 Generated Policies ───────────────────────────────────────────────────
def seed_generated_policies(cur, inst_map: dict, user_map: dict) -> dict:
    """
    4 policies per institution. One policy has 2 versions (parent_policy_id chain).
    Returns policy_map: {(inst_short, n): policy_id}
    """
    policy_map = {}
    statuses = ["approved", "approved", "pending_approval", "rejected"]

    for inst_short in ("BIT", "SEC", "NMTI"):
        inst_id = inst_map[inst_short]
        co_id = next(u["id"] for e, u in user_map.items()
                     if u["inst_short"] == inst_short and u["role_name"] == "Compliance Officer")
        pa_id = next(u["id"] for e, u in user_map.items()
                     if u["inst_short"] == inst_short and u["role_name"] == "Policy Approver")
        parent_id = None

        for n, (pname, pstatus) in enumerate(zip(POLICY_TEMPLATES, statuses)):
            pid = uid()
            policy_map[(inst_short, n)] = pid
            approved_at = days_ago(random.randint(5, 30)) if pstatus == "approved" else None
            rejection_reason = (
                "Policy lacks specific data retention periods for different data categories. "
                "Please revise Section 3 to include explicit retention timelines."
                if pstatus == "rejected" else None
            )

            # Policy 0: create v1 (approved), then v2 (pending_approval)
            version = 1
            this_parent = None
            if n == 0:
                # v1
                pid_v1 = uid()
                policy_map[(inst_short, f"{n}_v1")] = pid_v1
                cur.execute(
                    """INSERT INTO generated_policies
                       (policy_id, institution_id, related_control_id, policy_name,
                        policy_content, version_number, policy_status, generated_by,
                        submitted_to, approved_by, approved_at, rejection_reason, parent_policy_id)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (pid_v1, inst_id, pick(list(CONTROL_POOL["DPDP Act 2023"])),
                     f"{pname} (v1)",
                     f"Policy content stored in MongoDB. Document ID: {pid_v1}",
                     1, "approved", co_id, pa_id, pa_id,
                     days_ago(60), None, None),
                )
                # v2 points to v1
                pid_v2 = uid()
                policy_map[(inst_short, n)] = pid_v2
                cur.execute(
                    """INSERT INTO generated_policies
                       (policy_id, institution_id, related_control_id, policy_name,
                        policy_content, version_number, policy_status, generated_by,
                        submitted_to, approved_by, approved_at, rejection_reason, parent_policy_id)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (pid_v2, inst_id, pick(list(CONTROL_POOL["DPDP Act 2023"])),
                     pname,
                     f"Policy content stored in MongoDB. Document ID: {pid_v2}",
                     2, "pending_approval", co_id, pa_id, None,
                     None, None, pid_v1),
                )
            else:
                cur.execute(
                    """INSERT INTO generated_policies
                       (policy_id, institution_id, related_control_id, policy_name,
                        policy_content, version_number, policy_status, generated_by,
                        submitted_to, approved_by, approved_at, rejection_reason, parent_policy_id)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (pid, inst_id,
                     pick(list(CONTROL_POOL["ISO 27001:2022"])),
                     pname,
                     f"Policy content stored in MongoDB. Document ID: {pid}",
                     version, pstatus, co_id,
                     pa_id if pstatus != "draft" else None,
                     pa_id if pstatus == "approved" else None,
                     approved_at, rejection_reason, None),
                )

    print(f"[seed] Generated policies: {len(policy_map)} entries (including versioned)")


# ── 4.20 Audit Observations ───────────────────────────────────────────────────
def seed_audit_observations(cur, assessment_map: dict, inst_map: dict, user_map: dict):
    obs_templates = [
        ("finding",        "Access control lists were not reviewed for 6 months. Multiple inactive accounts found with active privileges."),
        ("observation",    "Data classification policy exists but is not consistently applied across departments."),
        ("recommendation", "Implement automated access review tooling to reduce manual effort and ensure quarterly reviews are completed."),
        ("finding",        "Encryption at rest not implemented for student PII stored in the legacy database system."),
        ("observation",    "Incident response plan has not been tested via a tabletop exercise in the last 12 months."),
        ("recommendation", "Conduct quarterly phishing simulation exercises and track improvement over time."),
        ("finding",        "Vendor contracts do not include mandatory DPDP Act 2023 data processor clauses."),
        ("observation",    "Backup restoration has not been tested. Last verified restore was over 18 months ago."),
        ("recommendation", "Establish a formal change advisory board (CAB) process for IT changes above a defined risk threshold."),
        ("finding",        "Security awareness training completion rate is 43% — below the 90% policy target."),
    ]
    rows = []
    for inst_short in ("BIT", "SEC", "NMTI"):
        inst_id = inst_map[inst_short]
        auditor_id = next(u["id"] for e, u in user_map.items()
                          if u["inst_short"] == inst_short and u["role_name"] == "Auditor")
        assessment_id = assessment_map.get((inst_short, "DPDP"))
        controls_flat = [cid for ids in CONTROL_POOL.values() for cid in ids]

        for sev_type, obs_text in obs_templates:
            rows.append((
                uid(), inst_id, assessment_id,
                pick(controls_flat), None,
                obs_text, sev_type,
                weighted_status(["open", "acknowledged", "resolved"], [50, 30, 20]),
                auditor_id,
            ))

    cur.executemany(
        """INSERT INTO audit_observations
           (observation_id, institution_id, assessment_id, control_id, evidence_id,
            observation_text, severity, status, added_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        rows,
    )
    print(f"[seed] Audit observations: {len(rows)}")


# ── 4.21 Audit Reports ────────────────────────────────────────────────────────
def seed_audit_reports(cur, assessment_map: dict, inst_map: dict, user_map: dict):
    report_types = ["dpdp_assessment", "iso_readiness"]
    rows = []
    counter = 1
    for inst_short in ("BIT", "SEC", "NMTI"):
        inst_id = inst_map[inst_short]
        auditor_id = next(u["id"] for e, u in user_map.items()
                          if u["inst_short"] == inst_short and u["role_name"] == "Auditor")
        for fw_short, rtype in zip(("DPDP", "ISO"), report_types):
            assessment_id = assessment_map.get((inst_short, fw_short))
            if not assessment_id:
                continue
            filename = f"audit_report_{counter:04d}.pdf"
            rows.append((
                uid(), inst_id, assessment_id,
                f"{inst_short} {rtype.replace('_', ' ').title()} — 2025",
                rtype,
                f"audit-reports/{inst_id}/{assessment_id}/{filename}",
                auditor_id,
                days_ago(random.randint(1, 20)),
            ))
            counter += 1
    cur.executemany(
        """INSERT INTO audit_reports
           (report_id, institution_id, assessment_id, report_name, report_type,
            file_path, generated_by, generated_at)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
        rows,
    )
    print(f"[seed] Audit reports: {len(rows)}")


# ── 4.22 Compliance Calendar ─────────────────────────────────────────────────
def seed_compliance_calendar(cur, inst_map: dict, user_map: dict):
    event_configs = [
        ("control_due",           "control",    "DPDP Quarterly Control Review Due"),
        ("control_due",           "control",    "ISO 27001 Annual Control Verification"),
        ("assessment_scheduled",  "assessment", "NAAC Self-Study Assessment Due"),
        ("assessment_scheduled",  "assessment", "CERT-In Compliance Baseline Assessment"),
        ("evidence_expiry",       "control",    "Evidence Renewal: Access Control Logs"),
        ("evidence_expiry",       "control",    "Evidence Renewal: MFA Configuration"),
        ("policy_review",         "policy",     "Annual Data Protection Policy Review"),
        ("policy_review",         "policy",     "Incident Response Policy Review Cycle"),
        ("vendor_contract_expiry","vendor",      "Vendor Contract Renewal: Cloud Services"),
        ("vendor_contract_expiry","vendor",      "Vendor Contract Renewal: ERP System"),
        ("audit_scheduled",       "assessment", "Internal Audit Q3 2025"),
        ("audit_scheduled",       "assessment", "External ISO Certification Audit"),
        ("control_due",           "control",    "NIST CSF Risk Assessment Completion"),
        ("policy_review",         "policy",     "Acceptable Use Policy Annual Review"),
        ("evidence_expiry",       "control",    "Evidence Renewal: Backup Test Records"),
    ]
    rows = []
    for inst_short in ("BIT", "SEC", "NMTI"):
        inst_id = inst_map[inst_short]
        co_id = next(u["id"] for e, u in user_map.items()
                     if u["inst_short"] == inst_short and u["role_name"] == "Compliance Officer")
        for i, (etype, entity_type, title) in enumerate(event_configs):
            due = days_from_now(random.randint(-15, 90))
            completed = due < now() and random.random() > 0.4
            rows.append((
                uid(), inst_id, etype, entity_type, None,
                title, due, completed, co_id,
            ))
    cur.executemany(
        """INSERT INTO compliance_calendar
           (calendar_id, institution_id, event_type, related_entity_type, related_entity_id,
            title, due_date, is_completed, created_by)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        rows,
    )
    print(f"[seed] Calendar events: {len(rows)}")


# ── 4.23 Notifications ────────────────────────────────────────────────────────
def seed_notifications(cur, inst_map: dict, user_map: dict):
    notif_templates = [
        ("task_assigned",        "New Task Assigned",              "A new mitigation task has been assigned to you. Review and complete before the due date."),
        ("evidence_approved",    "Evidence Approved",              "Your submitted evidence has been reviewed and approved by the Compliance Officer."),
        ("evidence_rejected",    "Evidence Rejected — Action Required", "Your evidence submission was rejected. Please review the feedback and resubmit."),
        ("incident_logged",      "New Security Incident Logged",   "A new security incident has been logged and requires immediate attention."),
        ("policy_pending",       "Policy Awaiting Your Approval",  "A new policy draft has been submitted for your review and approval."),
        ("control_overdue",      "Control Assignment Overdue",     "One or more control assignments are past their due date. Immediate action required."),
        ("vendor_risk_flagged",  "High-Risk Vendor Identified",    "A vendor has been assessed as high risk. Review the assessment and take appropriate action."),
    ]
    rows = []
    for inst_short in ("BIT", "SEC", "NMTI"):
        inst_id = inst_map[inst_short]
        inst_users = [u for e, u in user_map.items() if u["inst_short"] == inst_short]

        # ~33 notifications per institution type × 3 inst ≈ 100 per inst
        for _ in range(100):
            ntype, title, message = pick(notif_templates)
            recipient = pick(inst_users)
            is_read = random.random() > 0.4  # 60% read
            rows.append((
                uid(), inst_id, recipient["id"],
                title, message, ntype,
                "mitigation_task", None, is_read,
                rnd_past(30),
            ))

    cur.executemany(
        """INSERT INTO notifications
           (notification_id, institution_id, user_id, title, message, notification_type,
            related_entity_type, related_entity_id, is_read, created_at)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        rows,
    )
    print(f"[seed] Notifications: {len(rows)}")


# ── 4.24 Audit Logs ───────────────────────────────────────────────────────────
def seed_audit_logs(cur, inst_map: dict, user_map: dict, role_map: dict):
    entity_types = ["control_assignment", "evidence_document", "incident",
                    "vendor", "policy", "mitigation_task", "assessment", "user"]
    rows = []
    for inst_short in ("BIT", "SEC", "NMTI"):
        inst_id = inst_map[inst_short]
        inst_users = [u for e, u in user_map.items() if u["inst_short"] == inst_short]

        # 500 logs per institution
        for _ in range(500):
            u = pick(inst_users)
            action = pick(AUDIT_LOG_ACTION_TYPES)
            entity_type = pick(entity_types)
            rows.append((
                uid(), inst_id, u["id"], role_map[u["role_name"]], None,
                action, entity_type, None,
                json.dumps({"detail": f"{action} performed by {u['full_name']}"}),
                f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
                rnd_past(90),
            ))

    cur.executemany(
        """INSERT INTO audit_logs
           (audit_log_id, institution_id, user_id, active_role_id,
            assumed_role_session_id, action_type, entity_type, entity_id,
            action_details, ip_address, created_at)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        rows,
    )
    print(f"[seed] Audit logs: {len(rows)}")


# ── 4.25 AI Conversations ────────────────────────────────────────────────────
def seed_ai_conversations(cur, inst_map: dict, user_map: dict):
    rows = []
    sample_pool = AI_CONVERSATION_SAMPLES * 10  # repeat to get enough for all insts

    for inst_short in ("BIT", "SEC", "NMTI"):
        inst_id = inst_map[inst_short]
        # pick users that use AI (CO, Assessors, IT Security)
        ai_users = [u for e, u in user_map.items()
                    if u["inst_short"] == inst_short and
                    u["role_name"] in ("Compliance Officer", "Read-Only Assessor", "IT Security Officer")]
        for i in range(10):
            tmpl = sample_pool[i % len(AI_CONVERSATION_SAMPLES)]
            u = pick(ai_users)
            rows.append((
                uid(), inst_id, u["id"],
                tmpl["agent_type"],
                json.dumps(tmpl["messages"]),
                rnd_past(30), rnd_past(10),
            ))

    cur.executemany(
        """INSERT INTO ai_conversations
           (conversation_id, institution_id, user_id, agent_type, messages, created_at, updated_at)
           VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        rows,
    )
    print(f"[seed] AI conversations: {len(rows)}")


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — MAIN
# ═══════════════════════════════════════════════════════════════════════════════

# ── Configure logging ────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stderr)],
)
log = logging.getLogger("seed")


def main():
    log.info("=" * 60)
    log.info(" ComplySense Seed Script")
    log.info("=" * 60)

    # ── Connect ──────────────────────────────────────────────────────────────
    try:
        conn = psycopg2.connect(DATABASE_URL)
    except psycopg2.OperationalError as conn_err:
        log.critical("Cannot connect to PostgreSQL — check DATABASE_URL in .env")
        log.critical("  Error: %s", conn_err)
        sys.exit(1)

    conn.autocommit = False          # single atomic transaction
    cur = conn.cursor()

    # Named steps — each tuple is (label, callable).  Order matters.
    # Callables return their result (or None); results are passed forward
    # via local variables so that later steps can reference earlier outputs.
    current_step = "(not started)"

    try:
        # ── Cleanup ──────────────────────────────────────────────────────────
        current_step = "cleanup"
        log.info("[1/22] %s", current_step)
        cleanup(cur)

        # ── Core reference data ──────────────────────────────────────────────
        current_step = "seed_roles"
        log.info("[2/22] %s", current_step)
        role_map = seed_roles(cur)

        current_step = "seed_permissions"
        log.info("[3/22] %s", current_step)
        perm_map = seed_permissions(cur)

        current_step = "seed_role_permissions"
        log.info("[4/22] %s", current_step)
        seed_role_permissions(cur, role_map, perm_map)

        # ── Institutions ─────────────────────────────────────────────────────
        current_step = "seed_institutions"
        log.info("[5/22] %s", current_step)
        inst_map = seed_institutions(cur)

        # ── Users ────────────────────────────────────────────────────────────
        current_step = "seed_users"
        log.info("[6/22] %s", current_step)
        user_map = seed_users(cur, inst_map, role_map)

        # ── Departments ──────────────────────────────────────────────────────
        current_step = "seed_departments"
        log.info("[7/22] %s", current_step)
        dept_map = seed_departments(cur, inst_map, user_map)

        # ── Role transitions ─────────────────────────────────────────────────
        current_step = "seed_allowed_transitions"
        log.info("[8/22] %s", current_step)
        seed_allowed_transitions(cur, role_map)

        # ── Control assignments ──────────────────────────────────────────────
        current_step = "seed_control_assignments"
        log.info("[9/22] %s", current_step)
        assignment_map = seed_control_assignments(cur, inst_map, user_map, dept_map)

        # ── Assessments ──────────────────────────────────────────────────────
        current_step = "seed_assessments"
        log.info("[10/22] %s", current_step)
        assessment_map = seed_assessments(cur, inst_map, user_map)

        current_step = "seed_assessment_responses"
        log.info("[11/22] %s", current_step)
        seed_assessment_responses(cur, assessment_map, user_map)

        current_step = "seed_compliance_results"
        log.info("[12/22] %s", current_step)
        seed_compliance_results(cur, assessment_map, inst_map)

        # ── Gaps & tasks ─────────────────────────────────────────────────────
        current_step = "seed_compliance_gaps"
        log.info("[13/22] %s", current_step)
        gap_map = seed_compliance_gaps(cur, assessment_map, inst_map)

        current_step = "seed_mitigation_tasks"
        log.info("[14/22] %s", current_step)
        seed_mitigation_tasks(cur, gap_map, assignment_map, user_map, dept_map, inst_map)

        # ── Evidence ─────────────────────────────────────────────────────────
        current_step = "seed_evidence_documents"
        log.info("[15/22] %s", current_step)
        seed_evidence_documents(cur, assignment_map, dept_map, user_map, inst_map)

        # ── Incidents ────────────────────────────────────────────────────────
        current_step = "seed_incidents"
        log.info("[16/22] %s", current_step)
        incident_map = seed_incidents(cur, inst_map, user_map)

        current_step = "seed_incident_timeline"
        log.info("[17/22] %s", current_step)
        seed_incident_timeline(cur, incident_map, user_map)

        # ── Vendors ──────────────────────────────────────────────────────────
        current_step = "seed_vendors"
        log.info("[18/22] %s", current_step)
        vendor_map = seed_vendors(cur, inst_map, user_map)

        current_step = "seed_vendor_risk_assessments"
        log.info("[19/22] %s", current_step)
        seed_vendor_risk_assessments(cur, vendor_map, user_map, inst_map)

        # ── Policies ─────────────────────────────────────────────────────────
        current_step = "seed_generated_policies"
        log.info("[20/22] %s", current_step)
        seed_generated_policies(cur, inst_map, user_map)

        # ── Audit observations & reports ─────────────────────────────────────
        current_step = "seed_audit_observations"
        log.info("[21/22] %s — audit_observations", current_step)
        seed_audit_observations(cur, assessment_map, inst_map, user_map)

        current_step = "seed_audit_reports"
        log.info("[21/22] %s — audit_reports", current_step)
        seed_audit_reports(cur, assessment_map, inst_map, user_map)

        # ── Calendar, notifications, audit logs, AI conversations ────────────
        current_step = "seed_compliance_calendar"
        log.info("[22/22] %s — calendar", current_step)
        seed_compliance_calendar(cur, inst_map, user_map)

        current_step = "seed_notifications"
        log.info("[22/22] %s — notifications", current_step)
        seed_notifications(cur, inst_map, user_map)

        current_step = "seed_audit_logs"
        log.info("[22/22] %s — audit_logs", current_step)
        seed_audit_logs(cur, inst_map, user_map, role_map)

        current_step = "seed_ai_conversations"
        log.info("[22/22] %s — ai_conversations", current_step)
        seed_ai_conversations(cur, inst_map, user_map)

        # ── Commit ───────────────────────────────────────────────────────────
        conn.commit()
        log.info("=" * 60)
        log.info(" ✅  Seed complete — ALL data committed successfully.")
        log.info("  Login with any seeded email using password: %s", _PWD)
        log.info("=" * 60)

    except Exception as exc:
        # ── INSTANT ROLLBACK — no partial data survives ──────────────────────
        conn.rollback()

        log.error("")
        log.error("=" * 60)
        log.error(" ❌  SEED FAILED — FULL ROLLBACK EXECUTED")
        log.error("=" * 60)
        log.error("  Failed during step : %s", current_step)
        log.error("  Exception type     : %s", type(exc).__name__)
        log.error("  Exception message  : %s", exc)

        # If it's a psycopg2 error, log the PostgreSQL-specific diagnostics
        if hasattr(exc, "pgcode"):
            log.error("  PostgreSQL code    : %s", exc.pgcode)
        if hasattr(exc, "pgerror") and exc.pgerror:
            log.error("  PostgreSQL detail  : %s", exc.pgerror.strip())
        if hasattr(exc, "diag") and exc.diag:
            diag = exc.diag
            if diag.table_name:
                log.error("  Table              : %s", diag.table_name)
            if diag.column_name:
                log.error("  Column             : %s", diag.column_name)
            if diag.constraint_name:
                log.error("  Constraint         : %s", diag.constraint_name)
            if diag.message_detail:
                log.error("  Detail             : %s", diag.message_detail)

        log.error("")
        log.error("--- Full Traceback ---")
        log.error(traceback.format_exc())
        log.error("--- End Traceback ----")
        log.error("")
        log.error("  No data was inserted. The database is unchanged.")
        log.error("  Fix the error above and re-run: python seed.py")
        log.error("=" * 60)

        sys.exit(1)

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()