--
-- PostgreSQL database dump
--

\restrict JnNdsgfJUEZ8hbldk8ZQbIcxrxwQqzHk4bUtVeTdTmAwepxDfZHxOBtgTile5i5

-- Dumped from database version 16.14 (7f2ba1b)
-- Dumped by pg_dump version 16.14

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: cs; Type: SCHEMA; Schema: -; Owner: neondb_owner
--

CREATE SCHEMA cs;


ALTER SCHEMA cs OWNER TO neondb_owner;

--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: assessment_response_value; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.assessment_response_value AS ENUM (
    'compliant',
    'partial',
    'non_compliant',
    'not_applicable'
);


ALTER TYPE public.assessment_response_value OWNER TO neondb_owner;

--
-- Name: assessment_status; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.assessment_status AS ENUM (
    'draft',
    'in_progress',
    'completed'
);


ALTER TYPE public.assessment_status OWNER TO neondb_owner;

--
-- Name: audit_status; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.audit_status AS ENUM (
    'planned',
    'in_progress',
    'completed'
);


ALTER TYPE public.audit_status OWNER TO neondb_owner;

--
-- Name: chat_role; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.chat_role AS ENUM (
    'user',
    'assistant'
);


ALTER TYPE public.chat_role OWNER TO neondb_owner;

--
-- Name: control_severity; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.control_severity AS ENUM (
    'critical',
    'high',
    'medium',
    'low'
);


ALTER TYPE public.control_severity OWNER TO neondb_owner;

--
-- Name: evidence_approval_status; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.evidence_approval_status AS ENUM (
    'pending',
    'approved',
    'rejected'
);


ALTER TYPE public.evidence_approval_status OWNER TO neondb_owner;

--
-- Name: finding_severity; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.finding_severity AS ENUM (
    'critical',
    'high',
    'medium',
    'low'
);


ALTER TYPE public.finding_severity OWNER TO neondb_owner;

--
-- Name: finding_status; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.finding_status AS ENUM (
    'open',
    'in_progress',
    'resolved',
    'closed'
);


ALTER TYPE public.finding_status OWNER TO neondb_owner;

--
-- Name: framework_type; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.framework_type AS ENUM (
    'dpdp',
    'iso27001',
    'iso27701',
    'nist_csf',
    'other'
);


ALTER TYPE public.framework_type OWNER TO neondb_owner;

--
-- Name: incident_severity; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.incident_severity AS ENUM (
    'critical',
    'high',
    'medium',
    'low'
);


ALTER TYPE public.incident_severity OWNER TO neondb_owner;

--
-- Name: incident_status; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.incident_status AS ENUM (
    'open',
    'investigating',
    'resolved',
    'closed'
);


ALTER TYPE public.incident_status OWNER TO neondb_owner;

--
-- Name: mitigation_status; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.mitigation_status AS ENUM (
    'todo',
    'in_progress',
    'done',
    'cancelled'
);


ALTER TYPE public.mitigation_status OWNER TO neondb_owner;

--
-- Name: policy_doc_status; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.policy_doc_status AS ENUM (
    'draft',
    'review',
    'approved',
    'rejected',
    'archived'
);


ALTER TYPE public.policy_doc_status OWNER TO neondb_owner;

--
-- Name: policy_status; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.policy_status AS ENUM (
    'draft',
    'submitted',
    'approved',
    'rejected'
);


ALTER TYPE public.policy_status OWNER TO neondb_owner;

--
-- Name: remediation_task_status; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.remediation_task_status AS ENUM (
    'pending',
    'in_progress',
    'completed'
);


ALTER TYPE public.remediation_task_status OWNER TO neondb_owner;

--
-- Name: risk_status; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.risk_status AS ENUM (
    'open',
    'mitigated',
    'accepted',
    'closed'
);


ALTER TYPE public.risk_status OWNER TO neondb_owner;

--
-- Name: vendor_risk_level; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.vendor_risk_level AS ENUM (
    'low',
    'medium',
    'high',
    'critical'
);


ALTER TYPE public.vendor_risk_level OWNER TO neondb_owner;

--
-- Name: vendor_status; Type: TYPE; Schema: public; Owner: neondb_owner
--

CREATE TYPE public.vendor_status AS ENUM (
    'active',
    'inactive',
    'under_review'
);


ALTER TYPE public.vendor_status OWNER TO neondb_owner;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: assessment_responses; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.assessment_responses (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.assessment_responses OWNER TO neondb_owner;

--
-- Name: assessments; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.assessments (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.assessments OWNER TO neondb_owner;

--
-- Name: audit_logs; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.audit_logs (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.audit_logs OWNER TO neondb_owner;

--
-- Name: audits; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.audits (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.audits OWNER TO neondb_owner;

--
-- Name: chat_messages; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.chat_messages (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.chat_messages OWNER TO neondb_owner;

--
-- Name: chat_sessions; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.chat_sessions (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.chat_sessions OWNER TO neondb_owner;

--
-- Name: control_assignments; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.control_assignments (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.control_assignments OWNER TO neondb_owner;

--
-- Name: controls; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.controls (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.controls OWNER TO neondb_owner;

--
-- Name: departments; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.departments (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.departments OWNER TO neondb_owner;

--
-- Name: document_analyses; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.document_analyses (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.document_analyses OWNER TO neondb_owner;

--
-- Name: evidence; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.evidence (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.evidence OWNER TO neondb_owner;

--
-- Name: findings; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.findings (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.findings OWNER TO neondb_owner;

--
-- Name: frameworks; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.frameworks (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.frameworks OWNER TO neondb_owner;

--
-- Name: incidents; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.incidents (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.incidents OWNER TO neondb_owner;

--
-- Name: notifications; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.notifications (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.notifications OWNER TO neondb_owner;

--
-- Name: organizations; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.organizations (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.organizations OWNER TO neondb_owner;

--
-- Name: password_resets; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.password_resets (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.password_resets OWNER TO neondb_owner;

--
-- Name: policies; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.policies (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.policies OWNER TO neondb_owner;

--
-- Name: policy_approvals; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.policy_approvals (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.policy_approvals OWNER TO neondb_owner;

--
-- Name: policy_sessions; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.policy_sessions (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.policy_sessions OWNER TO neondb_owner;

--
-- Name: policy_versions; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.policy_versions (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.policy_versions OWNER TO neondb_owner;

--
-- Name: remediation_tasks; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.remediation_tasks (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.remediation_tasks OWNER TO neondb_owner;

--
-- Name: risk_treatments; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.risk_treatments (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.risk_treatments OWNER TO neondb_owner;

--
-- Name: risks; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.risks (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.risks OWNER TO neondb_owner;

--
-- Name: user_preferences; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.user_preferences (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.user_preferences OWNER TO neondb_owner;

--
-- Name: users; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.users (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.users OWNER TO neondb_owner;

--
-- Name: vendor_assessments; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.vendor_assessments (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.vendor_assessments OWNER TO neondb_owner;

--
-- Name: vendors; Type: TABLE; Schema: cs; Owner: neondb_owner
--

CREATE TABLE cs.vendors (
    id text NOT NULL,
    data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE cs.vendors OWNER TO neondb_owner;

--
-- Name: ai_conversations; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.ai_conversations (
    conversation_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    institution_id uuid,
    user_id uuid,
    agent_type character varying(100) NOT NULL,
    messages jsonb DEFAULT '[]'::jsonb NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.ai_conversations OWNER TO neondb_owner;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO neondb_owner;

--
-- Name: assessment_responses; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.assessment_responses (
    id uuid NOT NULL,
    assessment_id uuid NOT NULL,
    control_id uuid NOT NULL,
    response public.assessment_response_value NOT NULL,
    notes text,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.assessment_responses OWNER TO neondb_owner;

--
-- Name: assessments; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.assessments (
    id uuid NOT NULL,
    org_id uuid NOT NULL,
    framework_id uuid NOT NULL,
    title character varying(255) NOT NULL,
    status public.assessment_status NOT NULL,
    overall_score numeric(5,2),
    maturity_level integer,
    due_date date,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.assessments OWNER TO neondb_owner;

--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.audit_logs (
    id uuid NOT NULL,
    org_id uuid,
    user_id uuid,
    user_email character varying(255) NOT NULL,
    action character varying(120) NOT NULL,
    resource_type character varying(120) NOT NULL,
    resource_id character varying(120),
    ip_address character varying(60),
    metadata jsonb,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_logs OWNER TO neondb_owner;

--
-- Name: audit_observations; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.audit_observations (
    id uuid NOT NULL,
    institution_id uuid NOT NULL,
    audit_id uuid NOT NULL,
    control_id character varying(120) NOT NULL,
    observed_by uuid NOT NULL,
    observation_text text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_observations OWNER TO neondb_owner;

--
-- Name: audit_reports; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.audit_reports (
    id uuid NOT NULL,
    institution_id uuid NOT NULL,
    audit_id uuid NOT NULL,
    generated_by uuid NOT NULL,
    report_data jsonb NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audit_reports OWNER TO neondb_owner;

--
-- Name: audits; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.audits (
    id uuid NOT NULL,
    org_id uuid NOT NULL,
    title character varying(500) NOT NULL,
    framework_id uuid,
    auditor_id uuid,
    status public.audit_status NOT NULL,
    start_date date,
    end_date date,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.audits OWNER TO neondb_owner;

--
-- Name: chat_messages; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.chat_messages (
    id uuid NOT NULL,
    session_id character varying(80) NOT NULL,
    user_id uuid NOT NULL,
    role public.chat_role NOT NULL,
    content text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.chat_messages OWNER TO neondb_owner;

--
-- Name: control_assignments; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.control_assignments (
    id uuid NOT NULL,
    institution_id uuid NOT NULL,
    control_id character varying(120) NOT NULL,
    assigned_to_user_id uuid,
    department_id uuid,
    status character varying(40) NOT NULL,
    due_date date,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.control_assignments OWNER TO neondb_owner;

--
-- Name: controls; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.controls (
    id uuid NOT NULL,
    framework_id uuid NOT NULL,
    control_id character varying(120) NOT NULL,
    title character varying(500) NOT NULL,
    domain character varying(255),
    description text,
    severity public.control_severity NOT NULL,
    keywords character varying[],
    evidence_required character varying[],
    maturity_weight numeric(4,2),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.controls OWNER TO neondb_owner;

--
-- Name: departments; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.departments (
    id uuid NOT NULL,
    org_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    head_user_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.departments OWNER TO neondb_owner;

--
-- Name: document_analyses; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.document_analyses (
    id uuid NOT NULL,
    org_id uuid NOT NULL,
    user_id uuid NOT NULL,
    filename character varying(500) NOT NULL,
    file_size bigint NOT NULL,
    hash_sha256 character varying(64),
    storage_path character varying(1024) NOT NULL,
    framework_key character varying(120),
    analysis_md text NOT NULL,
    used_ai boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.document_analyses OWNER TO neondb_owner;

--
-- Name: evidence_documents; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.evidence_documents (
    id uuid NOT NULL,
    institution_id uuid NOT NULL,
    control_assignment_id uuid,
    uploaded_by uuid NOT NULL,
    file_path character varying(1024) NOT NULL,
    file_name character varying(255) NOT NULL,
    mime_type character varying(120) NOT NULL,
    file_size bigint,
    sha256 character varying(64),
    title character varying(255),
    approval_status public.evidence_approval_status NOT NULL,
    approved_by uuid,
    approved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.evidence_documents OWNER TO neondb_owner;

--
-- Name: findings; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.findings (
    id uuid NOT NULL,
    org_id uuid NOT NULL,
    title character varying(500) NOT NULL,
    description text,
    severity public.finding_severity NOT NULL,
    status public.finding_status NOT NULL,
    source character varying(120),
    control_ref character varying(120),
    assigned_to uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.findings OWNER TO neondb_owner;

--
-- Name: frameworks; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.frameworks (
    id uuid NOT NULL,
    org_id uuid,
    name character varying(255) NOT NULL,
    version character varying(40) NOT NULL,
    type public.framework_type NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.frameworks OWNER TO neondb_owner;

--
-- Name: generated_policies; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.generated_policies (
    id uuid NOT NULL,
    institution_id uuid NOT NULL,
    title character varying(255) NOT NULL,
    content text NOT NULL,
    policy_status public.policy_status NOT NULL,
    created_by uuid NOT NULL,
    submitted_to uuid,
    approved_by uuid,
    approved_at timestamp with time zone,
    rejection_reason text,
    parent_policy_id uuid,
    version integer NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.generated_policies OWNER TO neondb_owner;

--
-- Name: incidents; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.incidents (
    id uuid NOT NULL,
    org_id uuid NOT NULL,
    title character varying(500) NOT NULL,
    description text,
    severity public.incident_severity NOT NULL,
    status public.incident_status NOT NULL,
    reported_by uuid,
    cert_in_notified boolean NOT NULL,
    dpdp_notified boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.incidents OWNER TO neondb_owner;

--
-- Name: institutions; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.institutions (
    id uuid NOT NULL,
    name character varying(255) NOT NULL,
    slug character varying(120) NOT NULL,
    subscription_tier character varying(40) NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.institutions OWNER TO neondb_owner;

--
-- Name: mitigation_tasks; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.mitigation_tasks (
    id uuid NOT NULL,
    institution_id uuid NOT NULL,
    finding_id uuid NOT NULL,
    assigned_to uuid,
    status public.mitigation_status NOT NULL,
    due_date date,
    completed_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.mitigation_tasks OWNER TO neondb_owner;

--
-- Name: notifications; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.notifications (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    org_id uuid NOT NULL,
    type character varying(60) NOT NULL,
    title character varying(255),
    message text NOT NULL,
    is_read boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.notifications OWNER TO neondb_owner;

--
-- Name: password_resets; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.password_resets (
    id uuid NOT NULL,
    user_id uuid NOT NULL,
    token_hash character varying(128) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    used boolean NOT NULL,
    purpose character varying(40),
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.password_resets OWNER TO neondb_owner;

--
-- Name: permissions; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.permissions (
    id uuid NOT NULL,
    name character varying(120) NOT NULL,
    description text
);


ALTER TABLE public.permissions OWNER TO neondb_owner;

--
-- Name: policies; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.policies (
    id uuid NOT NULL,
    org_id uuid NOT NULL,
    title character varying(500) NOT NULL,
    policy_type character varying(120) NOT NULL,
    status public.policy_doc_status NOT NULL,
    content_md text NOT NULL,
    framework_ref character varying(120),
    created_by uuid,
    approved_by uuid,
    approved_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.policies OWNER TO neondb_owner;

--
-- Name: policy_versions; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.policy_versions (
    id uuid NOT NULL,
    policy_id uuid NOT NULL,
    version_number integer NOT NULL,
    content_md text NOT NULL,
    change_note text,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.policy_versions OWNER TO neondb_owner;

--
-- Name: remediation_tasks; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.remediation_tasks (
    id uuid NOT NULL,
    finding_id uuid NOT NULL,
    org_id uuid NOT NULL,
    title character varying(500) NOT NULL,
    description text,
    status public.remediation_task_status NOT NULL,
    assigned_to uuid,
    due_date date,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.remediation_tasks OWNER TO neondb_owner;

--
-- Name: risk_treatments; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.risk_treatments (
    id uuid NOT NULL,
    risk_id uuid NOT NULL,
    treatment_type character varying(60) NOT NULL,
    description text,
    created_by uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.risk_treatments OWNER TO neondb_owner;

--
-- Name: risks; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.risks (
    id uuid NOT NULL,
    org_id uuid NOT NULL,
    title character varying(500) NOT NULL,
    description text,
    category character varying(120),
    likelihood integer NOT NULL,
    impact integer NOT NULL,
    inherent_score integer NOT NULL,
    status public.risk_status NOT NULL,
    owner_id uuid,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.risks OWNER TO neondb_owner;

--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.role_permissions (
    role_id uuid NOT NULL,
    permission_id uuid NOT NULL
);


ALTER TABLE public.role_permissions OWNER TO neondb_owner;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.roles (
    id uuid NOT NULL,
    institution_id uuid NOT NULL,
    name character varying(80) NOT NULL,
    is_system_role boolean NOT NULL
);


ALTER TABLE public.roles OWNER TO neondb_owner;

--
-- Name: users; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.users (
    id uuid NOT NULL,
    institution_id uuid NOT NULL,
    email character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    full_name character varying(255) NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    failed_login_attempts integer DEFAULT 0 NOT NULL,
    blocked_until timestamp without time zone
);


ALTER TABLE public.users OWNER TO neondb_owner;

--
-- Name: vendor_assessments; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vendor_assessments (
    id uuid NOT NULL,
    vendor_id uuid NOT NULL,
    org_id uuid NOT NULL,
    score integer NOT NULL,
    findings jsonb,
    notes text,
    assessed_by uuid,
    assessment_date date,
    next_review_date date,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.vendor_assessments OWNER TO neondb_owner;

--
-- Name: vendors; Type: TABLE; Schema: public; Owner: neondb_owner
--

CREATE TABLE public.vendors (
    id uuid NOT NULL,
    org_id uuid NOT NULL,
    name character varying(255) NOT NULL,
    category character varying(120),
    contact_email character varying(255),
    risk_level public.vendor_risk_level NOT NULL,
    status public.vendor_status NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE public.vendors OWNER TO neondb_owner;

--
-- Data for Name: assessment_responses; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.assessment_responses (id, data, created_at) FROM stdin;
44199814-c98a-49f1-b3dd-3aa565eb262d	{"id": "44199814-c98a-49f1-b3dd-3aa565eb262d", "score": 1.0, "response": "compliant", "control_id": "ff2baf56-c790-4ec3-8ae9-d3ebcba31912", "created_at": "2026-06-05T05:47:18.123912+00:00", "updated_at": "2026-06-05T05:47:18.123912+00:00", "reviewed_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "control_code": "DPDP-S4-C1", "assessment_id": "219984d9-5d21-4017-814c-961146a321f1", "evidence_notes": "TEST"}	2026-06-05 05:47:18.888668+00
3881c418-cea5-4550-9798-9c4a266d1eba	{"id": "3881c418-cea5-4550-9798-9c4a266d1eba", "score": 1.0, "response": "compliant", "control_id": "ff2baf56-c790-4ec3-8ae9-d3ebcba31912", "created_at": "2026-06-05T05:55:00.074261+00:00", "updated_at": "2026-06-05T05:55:00.074261+00:00", "reviewed_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "control_code": "DPDP-S4-C1", "assessment_id": "8215bdeb-89ea-4daa-9be6-462d0df294bf", "evidence_notes": "TEST"}	2026-06-05 05:55:00.846107+00
a588ed4f-16e5-4b70-8bc7-815c5c54c7e2	{"id": "a588ed4f-16e5-4b70-8bc7-815c5c54c7e2", "score": 1.0, "response": "compliant", "control_id": "2969ac11-a93b-420a-b6c7-eef8b8efb0dc", "created_at": "2026-06-07T18:09:11.292399+00:00", "updated_at": "2026-06-07T18:09:11.292399+00:00", "reviewed_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "control_code": "ISO27701-6.2", "assessment_id": "7982833f-733c-4443-86ae-b13ff6ec72ca", "evidence_notes": ""}	2026-06-07 18:09:11.617582+00
f74085e3-31cf-418b-a235-9a1bcc145a9f	{"id": "f74085e3-31cf-418b-a235-9a1bcc145a9f", "score": 1.0, "response": "compliant", "control_id": "ad740353-e0fd-4e81-b2e7-09699c956f71", "created_at": "2026-06-07T18:09:17.964031+00:00", "updated_at": "2026-06-07T18:09:17.964031+00:00", "reviewed_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "control_code": "ISO27701-7.2.2", "assessment_id": "7982833f-733c-4443-86ae-b13ff6ec72ca", "evidence_notes": ""}	2026-06-07 18:09:18.322113+00
46c63e38-3129-4103-b732-b06a0dad6bdc	{"id": "46c63e38-3129-4103-b732-b06a0dad6bdc", "score": 1.0, "response": "compliant", "control_id": "0c4c9e19-0f17-45a9-8b22-15e9c7fcf003", "created_at": "2026-06-07T18:09:24.053397+00:00", "updated_at": "2026-06-07T18:09:24.053397+00:00", "reviewed_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "control_code": "ISO27701-7.3.4", "assessment_id": "7982833f-733c-4443-86ae-b13ff6ec72ca", "evidence_notes": ""}	2026-06-07 18:09:24.378864+00
b8eb2e45-4478-4a68-844e-96becc213952	{"id": "b8eb2e45-4478-4a68-844e-96becc213952", "score": 1.0, "response": "compliant", "control_id": "7a4edc19-9425-4ba5-bf51-f681d1cf74be", "created_at": "2026-06-07T18:09:29.039662+00:00", "updated_at": "2026-06-07T18:09:29.039662+00:00", "reviewed_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "control_code": "ISO27701-7.4.7", "assessment_id": "7982833f-733c-4443-86ae-b13ff6ec72ca", "evidence_notes": ""}	2026-06-07 18:09:29.357581+00
3beb3d51-02f5-4bfd-b101-f0bfca3e0ede	{"id": "3beb3d51-02f5-4bfd-b101-f0bfca3e0ede", "score": 1.0, "response": "compliant", "control_id": "8bf66023-5e80-4075-a773-6221b5606dc7", "created_at": "2026-06-07T18:09:32.938560+00:00", "updated_at": "2026-06-07T18:09:32.938560+00:00", "reviewed_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "control_code": "ISO27701-7.5.1", "assessment_id": "7982833f-733c-4443-86ae-b13ff6ec72ca", "evidence_notes": ""}	2026-06-07 18:09:33.260274+00
\.


--
-- Data for Name: assessments; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.assessments (id, data, created_at) FROM stdin;
bfc1c9a5-d452-4cd0-90ed-727edd8e033f	{"id": "bfc1c9a5-d452-4cd0-90ed-727edd8e033f", "name": "DPDP Baseline 2025", "scope": {"departments": ["Administration", "IT", "Examination"]}, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "completed", "created_at": "2026-06-05T05:30:58.695838+00:00", "started_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "completed_at": "2026-06-05T05:30:58.695838+00:00", "conducted_by": null, "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "overall_score": 62.5, "framework_name": "DPDP Act 2023", "maturity_level": 3}	2026-06-05 05:32:21.420686+00
bc34c07f-03fc-463a-85ae-68c69d8157fa	{"id": "bc34c07f-03fc-463a-85ae-68c69d8157fa", "name": "ISO 27001 Internal Audit Q1", "scope": {"departments": ["IT", "HR"]}, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "in_progress", "created_at": "2026-06-05T05:30:58.695838+00:00", "started_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "completed_at": null, "conducted_by": null, "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "overall_score": 48.0, "framework_name": "ISO 27001:2022", "maturity_level": 2}	2026-06-05 05:32:22.081064+00
219984d9-5d21-4017-814c-961146a321f1	{"id": "219984d9-5d21-4017-814c-961146a321f1", "name": "TEST Assessment 1780638431", "scope": {"description": "test"}, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "in_progress", "created_at": "2026-06-05T05:47:12.571246+00:00", "started_at": "2026-06-05T05:47:12.571246+00:00", "updated_at": "2026-06-05T05:47:20.084685+00:00", "completed_at": null, "conducted_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "overall_score": 100.0, "framework_name": "DPDP Act 2023", "maturity_level": 5}	2026-06-05 05:47:12.684752+00
8215bdeb-89ea-4daa-9be6-462d0df294bf	{"id": "8215bdeb-89ea-4daa-9be6-462d0df294bf", "name": "TEST Assessment 1780638893", "scope": {"description": "test"}, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "in_progress", "created_at": "2026-06-05T05:54:54.703536+00:00", "started_at": "2026-06-05T05:54:54.703536+00:00", "updated_at": "2026-06-05T05:55:02.048976+00:00", "completed_at": null, "conducted_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "overall_score": 100.0, "framework_name": "DPDP Act 2023", "maturity_level": 5}	2026-06-05 05:54:54.818033+00
7982833f-733c-4443-86ae-b13ff6ec72ca	{"id": "7982833f-733c-4443-86ae-b13ff6ec72ca", "name": "ram singh", "scope": {}, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "completed", "created_at": "2026-06-07T18:09:06.594127+00:00", "started_at": "2026-06-07T18:09:06.594127+00:00", "updated_at": "2026-06-07T18:09:33.702638+00:00", "completed_at": "2026-06-07T18:09:14.209251+00:00", "conducted_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "framework_id": "eed067e5-85ba-4db6-9362-402f615f5830", "overall_score": 100.0, "framework_name": "ISO 27701:2019", "maturity_level": 5}	2026-06-07 18:09:06.658152+00
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.audit_logs (id, data, created_at) FROM stdin;
a825a7f2-aa8c-4938-a474-b0b8cb754cf4	{"id": "a825a7f2-aa8c-4938-a474-b0b8cb754cf4", "action": "risks.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/risks", "method": "POST"}, "created_at": "2026-06-05T05:33:43.201055+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "risks"}	2026-06-05 05:33:43.315227+00
d3f26aae-8645-4159-938b-1460c05f06dd	{"id": "d3f26aae-8645-4159-938b-1460c05f06dd", "action": "settings.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/settings/user-preferences", "method": "PUT"}, "created_at": "2026-06-05T05:33:46.715186+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "user-preferences", "resource_type": "settings"}	2026-06-05 05:33:46.829411+00
cc11c282-a58e-4052-8f39-cf26b0e49656	{"id": "cc11c282-a58e-4052-8f39-cf26b0e49656", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-05T05:34:12.439426+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-05 05:34:12.553666+00
bf266356-ad85-45d1-b8a6-20dd76d4fe5e	{"id": "bf266356-ad85-45d1-b8a6-20dd76d4fe5e", "action": "controls.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/controls/search", "method": "POST"}, "created_at": "2026-06-05T05:42:22.318006+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "search", "resource_type": "controls"}	2026-06-05 05:42:22.432608+00
a7346ea5-d273-44ed-b2d4-e4ca048be95a	{"id": "a7346ea5-d273-44ed-b2d4-e4ca048be95a", "action": "risks.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/risks", "method": "POST"}, "created_at": "2026-06-05T05:42:39.218960+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": null, "resource_type": "risks"}	2026-06-05 05:42:39.333474+00
b3c7987d-aea4-4382-8b73-e11afd08fcbf	{"id": "b3c7987d-aea4-4382-8b73-e11afd08fcbf", "action": "risks.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/risks/823b0e0a-cc55-468e-9beb-0702f544a746", "method": "PUT"}, "created_at": "2026-06-05T05:42:43.431912+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "823b0e0a-cc55-468e-9beb-0702f544a746", "resource_type": "risks"}	2026-06-05 05:42:43.546306+00
c9b0b2d6-41ce-437a-aa53-61919a6d2b75	{"id": "c9b0b2d6-41ce-437a-aa53-61919a6d2b75", "action": "findings.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/findings", "method": "POST"}, "created_at": "2026-06-05T05:42:50.247311+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": null, "resource_type": "findings"}	2026-06-05 05:42:50.361905+00
293a2184-f3f8-4f50-a6a7-c9324877c428	{"id": "293a2184-f3f8-4f50-a6a7-c9324877c428", "action": "findings.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/findings/96d81b80-ce4c-4ea6-a168-41788d9bee8b", "method": "PUT"}, "created_at": "2026-06-05T05:42:53.795459+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "96d81b80-ce4c-4ea6-a168-41788d9bee8b", "resource_type": "findings"}	2026-06-05 05:42:53.909867+00
71b6fc60-4b85-42bc-8e23-5ebf02228dc4	{"id": "71b6fc60-4b85-42bc-8e23-5ebf02228dc4", "action": "remediation-tasks.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/remediation-tasks/f82e42e8-78e1-4fdd-9f6f-c4f04a152e17", "method": "PUT"}, "created_at": "2026-06-05T05:43:01.542415+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "f82e42e8-78e1-4fdd-9f6f-c4f04a152e17", "resource_type": "remediation-tasks"}	2026-06-05 05:43:01.657628+00
07f05140-31f7-44c2-95b6-b1b145021388	{"id": "07f05140-31f7-44c2-95b6-b1b145021388", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/generate-ai", "method": "POST"}, "created_at": "2026-06-05T05:43:09.171791+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "generate-ai", "resource_type": "policies"}	2026-06-05 05:43:09.287082+00
8c15131e-69f8-4f27-89c4-0c8f397b0127	{"id": "8c15131e-69f8-4f27-89c4-0c8f397b0127", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/generate-ai", "method": "POST"}, "created_at": "2026-06-05T05:43:11.854723+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "generate-ai", "resource_type": "policies"}	2026-06-05 05:43:11.970287+00
3aa58fda-8744-4540-b9c1-4d9bfc6e9cfb	{"id": "3aa58fda-8744-4540-b9c1-4d9bfc6e9cfb", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/generate-ai", "method": "POST"}, "created_at": "2026-06-05T05:43:14.541603+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "generate-ai", "resource_type": "policies"}	2026-06-05 05:43:14.656935+00
10dddb50-15fb-4784-a26d-a8aa82a5e9ef	{"id": "10dddb50-15fb-4784-a26d-a8aa82a5e9ef", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/generate-ai", "method": "POST"}, "created_at": "2026-06-05T05:43:17.225579+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "generate-ai", "resource_type": "policies"}	2026-06-05 05:43:17.339556+00
cde5c2a1-8732-4fe3-ba4d-bc90c177e7a5	{"id": "cde5c2a1-8732-4fe3-ba4d-bc90c177e7a5", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/generate-ai", "method": "POST"}, "created_at": "2026-06-05T05:43:19.897002+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "generate-ai", "resource_type": "policies"}	2026-06-05 05:43:20.011005+00
bc9470d8-2ddb-4546-9c81-05cd88b43023	{"id": "bc9470d8-2ddb-4546-9c81-05cd88b43023", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/generate-ai", "method": "POST"}, "created_at": "2026-06-05T05:43:22.567645+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "generate-ai", "resource_type": "policies"}	2026-06-05 05:43:22.683065+00
b03c2050-6438-4127-b08d-b78468055280	{"id": "b03c2050-6438-4127-b08d-b78468055280", "action": "policies.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/4465c968-03c8-4553-9ce8-9db59d03c14f", "method": "PUT"}, "created_at": "2026-06-05T05:43:28.819541+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "4465c968-03c8-4553-9ce8-9db59d03c14f", "resource_type": "policies"}	2026-06-05 05:43:28.934804+00
36ec25de-6519-4f37-8d68-1d6c627d031d	{"id": "36ec25de-6519-4f37-8d68-1d6c627d031d", "action": "vendors.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/vendors/8ddf017f-dc02-4aa5-a18b-19e45ffc4ed2/assess", "method": "POST"}, "created_at": "2026-06-05T05:43:40.574875+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "8ddf017f-dc02-4aa5-a18b-19e45ffc4ed2", "resource_type": "vendors"}	2026-06-05 05:43:40.690294+00
99a16a08-608f-4e2a-b30a-3535ffe352b6	{"id": "99a16a08-608f-4e2a-b30a-3535ffe352b6", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-05T05:43:57.638569+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-05 05:43:57.753831+00
b9d80e74-d9a8-4408-930b-657438e620b3	{"id": "b9d80e74-d9a8-4408-930b-657438e620b3", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/gap-analysis", "method": "POST"}, "created_at": "2026-06-05T05:44:03.888891+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "gap-analysis", "resource_type": "ai"}	2026-06-05 05:44:04.00418+00
4369ba2b-a576-4fac-96cf-e9cb4b67a01c	{"id": "4369ba2b-a576-4fac-96cf-e9cb4b67a01c", "action": "users.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/users", "method": "POST"}, "created_at": "2026-06-05T05:44:22.256630+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": null, "resource_type": "users"}	2026-06-05 05:44:22.372053+00
d8496560-a40a-41d4-8c3e-e2e3dd2c8e4f	{"id": "d8496560-a40a-41d4-8c3e-e2e3dd2c8e4f", "action": "users.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/users/f24296fd-aab0-4057-ac02-87e43b9bb968", "method": "PUT"}, "created_at": "2026-06-05T05:44:25.823285+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "f24296fd-aab0-4057-ac02-87e43b9bb968", "resource_type": "users"}	2026-06-05 05:44:25.938562+00
46edb14e-c5e6-4932-823a-75eab1a682cf	{"id": "46edb14e-c5e6-4932-823a-75eab1a682cf", "action": "users.delete", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/users/f24296fd-aab0-4057-ac02-87e43b9bb968", "method": "DELETE"}, "created_at": "2026-06-05T05:44:28.288338+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "f24296fd-aab0-4057-ac02-87e43b9bb968", "resource_type": "users"}	2026-06-05 05:44:28.403761+00
a1a2852a-1769-4ab4-a867-c45034a90125	{"id": "a1a2852a-1769-4ab4-a867-c45034a90125", "action": "assessments.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/assessments", "method": "POST"}, "created_at": "2026-06-05T05:47:13.226318+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": null, "resource_type": "assessments"}	2026-06-05 05:47:13.339795+00
92d598d0-6447-4d77-bae6-92c65da238c2	{"id": "92d598d0-6447-4d77-bae6-92c65da238c2", "action": "assessments.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/assessments/219984d9-5d21-4017-814c-961146a321f1/submit-response", "method": "POST"}, "created_at": "2026-06-05T05:47:21.614031+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "219984d9-5d21-4017-814c-961146a321f1", "resource_type": "assessments"}	2026-06-05 05:47:21.727142+00
6253e6fe-6317-4112-bb1b-9f010a2af1f8	{"id": "6253e6fe-6317-4112-bb1b-9f010a2af1f8", "action": "risks.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/risks", "method": "POST"}, "created_at": "2026-06-05T05:47:26.934446+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": null, "resource_type": "risks"}	2026-06-05 05:47:27.047853+00
a2f1973c-935a-40b4-8c30-a567a1cd16ea	{"id": "a2f1973c-935a-40b4-8c30-a567a1cd16ea", "action": "risks.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/risks/6adc9487-0bd8-4243-8e46-039240b77172", "method": "PUT"}, "created_at": "2026-06-05T05:47:31.123615+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "6adc9487-0bd8-4243-8e46-039240b77172", "resource_type": "risks"}	2026-06-05 05:47:31.236788+00
8593e44b-20fd-4c45-94d3-3294ef98551a	{"id": "8593e44b-20fd-4c45-94d3-3294ef98551a", "action": "risks.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/risks/6adc9487-0bd8-4243-8e46-039240b77172/treatments", "method": "POST"}, "created_at": "2026-06-05T05:47:33.784646+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "6adc9487-0bd8-4243-8e46-039240b77172", "resource_type": "risks"}	2026-06-05 05:47:33.897992+00
2910c741-32c3-4508-b028-8e8a7ce562e4	{"id": "2910c741-32c3-4508-b028-8e8a7ce562e4", "action": "findings.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/findings", "method": "POST"}, "created_at": "2026-06-05T05:47:35.794841+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": null, "resource_type": "findings"}	2026-06-05 05:47:35.908303+00
332c5ad2-b15f-4516-9afd-3e5fc1c1732d	{"id": "332c5ad2-b15f-4516-9afd-3e5fc1c1732d", "action": "findings.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/findings/d0e7c31c-fcfd-4220-89ec-690aae1378b5", "method": "PUT"}, "created_at": "2026-06-05T05:47:39.331910+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "d0e7c31c-fcfd-4220-89ec-690aae1378b5", "resource_type": "findings"}	2026-06-05 05:47:39.445067+00
7b02d364-8bb7-42f5-b0f5-0b2233db65c7	{"id": "7b02d364-8bb7-42f5-b0f5-0b2233db65c7", "action": "findings.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/findings/d0e7c31c-fcfd-4220-89ec-690aae1378b5/assign", "method": "POST"}, "created_at": "2026-06-05T05:47:42.909974+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "d0e7c31c-fcfd-4220-89ec-690aae1378b5", "resource_type": "findings"}	2026-06-05 05:47:43.02314+00
27709afb-3311-4eb8-9e56-f0ac79a130cf	{"id": "27709afb-3311-4eb8-9e56-f0ac79a130cf", "action": "evidence.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/evidence", "method": "POST"}, "created_at": "2026-06-05T05:47:45.039235+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": null, "resource_type": "evidence"}	2026-06-05 05:47:45.152422+00
ec44178a-1ad9-4200-b284-c8980d3df6d1	{"id": "ec44178a-1ad9-4200-b284-c8980d3df6d1", "action": "audits.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/audits", "method": "POST"}, "created_at": "2026-06-05T05:47:47.081982+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": null, "resource_type": "audits"}	2026-06-05 05:47:47.195168+00
9a780f1d-d3ce-40eb-a16c-077b3bfe8ee3	{"id": "9a780f1d-d3ce-40eb-a16c-077b3bfe8ee3", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/suggest-controls", "method": "POST"}, "created_at": "2026-06-05T05:47:51.966567+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "suggest-controls", "resource_type": "ai"}	2026-06-05 05:47:52.079748+00
c6796339-baa2-4717-acf4-fdd511375369	{"id": "c6796339-baa2-4717-acf4-fdd511375369", "action": "evidence.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/evidence", "method": "POST"}, "created_at": "2026-06-05T05:50:09.478787+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": null, "resource_type": "evidence"}	2026-06-05 05:50:09.59374+00
3d91b814-8a4f-45e9-9c9b-7ca8b0b26a18	{"id": "3d91b814-8a4f-45e9-9c9b-7ca8b0b26a18", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/suggest-controls", "method": "POST"}, "created_at": "2026-06-05T05:50:12.160304+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "suggest-controls", "resource_type": "ai"}	2026-06-05 05:50:12.275286+00
e74f4520-8022-471b-abd7-c66ed5e6f1f7	{"id": "e74f4520-8022-471b-abd7-c66ed5e6f1f7", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/suggest-controls", "method": "POST"}, "created_at": "2026-06-05T05:50:34.827080+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "suggest-controls", "resource_type": "ai"}	2026-06-05 05:50:34.942257+00
523c75c2-6b24-448d-ae14-c42cc0fa96f6	{"id": "523c75c2-6b24-448d-ae14-c42cc0fa96f6", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/suggest-controls", "method": "POST"}, "created_at": "2026-06-05T05:50:37.384474+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "suggest-controls", "resource_type": "ai"}	2026-06-05 05:50:37.49942+00
2c1e7ca8-88e5-4c1b-9609-cb1d63fa1401	{"id": "2c1e7ca8-88e5-4c1b-9609-cb1d63fa1401", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/ai-session/start", "method": "POST"}, "created_at": "2026-06-05T05:53:07.875819+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "ai-session", "resource_type": "policies"}	2026-06-05 05:53:07.990412+00
1babf0ed-abd5-4d74-9ef8-3b778dee3d43	{"id": "1babf0ed-abd5-4d74-9ef8-3b778dee3d43", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/ai-session/88c6f763-ac94-4a0f-876b-4fb563402196/finalize", "method": "POST"}, "created_at": "2026-06-05T05:53:14.182529+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "ai-session", "resource_type": "policies"}	2026-06-05 05:53:14.297026+00
193bfb26-1d5a-4cf1-9471-d73662fdd4a7	{"id": "193bfb26-1d5a-4cf1-9471-d73662fdd4a7", "action": "controls.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/controls/search", "method": "POST"}, "created_at": "2026-06-05T05:54:40.880250+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "search", "resource_type": "controls"}	2026-06-05 05:54:40.994716+00
cbc79861-516e-4c24-87d8-3eaf6ec68979	{"id": "cbc79861-516e-4c24-87d8-3eaf6ec68979", "action": "assessments.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/assessments", "method": "POST"}, "created_at": "2026-06-05T05:54:55.362809+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": null, "resource_type": "assessments"}	2026-06-05 05:54:55.477348+00
b741bc3b-6c1a-4c0a-b474-afec66322e09	{"id": "b741bc3b-6c1a-4c0a-b474-afec66322e09", "action": "assessments.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/assessments/8215bdeb-89ea-4daa-9be6-462d0df294bf/submit-response", "method": "POST"}, "created_at": "2026-06-05T05:55:03.584285+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "8215bdeb-89ea-4daa-9be6-462d0df294bf", "resource_type": "assessments"}	2026-06-05 05:55:03.698687+00
03f05373-3572-4703-b5f7-b39e80cd6880	{"id": "03f05373-3572-4703-b5f7-b39e80cd6880", "action": "risks.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/risks", "method": "POST"}, "created_at": "2026-06-05T05:55:10.291804+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": null, "resource_type": "risks"}	2026-06-05 05:55:10.405462+00
4ce1f941-1053-4406-b93f-24cc04bf8c0a	{"id": "4ce1f941-1053-4406-b93f-24cc04bf8c0a", "action": "risks.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/risks/1f147371-9490-406d-96ef-8faeebe4190f", "method": "PUT"}, "created_at": "2026-06-05T05:55:14.491002+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "1f147371-9490-406d-96ef-8faeebe4190f", "resource_type": "risks"}	2026-06-05 05:55:14.611677+00
3132e80d-b239-46d4-864d-6705a17bcba3	{"id": "3132e80d-b239-46d4-864d-6705a17bcba3", "action": "risks.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/risks/1f147371-9490-406d-96ef-8faeebe4190f/treatments", "method": "POST"}, "created_at": "2026-06-05T05:55:17.176786+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "1f147371-9490-406d-96ef-8faeebe4190f", "resource_type": "risks"}	2026-06-05 05:55:17.29047+00
2f511256-2d9b-413e-8127-56e66d4ceacf	{"id": "2f511256-2d9b-413e-8127-56e66d4ceacf", "action": "findings.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/findings", "method": "POST"}, "created_at": "2026-06-05T05:55:23.277230+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": null, "resource_type": "findings"}	2026-06-05 05:55:23.390811+00
1260e18e-d4b0-48e6-9b1e-88bb69d7bcea	{"id": "1260e18e-d4b0-48e6-9b1e-88bb69d7bcea", "action": "findings.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/findings/6e4b45eb-35ce-437f-bd41-9d0d4c32c561", "method": "PUT"}, "created_at": "2026-06-05T05:55:26.824725+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "6e4b45eb-35ce-437f-bd41-9d0d4c32c561", "resource_type": "findings"}	2026-06-05 05:55:26.938425+00
88f4fbee-9a1e-4656-95d0-f39bc554f663	{"id": "88f4fbee-9a1e-4656-95d0-f39bc554f663", "action": "findings.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/findings/6e4b45eb-35ce-437f-bd41-9d0d4c32c561/assign", "method": "POST"}, "created_at": "2026-06-05T05:55:30.438076+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "6e4b45eb-35ce-437f-bd41-9d0d4c32c561", "resource_type": "findings"}	2026-06-05 05:55:30.551955+00
cc38b2e9-2ecb-48ed-9b9a-ee5816e2ea94	{"id": "cc38b2e9-2ecb-48ed-9b9a-ee5816e2ea94", "action": "remediation-tasks.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/remediation-tasks/b76995cc-42d1-4307-aa0c-d53dcc8918e1", "method": "PUT"}, "created_at": "2026-06-05T05:55:36.699999+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "b76995cc-42d1-4307-aa0c-d53dcc8918e1", "resource_type": "remediation-tasks"}	2026-06-05 05:55:36.813652+00
064c6857-e1ab-410b-aa76-6099be4de06a	{"id": "064c6857-e1ab-410b-aa76-6099be4de06a", "action": "evidence.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/evidence", "method": "POST"}, "created_at": "2026-06-05T05:55:40.211004+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": null, "resource_type": "evidence"}	2026-06-05 05:55:40.324646+00
96249df9-e8c5-4317-85f8-d62dc7bcccf1	{"id": "96249df9-e8c5-4317-85f8-d62dc7bcccf1", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/generate-ai", "method": "POST"}, "created_at": "2026-06-05T05:55:45.887350+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "generate-ai", "resource_type": "policies"}	2026-06-05 05:55:46.001026+00
b051fad2-c941-403a-9c2a-6c30be75e594	{"id": "b051fad2-c941-403a-9c2a-6c30be75e594", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/generate-ai", "method": "POST"}, "created_at": "2026-06-05T05:55:48.578508+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "generate-ai", "resource_type": "policies"}	2026-06-05 05:55:48.69234+00
e9b791dd-0448-404b-814f-6deaf772dec8	{"id": "e9b791dd-0448-404b-814f-6deaf772dec8", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/generate-ai", "method": "POST"}, "created_at": "2026-06-05T05:55:51.250552+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "generate-ai", "resource_type": "policies"}	2026-06-05 05:55:51.364209+00
f1f308f4-184f-4e0e-aca8-90873cbf1d5a	{"id": "f1f308f4-184f-4e0e-aca8-90873cbf1d5a", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/generate-ai", "method": "POST"}, "created_at": "2026-06-05T05:55:53.918488+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "generate-ai", "resource_type": "policies"}	2026-06-05 05:55:54.032186+00
b4604fbd-f822-47a8-a2f7-84ea4a17e238	{"id": "b4604fbd-f822-47a8-a2f7-84ea4a17e238", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/generate-ai", "method": "POST"}, "created_at": "2026-06-05T05:55:56.586364+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "generate-ai", "resource_type": "policies"}	2026-06-05 05:55:56.700015+00
a45ff40a-ddc0-4138-9bef-3a60106cb875	{"id": "a45ff40a-ddc0-4138-9bef-3a60106cb875", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/generate-ai", "method": "POST"}, "created_at": "2026-06-05T05:55:59.258645+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "generate-ai", "resource_type": "policies"}	2026-06-05 05:55:59.372438+00
3826c3a0-0a31-4cf4-9ac0-6a6e259e1247	{"id": "3826c3a0-0a31-4cf4-9ac0-6a6e259e1247", "action": "policies.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/9523ab29-9134-4684-a082-c056777c9ba0", "method": "PUT"}, "created_at": "2026-06-05T05:56:05.694053+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "9523ab29-9134-4684-a082-c056777c9ba0", "resource_type": "policies"}	2026-06-05 05:56:05.807709+00
bd266eb1-5e99-4311-bf94-2ec8928bdd16	{"id": "bd266eb1-5e99-4311-bf94-2ec8928bdd16", "action": "audits.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/audits", "method": "POST"}, "created_at": "2026-06-05T05:56:11.995406+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": null, "resource_type": "audits"}	2026-06-05 05:56:12.10904+00
e48750a5-c3b8-4ad8-adf3-d85237271325	{"id": "e48750a5-c3b8-4ad8-adf3-d85237271325", "action": "vendors.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/vendors/06b0d114-b3f1-470d-a304-cd20a75fa1b5/assess", "method": "POST"}, "created_at": "2026-06-05T05:56:21.601922+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "06b0d114-b3f1-470d-a304-cd20a75fa1b5", "resource_type": "vendors"}	2026-06-05 05:56:21.715599+00
3ebb8b4b-589a-42d6-8eed-175eb0c982c9	{"id": "3ebb8b4b-589a-42d6-8eed-175eb0c982c9", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-05T05:56:38.661844+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-05 05:56:38.77556+00
556569f0-fcd8-414c-b6f5-4031956d28b8	{"id": "556569f0-fcd8-414c-b6f5-4031956d28b8", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/gap-analysis", "method": "POST"}, "created_at": "2026-06-05T05:56:44.879230+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "gap-analysis", "resource_type": "ai"}	2026-06-05 05:56:44.99288+00
21b638eb-5f65-4ebd-8ebe-f4f76c0b4ae6	{"id": "21b638eb-5f65-4ebd-8ebe-f4f76c0b4ae6", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/suggest-controls", "method": "POST"}, "created_at": "2026-06-05T05:56:47.109749+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "suggest-controls", "resource_type": "ai"}	2026-06-05 05:56:47.223471+00
9df32857-91c8-4065-a7eb-fed70f54ffa0	{"id": "9df32857-91c8-4065-a7eb-fed70f54ffa0", "action": "users.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/users", "method": "POST"}, "created_at": "2026-06-05T05:57:04.716068+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": null, "resource_type": "users"}	2026-06-05 05:57:04.829714+00
caec247d-8ebe-467c-843f-7fc99b25761d	{"id": "caec247d-8ebe-467c-843f-7fc99b25761d", "action": "users.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/users/60454675-226f-4d13-86cb-b573da1d57fd", "method": "PUT"}, "created_at": "2026-06-05T05:57:08.256000+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "60454675-226f-4d13-86cb-b573da1d57fd", "resource_type": "users"}	2026-06-05 05:57:08.369708+00
8a5e4443-bbde-4633-9292-2a12262dc855	{"id": "8a5e4443-bbde-4633-9292-2a12262dc855", "action": "users.delete", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/users/60454675-226f-4d13-86cb-b573da1d57fd", "method": "DELETE"}, "created_at": "2026-06-05T05:57:10.710112+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "60454675-226f-4d13-86cb-b573da1d57fd", "resource_type": "users"}	2026-06-05 05:57:10.823773+00
55a5d237-cf58-4eba-b76f-bd60cacb3387	{"id": "55a5d237-cf58-4eba-b76f-bd60cacb3387", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-05T06:14:49.369236+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-05 06:14:49.483272+00
d138457b-f4af-46ed-983c-1d70280c03c2	{"id": "d138457b-f4af-46ed-983c-1d70280c03c2", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/0d574575-fb40-4188-b141-fc14ce62f436/read", "method": "PUT"}, "created_at": "2026-06-05T06:17:39.057109+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "0d574575-fb40-4188-b141-fc14ce62f436", "resource_type": "notifications"}	2026-06-05 06:17:39.172641+00
2d08d7ed-d1af-490d-bda2-2afb7fdb1550	{"id": "2d08d7ed-d1af-490d-bda2-2afb7fdb1550", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/15f4087d-261c-4c29-a2b1-d8a8a8350433/read", "method": "PUT"}, "created_at": "2026-06-05T06:17:39.579737+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "15f4087d-261c-4c29-a2b1-d8a8a8350433", "resource_type": "notifications"}	2026-06-05 06:17:39.694968+00
268bf069-cbe3-4765-878a-a6c9f5a4485f	{"id": "268bf069-cbe3-4765-878a-a6c9f5a4485f", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/f8e46e9d-2255-4cfd-8362-063296639d1b/read", "method": "PUT"}, "created_at": "2026-06-05T06:17:40.147714+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "f8e46e9d-2255-4cfd-8362-063296639d1b", "resource_type": "notifications"}	2026-06-05 06:17:40.264777+00
97159155-34bc-469a-8f3c-bc885e5833f7	{"id": "97159155-34bc-469a-8f3c-bc885e5833f7", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/f8e46e9d-2255-4cfd-8362-063296639d1b/read", "method": "PUT"}, "created_at": "2026-06-05T06:17:40.717470+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "f8e46e9d-2255-4cfd-8362-063296639d1b", "resource_type": "notifications"}	2026-06-05 06:17:40.832313+00
1095340b-b40e-4d76-8b9d-71006bff0e58	{"id": "1095340b-b40e-4d76-8b9d-71006bff0e58", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/f8e46e9d-2255-4cfd-8362-063296639d1b/read", "method": "PUT"}, "created_at": "2026-06-05T06:17:40.934444+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "f8e46e9d-2255-4cfd-8362-063296639d1b", "resource_type": "notifications"}	2026-06-05 06:17:41.048241+00
37e6c728-7a54-42f6-88ed-5ca3b13ee7d1	{"id": "37e6c728-7a54-42f6-88ed-5ca3b13ee7d1", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/0d574575-fb40-4188-b141-fc14ce62f436/read", "method": "PUT"}, "created_at": "2026-06-05T06:17:41.358726+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "0d574575-fb40-4188-b141-fc14ce62f436", "resource_type": "notifications"}	2026-06-05 06:17:41.471876+00
2a7ebee0-e4b3-41c5-a384-870d31bf58a9	{"id": "2a7ebee0-e4b3-41c5-a384-870d31bf58a9", "action": "dashboard.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/dashboard/refresh", "method": "POST"}, "created_at": "2026-06-05T06:18:20.522081+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "refresh", "resource_type": "dashboard"}	2026-06-05 06:18:20.636595+00
e5e6f189-95aa-40ee-b8d7-07ee1a36f84e	{"id": "e5e6f189-95aa-40ee-b8d7-07ee1a36f84e", "action": "dashboard.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/dashboard/refresh", "method": "POST"}, "created_at": "2026-06-05T06:18:22.179205+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "refresh", "resource_type": "dashboard"}	2026-06-05 06:18:22.292404+00
0a32e050-d51f-4159-803f-bde662d2f161	{"id": "0a32e050-d51f-4159-803f-bde662d2f161", "action": "incident.created", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "metadata": {"type": "unauthorized_access", "severity": "high"}, "created_at": "2026-06-05T06:27:05.778760+00:00", "ip_address": null, "user_email": "itsec@rut.edu.in", "resource_id": "59ab09d6-8386-4eab-b715-86afa08d91fc", "resource_type": "incident"}	2026-06-05 06:27:05.894215+00
ddb3fd97-df03-423a-8eb7-d08d76343851	{"id": "ddb3fd97-df03-423a-8eb7-d08d76343851", "action": "incidents.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "metadata": {"path": "/api/v1/incidents", "method": "POST"}, "created_at": "2026-06-05T06:27:06.441025+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "incidents"}	2026-06-05 06:27:06.556344+00
3a3faa19-6b2b-43a9-8451-ebb69eb90592	{"id": "3a3faa19-6b2b-43a9-8451-ebb69eb90592", "action": "task.assigned", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "metadata": {"control": "DPDP-S8-C1", "department": "IT", "assignee_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6"}, "created_at": "2026-06-05T06:27:37.495560+00:00", "ip_address": null, "user_email": "ciso@rut.edu.in", "resource_id": "5cceb3f3-971f-4ac7-84f1-57be6362244f", "resource_type": "control_assignment"}	2026-06-05 06:27:37.611045+00
65c8b787-5947-442a-a53b-b264a9feec9b	{"id": "65c8b787-5947-442a-a53b-b264a9feec9b", "action": "control-assignments.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "metadata": {"path": "/api/v1/control-assignments", "method": "POST"}, "created_at": "2026-06-05T06:27:38.159801+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "control-assignments"}	2026-06-05 06:27:38.275242+00
a6b3296f-88f3-4ff0-9a9f-f5730fc23f81	{"id": "a6b3296f-88f3-4ff0-9a9f-f5730fc23f81", "action": "department.created", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"name": "TEST_QA_Dept_1780641487"}, "created_at": "2026-06-05T06:38:09.871081+00:00", "ip_address": null, "user_email": "admin@rut.edu.in", "resource_id": "91813244-254d-45dc-8d77-1674c7fabd68", "resource_type": "department"}	2026-06-05 06:38:09.985285+00
d8de740f-fb44-4585-a740-52d2a01a8004	{"id": "d8de740f-fb44-4585-a740-52d2a01a8004", "action": "departments.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/departments", "method": "POST"}, "created_at": "2026-06-05T06:38:10.526390+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "departments"}	2026-06-05 06:38:10.640524+00
3e2b55f8-5065-49f4-8a15-c6d1d6319d15	{"id": "3e2b55f8-5065-49f4-8a15-c6d1d6319d15", "action": "departments.delete", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/departments/91813244-254d-45dc-8d77-1674c7fabd68", "method": "DELETE"}, "created_at": "2026-06-05T06:38:12.925632+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "91813244-254d-45dc-8d77-1674c7fabd68", "resource_type": "departments"}	2026-06-05 06:38:13.03985+00
d727d2b2-0b7d-4d59-a2fd-77b335865011	{"id": "d727d2b2-0b7d-4d59-a2fd-77b335865011", "action": "task.assigned", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "metadata": {"control": "DPDP-S8-C1", "department": "IT", "assignee_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6"}, "created_at": "2026-06-05T06:38:26.443083+00:00", "ip_address": null, "user_email": "ciso@rut.edu.in", "resource_id": "48dbe9e3-9e09-4480-98d4-06cbfe84de0e", "resource_type": "control_assignment"}	2026-06-05 06:38:26.557185+00
f814cc21-10fc-43d9-8ade-e8a13c2d7e41	{"id": "f814cc21-10fc-43d9-8ade-e8a13c2d7e41", "action": "control-assignments.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "metadata": {"path": "/api/v1/control-assignments", "method": "POST"}, "created_at": "2026-06-05T06:38:27.096871+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "control-assignments"}	2026-06-05 06:38:27.211139+00
d91165fa-f0bb-4a38-8d65-58489363fc5f	{"id": "d91165fa-f0bb-4a38-8d65-58489363fc5f", "action": "task.status_changed", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "metadata": {"to_status": "in_progress"}, "created_at": "2026-06-05T06:38:34.511873+00:00", "ip_address": null, "user_email": "itsec@rut.edu.in", "resource_id": "48dbe9e3-9e09-4480-98d4-06cbfe84de0e", "resource_type": "control_assignment"}	2026-06-05 06:38:34.626055+00
a8bf763f-ff3d-4d71-9552-e7324cba5eb2	{"id": "a8bf763f-ff3d-4d71-9552-e7324cba5eb2", "action": "control-assignments.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "metadata": {"path": "/api/v1/control-assignments/48dbe9e3-9e09-4480-98d4-06cbfe84de0e/status", "method": "PUT"}, "created_at": "2026-06-05T06:38:35.819476+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "48dbe9e3-9e09-4480-98d4-06cbfe84de0e", "resource_type": "control-assignments"}	2026-06-05 06:38:35.933633+00
27d14fc8-33f0-408c-937c-488fdbaa9c7b	{"id": "27d14fc8-33f0-408c-937c-488fdbaa9c7b", "action": "task.status_changed", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "metadata": {"to_status": "submitted"}, "created_at": "2026-06-05T06:38:39.964043+00:00", "ip_address": null, "user_email": "itsec@rut.edu.in", "resource_id": "48dbe9e3-9e09-4480-98d4-06cbfe84de0e", "resource_type": "control_assignment"}	2026-06-05 06:38:40.078194+00
c2042176-bef2-44c0-aaef-3b5b20000111	{"id": "c2042176-bef2-44c0-aaef-3b5b20000111", "action": "control-assignments.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "metadata": {"path": "/api/v1/control-assignments/48dbe9e3-9e09-4480-98d4-06cbfe84de0e/status", "method": "PUT"}, "created_at": "2026-06-05T06:38:41.270853+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "48dbe9e3-9e09-4480-98d4-06cbfe84de0e", "resource_type": "control-assignments"}	2026-06-05 06:38:41.384934+00
27b8b52d-9fe4-4d5c-9c11-c05e8b3a80e2	{"id": "27b8b52d-9fe4-4d5c-9c11-c05e8b3a80e2", "action": "incident.created", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "metadata": {"type": "phishing", "severity": "high"}, "created_at": "2026-06-05T06:38:48.474076+00:00", "ip_address": null, "user_email": "itsec@rut.edu.in", "resource_id": "02264061-90d4-4ac7-9c5b-066c5433ed0d", "resource_type": "incident"}	2026-06-05 06:38:48.588234+00
6fc5ab32-d26f-45bf-a3f6-f0aad0933e25	{"id": "6fc5ab32-d26f-45bf-a3f6-f0aad0933e25", "action": "incidents.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "metadata": {"path": "/api/v1/incidents", "method": "POST"}, "created_at": "2026-06-05T06:38:49.127993+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "incidents"}	2026-06-05 06:38:49.24234+00
d6eacb0e-6b4e-487b-be23-88ef7a31ab1a	{"id": "d6eacb0e-6b4e-487b-be23-88ef7a31ab1a", "action": "incident.cert_in_reported", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "metadata": {}, "created_at": "2026-06-05T06:38:53.276780+00:00", "ip_address": null, "user_email": "itsec@rut.edu.in", "resource_id": "02264061-90d4-4ac7-9c5b-066c5433ed0d", "resource_type": "incident"}	2026-06-05 06:38:53.391084+00
1b553c8e-c479-4166-981f-a06b8912677a	{"id": "1b553c8e-c479-4166-981f-a06b8912677a", "action": "incidents.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "metadata": {"path": "/api/v1/incidents/02264061-90d4-4ac7-9c5b-066c5433ed0d/report-cert-in", "method": "POST"}, "created_at": "2026-06-05T06:38:54.584372+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "02264061-90d4-4ac7-9c5b-066c5433ed0d", "resource_type": "incidents"}	2026-06-05 06:38:54.698466+00
71f9e716-47a3-43c3-9d07-4a6c6f3c5aa1	{"id": "71f9e716-47a3-43c3-9d07-4a6c6f3c5aa1", "action": "incident.dpdp_notified", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "metadata": {}, "created_at": "2026-06-05T06:38:57.419086+00:00", "ip_address": null, "user_email": "itsec@rut.edu.in", "resource_id": "02264061-90d4-4ac7-9c5b-066c5433ed0d", "resource_type": "incident"}	2026-06-05 06:38:57.533258+00
b2e6122a-4697-43de-a9e7-c6c14fc555f4	{"id": "b2e6122a-4697-43de-a9e7-c6c14fc555f4", "action": "incidents.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "metadata": {"path": "/api/v1/incidents/02264061-90d4-4ac7-9c5b-066c5433ed0d/notify-dpdp", "method": "POST"}, "created_at": "2026-06-05T06:38:58.727420+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "02264061-90d4-4ac7-9c5b-066c5433ed0d", "resource_type": "incidents"}	2026-06-05 06:38:58.841682+00
12928920-e288-4b30-bf26-3f79cc6d3da9	{"id": "12928920-e288-4b30-bf26-3f79cc6d3da9", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-05T06:39:25.023282+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-05 06:39:25.137409+00
d93f1ec6-d478-4223-90e8-5405204ad8e4	{"id": "d93f1ec6-d478-4223-90e8-5405204ad8e4", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "metadata": {"path": "/api/v1/policies/ai-session/start", "method": "POST"}, "created_at": "2026-06-05T06:39:33.309345+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "ai-session", "resource_type": "policies"}	2026-06-05 06:39:33.423614+00
62af5c59-9541-43cd-a936-c6ab76c5ca52	{"id": "62af5c59-9541-43cd-a936-c6ab76c5ca52", "action": "control-assignments.delete", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "metadata": {"path": "/api/v1/control-assignments/48dbe9e3-9e09-4480-98d4-06cbfe84de0e", "method": "DELETE"}, "created_at": "2026-06-05T06:39:35.709532+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "48dbe9e3-9e09-4480-98d4-06cbfe84de0e", "resource_type": "control-assignments"}	2026-06-05 06:39:35.823681+00
32d19668-dfa8-41cc-bf22-f5579bba6d9e	{"id": "32d19668-dfa8-41cc-bf22-f5579bba6d9e", "action": "users.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/users/invite", "method": "POST"}, "created_at": "2026-06-07T12:56:33.856145+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "invite", "resource_type": "users"}	2026-06-07 12:56:33.969907+00
70ab2dd8-ffdd-4b8c-85d9-35289c6aeb72	{"id": "70ab2dd8-ffdd-4b8c-85d9-35289c6aeb72", "action": "users.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/users/invite", "method": "POST"}, "created_at": "2026-06-07T12:59:28.552030+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "invite", "resource_type": "users"}	2026-06-07 12:59:28.666003+00
21661dac-fa76-4f2c-9798-870adfa9690b	{"id": "21661dac-fa76-4f2c-9798-870adfa9690b", "action": "users.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/users/invite", "method": "POST"}, "created_at": "2026-06-07T13:04:14.754884+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "invite", "resource_type": "users"}	2026-06-07 13:04:14.867938+00
01763f83-7077-4081-b10a-3b45351b0a5d	{"id": "01763f83-7077-4081-b10a-3b45351b0a5d", "action": "settings.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/settings/user-preferences", "method": "PUT"}, "created_at": "2026-06-07T13:06:13.551977+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "user-preferences", "resource_type": "settings"}	2026-06-07 13:06:13.665765+00
a722c8b1-25b5-4aee-8353-385f509a5e59	{"id": "a722c8b1-25b5-4aee-8353-385f509a5e59", "action": "findings.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c1875549-56b3-4685-82a6-81580c677006", "metadata": {"path": "/api/v1/findings", "method": "POST"}, "created_at": "2026-06-07T13:25:03.012065+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "findings"}	2026-06-07 13:25:03.125854+00
95de3052-0395-43cc-b7fd-5958f9a24fd4	{"id": "95de3052-0395-43cc-b7fd-5958f9a24fd4", "action": "risks.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/risks", "method": "POST"}, "created_at": "2026-06-07T13:25:05.025966+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "risks"}	2026-06-07 13:25:05.139845+00
76f5834d-2fb0-4364-9199-f9944d6fc683	{"id": "76f5834d-2fb0-4364-9199-f9944d6fc683", "action": "findings.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c1875549-56b3-4685-82a6-81580c677006", "metadata": {"path": "/api/v1/findings", "method": "POST"}, "created_at": "2026-06-07T13:29:37.918264+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "findings"}	2026-06-07 13:29:38.03176+00
2c00916a-6a17-4a4c-92a4-972c2a26fcae	{"id": "2c00916a-6a17-4a4c-92a4-972c2a26fcae", "action": "risks.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/risks", "method": "POST"}, "created_at": "2026-06-07T13:29:39.925708+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "risks"}	2026-06-07 13:29:40.038847+00
1cea1544-9af3-4a0e-88cf-e95d1ca90fa8	{"id": "1cea1544-9af3-4a0e-88cf-e95d1ca90fa8", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "metadata": {"path": "/api/v1/policies", "method": "POST"}, "created_at": "2026-06-07T13:29:45.774051+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "policies"}	2026-06-07 13:29:45.887104+00
a554dea4-182e-492d-a80d-6b6f8e211e1f	{"id": "a554dea4-182e-492d-a80d-6b6f8e211e1f", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "5b27c9dc-8ed6-4cb0-b255-b75b8e09bbf9", "metadata": {"path": "/api/v1/policies/f4b810bc-b183-42d8-b286-c5743afaf037/approve", "method": "POST"}, "created_at": "2026-06-07T13:29:53.101523+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "f4b810bc-b183-42d8-b286-c5743afaf037", "resource_type": "policies"}	2026-06-07 13:29:53.214598+00
7d001e63-24ba-4e75-9cc2-3db052659337	{"id": "7d001e63-24ba-4e75-9cc2-3db052659337", "action": "users.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/users/invite", "method": "POST"}, "created_at": "2026-06-07T13:30:58.690991+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "invite", "resource_type": "users"}	2026-06-07 13:30:58.804109+00
1a9e9a89-8295-4247-9409-9d7ad81a2f2f	{"id": "1a9e9a89-8295-4247-9409-9d7ad81a2f2f", "action": "settings.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/settings/user-preferences", "method": "PUT"}, "created_at": "2026-06-07T13:34:13.185426+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "user-preferences", "resource_type": "settings"}	2026-06-07 13:34:13.298916+00
8e2c4b6e-881a-474b-9af7-ff1bb4ac99d2	{"id": "8e2c4b6e-881a-474b-9af7-ff1bb4ac99d2", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/785fb0ba-e8f4-4ffc-92c0-ffede817daf4/read", "method": "PUT"}, "created_at": "2026-06-07T13:43:04.910186+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "785fb0ba-e8f4-4ffc-92c0-ffede817daf4", "resource_type": "notifications"}	2026-06-07 13:43:05.02334+00
e1524917-ebe4-4568-8a64-54bed31b58a0	{"id": "e1524917-ebe4-4568-8a64-54bed31b58a0", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/48a7b5ad-a3dd-40a6-b8b1-63bbdc7d1a84/read", "method": "PUT"}, "created_at": "2026-06-07T13:43:05.551298+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "48a7b5ad-a3dd-40a6-b8b1-63bbdc7d1a84", "resource_type": "notifications"}	2026-06-07 13:43:05.664648+00
aac966c1-3a42-4876-ac5c-1abde134f698	{"id": "aac966c1-3a42-4876-ac5c-1abde134f698", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/48a7b5ad-a3dd-40a6-b8b1-63bbdc7d1a84/read", "method": "PUT"}, "created_at": "2026-06-07T13:43:05.802078+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "48a7b5ad-a3dd-40a6-b8b1-63bbdc7d1a84", "resource_type": "notifications"}	2026-06-07 13:43:05.916004+00
3a653334-1bce-446f-bbc5-5542326eed73	{"id": "3a653334-1bce-446f-bbc5-5542326eed73", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/48a7b5ad-a3dd-40a6-b8b1-63bbdc7d1a84/read", "method": "PUT"}, "created_at": "2026-06-07T13:43:06.501951+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "48a7b5ad-a3dd-40a6-b8b1-63bbdc7d1a84", "resource_type": "notifications"}	2026-06-07 13:43:06.615167+00
3da6f7ca-81bf-4eb3-8559-86881e189ab2	{"id": "3da6f7ca-81bf-4eb3-8559-86881e189ab2", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/785fb0ba-e8f4-4ffc-92c0-ffede817daf4/read", "method": "PUT"}, "created_at": "2026-06-07T13:43:07.385275+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "785fb0ba-e8f4-4ffc-92c0-ffede817daf4", "resource_type": "notifications"}	2026-06-07 13:43:07.498515+00
71f4c6dc-30be-4ca9-b2fc-f4291754c8f2	{"id": "71f4c6dc-30be-4ca9-b2fc-f4291754c8f2", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/48a7b5ad-a3dd-40a6-b8b1-63bbdc7d1a84/read", "method": "PUT"}, "created_at": "2026-06-07T13:43:09.178142+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "48a7b5ad-a3dd-40a6-b8b1-63bbdc7d1a84", "resource_type": "notifications"}	2026-06-07 13:43:09.290774+00
e8c1b118-962c-47ac-b0fb-542efcbc6d16	{"id": "e8c1b118-962c-47ac-b0fb-542efcbc6d16", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/48a7b5ad-a3dd-40a6-b8b1-63bbdc7d1a84/read", "method": "PUT"}, "created_at": "2026-06-07T13:43:09.397002+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "48a7b5ad-a3dd-40a6-b8b1-63bbdc7d1a84", "resource_type": "notifications"}	2026-06-07 13:43:09.510971+00
2cfd0336-e6a6-4a50-ab9a-c524131625db	{"id": "2cfd0336-e6a6-4a50-ab9a-c524131625db", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/48a7b5ad-a3dd-40a6-b8b1-63bbdc7d1a84/read", "method": "PUT"}, "created_at": "2026-06-07T13:43:06.924115+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "48a7b5ad-a3dd-40a6-b8b1-63bbdc7d1a84", "resource_type": "notifications"}	2026-06-07 13:43:07.037434+00
d3d82008-ca8b-4128-9504-d7954a949fef	{"id": "d3d82008-ca8b-4128-9504-d7954a949fef", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/c7017120-74cd-4a5a-b777-51b59344e591/read", "method": "PUT"}, "created_at": "2026-06-07T13:43:13.715934+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "c7017120-74cd-4a5a-b777-51b59344e591", "resource_type": "notifications"}	2026-06-07 13:43:13.829282+00
e588267b-0f62-4745-a54c-06f6114de761	{"id": "e588267b-0f62-4745-a54c-06f6114de761", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/c7017120-74cd-4a5a-b777-51b59344e591/read", "method": "PUT"}, "created_at": "2026-06-07T13:43:17.310637+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "c7017120-74cd-4a5a-b777-51b59344e591", "resource_type": "notifications"}	2026-06-07 13:43:17.42397+00
d1cc21a7-2854-462a-92dd-9f13ead2e995	{"id": "d1cc21a7-2854-462a-92dd-9f13ead2e995", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/785fb0ba-e8f4-4ffc-92c0-ffede817daf4/read", "method": "PUT"}, "created_at": "2026-06-07T13:43:08.744024+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "785fb0ba-e8f4-4ffc-92c0-ffede817daf4", "resource_type": "notifications"}	2026-06-07 13:43:08.857136+00
84764106-4794-4e55-8e7d-d7b04a50f8ee	{"id": "84764106-4794-4e55-8e7d-d7b04a50f8ee", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/785fb0ba-e8f4-4ffc-92c0-ffede817daf4/read", "method": "PUT"}, "created_at": "2026-06-07T13:43:10.258182+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "785fb0ba-e8f4-4ffc-92c0-ffede817daf4", "resource_type": "notifications"}	2026-06-07 13:43:10.371686+00
95587bfd-e310-4372-98f7-cd7847cad786	{"id": "95587bfd-e310-4372-98f7-cd7847cad786", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/c7017120-74cd-4a5a-b777-51b59344e591/read", "method": "PUT"}, "created_at": "2026-06-07T13:43:17.527354+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "c7017120-74cd-4a5a-b777-51b59344e591", "resource_type": "notifications"}	2026-06-07 13:43:17.640417+00
6e7877e4-b5cb-413b-93ea-349fc5727c0c	{"id": "6e7877e4-b5cb-413b-93ea-349fc5727c0c", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/c7017120-74cd-4a5a-b777-51b59344e591/read", "method": "PUT"}, "created_at": "2026-06-07T13:43:17.748813+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "c7017120-74cd-4a5a-b777-51b59344e591", "resource_type": "notifications"}	2026-06-07 13:43:17.862918+00
1808562d-e804-45b2-ac01-2c1d7b52aab6	{"id": "1808562d-e804-45b2-ac01-2c1d7b52aab6", "action": "findings.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c1875549-56b3-4685-82a6-81580c677006", "metadata": {"path": "/api/v1/findings", "method": "POST"}, "created_at": "2026-06-07T13:44:22.162796+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "findings"}	2026-06-07 13:44:22.276579+00
80ae072c-0700-4613-8997-82065b6105e9	{"id": "80ae072c-0700-4613-8997-82065b6105e9", "action": "risks.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/risks", "method": "POST"}, "created_at": "2026-06-07T13:44:24.178000+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "risks"}	2026-06-07 13:44:24.291998+00
644bdbe0-6e8b-4d82-8043-56d23448990a	{"id": "644bdbe0-6e8b-4d82-8043-56d23448990a", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "metadata": {"path": "/api/v1/policies", "method": "POST"}, "created_at": "2026-06-07T13:44:30.004042+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "policies"}	2026-06-07 13:44:30.118037+00
64362704-f30e-494d-843a-7e3de98b134e	{"id": "64362704-f30e-494d-843a-7e3de98b134e", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "5b27c9dc-8ed6-4cb0-b255-b75b8e09bbf9", "metadata": {"path": "/api/v1/policies/9d5f8a67-2953-4da9-831d-9730bb151317/approve", "method": "POST"}, "created_at": "2026-06-07T13:44:37.366273+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "9d5f8a67-2953-4da9-831d-9730bb151317", "resource_type": "policies"}	2026-06-07 13:44:37.480158+00
4b726ec2-bbfb-4cf9-9ca2-6f5e4a8005b4	{"id": "4b726ec2-bbfb-4cf9-9ca2-6f5e4a8005b4", "action": "users.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/users", "method": "POST"}, "created_at": "2026-06-07T14:01:30.800845+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "users"}	2026-06-07 14:01:30.914775+00
fcbdb909-e780-4d7f-9cf2-e99d3692cd46	{"id": "fcbdb909-e780-4d7f-9cf2-e99d3692cd46", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies", "method": "POST"}, "created_at": "2026-06-07T14:01:53.699676+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "policies"}	2026-06-07 14:01:53.813664+00
ec4f6fed-187e-45d4-86ed-09ec21c1e0d9	{"id": "ec4f6fed-187e-45d4-86ed-09ec21c1e0d9", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/a3c3b0ae-cad1-4917-a9c5-e5eb4e9c7820/submit", "method": "POST"}, "created_at": "2026-06-07T14:01:59.618141+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "a3c3b0ae-cad1-4917-a9c5-e5eb4e9c7820", "resource_type": "policies"}	2026-06-07 14:01:59.732394+00
dab569c2-666f-495c-8b14-131de9bbdfa2	{"id": "dab569c2-666f-495c-8b14-131de9bbdfa2", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/a3c3b0ae-cad1-4917-a9c5-e5eb4e9c7820/approve", "method": "POST"}, "created_at": "2026-06-07T14:02:05.479610+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "a3c3b0ae-cad1-4917-a9c5-e5eb4e9c7820", "resource_type": "policies"}	2026-06-07 14:02:05.593616+00
9d6ef5e4-fa0a-4f1b-ab00-57f6cd3df93b	{"id": "9d6ef5e4-fa0a-4f1b-ab00-57f6cd3df93b", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-07T14:12:38.572290+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-07 14:12:38.686224+00
38dea177-6b22-462a-a808-9f75141db276	{"id": "38dea177-6b22-462a-a808-9f75141db276", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-07T15:26:24.838469+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-07 15:26:24.95303+00
1c592a60-f8be-4642-ba68-1163b64db660	{"id": "1c592a60-f8be-4642-ba68-1163b64db660", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/ai-session/start", "method": "POST"}, "created_at": "2026-06-07T15:27:01.497549+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "ai-session", "resource_type": "policies"}	2026-06-07 15:27:01.610832+00
4a0b8ba3-ddbe-422f-be1c-3f4b7c6adf30	{"id": "4a0b8ba3-ddbe-422f-be1c-3f4b7c6adf30", "action": "findings.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "c1875549-56b3-4685-82a6-81580c677006", "metadata": {"path": "/api/v1/findings", "method": "POST"}, "created_at": "2026-06-07T15:41:36.420202+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "findings"}	2026-06-07 15:41:36.534284+00
817b953d-7fce-40ae-94c6-30bf879f40a3	{"id": "817b953d-7fce-40ae-94c6-30bf879f40a3", "action": "risks.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/risks", "method": "POST"}, "created_at": "2026-06-07T15:41:38.469583+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "risks"}	2026-06-07 15:41:38.583528+00
6026fda7-f100-4268-83db-4af2f6a30e44	{"id": "6026fda7-f100-4268-83db-4af2f6a30e44", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "metadata": {"path": "/api/v1/policies", "method": "POST"}, "created_at": "2026-06-07T15:41:52.412961+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "policies"}	2026-06-07 15:41:52.526956+00
772ea63e-9474-4059-96cb-34e39a1825bd	{"id": "772ea63e-9474-4059-96cb-34e39a1825bd", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "5b27c9dc-8ed6-4cb0-b255-b75b8e09bbf9", "metadata": {"path": "/api/v1/policies/4d7e169f-2110-49da-a850-8a6cb667d804/approve", "method": "POST"}, "created_at": "2026-06-07T15:42:02.417470+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "4d7e169f-2110-49da-a850-8a6cb667d804", "resource_type": "policies"}	2026-06-07 15:42:02.531295+00
a9cfb71c-df6b-44fc-8542-6093ec1e0167	{"id": "a9cfb71c-df6b-44fc-8542-6093ec1e0167", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-07T15:48:11.494607+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-07 15:48:11.608033+00
31708924-554c-4025-8039-ebc9f5f7e94d	{"id": "31708924-554c-4025-8039-ebc9f5f7e94d", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-07T15:58:44.566570+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-07 15:58:44.679527+00
56240682-39a7-46cc-8cd5-fb507ae9245f	{"id": "56240682-39a7-46cc-8cd5-fb507ae9245f", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-07T16:48:25.130607+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-07 16:48:25.194435+00
afb0e0f9-a0c1-426b-9517-c6f7efe31e93	{"id": "afb0e0f9-a0c1-426b-9517-c6f7efe31e93", "action": "dashboard.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/dashboard/refresh", "method": "POST"}, "created_at": "2026-06-07T16:50:32.382017+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "refresh", "resource_type": "dashboard"}	2026-06-07 16:50:32.454242+00
4dd00473-8c74-4e16-bd5b-647f2069be23	{"id": "4dd00473-8c74-4e16-bd5b-647f2069be23", "action": "dashboard.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/dashboard/refresh", "method": "POST"}, "created_at": "2026-06-07T16:50:35.076123+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "refresh", "resource_type": "dashboard"}	2026-06-07 16:50:35.147938+00
2e82037b-d734-4f71-9032-09c1e62f32bf	{"id": "2e82037b-d734-4f71-9032-09c1e62f32bf", "action": "dashboard.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/dashboard/refresh", "method": "POST"}, "created_at": "2026-06-07T16:50:35.078969+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "refresh", "resource_type": "dashboard"}	2026-06-07 16:50:35.150062+00
214005ec-1a43-44b4-81a0-bb412b879741	{"id": "214005ec-1a43-44b4-81a0-bb412b879741", "action": "dashboard.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/dashboard/refresh", "method": "POST"}, "created_at": "2026-06-07T16:50:35.090426+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "refresh", "resource_type": "dashboard"}	2026-06-07 16:50:35.161003+00
cddcfd8c-e289-4efe-bcfb-27d257e8a8df	{"id": "cddcfd8c-e289-4efe-bcfb-27d257e8a8df", "action": "dashboard.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/dashboard/refresh", "method": "POST"}, "created_at": "2026-06-07T16:50:36.164329+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "refresh", "resource_type": "dashboard"}	2026-06-07 16:50:36.236081+00
eb3f66a4-f5d3-4173-814a-4b7d72321cca	{"id": "eb3f66a4-f5d3-4173-814a-4b7d72321cca", "action": "assessments.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/assessments", "method": "POST"}, "created_at": "2026-06-07T18:09:06.855481+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": null, "resource_type": "assessments"}	2026-06-07 18:09:06.922963+00
304507c0-25f4-48ef-a18d-d90c6696453f	{"id": "304507c0-25f4-48ef-a18d-d90c6696453f", "action": "assessments.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/assessments/7982833f-733c-4443-86ae-b13ff6ec72ca/submit-response", "method": "POST"}, "created_at": "2026-06-07T18:09:12.664874+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "7982833f-733c-4443-86ae-b13ff6ec72ca", "resource_type": "assessments"}	2026-06-07 18:09:12.73197+00
a65951f4-6310-4378-bada-a5c6c29f7101	{"id": "a65951f4-6310-4378-bada-a5c6c29f7101", "action": "assessments.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/assessments/7982833f-733c-4443-86ae-b13ff6ec72ca", "method": "PUT"}, "created_at": "2026-06-07T18:09:13.644408+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "7982833f-733c-4443-86ae-b13ff6ec72ca", "resource_type": "assessments"}	2026-06-07 18:09:13.705189+00
8a6c076f-fb8a-4e94-9a38-1002b399f933	{"id": "8a6c076f-fb8a-4e94-9a38-1002b399f933", "action": "assessments.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/assessments/7982833f-733c-4443-86ae-b13ff6ec72ca", "method": "PUT"}, "created_at": "2026-06-07T18:09:15.055101+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "7982833f-733c-4443-86ae-b13ff6ec72ca", "resource_type": "assessments"}	2026-06-07 18:09:15.1195+00
81ce184b-8f54-4b04-8117-5d9866e2f662	{"id": "81ce184b-8f54-4b04-8117-5d9866e2f662", "action": "assessments.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/assessments/7982833f-733c-4443-86ae-b13ff6ec72ca/submit-response", "method": "POST"}, "created_at": "2026-06-07T18:09:19.473110+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "7982833f-733c-4443-86ae-b13ff6ec72ca", "resource_type": "assessments"}	2026-06-07 18:09:19.540416+00
f28880a5-95ca-4bc7-9892-0ebbad81e4b7	{"id": "f28880a5-95ca-4bc7-9892-0ebbad81e4b7", "action": "assessments.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/assessments/7982833f-733c-4443-86ae-b13ff6ec72ca/submit-response", "method": "POST"}, "created_at": "2026-06-07T18:09:25.431367+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "7982833f-733c-4443-86ae-b13ff6ec72ca", "resource_type": "assessments"}	2026-06-07 18:09:25.498289+00
42ce8762-9988-4015-9ccd-77c734ba589c	{"id": "42ce8762-9988-4015-9ccd-77c734ba589c", "action": "assessments.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/assessments/7982833f-733c-4443-86ae-b13ff6ec72ca/submit-response", "method": "POST"}, "created_at": "2026-06-07T18:09:30.385878+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "7982833f-733c-4443-86ae-b13ff6ec72ca", "resource_type": "assessments"}	2026-06-07 18:09:30.451349+00
a56fdee5-3e7f-4368-b1af-7681738524b8	{"id": "a56fdee5-3e7f-4368-b1af-7681738524b8", "action": "assessments.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/assessments/7982833f-733c-4443-86ae-b13ff6ec72ca/submit-response", "method": "POST"}, "created_at": "2026-06-07T18:09:34.302015+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "7982833f-733c-4443-86ae-b13ff6ec72ca", "resource_type": "assessments"}	2026-06-07 18:09:34.367101+00
18fc62ee-19a8-4549-b8b6-c9ff295d33a5	{"id": "18fc62ee-19a8-4549-b8b6-c9ff295d33a5", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/gap-analysis", "method": "POST"}, "created_at": "2026-06-07T18:24:38.931923+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "gap-analysis", "resource_type": "ai"}	2026-06-07 18:24:38.987891+00
d5d5a9b6-8911-4295-8d7f-0b9e706c524f	{"id": "d5d5a9b6-8911-4295-8d7f-0b9e706c524f", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/gap-analysis", "method": "POST"}, "created_at": "2026-06-07T18:24:50.777137+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "gap-analysis", "resource_type": "ai"}	2026-06-07 18:24:50.835206+00
c505993e-3770-43ce-b8a4-e48f7e241f38	{"id": "c505993e-3770-43ce-b8a4-e48f7e241f38", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/ai-session/start", "method": "POST"}, "created_at": "2026-06-07T18:25:55.649852+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "ai-session", "resource_type": "policies"}	2026-06-07 18:25:55.711966+00
07b6200e-39e6-4549-b89a-3a362c3bd505	{"id": "07b6200e-39e6-4549-b89a-3a362c3bd505", "action": "policies.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/policies/ai-session/ac96bf03-0c7e-45d1-b84d-6920a04290eb/finalize", "method": "POST"}, "created_at": "2026-06-07T18:26:06.400655+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "ai-session", "resource_type": "policies"}	2026-06-07 18:26:06.462705+00
4c61656f-48be-4247-92e7-74f0ea9d3714	{"id": "4c61656f-48be-4247-92e7-74f0ea9d3714", "action": "departments.delete", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/departments/10006dc3-af42-438e-896c-ee672b5315a5", "method": "DELETE"}, "created_at": "2026-06-07T18:32:49.883527+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "10006dc3-af42-438e-896c-ee672b5315a5", "resource_type": "departments"}	2026-06-07 18:32:49.948021+00
596b6685-ddca-4b2f-adb8-99158ae977e5	{"id": "596b6685-ddca-4b2f-adb8-99158ae977e5", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/69c87202-e8e7-4951-ad51-f9b0bbe1f03e/read", "method": "PUT"}, "created_at": "2026-06-07T18:39:42.768246+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "69c87202-e8e7-4951-ad51-f9b0bbe1f03e", "resource_type": "notifications"}	2026-06-07 18:39:42.8352+00
7d510e39-8038-4d1f-8b1c-d92ad4215c0c	{"id": "7d510e39-8038-4d1f-8b1c-d92ad4215c0c", "action": "notifications.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/notifications/69c87202-e8e7-4951-ad51-f9b0bbe1f03e/read", "method": "PUT"}, "created_at": "2026-06-07T18:39:43.428812+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "69c87202-e8e7-4951-ad51-f9b0bbe1f03e", "resource_type": "notifications"}	2026-06-07 18:39:43.491525+00
1cf044ad-27f8-48bc-8073-2d6b11cfc350	{"id": "1cf044ad-27f8-48bc-8073-2d6b11cfc350", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-07T18:39:54.252521+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-07 18:39:54.317574+00
47f802e0-ce88-4122-b87d-c5f820a39e06	{"id": "47f802e0-ce88-4122-b87d-c5f820a39e06", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-09T04:43:53.971558+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-09 04:43:54.085969+00
87f9c145-cd9a-4ee1-8802-b7f3eeb866fd	{"id": "87f9c145-cd9a-4ee1-8802-b7f3eeb866fd", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-09T04:44:57.376822+00:00", "ip_address": "10.79.128.133", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-09 04:44:57.489826+00
8c0609a0-cdcc-4a46-9158-9962e4b313fc	{"id": "8c0609a0-cdcc-4a46-9158-9962e4b313fc", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-11T05:30:20.320914+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-11 05:30:20.445261+00
0cffec94-c144-4e8e-8348-ada073348500	{"id": "0cffec94-c144-4e8e-8348-ada073348500", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-11T06:23:44.399885+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-11 06:23:44.64938+00
e8173bf1-c4a0-48ae-9cd4-3b0b5e504e96	{"id": "e8173bf1-c4a0-48ae-9cd4-3b0b5e504e96", "action": "ai.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/ai/chat", "method": "POST"}, "created_at": "2026-06-11T06:25:12.752672+00:00", "ip_address": "127.0.0.1", "user_email": "", "resource_id": "chat", "resource_type": "ai"}	2026-06-11 06:25:12.994877+00
51a80bac-70f3-4dfc-b395-7f7bddf2f3f4	{"id": "51a80bac-70f3-4dfc-b395-7f7bddf2f3f4", "action": "dashboard.post", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/dashboard/refresh", "method": "POST"}, "created_at": "2026-06-11T09:00:32.054205+00:00", "ip_address": "10.79.138.194", "user_email": "", "resource_id": "refresh", "resource_type": "dashboard"}	2026-06-11 09:00:32.168008+00
dcf44311-1e98-4160-9fd9-ccbdef661264	{"id": "dcf44311-1e98-4160-9fd9-ccbdef661264", "action": "settings.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/settings/user-preferences", "method": "PUT"}, "created_at": "2026-06-17T07:42:40.775177+00:00", "ip_address": "10.79.128.146", "user_email": "", "resource_id": "user-preferences", "resource_type": "settings"}	2026-06-17 07:42:40.887814+00
640f6fba-858f-4c12-9056-fe52c24a6e41	{"id": "640f6fba-858f-4c12-9056-fe52c24a6e41", "action": "settings.put", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"path": "/api/v1/settings/user-preferences", "method": "PUT"}, "created_at": "2026-06-17T07:42:47.334846+00:00", "ip_address": "10.79.128.146", "user_email": "", "resource_id": "user-preferences", "resource_type": "settings"}	2026-06-17 07:42:47.447481+00
\.


--
-- Data for Name: audits; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.audits (id, data, created_at) FROM stdin;
c3439b25-5725-43e7-b731-8d32baf9d6f6	{"id": "c3439b25-5725-43e7-b731-8d32baf9d6f6", "name": "NAAC Cycle 3 Readiness Audit", "scope": {"departments": ["IQAC", "IT", "Library"]}, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "scheduled", "audit_type": "naac", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "report_data": {}, "completed_at": null, "lead_auditor": null, "scheduled_at": "2026-07-05T05:32:23.275438+00:00"}	2026-06-05 05:32:23.389649+00
f2a9b76a-7e2b-4ea8-b045-bc5861da88be	{"id": "f2a9b76a-7e2b-4ea8-b045-bc5861da88be", "name": "TEST Audit 1780638465", "scope": {"description": "test scope"}, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "scheduled", "audit_type": "internal", "created_at": "2026-06-05T05:47:46.428614+00:00", "updated_at": "2026-06-05T05:47:46.428614+00:00", "report_data": {}, "completed_at": null, "lead_auditor": "dc4d7985-f933-4460-b13f-23b1054b196d", "scheduled_at": null}	2026-06-05 05:47:46.541865+00
f47de518-083f-4016-8207-2a78846d6f5f	{"id": "f47de518-083f-4016-8207-2a78846d6f5f", "name": "TEST Audit 1780638970", "scope": {"description": "test scope"}, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "scheduled", "audit_type": "internal", "created_at": "2026-06-05T05:56:11.338484+00:00", "updated_at": "2026-06-05T05:56:11.338484+00:00", "report_data": {}, "completed_at": null, "lead_auditor": "dc4d7985-f933-4460-b13f-23b1054b196d", "scheduled_at": null}	2026-06-05 05:56:11.452411+00
\.


--
-- Data for Name: chat_messages; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.chat_messages (id, data, created_at) FROM stdin;
6626961e-96d7-4d7a-987a-5d65f07a8292	{"id": "6626961e-96d7-4d7a-987a-5d65f07a8292", "role": "user", "content": "What is DPDP S.8(5) in one sentence?", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T05:34:11.121138+00:00", "session_id": "762b70c8-3b66-4106-b7c4-4a5fed105b8c"}	2026-06-05 05:34:11.236112+00
cfb5814a-fe12-4a01-886b-5d62b9da7e73	{"id": "cfb5814a-fe12-4a01-886b-5d62b9da7e73", "role": "assistant", "content": "**DPDP S.8(5)** requires the Data Fiduciary to erase personal data once the purpose of processing is fulfilled and retention is no longer necessary, unless continued retention is required by law.", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T05:34:11.121138+00:00", "session_id": "762b70c8-3b66-4106-b7c4-4a5fed105b8c"}	2026-06-05 05:34:11.899271+00
cf79a40a-b346-4ccb-84a1-4203020d3464	{"id": "cf79a40a-b346-4ccb-84a1-4203020d3464", "role": "user", "content": "What is DPDP Act?", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T05:43:56.316596+00:00", "session_id": "d1ecd7aa-1bc3-4525-941a-62c4e702f07f"}	2026-06-05 05:43:56.432875+00
5b91a106-5466-46fd-9265-2e3579b4bcb5	{"id": "5b91a106-5466-46fd-9265-2e3579b4bcb5", "role": "assistant", "content": "The **DPDP Act** refers to India's **Digital Personal Data Protection Act, 2023** — the country's primary data protection legislation.\\n\\n## Key Points:\\n\\n**Purpose:** Protects individuals' personal data while enabling legitimate processing for lawful purposes.\\n\\n**Core Principles:**\\n- **Lawfulness, fairness & transparency** in data processing\\n- **Purpose limitation** — data collected only for specified purposes\\n- **Data minimization** — collect only what's necessary\\n- **Accuracy** — keep data correct and updated\\n- **Storage limitation** — retain only as long as needed\\n- **Reasonable security safeguards**\\n\\n**Key Rights (Chapter III):**\\n- Right to access your data\\n- Right to correction and erasure\\n- Right to grievance redressal\\n- Right to nominate (for deceased persons' data)\\n\\n**Obligations for \\"Data Fiduciaries\\" (organizations):**\\n- Obtain valid consent (DPDP S.6)\\n- Implement security safeguards (DPDP S.8)\\n- Report data breaches (DPDP S.8(5))\\n- Appoint a Data Protection Officer if significant processing (DPDP S.10)\\n- Conduct Data Protection Impact Assessments for certain activities\\n\\n**Penalties:** Up to ₹250 crores for serious violations\\n\\n**Applicability:** Organizations processing personal data of individuals in India, regardless of where the processing occurs.\\n\\n---\\n\\n**For your institution:** Your DPDP Act 2023 assessment shows **62.5% compliance** with **Maturity Level 3** (Defined). Would you like to review gaps or critical findings?", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T05:43:56.316596+00:00", "session_id": "d1ecd7aa-1bc3-4525-941a-62c4e702f07f"}	2026-06-05 05:43:57.093609+00
4d6f0e87-8bdb-4092-a8f0-a21ce4829d57	{"id": "4d6f0e87-8bdb-4092-a8f0-a21ce4829d57", "role": "user", "content": "What is DPDP Act?", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T05:56:37.347308+00:00", "session_id": "e6e3b8e1-e2e1-49fe-80ea-0cbee7b2e916"}	2026-06-05 05:56:37.461807+00
8b2bd6ce-16a0-4573-994a-bf00b961ba8f	{"id": "8b2bd6ce-16a0-4573-994a-bf00b961ba8f", "role": "assistant", "content": "# DPDP Act 2023\\n\\nThe **Digital Personal Data Protection Act, 2023 (DPDP Act)** is India's primary data protection legislation that governs how organizations collect, process, store, and handle personal data of individuals (called \\"Data Principals\\").\\n\\n## Key Highlights:\\n\\n**Purpose**: Protect individuals' digital personal data while enabling legitimate data processing for lawful purposes.\\n\\n**Applicability**:\\n- Applies to processing of digital personal data within India\\n- Also covers processing of data outside India if connected to offering goods/services in India\\n\\n**Core Principles**:\\n- **Consent-based processing** - Organizations (\\"Data Fiduciaries\\") must obtain clear consent\\n- **Purpose limitation** - Data used only for stated purposes\\n- **Data minimization** - Collect only necessary data\\n- **Accuracy & storage limitation** - Keep data accurate and don't retain longer than needed\\n\\n**Key Rights of Individuals** (Sections 11-14):\\n- Right to access personal data\\n- Right to correction and erasure\\n- Right to grievance redressal\\n- Right to nominate a successor\\n\\n**Organization Obligations**:\\n- Implement security safeguards (S.8)\\n- Report data breaches (S.8(5))\\n- Appoint Data Protection Officer (for Significant Data Fiduciaries)\\n- Maintain transparency about processing\\n\\n**Penalties**: Monetary penalties up to ₹250 crores for violations\\n\\n---\\n\\n**Your Institution's DPDP Compliance**: Your assessments show varying maturity - one at 62.5% (Maturity 3) and two at 100% (Maturity 5). Focus on the 62.5% assessment to close gaps.\\n\\nWould you like guidance on specific DPDP sections or compliance requirements?", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T05:56:37.347308+00:00", "session_id": "e6e3b8e1-e2e1-49fe-80ea-0cbee7b2e916"}	2026-06-05 05:56:38.119543+00
3e4ab3f7-b3a5-4753-afe8-59c77339a68d	{"id": "3e4ab3f7-b3a5-4753-afe8-59c77339a68d", "role": "user", "content": "Cite the DPDP S.5 obligation that maps to giving notice", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T06:14:48.060585+00:00", "session_id": "ede6a79f-32b4-41a3-8d1b-2e308c318863"}	2026-06-05 06:14:48.175511+00
e1de043f-beff-443b-a8c9-53d94da9609c	{"id": "e1de043f-beff-443b-a8c9-53d94da9609c", "role": "assistant", "content": "Under **DPDP Act 2023, Section 5** (Obligations of Data Fiduciaries), the relevant obligation for giving notice is:\\n\\n**Section 5(1)** — A Data Fiduciary shall give notice to the Data Principal containing the following information:\\n- (a) Personal data being collected and the purpose of processing\\n- (b) How the Data Principal can exercise their rights (withdraw consent, nominate, grievance redressal)\\n- (c) How the Data Principal can make a complaint to the Data Protection Board\\n\\nThis notice must be provided:\\n- In **clear and plain language** (Section 5(2))\\n- Before or at the time of seeking consent\\n- Through accessible means appropriate to the context\\n\\n---\\n\\n**Practical Compliance Tip:**  \\nThis maps to **ISO 27701:2019 control 7.3.2** (providing privacy notices) and requires you to maintain template notices for different processing scenarios (student enrollment, research participation, alumni engagement, etc.).", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T06:14:48.060585+00:00", "session_id": "ede6a79f-32b4-41a3-8d1b-2e308c318863"}	2026-06-05 06:14:48.83027+00
c11bd7cf-f0f4-4965-bf2a-6931effa4a5b	{"id": "c11bd7cf-f0f4-4965-bf2a-6931effa4a5b", "role": "user", "content": "What does DPDP Section 8(6) require?", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T06:39:23.710742+00:00", "session_id": "236965cf-8fc4-431c-84e2-917d48596608"}	2026-06-05 06:39:23.825548+00
08a09e8e-88a6-46a0-87ef-60c35163c119	{"id": "08a09e8e-88a6-46a0-87ef-60c35163c119", "role": "assistant", "content": "Local LLM not connected: Local LLM service is not available. Please ensure Ollama is running. Falling back to context summary.\\n\\nINSTITUTION CONTEXT:\\n- Total risks: 18. Critical (score≥20): 0\\n- Open critical findings: 2; total open: 11\\n- Assessments: DPDP Act 2023 score=62.5% maturity=3; ISO 27001:2022 score=48.0% maturity=2; DPDP Act 2023 score=100.0% maturity=5; DPDP Act 2023 score=100.0% maturity=5; ISO 27701:2019 score=100.0% maturity=5\\n- Policies: 19 policies on file\\n", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T18:39:53.759064+00:00", "session_id": "63770766-259c-4635-9629-f3bf1b0754eb"}	2026-06-07 18:39:54.070426+00
e5cbe7bb-59d2-4fe8-a732-16a330a94f07	{"id": "e5cbe7bb-59d2-4fe8-a732-16a330a94f07", "role": "assistant", "content": "**DPDP Act 2023, Section 8(6)** requires that:\\n\\n> **The Data Fiduciary shall erase personal data when consent is withdrawn**, or when the specified purpose is no longer being served, **unless retention is required by law**.\\n\\n## Key Requirements:\\n\\n1. **Trigger for Erasure:**\\n   - When the Data Principal withdraws consent\\n   - When the processing purpose has been fulfilled\\n   - When retention is no longer necessary\\n\\n2. **Exception:**\\n   - Personal data may be retained **only if** mandated by any law in force\\n\\n3. **Practical Implication:**\\n   - Institutions must implement automated or manual deletion workflows\\n   - Document legal retention requirements (e.g., UGC norms, audit trails)\\n   - Maintain logs of erasure requests and actions taken\\n\\n---\\n\\n### 🎓 **For Your University:**\\nWith your **62.5% - 100% DPDP compliance scores** (depending on assessment), ensure:\\n- Clear **data retention schedules** aligned with academic and legal requirements\\n- Processes to honor erasure requests within reasonable timelines\\n- Exception handling for statutory obligations (e.g., student records, financial audits)\\n\\nWould you like guidance on implementing an erasure policy or mapping retention requirements?", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T06:39:23.710742+00:00", "session_id": "236965cf-8fc4-431c-84e2-917d48596608"}	2026-06-05 06:39:24.4806+00
85fc26e1-9003-4c81-8f96-f240e7d51f7b	{"id": "85fc26e1-9003-4c81-8f96-f240e7d51f7b", "role": "user", "content": "What are the DPDP Act obligations for student data?", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T14:12:37.211181+00:00", "session_id": "9df3ab57-da8f-4451-8e6f-29a2f607a1f5"}	2026-06-07 14:12:37.325099+00
62218020-4a82-49eb-9115-e8906ffcabee	{"id": "62218020-4a82-49eb-9115-e8906ffcabee", "role": "assistant", "content": "Local LLM not connected: Local LLM service is not available. Please ensure Ollama is running. Falling back to context summary.\\n\\nINSTITUTION CONTEXT:\\n- Total risks: 17. Critical (score≥20): 0\\n- Open critical findings: 2; total open: 10\\n- Assessments: DPDP Act 2023 score=62.5% maturity=3; ISO 27001:2022 score=48.0% maturity=2; DPDP Act 2023 score=100.0% maturity=5; DPDP Act 2023 score=100.0% maturity=5\\n- Policies: 18 policies on file\\n", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T14:12:37.211181+00:00", "session_id": "9df3ab57-da8f-4451-8e6f-29a2f607a1f5"}	2026-06-07 14:12:38.029769+00
a15f3aa7-0b29-4c1b-b3af-0dec9ee8d780	{"id": "a15f3aa7-0b29-4c1b-b3af-0dec9ee8d780", "role": "user", "content": "What are my missing DPDP controls?", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T15:26:23.515356+00:00", "session_id": "bfbd1f9f-73db-432d-806c-47b35370d5f7"}	2026-06-07 15:26:23.629765+00
2e583b2f-15d8-4046-89d5-78f98bb46b63	{"id": "2e583b2f-15d8-4046-89d5-78f98bb46b63", "role": "assistant", "content": "Local LLM not connected: Local LLM service is not available. Please ensure Ollama is running. Falling back to context summary.\\n\\nINSTITUTION CONTEXT:\\n- Total risks: 17. Critical (score≥20): 0\\n- Open critical findings: 2; total open: 10\\n- Assessments: DPDP Act 2023 score=62.5% maturity=3; ISO 27001:2022 score=48.0% maturity=2; DPDP Act 2023 score=100.0% maturity=5; DPDP Act 2023 score=100.0% maturity=5\\n- Policies: 18 policies on file\\n", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T15:26:23.515356+00:00", "session_id": "bfbd1f9f-73db-432d-806c-47b35370d5f7"}	2026-06-07 15:26:24.295166+00
d9a6850a-82cf-495c-a7fa-4466b7616028	{"id": "d9a6850a-82cf-495c-a7fa-4466b7616028", "role": "user", "content": "Generate an ISO 27001 gap report.", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T15:48:10.166960+00:00", "session_id": "693529af-5014-4759-946a-e717feb2bcea"}	2026-06-07 15:48:10.280213+00
097defbd-e4fd-4b0d-89d6-80c6c357c775	{"id": "097defbd-e4fd-4b0d-89d6-80c6c357c775", "role": "assistant", "content": "Local LLM not connected: Local LLM service is not available. Please ensure Ollama is running. Falling back to context summary.\\n\\nINSTITUTION CONTEXT:\\n- Total risks: 18. Critical (score≥20): 0\\n- Open critical findings: 2; total open: 11\\n- Assessments: DPDP Act 2023 score=62.5% maturity=3; ISO 27001:2022 score=48.0% maturity=2; DPDP Act 2023 score=100.0% maturity=5; DPDP Act 2023 score=100.0% maturity=5\\n- Policies: 18 policies on file\\n", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T15:48:10.166960+00:00", "session_id": "693529af-5014-4759-946a-e717feb2bcea"}	2026-06-07 15:48:10.943973+00
c630bdb3-9725-4ac6-b24e-250646007c26	{"id": "c630bdb3-9725-4ac6-b24e-250646007c26", "role": "user", "content": "What are my missing DPDP controls?", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T15:58:43.259515+00:00", "session_id": "ee893774-ea32-4f75-8d09-4a9f9cc2ef3d"}	2026-06-07 15:58:43.372685+00
5c485fe5-20d2-497e-80de-f950a056b232	{"id": "5c485fe5-20d2-497e-80de-f950a056b232", "role": "assistant", "content": "Local LLM not connected: Local LLM service is not available. Please ensure Ollama is running. Falling back to context summary.\\n\\nINSTITUTION CONTEXT:\\n- Total risks: 18. Critical (score≥20): 0\\n- Open critical findings: 2; total open: 11\\n- Assessments: DPDP Act 2023 score=62.5% maturity=3; ISO 27001:2022 score=48.0% maturity=2; DPDP Act 2023 score=100.0% maturity=5; DPDP Act 2023 score=100.0% maturity=5\\n- Policies: 18 policies on file\\n", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T15:58:43.259515+00:00", "session_id": "ee893774-ea32-4f75-8d09-4a9f9cc2ef3d"}	2026-06-07 15:58:44.025713+00
4e3c4d3d-1ed2-4832-80f1-c85eb1948e0f	{"id": "4e3c4d3d-1ed2-4832-80f1-c85eb1948e0f", "role": "user", "content": "What are my missing DPDP controls?", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T16:48:23.789662+00:00", "session_id": "7e401674-81ec-4160-9ee6-838547e1a38e"}	2026-06-07 16:48:23.851301+00
40cdeb5e-17e3-407c-9239-1bc876a66b67	{"id": "40cdeb5e-17e3-407c-9239-1bc876a66b67", "role": "assistant", "content": "Local LLM not connected: Local LLM service is not available. Please ensure Ollama is running. Falling back to context summary.\\n\\nINSTITUTION CONTEXT:\\n- Total risks: 18. Critical (score≥20): 0\\n- Open critical findings: 2; total open: 11\\n- Assessments: DPDP Act 2023 score=62.5% maturity=3; ISO 27001:2022 score=48.0% maturity=2; DPDP Act 2023 score=100.0% maturity=5; DPDP Act 2023 score=100.0% maturity=5\\n- Policies: 18 policies on file\\n", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T16:48:23.789662+00:00", "session_id": "7e401674-81ec-4160-9ee6-838547e1a38e"}	2026-06-07 16:48:24.72013+00
82a65ce3-167d-414d-9d5f-bce523d58115	{"id": "82a65ce3-167d-414d-9d5f-bce523d58115", "role": "user", "content": "What are my missing DPDP controls?", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T18:39:53.759064+00:00", "session_id": "63770766-259c-4635-9629-f3bf1b0754eb"}	2026-06-07 18:39:53.823637+00
9cb04987-77e2-4fb9-98d8-7db9992d0f2f	{"id": "9cb04987-77e2-4fb9-98d8-7db9992d0f2f", "role": "user", "content": "hi", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-09T04:43:52.656075+00:00", "session_id": "04e1037a-9b83-4801-85d1-92936583b0be"}	2026-06-09 04:43:52.770283+00
4000997f-fe59-4b23-933f-4c2a08b77276	{"id": "4000997f-fe59-4b23-933f-4c2a08b77276", "role": "assistant", "content": "Local LLM not connected: Local LLM service is not available. Please ensure Ollama is running. Falling back to context summary.\\n\\nINSTITUTION CONTEXT:\\n- Total risks: 18. Critical (score≥20): 0\\n- Open critical findings: 2; total open: 11\\n- Assessments: DPDP Act 2023 score=62.5% maturity=3; ISO 27001:2022 score=48.0% maturity=2; DPDP Act 2023 score=100.0% maturity=5; DPDP Act 2023 score=100.0% maturity=5; ISO 27701:2019 score=100.0% maturity=5\\n- Policies: 19 policies on file\\n", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-09T04:43:52.656075+00:00", "session_id": "04e1037a-9b83-4801-85d1-92936583b0be"}	2026-06-09 04:43:53.431558+00
3d0a46d5-e419-486e-8b61-17d999c94c8a	{"id": "3d0a46d5-e419-486e-8b61-17d999c94c8a", "role": "user", "content": "hi", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-09T04:44:56.077003+00:00", "session_id": "17b71350-425b-4f94-a1b9-f827fe48f5bc"}	2026-06-09 04:44:56.190127+00
f3dfb552-8f45-44d8-83ab-d562a54a2875	{"id": "f3dfb552-8f45-44d8-83ab-d562a54a2875", "role": "assistant", "content": "Local LLM not connected: Local LLM service is not available. Please ensure Ollama is running. Falling back to context summary.\\n\\nINSTITUTION CONTEXT:\\n- Total risks: 18. Critical (score≥20): 0\\n- Open critical findings: 2; total open: 11\\n- Assessments: DPDP Act 2023 score=62.5% maturity=3; ISO 27001:2022 score=48.0% maturity=2; DPDP Act 2023 score=100.0% maturity=5; DPDP Act 2023 score=100.0% maturity=5; ISO 27701:2019 score=100.0% maturity=5\\n- Policies: 19 policies on file\\n", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-09T04:44:56.077003+00:00", "session_id": "17b71350-425b-4f94-a1b9-f827fe48f5bc"}	2026-06-09 04:44:56.839965+00
2bff9890-dd62-459b-a7f1-b787c7b56ca4	{"id": "2bff9890-dd62-459b-a7f1-b787c7b56ca4", "role": "user", "content": "What are my missing DPDP controls?", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-11T05:30:19.817040+00:00", "session_id": "ee2971b4-feed-4e4e-8bcb-76d5228574ff"}	2026-06-11 05:30:19.940425+00
e667d340-01c8-4ee2-aefe-0da71679e085	{"id": "e667d340-01c8-4ee2-aefe-0da71679e085", "role": "assistant", "content": "Local LLM not connected: Local LLM service is not available. Please ensure Ollama is running. Falling back to context summary.\\n\\nINSTITUTION CONTEXT:\\n- Total risks: 18. Critical (score≥20): 0\\n- Open critical findings: 2; total open: 11\\n- Assessments: DPDP Act 2023 score=62.5% maturity=3; ISO 27001:2022 score=48.0% maturity=2; DPDP Act 2023 score=100.0% maturity=5; DPDP Act 2023 score=100.0% maturity=5; ISO 27701:2019 score=100.0% maturity=5\\n- Policies: 19 policies on file\\n", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-11T05:30:19.817040+00:00", "session_id": "ee2971b4-feed-4e4e-8bcb-76d5228574ff"}	2026-06-11 05:30:20.19352+00
2fdf0575-915b-4fbb-b1eb-c86d5f4daa10	{"id": "2fdf0575-915b-4fbb-b1eb-c86d5f4daa10", "role": "user", "content": "What are my missing DPDP controls?", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-11T06:23:43.868388+00:00", "session_id": "4b2bf75a-1f1c-41ce-9bc9-02585df26ba9"}	2026-06-11 06:23:44.108924+00
4afd9cc5-0730-492e-9708-f21dd393e4fd	{"id": "4afd9cc5-0730-492e-9708-f21dd393e4fd", "role": "assistant", "content": "Local LLM not connected: Local LLM service returned HTTP 500: {\\"error\\":\\"error starting llama-server: llama-server binary not found (checked: /opt/homebrew/Cellar/ollama/0.30.6/libexec/lib/ollama/llama-server, /opt/homebrew/Cellar/ollama/0.30.6/libexec/llama-server, /opt/homebrew/Cellar/ollama/0.30.6/lib/ollama/llama-server, /opt/homebrew/Cellar/ollama/0.30.6/l Falling back to context summary.\\n\\nINSTITUTION CONTEXT:\\n- Total risks: 18. Critical (score≥20): 0\\n- Open critical findings: 2; total open: 11\\n- Assessments: DPDP Act 2023 score=62.5% maturity=3; ISO 27001:2022 score=48.0% maturity=2; DPDP Act 2023 score=100.0% maturity=5; DPDP Act 2023 score=100.0% maturity=5; ISO 27701:2019 score=100.0% maturity=5\\n- Policies: 19 policies on file\\n", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-11T06:23:43.868388+00:00", "session_id": "4b2bf75a-1f1c-41ce-9bc9-02585df26ba9"}	2026-06-11 06:23:44.362801+00
cbc577bf-10ab-4c4f-a60e-f3bfcac828e6	{"id": "cbc577bf-10ab-4c4f-a60e-f3bfcac828e6", "role": "user", "content": "What are the top DPDP Act 2023 obligations for student data?", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-11T06:25:12.228126+00:00", "session_id": "20ce84cb-313a-4803-ada0-3f41c9f8de6d"}	2026-06-11 06:25:12.471064+00
2683f2b6-b7f9-4600-b6d0-46a147a0b5d8	{"id": "2683f2b6-b7f9-4600-b6d0-46a147a0b5d8", "role": "assistant", "content": "Local LLM not connected: Local LLM service returned HTTP 500: {\\"error\\":\\"error starting llama-server: llama-server binary not found (checked: /opt/homebrew/Cellar/ollama/0.30.6/libexec/lib/ollama/llama-server, /opt/homebrew/Cellar/ollama/0.30.6/libexec/llama-server, /opt/homebrew/Cellar/ollama/0.30.6/lib/ollama/llama-server, /opt/homebrew/Cellar/ollama/0.30.6/l Falling back to context summary.\\n\\nINSTITUTION CONTEXT:\\n- Total risks: 18. Critical (score≥20): 0\\n- Open critical findings: 2; total open: 11\\n- Assessments: DPDP Act 2023 score=62.5% maturity=3; ISO 27001:2022 score=48.0% maturity=2; DPDP Act 2023 score=100.0% maturity=5; DPDP Act 2023 score=100.0% maturity=5; ISO 27701:2019 score=100.0% maturity=5\\n- Policies: 19 policies on file\\n", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-11T06:25:12.228126+00:00", "session_id": "20ce84cb-313a-4803-ada0-3f41c9f8de6d"}	2026-06-11 06:25:12.733662+00
\.


--
-- Data for Name: chat_sessions; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.chat_sessions (id, data, created_at) FROM stdin;
\.


--
-- Data for Name: control_assignments; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.control_assignments (id, data, created_at) FROM stdin;
5cceb3f3-971f-4ac7-84f1-57be6362244f	{"id": "5cceb3f3-971f-4ac7-84f1-57be6362244f", "notes": "Submit access-review evidence and security playbook", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "pending", "due_date": "2026-07-15", "control_id": "92e044eb-7fa0-4924-942c-43d068e8b69f", "created_at": "2026-06-05T06:27:36.164841+00:00", "updated_at": "2026-06-05T06:27:36.164841+00:00", "control_code": "DPDP-S8-C1", "evidence_ids": [], "control_title": "Accuracy, completeness and consistency of personal data", "department_id": "10006dc3-af42-438e-896c-ee672b5315a5", "assigned_by_id": "56ba859d-20d6-4470-974f-33d3165c9833", "response_notes": null, "department_name": "IT", "assignee_user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "assigned_by_email": "ciso@rut.edu.in"}	2026-06-05 06:27:36.280257+00
ed7766c4-d6cc-4105-ab63-b11805907b57	{"id": "ed7766c4-d6cc-4105-ab63-b11805907b57", "org_id": "7bab9ff2-c2fd-4dc2-b0c2-6ec6bd8bf129", "status": "pending", "control_id": "ff2baf56-c790-4ec3-8ae9-d3ebcba31912", "created_at": "2026-06-07T13:42:47.143124+00:00", "updated_at": "2026-06-07T13:42:47.143124+00:00", "control_code": "DPDP-S4-C1", "evidence_ids": [], "control_title": "Consent or legitimate use as basis for processing", "department_id": "3ee766ca-d414-4b9b-8713-73b70cc4ae49", "assigned_by_id": "0c272a62-9d99-4461-a4ef-c5545f1bdf77", "department_name": "OrgBDept", "assignee_user_id": "b2284cc6-c822-4a71-8ac5-23bb1793258d", "assigned_by_email": "admin@iit-testopolis.edu.in"}	2026-06-07 13:42:59.72948+00
\.


--
-- Data for Name: controls; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.controls (id, data, created_at) FROM stdin;
ff2baf56-c790-4ec3-8ae9-d3ebcba31912	{"id": "ff2baf56-c790-4ec3-8ae9-d3ebcba31912", "title": "Consent or legitimate use as basis for processing", "domain": "Lawful Processing", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["consent", "lawful", "processing", "data fiduciary", "purpose"], "severity": "critical", "control_id": "DPDP-S4-C1", "created_at": "2026-06-05T05:30:19.780727+00:00", "updated_at": "2026-06-05T05:30:19.780727+00:00", "description": "A Data Fiduciary may process personal data of a Data Principal only for a lawful purpose for which the Data Principal has given her consent, or for certain legitimate uses (Section 4).", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Does the institution document the lawful basis for every personal-data processing activity (admissions, exams, hostel, alumni)?", "Is consent captured separately from other terms and conditions?"], "mapped_controls": ["ISO27701-7.2.2", "NIST-GV.PO-01"], "maturity_weight": 1.0, "evidence_required": ["RoPA (Record of Processing Activities)", "Consent capture screenshots/forms"]}	2026-06-05 05:30:30.85429+00
15af9e59-0710-4d2d-b804-9cf6486e55b6	{"id": "15af9e59-0710-4d2d-b804-9cf6486e55b6", "title": "Notice to Data Principal before consent", "domain": "Notice", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["notice", "privacy", "language", "purpose"], "severity": "high", "control_id": "DPDP-S5-C1", "created_at": "2026-06-05T05:30:19.780727+00:00", "updated_at": "2026-06-05T05:30:19.780727+00:00", "description": "Every request for consent must be accompanied by or preceded by a clear notice in English or any language listed in the Eighth Schedule, describing the personal data and purpose of processing, contact of DPO, and rights of the Data Principal (Section 5).", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Is a multilingual privacy notice presented at every data-collection touchpoint (admission portal, LMS, library, hostel)?", "Does the notice list the DPO contact and the means to exercise rights?"], "mapped_controls": ["ISO27701-7.3.2", "NIST-GV.PO-02"], "maturity_weight": 0.9, "evidence_required": ["Published privacy notice (URL)", "Translation log"]}	2026-06-05 05:30:32.167011+00
ac03c3a1-95ee-4364-8607-0970ec4fd94f	{"id": "ac03c3a1-95ee-4364-8607-0970ec4fd94f", "title": "Free, specific, informed and unambiguous consent", "domain": "Consent Management", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["consent", "withdrawal", "specific", "informed"], "severity": "high", "control_id": "DPDP-S6-C1", "created_at": "2026-06-05T05:30:19.780727+00:00", "updated_at": "2026-06-05T05:30:19.780727+00:00", "description": "Consent must be free, specific, informed, unconditional and unambiguous with a clear affirmative action (Section 6). Withdrawal must be as easy as giving consent.", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Is the institution using a Consent Management Platform that records grant and withdrawal events?", "Can a student withdraw consent online without contacting the office?"], "mapped_controls": ["ISO27701-7.2.4"], "maturity_weight": 0.95, "evidence_required": ["CMP architecture", "Withdrawal flow walkthrough"]}	2026-06-05 05:30:33.476237+00
ff888aee-1508-4d15-9e25-1d28c76cdfaf	{"id": "ff888aee-1508-4d15-9e25-1d28c76cdfaf", "title": "Legitimate uses without consent (employment, public interest)", "domain": "Legitimate Uses", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["legitimate", "employment", "state function"], "severity": "medium", "control_id": "DPDP-S7-C1", "created_at": "2026-06-05T05:30:19.780727+00:00", "updated_at": "2026-06-05T05:30:19.780727+00:00", "description": "Processing without consent is permitted for specified legitimate uses including employment, performance of state functions, medical emergency, disaster, and compliance with judgment (Section 7).", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Are legitimate-use processing activities (e.g., employee payroll, statutory reporting to AICTE/UGC) clearly identified?"], "mapped_controls": ["ISO27701-7.2.2"], "maturity_weight": 0.7, "evidence_required": ["Legitimate-use register"]}	2026-06-05 05:30:34.785576+00
92e044eb-7fa0-4924-942c-43d068e8b69f	{"id": "92e044eb-7fa0-4924-942c-43d068e8b69f", "title": "Accuracy, completeness and consistency of personal data", "domain": "Data Fiduciary Obligations", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["accuracy", "completeness", "data quality"], "severity": "high", "control_id": "DPDP-S8-C1", "created_at": "2026-06-05T05:30:19.780727+00:00", "updated_at": "2026-06-05T05:30:19.780727+00:00", "description": "Data Fiduciary must ensure the completeness, accuracy and consistency of personal data where it is used to make a decision that affects the Data Principal or is to be disclosed to another Data Fiduciary (Section 8(3)).", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["How is student / faculty data periodically reviewed for accuracy in the ERP / SIS?", "Are corrections logged with timestamps and owner?"], "mapped_controls": ["ISO27001-A.5.34"], "maturity_weight": 0.8, "evidence_required": ["Data quality SOP", "Correction logs"]}	2026-06-05 05:30:36.098645+00
092110e3-bcb0-45b0-a9cb-a5c169c53dd4	{"id": "092110e3-bcb0-45b0-a9cb-a5c169c53dd4", "title": "Reasonable security safeguards", "domain": "Data Fiduciary Obligations", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["security", "safeguards", "breach prevention"], "severity": "critical", "control_id": "DPDP-S8-C2", "created_at": "2026-06-05T05:30:19.780727+00:00", "updated_at": "2026-06-05T05:30:19.780727+00:00", "description": "Implement appropriate technical and organisational measures to prevent personal data breaches (Section 8(5)).", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Is access to the SIS/ERP encrypted in transit and at rest?", "Are administrative privileges reviewed quarterly?"], "mapped_controls": ["ISO27001-A.8.24", "NIST-PR.DS-01"], "maturity_weight": 1.0, "evidence_required": ["Encryption policy", "Access review report"]}	2026-06-05 05:30:37.408055+00
13d93e10-c971-402f-8468-c4e8136b7ece	{"id": "13d93e10-c971-402f-8468-c4e8136b7ece", "title": "Personal data breach notification to Board and Principal", "domain": "Data Fiduciary Obligations", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["breach", "notification", "incident"], "severity": "critical", "control_id": "DPDP-S8-C3", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "In the event of a personal data breach, notify the Data Protection Board of India and each affected Data Principal in the prescribed manner (Section 8(6)).", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Is there a documented breach-response runbook with SLAs?", "Has a tabletop exercise been conducted in the last 12 months?"], "mapped_controls": ["ISO27001-A.5.24", "NIST-RS.MA-01"], "maturity_weight": 1.0, "evidence_required": ["IR plan", "Tabletop minutes"]}	2026-06-05 05:31:08.194957+00
81809c43-6bfb-4f43-83b3-e8b8e689d3c1	{"id": "81809c43-6bfb-4f43-83b3-e8b8e689d3c1", "title": "Erasure on withdrawal or purpose completion", "domain": "Data Retention", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["retention", "erasure", "deletion"], "severity": "high", "control_id": "DPDP-S8-C4", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Erase personal data upon withdrawal of consent or as soon as it is reasonable to assume the purpose is no longer served (Section 8(7)).", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Is a retention schedule defined for student, faculty, alumni and applicant records?", "Is erasure automated in ERP / LMS?"], "mapped_controls": ["ISO27701-7.4.7"], "maturity_weight": 0.85, "evidence_required": ["Retention schedule", "Erasure logs"]}	2026-06-05 05:31:09.535824+00
3af7d895-9974-44fd-855c-c015fec92df4	{"id": "3af7d895-9974-44fd-855c-c015fec92df4", "title": "Verifiable parental consent for processing children's data", "domain": "Children's Data", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["child", "parental consent", "minor", "tracking"], "severity": "critical", "control_id": "DPDP-S9-C1", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Obtain verifiable parental consent before processing personal data of a child (under 18). No tracking, behavioural monitoring or targeted advertising directed at children (Section 9).", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Is parental consent captured for applicants under 18 and for school-affiliated programmes?", "Is behavioural analytics disabled for minor accounts in LMS?"], "mapped_controls": ["ISO27701-7.2.5"], "maturity_weight": 0.95, "evidence_required": ["Parental consent form", "LMS configuration evidence"]}	2026-06-05 05:31:10.878926+00
aad047b8-b832-4591-842a-9bc34c35b08b	{"id": "aad047b8-b832-4591-842a-9bc34c35b08b", "title": "DPO, DPIA and independent data auditor", "domain": "Significant Data Fiduciary", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["DPO", "DPIA", "audit", "significant"], "severity": "high", "control_id": "DPDP-S10-C1", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "If notified as a Significant Data Fiduciary, appoint a Data Protection Officer based in India, conduct DPIAs and undergo periodic independent data audits (Section 10).", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Has a DPO been formally appointed and announced?", "Is a DPIA template in use for new processing activities?"], "mapped_controls": ["ISO27701-6.3.1", "NIST-GV.RR-01"], "maturity_weight": 0.85, "evidence_required": ["DPO appointment letter", "DPIA template"]}	2026-06-05 05:31:12.219284+00
c1cb6596-06c7-4a56-884b-1eda01f49d1c	{"id": "c1cb6596-06c7-4a56-884b-1eda01f49d1c", "title": "Right to access information about personal data", "domain": "Data Principal Rights", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["access", "right", "DSAR", "subject access"], "severity": "high", "control_id": "DPDP-S11-C1", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Data Principal has the right to obtain a summary of the personal data being processed, the processing activities, and identities of all other Data Fiduciaries with whom data has been shared (Section 11).", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Is a self-service portal available for students to view what data is held about them?", "Is response time tracked against a SLA (e.g., 30 days)?"], "mapped_controls": ["ISO27701-7.3.4"], "maturity_weight": 0.9, "evidence_required": ["DSAR SOP", "Sample DSAR response"]}	2026-06-05 05:31:13.559529+00
595ac56e-92e2-438f-a23f-608e7d6bd022	{"id": "595ac56e-92e2-438f-a23f-608e7d6bd022", "title": "Right to correction, completion, updation and erasure", "domain": "Data Principal Rights", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["correction", "erasure", "update"], "severity": "high", "control_id": "DPDP-S12-C1", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Data Principal has the right to correct, complete, update and erase her personal data, subject to applicable retention obligations (Section 12).", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Can a graduate request erasure of optional fields such as photographs?", "Are correction requests audit-logged?"], "mapped_controls": ["ISO27701-7.3.6"], "maturity_weight": 0.85, "evidence_required": ["Rights workflow", "Audit log sample"]}	2026-06-05 05:31:14.900494+00
cb9f4b2e-38a7-4780-b9d5-ec6099e85984	{"id": "cb9f4b2e-38a7-4780-b9d5-ec6099e85984", "title": "Right to grievance redressal", "domain": "Data Principal Rights", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["grievance", "redressal", "officer"], "severity": "high", "control_id": "DPDP-S13-C1", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "A Data Fiduciary must provide a readily available means of grievance redressal and respond within prescribed time (Section 13).", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Is the grievance officer's contact published on the institution website?", "What is the average grievance turnaround time?"], "mapped_controls": ["ISO27701-7.3.7"], "maturity_weight": 0.8, "evidence_required": ["Grievance officer notification", "Turnaround report"]}	2026-06-05 05:31:16.241643+00
f8715b57-2c71-4a30-abb2-41dadb82afe1	{"id": "f8715b57-2c71-4a30-abb2-41dadb82afe1", "title": "Restriction on transfer outside India", "domain": "Cross-Border Transfer", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["cross-border", "transfer", "outside India"], "severity": "high", "control_id": "DPDP-S16-C1", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Central Government may, by notification, restrict the transfer of personal data by a Data Fiduciary to any country or territory outside India (Section 16).", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Are foreign-hosted SaaS tools (LMS, plagiarism check) inventoried with country of processing?", "Are contractual safeguards (DPA) in place with foreign sub-processors?"], "mapped_controls": ["ISO27701-7.5.1"], "maturity_weight": 0.75, "evidence_required": ["Cross-border transfer register", "DPAs"]}	2026-06-05 05:31:17.581932+00
622f0f00-8ea9-4e67-8f9b-42121e00a477	{"id": "622f0f00-8ea9-4e67-8f9b-42121e00a477", "title": "Awareness of monetary penalties up to INR 250 crore", "domain": "Penalties", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["penalty", "fine", "schedule", "250 crore"], "severity": "critical", "control_id": "DPDP-PEN-C1", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "The Schedule to the Act specifies penalties up to ₹250 crore per breach for failure to protect personal data; ₹200 crore for failure to notify; ₹50 crore for breaches involving children's data.", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Has senior leadership been formally briefed on the financial exposure of non-compliance?"], "mapped_controls": ["NIST-GV.OV-03"], "maturity_weight": 0.7, "evidence_required": ["Board / governing council minutes"]}	2026-06-05 05:31:18.923063+00
15ec9217-09ab-4528-9271-5699688f8136	{"id": "15ec9217-09ab-4528-9271-5699688f8136", "title": "Policies for information security", "domain": "A.5 Organizational", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["policy", "information security"], "severity": "high", "control_id": "ISO27001-A.5.1", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "A set of policies for information security shall be defined, approved by management, published, communicated to and acknowledged by relevant personnel and relevant interested parties.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Is an information security policy approved by the Vice-Chancellor / Governing Council?", "Is it reviewed annually?"], "mapped_controls": ["NIST-GV.PO-01"], "maturity_weight": 1.0, "evidence_required": ["Signed policy", "Review minutes"]}	2026-06-05 05:31:21.604044+00
c6f381e0-6cd8-42a7-946d-28e466abd6f9	{"id": "c6f381e0-6cd8-42a7-946d-28e466abd6f9", "title": "Threat intelligence", "domain": "A.5 Organizational", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["threat", "intelligence", "cert-in"], "severity": "medium", "control_id": "ISO27001-A.5.7", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Information relating to information security threats shall be collected and analysed to produce threat intelligence.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Is the institution subscribed to CERT-In / academic ISAC threat feeds?"], "mapped_controls": ["NIST-ID.RA-02"], "maturity_weight": 0.6, "evidence_required": ["Subscription proof", "Threat brief"]}	2026-06-05 05:31:22.944914+00
b719bf43-82da-4180-bf97-e227523e25f1	{"id": "b719bf43-82da-4180-bf97-e227523e25f1", "title": "Information security in supplier relationships", "domain": "A.5 Organizational", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["supplier", "vendor", "third-party"], "severity": "high", "control_id": "ISO27001-A.5.19", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Processes and procedures shall be defined and implemented to manage the information security risks associated with the use of supplier's products or services.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Is a vendor risk assessment performed for every major SaaS (ERP, LMS, plagiarism, library)?"], "mapped_controls": ["NIST-GV.SC-01", "DPDP-S8-C7"], "maturity_weight": 0.85, "evidence_required": ["Vendor risk register"]}	2026-06-05 05:31:24.285141+00
42485e25-65cd-488d-80be-79819745d067	{"id": "42485e25-65cd-488d-80be-79819745d067", "title": "Information security incident management planning and preparation", "domain": "A.5 Organizational", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["incident", "response", "preparation"], "severity": "critical", "control_id": "ISO27001-A.5.24", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "The organization shall plan and prepare for managing information security incidents by defining, establishing and communicating processes, roles and responsibilities.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Is the IR plan tested at least annually?", "Are escalation contacts current?"], "mapped_controls": ["NIST-RS.MA-01", "DPDP-S8-C6"], "maturity_weight": 0.95, "evidence_required": ["IR plan", "Drill report"]}	2026-06-05 05:31:25.626522+00
70d54696-3640-4a3c-ba27-037b2b0ea1ce	{"id": "70d54696-3640-4a3c-ba27-037b2b0ea1ce", "title": "Privacy and protection of PII", "domain": "A.5 Organizational", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["privacy", "PII", "personal data"], "severity": "critical", "control_id": "ISO27001-A.5.34", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "The organization shall identify and meet requirements regarding the preservation of privacy and protection of PII according to applicable laws and regulations and contractual requirements.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Are PII inventories maintained for each department (admissions, exam cell, HR)?"], "mapped_controls": ["ISO27701-6.2", "DPDP-S8-C1"], "maturity_weight": 1.0, "evidence_required": ["PII inventory", "DPDP applicability matrix"]}	2026-06-05 05:31:26.967658+00
6a6de594-0a40-4469-8caa-7c5885df003d	{"id": "6a6de594-0a40-4469-8caa-7c5885df003d", "title": "Information security awareness, education and training", "domain": "A.6 People", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["awareness", "training", "education"], "severity": "medium", "control_id": "ISO27001-A.6.3", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Personnel of the organization and relevant interested parties shall receive appropriate awareness education and training and regular updates of the organization's information security policy.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Is annual security awareness training mandatory for faculty, staff and student-workers?"], "mapped_controls": ["NIST-PR.AT-01"], "maturity_weight": 0.8, "evidence_required": ["Training completion reports"]}	2026-06-05 05:31:28.312188+00
31817fce-d2a1-4d95-aca3-ce0f842b46ec	{"id": "31817fce-d2a1-4d95-aca3-ce0f842b46ec", "title": "Physical security perimeters", "domain": "A.7 Physical", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["physical", "perimeter", "server room"], "severity": "medium", "control_id": "ISO27001-A.7.1", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Security perimeters shall be defined and used to protect areas that contain information and other associated assets.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Are server rooms and exam evaluation rooms protected by access-controlled doors?"], "mapped_controls": ["NIST-PR.AA-06"], "maturity_weight": 0.7, "evidence_required": ["Access logs", "CCTV footage retention policy"]}	2026-06-05 05:31:29.658684+00
cf596709-266d-4be4-9f05-5ccf9591435d	{"id": "cf596709-266d-4be4-9f05-5ccf9591435d", "title": "Information access restriction", "domain": "A.8 Technological", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["access control", "RBAC", "authorization"], "severity": "high", "control_id": "ISO27001-A.8.3", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Access to information and other associated assets shall be restricted in accordance with the established topic-specific policy on access control.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Are role-based access controls implemented in the ERP / SIS?", "Are accounts of former employees disabled within 24 hours?"], "mapped_controls": ["NIST-PR.AA-01", "DPDP-S8-C5"], "maturity_weight": 0.95, "evidence_required": ["RBAC matrix", "Deprovisioning log"]}	2026-06-05 05:31:31.00108+00
b7125076-e986-479c-ba3f-58403cc8990d	{"id": "b7125076-e986-479c-ba3f-58403cc8990d", "title": "Information backup", "domain": "A.8 Technological", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["backup", "restore", "recovery"], "severity": "high", "control_id": "ISO27001-A.8.13", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Backup copies of information, software and systems shall be maintained and regularly tested in accordance with the agreed topic-specific policy on backup.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Are SIS and ERP backups taken daily, encrypted and tested via restore drills quarterly?"], "mapped_controls": ["NIST-PR.DS-11"], "maturity_weight": 0.85, "evidence_required": ["Backup policy", "Restore drill report"]}	2026-06-05 05:31:32.335962+00
5c051771-a9ec-47b1-b717-23ec1dcc6f1a	{"id": "5c051771-a9ec-47b1-b717-23ec1dcc6f1a", "title": "Use of cryptography", "domain": "A.8 Technological", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["cryptography", "encryption", "TLS", "key"], "severity": "high", "control_id": "ISO27001-A.8.24", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Rules for the effective use of cryptography, including cryptographic key management, shall be defined and implemented.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Is data in transit secured via TLS 1.2+?", "Is sensitive PII encrypted at rest?"], "mapped_controls": ["NIST-PR.DS-01", "DPDP-S8-C5"], "maturity_weight": 0.9, "evidence_required": ["TLS scan report", "Encryption inventory"]}	2026-06-05 05:31:33.643684+00
2969ac11-a93b-420a-b6c7-eef8b8efb0dc	{"id": "2969ac11-a93b-420a-b6c7-eef8b8efb0dc", "title": "Information security policies for PII", "domain": "PIMS – Information Security", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["PII", "policy", "PIMS"], "severity": "high", "control_id": "ISO27701-6.2", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Define and maintain information security policies that also address PII protection.", "framework_id": "eed067e5-85ba-4db6-9362-402f615f5830", "framework_name": "ISO 27701:2019", "audit_questions": ["Does the InfoSec policy explicitly reference PII handling?"], "mapped_controls": ["ISO27001-A.5.1"], "maturity_weight": 0.85, "evidence_required": ["Updated InfoSec policy"]}	2026-06-05 05:31:36.260533+00
ad740353-e0fd-4e81-b2e7-09699c956f71	{"id": "ad740353-e0fd-4e81-b2e7-09699c956f71", "title": "Identify lawful basis", "domain": "PII Controllers – Conditions for Collection", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["lawful basis", "RoPA"], "severity": "critical", "control_id": "ISO27701-7.2.2", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "The organization shall determine, document and comply with the relevant lawful basis for the processing of PII.", "framework_id": "eed067e5-85ba-4db6-9362-402f615f5830", "framework_name": "ISO 27701:2019", "audit_questions": ["Is each processing activity tagged with a DPDP lawful basis?"], "mapped_controls": ["DPDP-S4-C1"], "maturity_weight": 1.0, "evidence_required": ["RoPA"]}	2026-06-05 05:31:37.568276+00
0c4c9e19-0f17-45a9-8b22-15e9c7fcf003	{"id": "0c4c9e19-0f17-45a9-8b22-15e9c7fcf003", "title": "Providing access to PII principals", "domain": "PII Controllers – Principal Rights", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["DSAR", "access", "principal"], "severity": "high", "control_id": "ISO27701-7.3.4", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "The organization shall implement appropriate procedures for granting PII principals access to their PII.", "framework_id": "eed067e5-85ba-4db6-9362-402f615f5830", "framework_name": "ISO 27701:2019", "audit_questions": ["Is a DSAR portal in production?"], "mapped_controls": ["DPDP-S11-C1"], "maturity_weight": 0.9, "evidence_required": ["DSAR SOP", "Tickets"]}	2026-06-05 05:31:38.876129+00
7a4edc19-9425-4ba5-bf51-f681d1cf74be	{"id": "7a4edc19-9425-4ba5-bf51-f681d1cf74be", "title": "Retention and disposal of PII", "domain": "PII Controllers – Retention", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["retention", "disposal"], "severity": "high", "control_id": "ISO27701-7.4.7", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "The organization shall determine and document a policy regarding retention and disposal of PII.", "framework_id": "eed067e5-85ba-4db6-9362-402f615f5830", "framework_name": "ISO 27701:2019", "audit_questions": ["Is the retention schedule signed off by the registrar?"], "mapped_controls": ["DPDP-S8-C4"], "maturity_weight": 0.85, "evidence_required": ["Retention schedule"]}	2026-06-05 05:31:40.183627+00
8bf66023-5e80-4075-a773-6221b5606dc7	{"id": "8bf66023-5e80-4075-a773-6221b5606dc7", "title": "Identify basis for PII transfer between jurisdictions", "domain": "PII Controllers – Sharing & Transfer", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["cross-border", "transfer"], "severity": "high", "control_id": "ISO27701-7.5.1", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Document the basis for transfers of PII between jurisdictions and ensure equivalent safeguards.", "framework_id": "eed067e5-85ba-4db6-9362-402f615f5830", "framework_name": "ISO 27701:2019", "audit_questions": ["Are cross-border transfers logged with country and safeguard?"], "mapped_controls": ["DPDP-S16-C1"], "maturity_weight": 0.8, "evidence_required": ["Transfer register"]}	2026-06-05 05:31:41.49174+00
731670aa-0e93-46a7-a3d4-f03f7dfd719c	{"id": "731670aa-0e93-46a7-a3d4-f03f7dfd719c", "title": "Organizational mission, expectations and obligations are understood", "domain": "GOVERN – Organizational Context", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["mission", "context", "governance"], "severity": "medium", "control_id": "NIST-GV.OC-01", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "The organizational mission is understood and informs cybersecurity risk management.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Is cyber risk linked to the institution's NAAC and NIRF objectives?"], "mapped_controls": [], "maturity_weight": 0.7, "evidence_required": ["Risk-strategy memo"]}	2026-06-05 05:31:44.10806+00
a848f003-8609-4a88-a914-4da82821581c	{"id": "a848f003-8609-4a88-a914-4da82821581c", "title": "Risk management objectives are established and agreed", "domain": "GOVERN – Risk Management Strategy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["risk", "appetite", "strategy"], "severity": "high", "control_id": "NIST-GV.RM-01", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Risk management objectives are established, agreed and communicated.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Is the institution's risk appetite documented?"], "mapped_controls": [], "maturity_weight": 0.9, "evidence_required": ["Risk appetite statement"]}	2026-06-05 05:31:45.416001+00
dbddda22-e5ed-42fa-8403-641f3a1aec65	{"id": "dbddda22-e5ed-42fa-8403-641f3a1aec65", "title": "Cybersecurity roles and responsibilities are established", "domain": "GOVERN – Roles, Responsibilities & Authorities", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["roles", "responsibilities", "CISO"], "severity": "high", "control_id": "NIST-GV.RR-01", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Roles, responsibilities, and authorities to foster accountability, performance assessment, and continuous improvement are established and communicated.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Is a CISO / Information Security Officer designated?"], "mapped_controls": ["DPDP-S10-C1"], "maturity_weight": 0.9, "evidence_required": ["RACI matrix"]}	2026-06-05 05:31:46.72463+00
a8e9c139-9a22-467a-942a-5261d51b1a4c	{"id": "a8e9c139-9a22-467a-942a-5261d51b1a4c", "title": "Cybersecurity policy is established", "domain": "GOVERN – Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["policy"], "severity": "high", "control_id": "NIST-GV.PO-01", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Policy for managing cybersecurity risks is established, based on organizational context, and communicated.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Is the cyber policy approved and current within 12 months?"], "mapped_controls": ["ISO27001-A.5.1"], "maturity_weight": 0.85, "evidence_required": ["Approved policy"]}	2026-06-05 05:31:48.033598+00
41e626c9-4f8f-4774-b3d0-c287670398c1	{"id": "41e626c9-4f8f-4774-b3d0-c287670398c1", "title": "Inventories of hardware managed by the organization are maintained", "domain": "IDENTIFY – Asset Management", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["asset", "inventory", "CMDB"], "severity": "medium", "control_id": "NIST-ID.AM-01", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Inventories of hardware, software, services and systems are maintained.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Is a CMDB / asset inventory updated quarterly?"], "mapped_controls": [], "maturity_weight": 0.75, "evidence_required": ["Inventory export"]}	2026-06-05 05:31:49.341255+00
8e4ac506-decd-4fc4-b6de-b3821130c773	{"id": "8e4ac506-decd-4fc4-b6de-b3821130c773", "title": "Vulnerabilities in assets are identified, validated, recorded", "domain": "IDENTIFY – Risk Assessment", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["vulnerability", "scan"], "severity": "high", "control_id": "NIST-ID.RA-01", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Vulnerabilities in assets are identified, validated, and recorded.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Is a vulnerability scan run at least quarterly on internet-facing systems?"], "mapped_controls": [], "maturity_weight": 0.85, "evidence_required": ["VA report"]}	2026-06-05 05:31:50.648992+00
20566f2b-4372-4d7b-917b-5467bab19b92	{"id": "20566f2b-4372-4d7b-917b-5467bab19b92", "title": "Identities and credentials are managed", "domain": "PROTECT – Identity Management & Access Control", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["identity", "credentials", "MFA"], "severity": "high", "control_id": "NIST-PR.AA-01", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Identities and credentials for authorized users, services, and hardware are managed.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Is MFA enforced for all administrative accounts?"], "mapped_controls": ["ISO27001-A.8.3"], "maturity_weight": 0.9, "evidence_required": ["MFA enrollment report"]}	2026-06-05 05:31:51.956944+00
156f4b5f-0dd0-43d2-b6cc-66516f00ed46	{"id": "156f4b5f-0dd0-43d2-b6cc-66516f00ed46", "title": "Personnel are provided with cybersecurity awareness and training", "domain": "PROTECT – Awareness & Training", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["awareness", "training"], "severity": "medium", "control_id": "NIST-PR.AT-01", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Personnel are trained and have the awareness to perform their cybersecurity-related tasks.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Is training delivered to faculty AND non-teaching staff?"], "mapped_controls": ["ISO27001-A.6.3"], "maturity_weight": 0.75, "evidence_required": ["LMS completion"]}	2026-06-05 05:31:53.26481+00
8335c3b0-e617-4890-bc9a-dabdc181587b	{"id": "8335c3b0-e617-4890-bc9a-dabdc181587b", "title": "The confidentiality, integrity, and availability of data-at-rest is protected", "domain": "PROTECT – Data Security", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["encryption", "data at rest"], "severity": "critical", "control_id": "NIST-PR.DS-01", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Data-at-rest is protected through encryption and access controls.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Is the SIS database encrypted with managed keys?"], "mapped_controls": ["ISO27001-A.8.24"], "maturity_weight": 1.0, "evidence_required": ["DB encryption proof"]}	2026-06-05 05:31:54.572438+00
6d0dd51e-d720-4c51-b1a6-7ad79e4c76ee	{"id": "6d0dd51e-d720-4c51-b1a6-7ad79e4c76ee", "title": "Networks and network services are monitored", "domain": "DETECT – Continuous Monitoring", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["monitoring", "SIEM"], "severity": "high", "control_id": "NIST-DE.CM-01", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Networks and network services are monitored to find anomalies and potentially adverse events.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Is there a SIEM or log aggregator covering core systems?"], "mapped_controls": [], "maturity_weight": 0.8, "evidence_required": ["SIEM dashboard"]}	2026-06-05 05:31:55.880032+00
b70f2be9-d9b2-4ec4-953f-452a0fed0001	{"id": "b70f2be9-d9b2-4ec4-953f-452a0fed0001", "title": "The incident response process is executed", "domain": "RESPOND – Incident Management", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["incident", "response"], "severity": "critical", "control_id": "NIST-RS.MA-01", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "The incident response process is executed in coordination with relevant third parties once an incident is declared.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Is there a defined declaration trigger and runbook?"], "mapped_controls": ["ISO27001-A.5.24", "DPDP-S8-C6"], "maturity_weight": 0.95, "evidence_required": ["IR runbook"]}	2026-06-05 05:31:57.191466+00
81316638-f4a1-4c48-9771-1c8348107c0c	{"id": "81316638-f4a1-4c48-9771-1c8348107c0c", "title": "The recovery portion of the incident response plan is executed", "domain": "RECOVER – Incident Recovery Plan", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["recovery", "DR"], "severity": "high", "control_id": "NIST-RC.RP-01", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "The recovery portion of the incident response plan is executed once initiated from the incident response process.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Has DR for the SIS been tested?"], "mapped_controls": [], "maturity_weight": 0.85, "evidence_required": ["DR drill report"]}	2026-06-05 05:31:58.499633+00
314c568f-c84f-463c-b6fa-f7b44f51ce4d	{"id": "314c568f-c84f-463c-b6fa-f7b44f51ce4d", "title": "Issue retrospective notice for data processed before Act commencement", "domain": "Section 5: Notice Requirements for Pre-Existing Consent", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["retrospective notice", "legacy data", "pre-existing consent", "alumni data", "historical records", "consent withdrawal"], "severity": "high", "control_id": "DPDP-S5-C2", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "For personal data processed based on consent obtained before the DPDP Act's commencement, Data Fiduciaries must issue a retrospective notice as soon as reasonably practicable. This notice must inform Data Principals of the data processed, the purpose, their rights, and complaint mechanisms. Processing may continue unless consent is withdrawn. Universities must audit legacy data in alumni databases, historical student records, and long-term research datasets.", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Has the university identified all personal data collected and processed before the DPDP Act came into force (legacy student records, alumni data, historical HR records)?", "Have retrospective notices been issued to Data Principals whose data was collected pre-Act, informing them of processing and their rights?", "Is there a process to handle consent withdrawals for pre-Act data and cease processing accordingly?"], "mapped_controls": ["ISO27001-A.18.1.3", "ISO27701-7.3.3", "NIST-PR.IP-4"], "maturity_weight": 0.85, "evidence_required": ["Inventory of legacy personal data holdings (pre-Act student records, alumni database, historical employee records)", "Communication records showing retrospective notices sent to affected Data Principals", "Consent withdrawal tracking mechanism and records of data deletion or processing cessation upon withdrawal"]}	2026-06-05 06:08:06.983314+00
041917ff-24e9-44e2-ba1c-eeebfdbdb350	{"id": "041917ff-24e9-44e2-ba1c-eeebfdbdb350", "title": "Establish territorial and processing scope compliance framework", "domain": "Section 3: Application and Scope", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["territorial scope", "cross-border processing", "cloud services", "data localization", "publicly available data", "exemptions"], "severity": "medium", "control_id": "DPDP-S3-C1", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "Universities must understand and document the Act's application scope: it applies to digital personal data processed within India (collected digitally or digitized from non-digital form) and to processing outside India if related to offering goods or services to Indian Data Principals. Exclusions include personal/domestic use and publicly available data. Universities must map cross-border research collaborations, cloud services, and vendor processing locations.", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Has the university documented which personal data processing activities fall within the DPDP Act's territorial scope (domestic processing, cross-border transfers, cloud hosting)?", "Are third-party processors and cloud service providers assessed for compliance when processing university data outside India?", "Has the university identified and excluded from compliance scope any personal data processed for purely personal/domestic purposes or made publicly available by Data Principals?"], "mapped_controls": ["ISO27001-A.18.1.5", "ISO27701-7.2.8", "NIST-ID.AM-5"], "maturity_weight": 0.75, "evidence_required": ["Data processing inventory categorizing activities by location (India-based, offshore cloud, cross-border research collaborations)", "Vendor contracts and data processing agreements for offshore service providers (cloud hosting, SaaS platforms)", "Documentation of exclusions (publicly available research data, student-published content on university platforms)"]}	2026-06-05 06:08:08.311537+00
6b58ff43-1e7e-432c-98ff-c9d1c6c627cc	{"id": "6b58ff43-1e7e-432c-98ff-c9d1c6c627cc", "title": "Establish roles and responsibilities for Data Fiduciary, Processor, and Principal", "domain": "Section 2: Definitions and Key Concepts", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["data fiduciary", "data processor", "data principal", "minors consent", "disability rights", "roles and responsibilities"], "severity": "high", "control_id": "DPDP-S2-C1", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "Universities must clearly define and document their roles as Data Fiduciaries (determining purpose and means of processing), distinguish Data Processors (processing on behalf of the university), and recognize Data Principals (students, faculty, staff, alumni). Special provisions apply when Data Principals are children (under 18) or persons with disabilities, requiring parental or guardian consent. This foundational control underpins all subsequent compliance activities.", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Has the university formally documented its role as a Data Fiduciary for personal data processed in admissions, academics, HR, research, and alumni relations?", "Are Data Processors (third-party vendors, cloud service providers, outsourced services) identified and governed through appropriate contracts?", "Are special consent and notice procedures established for processing data of minors (under-18 students in integrated programs, K-12 university schools) and persons with disabilities?"], "mapped_controls": ["ISO27001-A.18.1.1", "ISO27701-7.2.2", "NIST-ID.AM-1"], "maturity_weight": 0.95, "evidence_required": ["RACI matrix or policy document defining Data Fiduciary responsibilities across university departments", "Data Processing Agreements with all identified Data Processors (vendors, service providers)", "Enhanced consent procedures and forms for minors and persons with disabilities, including parental/guardian consent mechanisms"]}	2026-06-05 06:08:09.639145+00
f895f10a-1217-43cd-bca8-ef7bff386749	{"id": "f895f10a-1217-43cd-bca8-ef7bff386749", "title": "Provide notice in multiple languages including English and constitutional languages", "domain": "Section 5: Notice Requirements", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["multilingual notice", "language accessibility", "eighth schedule", "regional languages", "notice translation", "linguistic diversity"], "severity": "medium", "control_id": "DPDP-S5-C3", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "Data Fiduciaries must give Data Principals the option to access notices in English or any language specified in the Eighth Schedule to the Constitution. This ensures accessibility and comprehension across diverse linguistic groups in Indian universities with students and staff from multiple states and backgrounds.", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Are notices and consent requests available in English and at least the primary regional languages relevant to the university's student and staff population?", "Is there a documented process for Data Principals to select their preferred language for receiving notices?", "Have notice templates been translated and verified for accuracy in all offered languages?"], "mapped_controls": ["ISO27001-A.7.2.1", "ISO27701-7.3.2", "NIST-PR.IP-2"], "maturity_weight": 0.7, "evidence_required": ["Multi-language notice templates for admissions, SIS, LMS, and HR systems", "Language selection mechanism in user interfaces (admissions portal, student/staff self-service)", "Translation verification records or certificates for non-English notice content"]}	2026-06-05 06:08:10.971907+00
ee6f21a0-e30a-4820-94b7-5eb4e136579f	{"id": "ee6f21a0-e30a-4820-94b7-5eb4e136579f", "title": "Enable easy withdrawal of consent comparable to ease of giving consent", "domain": "Section 6: Consent Requirements", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["consent withdrawal", "right to withdraw", "easy withdrawal", "processing cessation", "data processor instruction", "user rights"], "severity": "high", "control_id": "DPDP-S6-C2", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "Data Principals must have the right to withdraw consent at any time, with the withdrawal process being as easy as the consent process. Upon withdrawal, the Data Fiduciary must cease processing within a reasonable time and instruct Data Processors to cease processing, unless other legal grounds exist. Universities must implement withdrawal mechanisms in student portals, alumni systems, and marketing platforms. Processing already completed (e.g., fulfilled orders, issued degrees) remains legal.", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Are consent withdrawal mechanisms readily accessible in all university systems where consent was originally obtained (SIS, LMS, alumni portal, research platforms)?", "Is the consent withdrawal process equally or more simple than the consent-giving process (e.g., one-click withdrawal if consent was one-click)?", "Is there a documented procedure to cease processing and notify Data Processors within a reasonable timeframe after consent withdrawal?"], "mapped_controls": ["ISO27001-A.18.1.4", "ISO27701-7.3.4", "NIST-PR.IP-6"], "maturity_weight": 0.9, "evidence_required": ["User interface designs showing consent withdrawal options in student/staff portals", "Workflow documentation for processing cessation upon consent withdrawal", "Data Processor agreements requiring cessation of processing upon university instruction", "Logs or audit trails of consent withdrawals and corresponding processing cessation actions"]}	2026-06-05 06:08:12.963356+00
4feefa92-563f-46f7-bf60-1ceabcf2825c	{"id": "4feefa92-563f-46f7-bf60-1ceabcf2825c", "title": "Maintain burden of proof for consent and notice compliance", "domain": "Section 6: Consent Requirements", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["burden of proof", "consent records", "audit trail", "consent logging", "evidence retention", "compliance documentation"], "severity": "high", "control_id": "DPDP-S6-C3", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "Where consent is the basis for processing, the Data Fiduciary bears the burden of proving that proper notice was given and valid consent was obtained in accordance with the Act. Universities must maintain comprehensive consent records, notice delivery confirmations, and audit logs to demonstrate compliance during Board proceedings or legal challenges. This is critical for defending against student/employee complaints or regulatory investigations.", "framework_id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "framework_name": "DPDP Act 2023", "audit_questions": ["Are consent records comprehensively logged with timestamps, user identifiers, notice version, and consent scope for all data processing activities?", "Can the university produce evidence of notice delivery and consent receipt for any Data Principal upon request or during a Board proceeding?", "Are consent records retained for an appropriate period and protected from tampering or loss?"], "mapped_controls": ["ISO27001-A.18.1.1", "ISO27701-7.5.1", "NIST-PR.PT-2"], "maturity_weight": 0.85, "evidence_required": ["Consent management system with tamper-proof logs of consent transactions", "Notice delivery confirmations (email receipts, system logs, read receipts)", "Sample consent audit report demonstrating ability to prove consent for any Data Principal", "Data retention policy for consent records aligned with legal requirements"]}	2026-06-05 06:08:14.29116+00
195fcb04-a107-457e-8cd7-e26bec686171	{"id": "195fcb04-a107-457e-8cd7-e26bec686171", "title": "Understanding the organization and its context", "domain": "Clause 4 - Context of the Organization", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["organizational context", "external issues", "internal issues", "isms scope", "environment analysis"], "severity": "high", "control_id": "ISO27001-CL.4.1", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "The organization must determine external and internal issues that are relevant to its purpose and that affect its ability to achieve the intended outcomes of its information security management system. This includes understanding the institutional environment, regulatory landscape (UGC, AICTE, NAAC), and operational dependencies (ERP, SIS, LMS systems).", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Has the university documented internal and external issues affecting information security (e.g., regulatory requirements, technology dependencies)?", "Are context factors reviewed and updated periodically to reflect changes in the university environment?", "Does the context analysis explicitly consider critical systems like ERP, SIS, and LMS?"], "mapped_controls": ["ISO27701-CL.4.1", "NIST-CSF-ID.BE-1"], "maturity_weight": 0.95, "evidence_required": ["Context analysis document listing internal and external issues", "Minutes of management meetings discussing organizational context", "Risk register linking context factors to ISMS scope"]}	2026-06-05 06:08:20.26268+00
9ff06144-eb4a-4319-8207-ea2cea2b23ca	{"id": "9ff06144-eb4a-4319-8207-ea2cea2b23ca", "title": "Understanding the needs and expectations of interested parties", "domain": "Clause 4 - Context of the Organization", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["interested parties", "stakeholders", "requirements", "expectations", "compliance obligations"], "severity": "high", "control_id": "ISO27001-CL.4.2", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "The organization must determine interested parties relevant to the ISMS and their requirements related to information security. For universities, this includes students, faculty, regulatory bodies (UGC, AICTE), accreditation agencies (NAAC), research partners, and service providers.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Has the university identified all relevant interested parties (students, faculty, regulators, vendors)?", "Are the information security requirements of each interested party documented?", "Is there a process to review and update interested party requirements periodically?"], "mapped_controls": ["DPDP-CL.4", "ISO27701-CL.4.2", "NIST-CSF-ID.BE-2"], "maturity_weight": 0.9, "evidence_required": ["Interested parties register with security requirements", "Stakeholder consultation records or surveys", "Compliance mapping to regulatory requirements (UGC, AICTE, DPDP)"]}	2026-06-05 06:08:21.590284+00
4073ae85-f6c3-4627-bbdc-dc2648cb86c9	{"id": "4073ae85-f6c3-4627-bbdc-dc2648cb86c9", "title": "Determining the scope of the information security management system", "domain": "Clause 4 - Context of the Organization", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["isms scope", "boundaries", "applicability", "scope definition", "exclusions"], "severity": "critical", "control_id": "ISO27001-CL.4.3", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "The organization must define the boundaries and applicability of the ISMS considering external and internal issues, interested party requirements, and organizational interfaces. The scope must be documented and explicitly state what is included and excluded, covering systems like ERP, SIS, LMS, research infrastructure, and administrative systems.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Is the ISMS scope formally documented and approved by top management?", "Does the scope explicitly list in-scope systems (ERP, SIS, LMS) and excluded areas?", "Has the scope been communicated to all relevant stakeholders and interested parties?"], "mapped_controls": ["ISO27701-CL.4.3", "NIST-CSF-ID.AM-4"], "maturity_weight": 1.0, "evidence_required": ["ISMS scope document with boundaries and exclusions", "Management approval of scope statement", "Asset inventory mapping to ISMS scope"]}	2026-06-05 06:08:22.917704+00
b57c4d30-3aa4-4d83-b04c-624ab8d73ba5	{"id": "b57c4d30-3aa4-4d83-b04c-624ab8d73ba5", "title": "Leadership and commitment for ISMS", "domain": "Clause 5 - Leadership", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["top management", "leadership commitment", "resource allocation", "management responsibility", "accountability"], "severity": "critical", "control_id": "ISO27001-CL.5.1", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "Top management must demonstrate leadership and commitment to the ISMS by ensuring its integration with business processes, allocating necessary resources, communicating the importance of information security, and ensuring achievement of intended outcomes. In universities, this requires active engagement from Vice-Chancellors, Registrars, and Deans.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Does top management (VC, Registrar) actively participate in ISMS governance and review meetings?", "Are adequate resources (budget, personnel, technology) allocated to information security?", "Is there documented evidence of top management communicating information security importance to the organization?"], "mapped_controls": ["ISO27701-CL.5.1", "NIST-CSF-ID.GV-1"], "maturity_weight": 1.0, "evidence_required": ["Management review meeting minutes with top management attendance", "ISMS budget allocation and resource assignment documents", "Communication records from leadership on information security initiatives"]}	2026-06-05 06:08:24.245763+00
ae6d1d1b-755b-45ce-8c8d-cf265730c274	{"id": "ae6d1d1b-755b-45ce-8c8d-cf265730c274", "title": "Information security policy establishment", "domain": "Clause 5 - Leadership", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["information security policy", "policy approval", "security objectives", "continual improvement", "policy communication"], "severity": "critical", "control_id": "ISO27001-CL.5.2", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "Top management must establish an information security policy that is appropriate to the organization's purpose, includes objectives or framework for setting objectives, and includes commitments to satisfy applicable requirements and continual improvement. The policy must be documented, communicated, and available to interested parties.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Is there a formally documented and approved information security policy?", "Does the policy include commitments to compliance with legal requirements (DPDP Act, IT Act) and continual improvement?", "Has the policy been communicated to all staff, faculty, and students and made available to external parties?"], "mapped_controls": ["DPDP-CL.8", "ISO27701-CL.5.2", "NIST-CSF-ID.GV-2"], "maturity_weight": 1.0, "evidence_required": ["Signed information security policy document", "Policy approval records by top management", "Evidence of policy communication (emails, training records, website publication)"]}	2026-06-05 06:08:25.573962+00
74f07626-208e-424d-bc81-d21b3877a1f6	{"id": "74f07626-208e-424d-bc81-d21b3877a1f6", "title": "Organizational roles, responsibilities and authorities for information security", "domain": "Clause 5 - Leadership", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["roles and responsibilities", "authorities", "accountability", "organizational structure", "role assignment"], "severity": "high", "control_id": "ISO27001-CL.5.3", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "Top management must ensure that responsibilities and authorities for roles relevant to information security are assigned and communicated within the organization. This includes defining roles for information security management, incident response, data protection, and system ownership across departments (IT, Administration, Academics, Research).", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Are information security roles and responsibilities formally documented and assigned?", "Have role assignments been communicated to all relevant personnel across departments?", "Is there a RACI or similar matrix showing accountability for information security activities?"], "mapped_controls": ["ISO27701-CL.5.3", "NIST-CSF-ID.GV-2", "ISO27001-A.5.1"], "maturity_weight": 0.95, "evidence_required": ["Organizational chart with information security roles", "Role and responsibility matrix (RACI) for ISMS activities", "Job descriptions including information security responsibilities"]}	2026-06-05 06:08:26.901886+00
0f8f9154-b8b3-42ab-b432-d4d1511af34b	{"id": "0f8f9154-b8b3-42ab-b432-d4d1511af34b", "title": "General planning for actions to address risks and opportunities", "domain": "Clause 6 - Planning", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["risk management", "opportunities", "risk treatment", "isms planning", "risk assessment"], "severity": "critical", "control_id": "ISO27001-CL.6.1.1", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "When planning for the ISMS, the organization must determine risks and opportunities that need to be addressed to ensure the ISMS achieves intended outcomes, prevents or reduces undesired effects, and achieves continual improvement. The organization must plan actions to address these risks and opportunities and integrate them into ISMS processes.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Has the university identified risks and opportunities relevant to ISMS objectives?", "Are planned actions to address risks and opportunities documented and assigned?", "Is there a process to evaluate the effectiveness of actions taken to address risks?"], "mapped_controls": ["ISO27701-CL.6.1", "NIST-CSF-ID.RM-1", "DPDP-CL.8"], "maturity_weight": 1.0, "evidence_required": ["Risk and opportunity register", "Risk treatment plan with assigned actions", "Risk assessment methodology document"]}	2026-06-05 06:08:28.229503+00
ac21e598-ad54-4270-a0f3-586c358bf3ea	{"id": "ac21e598-ad54-4270-a0f3-586c358bf3ea", "title": "Information security risk assessment process", "domain": "Clause 6 - Planning", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["risk assessment", "risk criteria", "threat analysis", "vulnerability assessment", "risk identification"], "severity": "critical", "control_id": "ISO27001-CL.6.1.2", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "The organization must define and apply an information security risk assessment process that establishes and maintains risk criteria (including risk acceptance criteria and criteria for performing assessments), ensures assessments produce consistent and comparable results, and identifies information security risks through asset identification, threat and vulnerability analysis, and consequence evaluation.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Is there a documented information security risk assessment methodology?", "Does the methodology define risk acceptance criteria approved by management?", "Are risk assessments conducted systematically for all in-scope systems (ERP, SIS, LMS, research platforms)?"], "mapped_controls": ["NIST-CSF-ID.RM-1", "ISO27701-CL.6.1", "DPDP-CL.8"], "maturity_weight": 1.0, "evidence_required": ["Information security risk assessment methodology document", "Risk acceptance criteria approved by top management", "Completed risk assessment reports for critical systems"]}	2026-06-05 06:08:29.55705+00
a9ff4cb0-aee8-4fda-8f44-783852fa8d31	{"id": "a9ff4cb0-aee8-4fda-8f44-783852fa8d31", "title": "Information security risk treatment process", "domain": "Clause 6 - Planning", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["risk treatment", "statement of applicability", "risk mitigation", "control selection", "risk acceptance"], "severity": "critical", "control_id": "ISO27001-CL.6.1.3", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "The organization must define and apply an information security risk treatment process to select appropriate risk treatment options (mitigate, avoid, accept, transfer), determine necessary controls to implement chosen options, compare against Annex A controls, produce a Statement of Applicability (SoA), and formulate a risk treatment plan with resource allocation and responsibilities.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Is there a risk treatment plan documenting chosen treatment options for identified risks?", "Has a Statement of Applicability been prepared comparing required controls against Annex A?", "Are risk treatment decisions approved by management with clear justifications for risk acceptance?"], "mapped_controls": ["NIST-CSF-ID.RM-2", "ISO27701-CL.6.1", "DPDP-CL.8"], "maturity_weight": 1.0, "evidence_required": ["Risk treatment plan with assigned controls and owners", "Statement of Applicability (SoA) document", "Management approval records for risk acceptance decisions"]}	2026-06-05 06:08:30.885332+00
c69d03a1-2163-47f9-8f23-63b10230e257	{"id": "c69d03a1-2163-47f9-8f23-63b10230e257", "title": "Information security objectives and planning to achieve them", "domain": "Clause 6 - Planning", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["security objectives", "measurable goals", "objective planning", "performance targets", "continual improvement"], "severity": "high", "control_id": "ISO27001-CL.6.2", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "The organization must establish information security objectives at relevant functions and levels that are consistent with the information security policy, measurable, consider applicable requirements, relate to conformity assessment and continual improvement, are monitored and communicated, and updated as appropriate. Planning must determine what, who, when, and how objectives will be achieved and evaluated.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Are information security objectives documented and aligned with the information security policy?", "Are objectives measurable with defined metrics and target dates?", "Is there documented evidence of objective achievement monitoring and review?"], "mapped_controls": ["ISO27701-CL.6.2", "NIST-CSF-ID.GV-3"], "maturity_weight": 0.85, "evidence_required": ["Information security objectives document with measurable targets", "Action plans showing who, what, when, and how for each objective", "Progress reports and monitoring records for objectives"]}	2026-06-05 06:08:32.212617+00
9f140e1d-bd88-44d0-9897-ec613d2fe620	{"id": "9f140e1d-bd88-44d0-9897-ec613d2fe620", "title": "Planning of changes to the ISMS", "domain": "Clause 6 - Planning", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["change management", "planned changes", "isms changes", "change control", "impact assessment"], "severity": "high", "control_id": "ISO27001-CL.6.3", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "When the organization determines the need for changes to the information security management system, the changes must be carried out in a planned manner. This includes changes to systems (ERP, SIS, LMS upgrades), processes, infrastructure, or organizational structure that may impact information security.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Is there a documented change management process for ISMS-related changes?", "Are significant changes to information systems and processes planned and assessed for security impact?", "Is there evidence of planned implementation for recent ISMS changes (e.g., system upgrades, policy updates)?"], "mapped_controls": ["ISO27001-A.8.32", "ISO27701-CL.6.3", "NIST-CSF-PR.IP-3"], "maturity_weight": 0.85, "evidence_required": ["Change management procedure document", "Change request logs with security impact assessments", "Change implementation plans and approval records"]}	2026-06-05 06:08:33.540104+00
880c3469-ebc2-48f2-996e-698560771baa	{"id": "880c3469-ebc2-48f2-996e-698560771baa", "title": "Resources for ISMS", "domain": "Clause 7 - Support", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["resource allocation", "budget", "staffing", "security tools", "infrastructure"], "severity": "high", "control_id": "ISO27001-CL.7.1", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "The organization must determine and provide the resources needed for the establishment, implementation, maintenance and continual improvement of the information security management system. This includes human resources, technology infrastructure, budget allocation, and tools necessary for security operations in university environments.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Has the university allocated adequate budget for information security activities?", "Are sufficient personnel assigned to information security roles (CISO, security analysts, DPO)?", "Are necessary security tools and technologies available (SIEM, firewalls, encryption, backup systems)?"], "mapped_controls": ["ISO27701-CL.7.1", "NIST-CSF-ID.GV-1"], "maturity_weight": 0.9, "evidence_required": ["ISMS budget allocation document", "Staffing plan showing security personnel assignments", "Inventory of security tools and infrastructure"]}	2026-06-05 06:08:34.86926+00
2f20ab30-35a6-41a2-80f1-4f893b607fa3	{"id": "2f20ab30-35a6-41a2-80f1-4f893b607fa3", "title": "Competence of personnel affecting information security", "domain": "Clause 7 - Support", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["competence", "training", "skills", "qualifications", "personnel development"], "severity": "high", "control_id": "ISO27001-CL.7.2", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "The organization must determine necessary competence of persons doing work that affects information security performance, ensure competence based on education, training or experience, take actions to acquire necessary competence, evaluate effectiveness of actions, and retain evidence of competence. This applies to IT staff, faculty handling research data, administrators managing student information, and outsourced service providers.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Are competency requirements defined for roles affecting information security (IT staff, data handlers, administrators)?", "Is there documented evidence of security training completion for relevant personnel?", "Are competency evaluations conducted and effectiveness of training measured?"], "mapped_controls": ["ISO27001-A.6.3", "ISO27701-CL.7.2", "NIST-CSF-PR.AT-1"], "maturity_weight": 0.9, "evidence_required": ["Competency matrix defining requirements for security-relevant roles", "Training records and certificates for security personnel", "Competency assessment reports and skill gap analyses"]}	2026-06-05 06:08:36.196693+00
7a98b55e-6fcf-4df1-b3b1-f920e4a4a532	{"id": "7a98b55e-6fcf-4df1-b3b1-f920e4a4a532", "title": "Awareness of information security", "domain": "Clause 7 - Support", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["awareness", "security training", "user education", "policy communication", "security culture"], "severity": "medium", "control_id": "ISO27001-CL.7.3", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "Persons doing work under the organization's control must be aware of the information security policy, their contribution to ISMS effectiveness including benefits of improved performance, and implications of non-conformance. This includes awareness programs for students, faculty, staff, and contractors accessing university systems and handling sensitive data.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Is there an information security awareness program covering all personnel categories (students, faculty, staff, contractors)?", "Are personnel aware of the information security policy and their responsibilities?", "Is awareness training documented and completion tracked across the institution?"], "mapped_controls": ["ISO27001-A.6.3", "ISO27701-CL.7.3", "NIST-CSF-PR.AT-1"], "maturity_weight": 0.8, "evidence_required": ["Information security awareness program materials", "Training completion records by department and role", "Awareness campaign communications (emails, posters, workshops)"]}	2026-06-05 06:08:37.524935+00
6abdadf8-cf43-4ecf-8efa-0a6501dcaa89	{"id": "6abdadf8-cf43-4ecf-8efa-0a6501dcaa89", "title": "Communication regarding information security", "domain": "Clause 7 - Support", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["communication", "stakeholder engagement", "incident notification", "reporting", "information sharing"], "severity": "medium", "control_id": "ISO27001-CL.7.4", "created_at": "2026-06-05T06:08:00.231532+00:00", "updated_at": "2026-06-05T06:08:00.231532+00:00", "description": "The organization must determine the need for internal and external communications relevant to the ISMS including: what to communicate, when to communicate, with whom to communicate, and how to communicate. This covers incident notifications, policy updates, compliance communications to regulators (UGC, AICTE), and stakeholder engagement.", "framework_id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "framework_name": "ISO 27001:2022", "audit_questions": ["Is there a communication plan defining internal and external ISMS communications?", "Are communication channels established for security incidents, policy updates, and compliance matters?", "Is there evidence of regular ISMS communications to stakeholders (management, staff, regulators)?"], "mapped_controls": ["ISO27701-CL.7.4", "NIST-CSF-RS.CO-2", "DPDP-CL.6"], "maturity_weight": 0.75, "evidence_required": ["ISMS communication plan or procedure", "Records of security communications (incident notifications, policy updates)", "Communication logs showing internal and external ISMS reporting"]}	2026-06-05 06:08:38.852655+00
ac5c6d0b-4cb2-47bc-9b72-37c8d3c83d28	{"id": "ac5c6d0b-4cb2-47bc-9b72-37c8d3c83d28", "title": "Develop Current and Target State Organizational Profiles", "domain": "GOVERN – Organizational Context", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["organizational profile", "current state", "target state", "gap analysis", "maturity assessment", "cybersecurity posture"], "severity": "high", "control_id": "NIST-GV.OC-02", "created_at": "2026-06-05T06:10:14.941956+00:00", "updated_at": "2026-06-05T06:10:14.941956+00:00", "description": "The organization must create CSF Organizational Profiles that describe both current cybersecurity posture and target cybersecurity outcomes. These profiles enable the organization to compare where they are versus where they want or need to be, facilitating gap analysis and prioritization of security controls. Profiles should be updated regularly to reflect changing risks and organizational objectives.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Has the organization documented a current state Organizational Profile based on CSF Core outcomes?", "Has the organization defined a target state Organizational Profile aligned with risk appetite and business objectives?", "Does the organization conduct regular gap analysis between current and target profiles?"], "mapped_controls": ["ISO27001-4.1", "ISO27001-6.1.2", "NIST-800-53-CA-2"], "maturity_weight": 0.9, "evidence_required": ["Current state CSF Organizational Profile document", "Target state CSF Organizational Profile document", "Gap analysis report with prioritized remediation plan"]}	2026-06-05 06:10:47.180088+00
9d773621-c650-436e-bd27-1d53188e3793	{"id": "9d773621-c650-436e-bd27-1d53188e3793", "title": "Apply CSF Tiers to Characterize Risk Governance Rigor", "domain": "GOVERN – Organizational Context", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["tiers", "maturity level", "risk governance", "process rigor", "continuous improvement", "sophistication"], "severity": "medium", "control_id": "NIST-GV.OC-03", "created_at": "2026-06-05T06:10:14.941956+00:00", "updated_at": "2026-06-05T06:10:14.941956+00:00", "description": "The organization must assess and document its cybersecurity risk governance and management practices using CSF Tiers (Tier 1-4). Tiers characterize the rigor and sophistication of an organization's processes for managing cybersecurity risks and provide context for how the organization views cybersecurity risks. This assessment informs strategic decisions about improving governance maturity.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Has the organization assessed its current CSF Tier level for cybersecurity risk governance?", "Are CSF Tier characteristics documented and understood by leadership?", "Does the organization have a plan to progress to a higher Tier if needed based on risk profile?"], "mapped_controls": ["ISO27001-9.1", "ISO27001-10.1", "NIST-800-53-CA-7"], "maturity_weight": 0.75, "evidence_required": ["CSF Tier self-assessment report", "Leadership presentation on Tier level and implications", "Tier progression roadmap or justification for current Tier"]}	2026-06-05 06:10:48.490399+00
be20ca2a-df0c-4658-8b47-794a119380ef	{"id": "be20ca2a-df0c-4658-8b47-794a119380ef", "title": "Integrate Cybersecurity into Supply Chain Risk Management", "domain": "GOVERN – Supply Chain Risk Management", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["supply chain", "third party risk", "vendor management", "procurement", "outsourcing", "dependencies"], "severity": "high", "control_id": "NIST-GV.SC-01", "created_at": "2026-06-05T06:10:14.941956+00:00", "updated_at": "2026-06-05T06:10:14.941956+00:00", "description": "The organization must incorporate cybersecurity considerations into supply chain risk management processes. This includes assessing cybersecurity risks from vendors, service providers, and third-party dependencies. Special attention must be paid to supply chain security as highlighted in CSF 2.0, ensuring that third-party risks are identified, assessed, and mitigated as part of enterprise risk management.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Does the organization assess cybersecurity risks for all critical vendors and service providers?", "Are supply chain cybersecurity requirements included in procurement and vendor management processes?", "Does the organization monitor and review third-party cybersecurity posture on an ongoing basis?"], "mapped_controls": ["ISO27001-A.15.1.1", "ISO27001-A.15.2.1", "DPDP-SEC-03", "NIST-800-53-SR-2"], "maturity_weight": 0.9, "evidence_required": ["Supply chain risk assessment policy including cybersecurity criteria", "Vendor security assessment reports for critical suppliers (e.g., ERP, LMS, SIS vendors)", "Third-party contract clauses requiring cybersecurity compliance"]}	2026-06-05 06:10:50.240166+00
7821283a-a6e3-4845-9927-d41b9b1438ac	{"id": "7821283a-a6e3-4845-9927-d41b9b1438ac", "title": "Establish and Communicate Cybersecurity Risk Management Strategy", "domain": "GOVERN – Risk Management Strategy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["risk strategy", "governance", "enterprise risk management", "stakeholder expectations", "policy communication", "mission alignment"], "severity": "critical", "control_id": "NIST-GV.RM-02", "created_at": "2026-06-05T06:10:14.941956+00:00", "updated_at": "2026-06-05T06:10:14.941956+00:00", "description": "The organization must establish, communicate, and monitor a cybersecurity risk management strategy and policy that informs and prioritizes outcomes across all CSF Functions. This strategy must be incorporated into the broader enterprise risk management (ERM) approach and align with organizational mission, legal requirements, and stakeholder expectations. The governance strategy provides context for implementing IDENTIFY, PROTECT, DETECT, RESPOND, and RECOVER Functions.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Has the organization documented a cybersecurity risk management strategy that is integrated with enterprise risk management?", "Is the cybersecurity strategy communicated to all relevant stakeholders and monitored for effectiveness?", "Does the strategy inform prioritization decisions across all cybersecurity functions?"], "mapped_controls": ["ISO27001-5.2", "ISO27001-6.2", "DPDP-GRC-02", "NIST-800-53-PM-1"], "maturity_weight": 1.0, "evidence_required": ["Cybersecurity risk management strategy document", "Evidence of strategy communication (circulars, training records)", "Strategy monitoring and review reports showing alignment with ERM"]}	2026-06-05 06:10:52.205435+00
2d4537c1-a7b0-4ded-aa34-feeda346b1b6	{"id": "2d4537c1-a7b0-4ded-aa34-feeda346b1b6", "title": "Establish Cybersecurity Roles, Responsibilities, and Authorities", "domain": "GOVERN – Oversight", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["roles and responsibilities", "accountability", "authority", "oversight", "governance structure", "ciso"], "severity": "high", "control_id": "NIST-GV.OV-01", "created_at": "2026-06-05T06:10:14.941956+00:00", "updated_at": "2026-06-05T06:10:14.941956+00:00", "description": "The organization must establish and document clear roles, responsibilities, and authorities for cybersecurity risk management. This includes defining who is responsible for operationalizing risk management within the organization, assigning accountability for achieving cybersecurity outcomes, and ensuring oversight of the cybersecurity strategy. For Indian universities, this may include defining roles for IT heads, Chief Information Security Officers, data protection officers, and relevant academic/administrative leadership.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Are cybersecurity roles, responsibilities, and authorities formally documented and assigned?", "Do individuals responsible for cybersecurity outcomes have clear accountability and appropriate authority?", "Is there documented oversight of cybersecurity strategy by senior leadership or governance body?"], "mapped_controls": ["ISO27001-5.3", "ISO27001-A.7.1.2", "DPDP-DPO-02", "NIST-800-53-PM-2"], "maturity_weight": 0.95, "evidence_required": ["RACI matrix or roles and responsibilities document for cybersecurity", "Job descriptions including cybersecurity accountabilities", "Governance body charter showing cybersecurity oversight responsibilities"]}	2026-06-05 06:10:53.517162+00
c8add948-e1bc-4836-bd23-1d5ea6e9c27d	{"id": "c8add948-e1bc-4836-bd23-1d5ea6e9c27d", "title": "Establish Cybersecurity Supply Chain Risk Management Strategy", "domain": "GOVERN – Cybersecurity Supply Chain Risk Management", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["supply chain", "third party", "vendor risk", "supplier management", "outsourcing security", "service providers"], "severity": "high", "control_id": "NIST-GV.SC-02", "created_at": "2026-06-05T06:10:14.941956+00:00", "updated_at": "2026-06-05T06:10:14.941956+00:00", "description": "The organization must establish a cybersecurity supply chain risk management strategy that addresses suppliers, service providers, and third-party dependencies. This strategy must identify, assess, and manage cybersecurity risks from the supply chain including vendors providing critical services such as ERP systems, Student Information Systems (SIS), Learning Management Systems (LMS), cloud services, and other ICT infrastructure. CSF 2.0 emphasizes special attention to supply chain security as a critical governance outcome.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Does the organization have a documented cybersecurity supply chain risk management strategy?", "Are third-party suppliers and service providers assessed for cybersecurity risks before engagement?", "Is there ongoing monitoring of supplier cybersecurity posture throughout the relationship?"], "mapped_controls": ["ISO27001-A.15.1.1", "ISO27001-A.15.1.2", "DPDP-SEC-04", "NIST-800-53-SR-1"], "maturity_weight": 0.9, "evidence_required": ["Cybersecurity supply chain risk management policy", "Vendor cybersecurity assessment questionnaires and results for critical suppliers", "Supply chain risk register identifying key third-party risks"]}	2026-06-05 06:10:54.82628+00
12f7c7f3-99e7-4017-a27e-1a0450bdd122	{"id": "12f7c7f3-99e7-4017-a27e-1a0450bdd122", "title": "Identify and Document Improvement Opportunities for Cybersecurity Policies and Practices", "domain": "IDENTIFY – Improvement", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["continuous improvement", "gap analysis", "maturity enhancement", "lessons learned", "assessment", "optimization"], "severity": "medium", "control_id": "NIST-ID.IM-01", "created_at": "2026-06-05T06:10:14.941956+00:00", "updated_at": "2026-06-05T06:10:14.941956+00:00", "description": "The organization must systematically identify improvement opportunities for cybersecurity policies, plans, processes, procedures, and practices that support risk management across all six CSF Functions. This includes conducting regular assessments of current state versus desired outcomes, analyzing gaps, and prioritizing improvements consistent with risk management strategy and mission needs. Identified improvements should be tracked and implemented to enhance cybersecurity maturity over time.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Does the organization conduct regular assessments to identify cybersecurity improvement opportunities?", "Are improvement opportunities documented, prioritized, and tracked to closure?", "Is there evidence of implemented improvements enhancing cybersecurity posture over time?"], "mapped_controls": ["ISO27001-9.3", "ISO27001-10.2", "NIST-800-53-CA-7", "NIST-800-53-PM-6"], "maturity_weight": 0.7, "evidence_required": ["Cybersecurity assessment reports identifying gaps and improvement opportunities", "Improvement tracking register or project management system", "Before-and-after metrics demonstrating implemented improvements"]}	2026-06-05 06:10:56.136932+00
da6baca6-4492-4b79-a8bb-70a193fbde9a	{"id": "da6baca6-4492-4b79-a8bb-70a193fbde9a", "title": "Develop Target Profile Aligned with Risk Management Objectives", "domain": "GOVERN – Organizational Profiles", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["target profile", "desired outcomes", "gap analysis", "action plan", "risk objectives", "maturity roadmap"], "severity": "high", "control_id": "NIST-GV.PO-02", "created_at": "2026-06-05T06:10:14.941956+00:00", "updated_at": "2026-06-05T06:10:14.941956+00:00", "description": "The organization must develop a Target Profile specifying desired cybersecurity outcomes selected and prioritized for achieving risk management objectives. The Target Profile must consider anticipated changes such as new requirements (e.g., DPDP Act compliance for Indian universities), new technology adoption (cloud, AI systems), threat intelligence trends, mission objectives, stakeholder expectations, and the threat landscape. Organizations may use Community Profiles as a basis for their Target Profile and should conduct gap analysis to create prioritized action plans.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Has the organization developed a Target Profile defining desired cybersecurity outcomes?", "Does the Target Profile consider anticipated changes, new requirements, and threat trends?", "Is there a documented gap analysis between Current and Target Profiles with a prioritized action plan?"], "mapped_controls": ["ISO27001-6.1.2", "ISO27001-6.2", "NIST-800-53-CA-2", "NIST-800-53-PM-6"], "maturity_weight": 0.9, "evidence_required": ["Target Profile document showing desired CSF outcomes and priorities", "Gap analysis report comparing Current vs. Target Profiles", "Prioritized action plan or POA&M addressing identified gaps"]}	2026-06-05 06:10:58.75663+00
642ad39f-4853-466b-91ae-bd58e5e1594a	{"id": "642ad39f-4853-466b-91ae-bd58e5e1594a", "title": "Implement Continuous Improvement through Profile Updates", "domain": "GOVERN – Organizational Profiles", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["continuous improvement", "profile updates", "action plan implementation", "progress monitoring", "maturity progression", "iterative process"], "severity": "medium", "control_id": "NIST-GV.PO-03", "created_at": "2026-06-05T06:10:14.941956+00:00", "updated_at": "2026-06-05T06:10:14.941956+00:00", "description": "The organization must implement a continuous improvement process for cybersecurity by regularly updating Organizational Profiles. This includes implementing action plans to address gaps, monitoring progress toward Target Profile achievement, and repeating the profile creation cycle (scope, gather information, create profile, analyze gaps, implement actions, update) as needed. The process should account for changes in mission objectives, requirements, technology environments (cloud, mobile, AI, IoT, OT), and threat landscape.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Does the organization have a process for regularly updating and maintaining Organizational Profiles?", "Is there evidence of action plan implementation moving the organization toward the Target Profile?", "Are Profiles updated to reflect changes in technology, threats, and organizational requirements?"], "mapped_controls": ["ISO27001-9.1", "ISO27001-10.1", "NIST-800-53-CA-7"], "maturity_weight": 0.75, "evidence_required": ["Profile update logs showing regular review and revision cycles", "Action plan implementation tracking with completed milestones", "Updated Profiles reflecting changes in technology environment or threat landscape"]}	2026-06-05 06:11:00.067622+00
def1a92f-0865-4e4c-8ca6-1a574989d442	{"id": "def1a92f-0865-4e4c-8ca6-1a574989d442", "title": "Select and Apply CSF Tier to Characterize Risk Management Rigor", "domain": "GOVERN – CSF Tiers", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["tiers", "maturity levels", "risk informed", "repeatable", "adaptive", "governance rigor"], "severity": "medium", "control_id": "NIST-GV.TI-01", "created_at": "2026-06-05T06:10:14.941956+00:00", "updated_at": "2026-06-05T06:10:14.941956+00:00", "description": "The organization must select and apply an appropriate CSF Tier (Partial/Tier 1, Risk Informed/Tier 2, Repeatable/Tier 3, or Adaptive/Tier 4) to characterize the rigor of its cybersecurity risk governance and management practices. The Tier selection should complement the organization's risk management methodology, reflect how the organization views cybersecurity risks and processes to manage them, and inform Current and Target Profiles. Progression to higher Tiers should be considered when risks or mandates increase or when cost-benefit analysis indicates feasible risk reduction.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Has the organization assessed and documented its current CSF Tier level?", "Does the selected Tier appropriately characterize the organization's risk management practices?", "Is there justification for the current Tier or a plan for progression based on risk analysis?"], "mapped_controls": ["ISO27001-4.1", "ISO27001-9.1", "NIST-800-53-PM-9"], "maturity_weight": 0.7, "evidence_required": ["CSF Tier assessment documenting current level with supporting rationale", "Risk analysis or cost-benefit analysis justifying Tier selection or progression plan", "Evidence showing Tier characteristics reflected in governance and management practices"]}	2026-06-05 06:11:01.377355+00
c6839e65-b167-465e-b721-2a8fd5d8fd36	{"id": "c6839e65-b167-465e-b721-2a8fd5d8fd36", "title": "Use Profiles for Stakeholder Communication and Third-Party Requirements", "domain": "GOVERN – Organizational Profiles", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "keywords": ["stakeholder communication", "third party requirements", "vendor expectations", "supply chain", "transparency", "contract requirements"], "severity": "medium", "control_id": "NIST-GV.PO-04", "created_at": "2026-06-05T06:10:14.941956+00:00", "updated_at": "2026-06-05T06:10:14.941956+00:00", "description": "The organization must use Organizational Profiles to communicate cybersecurity posture with internal and external stakeholders. Current Profiles should document and communicate cybersecurity capabilities and improvement opportunities to business partners, customers, and other external parties. Target Profiles should express cybersecurity risk management requirements and expectations to suppliers, service providers (e.g., cloud, ERP, SIS, LMS vendors), and other third parties as targets for those parties to achieve, supporting supply chain risk management.", "framework_id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "framework_name": "NIST CSF 2.0", "audit_questions": ["Does the organization use Current Profiles to communicate cybersecurity capabilities to stakeholders?", "Are Target Profiles shared with third parties to establish cybersecurity expectations?", "Is there evidence of using Profiles in vendor assessments or partnership agreements?"], "mapped_controls": ["ISO27001-A.15.1.2", "ISO27001-A.15.2.1", "DPDP-SEC-05", "NIST-800-53-SR-2"], "maturity_weight": 0.75, "evidence_required": ["Stakeholder communication materials including Current Profile information", "Vendor contracts or SLAs incorporating Target Profile requirements", "Third-party assessment reports comparing vendor performance against Target Profile"]}	2026-06-05 06:11:02.686976+00
\.


--
-- Data for Name: departments; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.departments (id, data, created_at) FROM stdin;
d287d76f-b86c-47f4-8cd2-02a8ef1c7349	{"id": "d287d76f-b86c-47f4-8cd2-02a8ef1c7349", "name": "Registrar", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "created_at": "2026-06-05T06:22:33.049378+00:00", "updated_at": "2026-06-05T06:22:33.049378+00:00", "head_user_id": "70165d8e-092f-4b20-b446-4348d31589e8", "head_user_email": "registrar@rut.edu.in"}	2026-06-05 06:22:49.57919+00
aa85f938-4782-44c6-93dc-b307081d774b	{"id": "aa85f938-4782-44c6-93dc-b307081d774b", "name": "Library", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "created_at": "2026-06-05T06:22:33.049378+00:00", "updated_at": "2026-06-05T06:22:33.049378+00:00", "head_user_id": "c8f13c16-2605-4395-9f8c-181ab04d48ce", "head_user_email": "library@rut.edu.in"}	2026-06-05 06:22:51.545505+00
3ee766ca-d414-4b9b-8713-73b70cc4ae49	{"id": "3ee766ca-d414-4b9b-8713-73b70cc4ae49", "name": "OrgBDept", "org_id": "7bab9ff2-c2fd-4dc2-b0c2-6ec6bd8bf129", "created_at": "2026-06-07T13:42:47.143124+00:00", "updated_at": "2026-06-07T13:42:47.143124+00:00", "description": "Org B exclusive department", "head_user_id": "b2284cc6-c822-4a71-8ac5-23bb1793258d", "head_user_email": "reviewer@iit-testopolis.edu.in"}	2026-06-07 13:42:52.356234+00
3cb7a234-8acd-4308-9e00-1ba4545e09ee	{"id": "3cb7a234-8acd-4308-9e00-1ba4545e09ee", "name": "IT", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "created_at": "2026-06-09T04:41:43.384096+00:00", "updated_at": "2026-06-09T04:41:43.384096+00:00", "head_user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "head_user_email": "itsec@rut.edu.in"}	2026-06-09 04:41:51.846267+00
\.


--
-- Data for Name: document_analyses; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.document_analyses (id, data, created_at) FROM stdin;
\.


--
-- Data for Name: evidence; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.evidence (id, data, created_at) FROM stdin;
fd762850-cfc8-4542-a55c-e1a93c79e717	{"id": "fd762850-cfc8-4542-a55c-e1a93c79e717", "tags": [], "title": "TEST evidence", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "filename": "TEST_evidence.txt", "file_size": 20, "file_type": "text/plain", "control_id": null, "created_at": "2026-06-05T05:47:44.382748+00:00", "updated_at": "2026-06-05T05:47:44.382748+00:00", "description": "test", "hash_sha256": "019b2f52bca72502e01475c0c13d352b3dbf8139a4b9f378b37443ee218d7e5b", "is_verified": false, "uploaded_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "valid_until": null, "storage_path": "/app/backend/uploads/ecd3f0cc-533d-4b8a-b24d-f15041f3b26e/fd762850-cfc8-4542-a55c-e1a93c79e717_TEST_evidence.txt"}	2026-06-05 05:47:44.496061+00
04d9a24d-e447-4dbd-81ee-4f5106abf245	{"id": "04d9a24d-e447-4dbd-81ee-4f5106abf245", "tags": [], "title": "TEST evidence", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "filename": "TEST_evidence.txt", "file_size": 20, "file_type": "text/plain", "control_id": null, "created_at": "2026-06-05T05:50:08.818196+00:00", "updated_at": "2026-06-05T05:50:08.818196+00:00", "description": "test", "hash_sha256": "019b2f52bca72502e01475c0c13d352b3dbf8139a4b9f378b37443ee218d7e5b", "is_verified": false, "uploaded_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "valid_until": null, "storage_path": "/app/backend/uploads/ecd3f0cc-533d-4b8a-b24d-f15041f3b26e/04d9a24d-e447-4dbd-81ee-4f5106abf245_TEST_evidence.txt"}	2026-06-05 05:50:08.933257+00
9c896c56-a9a2-4c00-84f5-f413bac55c19	{"id": "9c896c56-a9a2-4c00-84f5-f413bac55c19", "tags": [], "title": "TEST evidence", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "filename": "TEST_evidence.txt", "file_size": 20, "file_type": "text/plain", "control_id": null, "created_at": "2026-06-05T05:55:39.553775+00:00", "updated_at": "2026-06-05T05:55:39.553775+00:00", "description": "test", "hash_sha256": "019b2f52bca72502e01475c0c13d352b3dbf8139a4b9f378b37443ee218d7e5b", "is_verified": false, "uploaded_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "valid_until": null, "storage_path": "/app/backend/uploads/ecd3f0cc-533d-4b8a-b24d-f15041f3b26e/9c896c56-a9a2-4c00-84f5-f413bac55c19_TEST_evidence.txt"}	2026-06-05 05:55:39.667567+00
\.


--
-- Data for Name: findings; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.findings (id, data, created_at) FROM stdin;
335a6d5b-8039-4754-a9c7-fc2bb6953b38	{"id": "335a6d5b-8039-4754-a9c7-fc2bb6953b38", "title": "No documented DPDP consent management workflow", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "due_date": "2026-07-20T05:32:12.789372+00:00", "severity": "critical", "control_id": null, "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "assigned_to": null, "description": "No documented DPDP consent management workflow", "assessment_id": null, "recommendation": "Develop a documented procedure, train owners, and verify quarterly."}	2026-06-05 05:32:12.9036+00
8359f7f0-036b-40c7-a43c-042cfe17ceda	{"id": "8359f7f0-036b-40c7-a43c-042cfe17ceda", "title": "Privileged accounts without MFA on ERP", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "due_date": "2026-07-20T05:32:14.107190+00:00", "severity": "critical", "control_id": null, "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "assigned_to": null, "description": "Privileged accounts without MFA on ERP", "assessment_id": null, "recommendation": "Develop a documented procedure, train owners, and verify quarterly."}	2026-06-05 05:32:14.221418+00
483ab799-7684-4be7-a8a4-a1b7c3f95468	{"id": "483ab799-7684-4be7-a8a4-a1b7c3f95468", "title": "Backup restore not tested in last 12 months", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "in_progress", "due_date": "2026-07-20T05:32:15.415917+00:00", "severity": "high", "control_id": null, "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "assigned_to": null, "description": "Backup restore not tested in last 12 months", "assessment_id": null, "recommendation": "Develop a documented procedure, train owners, and verify quarterly."}	2026-06-05 05:32:15.530309+00
fabb829a-a85a-482c-a376-9bfce10ab7ed	{"id": "fabb829a-a85a-482c-a376-9bfce10ab7ed", "title": "Vendor risk assessments outdated", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "due_date": "2026-07-20T05:32:16.724216+00:00", "severity": "high", "control_id": null, "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "assigned_to": null, "description": "Vendor risk assessments outdated", "assessment_id": null, "recommendation": "Develop a documented procedure, train owners, and verify quarterly."}	2026-06-05 05:32:16.838556+00
12470fd0-ed30-4e98-ac5d-b74d5092e7b7	{"id": "12470fd0-ed30-4e98-ac5d-b74d5092e7b7", "title": "Awareness training completion under 60%", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "due_date": "2026-07-20T05:32:18.033724+00:00", "severity": "medium", "control_id": null, "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "assigned_to": null, "description": "Awareness training completion under 60%", "assessment_id": null, "recommendation": "Develop a documented procedure, train owners, and verify quarterly."}	2026-06-05 05:32:18.148031+00
96d81b80-ce4c-4ea6-a168-41788d9bee8b	{"id": "96d81b80-ce4c-4ea6-a168-41788d9bee8b", "title": "TEST Finding 1780638168", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "due_date": null, "severity": "high", "control_id": null, "created_at": "2026-06-05T05:42:49.589637+00:00", "updated_at": "2026-06-05T05:42:51.603911+00:00", "assigned_to": null, "description": "test", "assessment_id": null, "recommendation": null}	2026-06-05 05:42:49.704174+00
d0e7c31c-fcfd-4220-89ec-690aae1378b5	{"id": "d0e7c31c-fcfd-4220-89ec-690aae1378b5", "title": "TEST Finding 1780638454", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "due_date": null, "severity": "high", "control_id": null, "created_at": "2026-06-05T05:47:35.140186+00:00", "updated_at": "2026-06-05T05:47:41.387109+00:00", "assigned_to": "dc4d7985-f933-4460-b13f-23b1054b196d", "description": "test", "assessment_id": null, "recommendation": null}	2026-06-05 05:47:35.253296+00
6e4b45eb-35ce-437f-bd41-9d0d4c32c561	{"id": "6e4b45eb-35ce-437f-bd41-9d0d4c32c561", "title": "TEST Finding 1780638921", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "due_date": null, "severity": "high", "control_id": null, "created_at": "2026-06-05T05:55:22.619019+00:00", "updated_at": "2026-06-05T05:55:28.907790+00:00", "assigned_to": "dc4d7985-f933-4460-b13f-23b1054b196d", "description": "test", "assessment_id": null, "recommendation": null}	2026-06-05 05:55:22.733585+00
c0bdcb93-bc71-41af-8155-ef771c6d03b5	{"id": "c0bdcb93-bc71-41af-8155-ef771c6d03b5", "title": "Audit observation: missing access review", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "due_date": null, "severity": "medium", "control_id": null, "created_at": "2026-06-07T13:25:02.313362+00:00", "updated_at": "2026-06-07T13:25:02.313362+00:00", "assigned_to": null, "description": "x", "assessment_id": null, "recommendation": null}	2026-06-07 13:25:02.427057+00
d68bf8dd-4163-4c95-91b2-296ab8131ab1	{"id": "d68bf8dd-4163-4c95-91b2-296ab8131ab1", "title": "Audit observation: missing access review", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "due_date": null, "severity": "medium", "control_id": null, "created_at": "2026-06-07T13:29:37.262924+00:00", "updated_at": "2026-06-07T13:29:37.262924+00:00", "assigned_to": null, "description": "x", "assessment_id": null, "recommendation": null}	2026-06-07 13:29:37.376108+00
e68de90e-d3f7-4b0e-aaa8-75bfea67c379	{"id": "e68de90e-d3f7-4b0e-aaa8-75bfea67c379", "title": "Audit observation: missing access review", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "due_date": null, "severity": "medium", "control_id": null, "created_at": "2026-06-07T13:44:21.502829+00:00", "updated_at": "2026-06-07T13:44:21.502829+00:00", "assigned_to": null, "description": "x", "assessment_id": null, "recommendation": null}	2026-06-07 13:44:21.616659+00
05b7be26-0203-475e-b9c3-44937c60ac5e	{"id": "05b7be26-0203-475e-b9c3-44937c60ac5e", "title": "Audit observation: missing access review", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "due_date": null, "severity": "medium", "control_id": null, "created_at": "2026-06-07T15:41:35.750368+00:00", "updated_at": "2026-06-07T15:41:35.750368+00:00", "assigned_to": null, "description": "x", "assessment_id": null, "recommendation": null}	2026-06-07 15:41:35.864222+00
\.


--
-- Data for Name: frameworks; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.frameworks (id, data, created_at) FROM stdin;
7d0fc54d-1ca3-4773-ad76-b426a625091a	{"id": "7d0fc54d-1ca3-4773-ad76-b426a625091a", "key": "DPDP_ACT_2023", "name": "DPDP Act 2023", "type": "regulatory", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "version": "2023", "metadata": {}, "is_system": true, "created_at": "2026-06-05T05:30:19.780727+00:00", "updated_at": "2026-06-05T05:30:19.780727+00:00", "imported_at": "2026-06-05T05:30:19.780727+00:00"}	2026-06-05 05:30:29.541814+00
b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1	{"id": "b24fb969-0b3b-4ba4-8fa0-de4a3b83b8d1", "key": "ISO_27001_2022", "name": "ISO 27001:2022", "type": "standard", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "version": "2022", "metadata": {}, "is_system": true, "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "imported_at": "2026-06-05T05:30:58.695838+00:00"}	2026-06-05 05:31:20.264152+00
eed067e5-85ba-4db6-9362-402f615f5830	{"id": "eed067e5-85ba-4db6-9362-402f615f5830", "key": "ISO_27701", "name": "ISO 27701:2019", "type": "standard", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "version": "2019", "metadata": {}, "is_system": true, "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "imported_at": "2026-06-05T05:30:58.695838+00:00"}	2026-06-05 05:31:34.952083+00
e47abb86-b14f-49a8-ad70-e12c81fa25a1	{"id": "e47abb86-b14f-49a8-ad70-e12c81fa25a1", "key": "NIST_CSF_2_0", "name": "NIST CSF 2.0", "type": "framework", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "version": "2.0", "metadata": {}, "is_system": true, "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "imported_at": "2026-06-05T05:30:58.695838+00:00"}	2026-06-05 05:31:42.799755+00
\.


--
-- Data for Name: incidents; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.incidents (id, data, created_at) FROM stdin;
59ab09d6-8386-4eab-b715-86afa08d91fc	{"id": "59ab09d6-8386-4eab-b715-86afa08d91fc", "title": "Suspicious login from unknown IP on student portal", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "detected", "severity": "high", "created_at": "2026-06-05T06:27:03.125551+00:00", "updated_at": "2026-06-05T06:27:03.125551+00:00", "description": "Burst of 320 failed logins followed by 4 successes on student SIS", "detected_at": "2026-06-05T06:27:03.125551+00:00", "incident_type": "unauthorized_access", "reported_by_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "response_notes": null, "response_steps": [{"done": false, "step": "Activate Incident Response Team", "owner": "IT Sec Officer", "deadline_hours": 1}, {"done": false, "step": "Isolate affected systems", "owner": "IT Ops", "deadline_hours": 1}, {"done": false, "step": "Preserve forensic evidence (snapshots, logs)", "owner": "IT Sec Officer", "deadline_hours": 2}, {"done": false, "step": "Notify CERT-In within 6 hours (cert-in.org.in)", "owner": "IT Sec Officer", "deadline_hours": 6}, {"done": false, "step": "Notify Data Principals + DP Board within 72h (DPDP S.8(6))", "owner": "Compliance Officer", "deadline_hours": 72}, {"done": false, "step": "Convene Board / VC for status briefing", "owner": "Institution Admin", "deadline_hours": 12}, {"done": false, "step": "Post-incident review + lessons-learned report", "owner": "IT Sec Officer", "deadline_hours": 168}], "affected_systems": ["SIS", "Auth Service"], "dpdp_notified_at": null, "reported_by_name": "Vikram Singh", "reported_by_email": "itsec@rut.edu.in", "cert_in_reported_at": null, "affected_data_categories": ["student_records"], "data_principals_affected": 4}	2026-06-05 06:27:03.241008+00
02264061-90d4-4ac7-9c5b-066c5433ed0d	{"id": "02264061-90d4-4ac7-9c5b-066c5433ed0d", "title": "TEST_QA Phishing 1780641525", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "detected", "severity": "high", "created_at": "2026-06-05T06:38:45.857637+00:00", "updated_at": "2026-06-05T06:38:55.894019+00:00", "description": "QA iteration5 — test incident", "detected_at": "2026-06-05T06:38:45.857637+00:00", "incident_type": "phishing", "reported_by_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "response_notes": null, "response_steps": [{"done": false, "step": "Activate Incident Response Team", "owner": "IT Sec Officer", "deadline_hours": 1}, {"done": false, "step": "Isolate affected systems", "owner": "IT Ops", "deadline_hours": 1}, {"done": false, "step": "Preserve forensic evidence (snapshots, logs)", "owner": "IT Sec Officer", "deadline_hours": 2}, {"done": false, "step": "Notify CERT-In within 6 hours (cert-in.org.in)", "owner": "IT Sec Officer", "deadline_hours": 6}, {"done": false, "step": "Notify Data Principals + DP Board within 72h (DPDP S.8(6))", "owner": "Compliance Officer", "deadline_hours": 72}, {"done": false, "step": "Reset credentials of affected accounts; enforce MFA", "owner": "IT Ops", "deadline_hours": 4}, {"done": false, "step": "Send awareness advisory to all staff/students", "owner": "Compliance Officer", "deadline_hours": 24}, {"done": false, "step": "Convene Board / VC for status briefing", "owner": "Institution Admin", "deadline_hours": 12}, {"done": false, "step": "Post-incident review + lessons-learned report", "owner": "IT Sec Officer", "deadline_hours": 168}], "affected_systems": ["email_server"], "dpdp_notified_at": "2026-06-05T06:38:55.894019+00:00", "reported_by_name": "Vikram Singh", "reported_by_email": "itsec@rut.edu.in", "cert_in_reported_at": "2026-06-05T06:38:51.748333+00:00", "affected_data_categories": ["student_records"], "data_principals_affected": 25}	2026-06-05 06:38:45.972068+00
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.notifications (id, data, created_at) FROM stdin;
e51ee0c3-a8ca-447f-9e99-7049d994ef4c	{"id": "e51ee0c3-a8ca-447f-9e99-7049d994ef4c", "type": "warning", "title": "Critical risk added", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "is_read": false, "message": "TEST Risk 1780638156 (score 20)", "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "metadata": {"risk_id": "823b0e0a-cc55-468e-9beb-0702f544a746"}, "created_at": "2026-06-05T05:42:38.555223+00:00"}	2026-06-05 05:42:38.669717+00
e7748b9b-90a0-4405-9439-316b06adbd4c	{"id": "e7748b9b-90a0-4405-9439-316b06adbd4c", "type": "warning", "title": "Critical risk added", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "is_read": false, "message": "TEST Risk 1780638444 (score 20)", "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "metadata": {"risk_id": "6adc9487-0bd8-4243-8e46-039240b77172"}, "created_at": "2026-06-05T05:47:26.281365+00:00"}	2026-06-05 05:47:26.394553+00
a5e2ef59-f7ef-44c7-b8cf-7e590d564a31	{"id": "a5e2ef59-f7ef-44c7-b8cf-7e590d564a31", "type": "warning", "title": "Critical risk added", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "is_read": false, "message": "TEST Risk 1780638907 (score 20)", "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "metadata": {"risk_id": "1f147371-9490-406d-96ef-8faeebe4190f"}, "created_at": "2026-06-05T05:55:09.635428+00:00"}	2026-06-05 05:55:09.749153+00
15f4087d-261c-4c29-a2b1-d8a8a8350433	{"id": "15f4087d-261c-4c29-a2b1-d8a8a8350433", "type": "warning", "title": "Critical risk added", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "is_read": true, "message": "TEST Risk 1780638444 (score 20)", "read_at": "2026-06-05T06:17:38.035766+00:00", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"risk_id": "6adc9487-0bd8-4243-8e46-039240b77172"}, "created_at": "2026-06-05T05:47:26.281365+00:00"}	2026-06-05 05:47:26.394553+00
f8e46e9d-2255-4cfd-8362-063296639d1b	{"id": "f8e46e9d-2255-4cfd-8362-063296639d1b", "type": "success", "title": "Policy drafted", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "is_read": true, "message": "Privacy Policy draft prepared from your intake", "read_at": "2026-06-05T06:17:39.380464+00:00", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"policy_id": "b3217cb3-8159-4b97-8883-d180d5003d43"}, "created_at": "2026-06-05T05:53:12.858136+00:00"}	2026-06-05 05:53:12.979129+00
0d574575-fb40-4188-b141-fc14ce62f436	{"id": "0d574575-fb40-4188-b141-fc14ce62f436", "type": "warning", "title": "Critical risk added", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "is_read": true, "message": "TEST Risk 1780638907 (score 20)", "read_at": "2026-06-05T06:17:39.839301+00:00", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"risk_id": "1f147371-9490-406d-96ef-8faeebe4190f"}, "created_at": "2026-06-05T05:55:09.635428+00:00"}	2026-06-05 05:55:09.749153+00
4b4242ab-3d8d-4b62-9706-d7edf84eb3a2	{"id": "4b4242ab-3d8d-4b62-9706-d7edf84eb3a2", "type": "incident_logged", "title": "Incident logged: HIGH", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "is_read": false, "message": "Vikram Singh reported \\"Suspicious login from unknown IP on student portal\\". CERT-In deadline in 6 hours.", "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "created_at": "2026-06-05T06:27:03.125551+00:00"}	2026-06-05 06:27:05.231989+00
6498ff64-e1ea-44c4-a06e-43661542cc32	{"id": "6498ff64-e1ea-44c4-a06e-43661542cc32", "type": "task_assigned", "title": "Control assigned: DPDP-S8-C1", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "is_read": false, "message": "You have been assigned the control \\"Accuracy, completeness and consistency of personal data\\" for IT. Due: 2026-07-15", "user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "created_at": "2026-06-05T06:27:36.830210+00:00"}	2026-06-05 06:27:36.947877+00
8e807834-dedb-4a6c-8b4b-6b14f34bfb38	{"id": "8e807834-dedb-4a6c-8b4b-6b14f34bfb38", "type": "task_assigned", "title": "Control assigned: DPDP-S8-C1", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "is_read": false, "message": "You have been assigned the control \\"Accuracy, completeness and consistency of personal data\\" for IT. Due: 2026-12-31", "user_id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "created_at": "2026-06-05T06:38:25.788153+00:00"}	2026-06-05 06:38:25.902582+00
5f0ec3ae-8e33-44c3-b9a0-f673128ec7e5	{"id": "5f0ec3ae-8e33-44c3-b9a0-f673128ec7e5", "type": "task_submitted", "title": "Task submitted: DPDP-S8-C1", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "is_read": false, "message": "Vikram Singh submitted evidence for \\"Accuracy, completeness and consistency of personal data\\" (IT)", "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "created_at": "2026-06-05T06:38:39.310471+00:00"}	2026-06-05 06:38:39.424613+00
f217767b-29ef-4a1a-9737-2e0eac68e3c4	{"id": "f217767b-29ef-4a1a-9737-2e0eac68e3c4", "type": "incident_logged", "title": "Incident logged: HIGH", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "is_read": false, "message": "Vikram Singh reported \\"TEST_QA Phishing 1780641525\\". CERT-In deadline in 6 hours.", "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "created_at": "2026-06-05T06:38:45.857637+00:00"}	2026-06-05 06:38:47.933894+00
48a7b5ad-a3dd-40a6-b8b1-63bbdc7d1a84	{"id": "48a7b5ad-a3dd-40a6-b8b1-63bbdc7d1a84", "type": "incident_logged", "title": "Incident logged: HIGH", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "is_read": true, "message": "Vikram Singh reported \\"Suspicious login from unknown IP on student portal\\". CERT-In deadline in 6 hours.", "read_at": "2026-06-07T13:43:07.477162+00:00", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T06:27:03.125551+00:00"}	2026-06-05 06:27:04.568315+00
785fb0ba-e8f4-4ffc-92c0-ffede817daf4	{"id": "785fb0ba-e8f4-4ffc-92c0-ffede817daf4", "type": "incident_logged", "title": "Incident logged: HIGH", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "is_read": true, "message": "Vikram Singh reported \\"TEST_QA Phishing 1780641525\\". CERT-In deadline in 6 hours.", "read_at": "2026-06-07T13:43:08.743623+00:00", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T06:38:45.857637+00:00"}	2026-06-05 06:38:47.280191+00
c7017120-74cd-4a5a-b777-51b59344e591	{"id": "c7017120-74cd-4a5a-b777-51b59344e591", "type": "warning", "title": "Critical risk added", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "is_read": true, "message": "TEST Risk 1780638156 (score 20)", "read_at": "2026-06-07T13:43:16.125764+00:00", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"risk_id": "823b0e0a-cc55-468e-9beb-0702f544a746"}, "created_at": "2026-06-05T05:42:38.555223+00:00"}	2026-06-05 05:42:38.669717+00
69c87202-e8e7-4951-ad51-f9b0bbe1f03e	{"id": "69c87202-e8e7-4951-ad51-f9b0bbe1f03e", "type": "success", "title": "Policy drafted", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "is_read": true, "message": "Information Security Policy draft prepared from your intake", "read_at": "2026-06-07T18:39:42.862252+00:00", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "metadata": {"policy_id": "66df77ba-b1ac-4a50-a6c6-f5a04431b623"}, "created_at": "2026-06-07T18:26:05.303730+00:00"}	2026-06-07 18:26:05.367896+00
\.


--
-- Data for Name: organizations; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.organizations (id, data, created_at) FROM stdin;
ecd3f0cc-533d-4b8a-b24d-f15041f3b26e	{"id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "name": "Rajasthan University of Technology", "slug": "rut", "type": "university", "settings": {"language": "en", "timezone": "Asia/Kolkata"}, "is_active": true, "created_at": "2026-06-05T05:30:19.780727+00:00", "updated_at": "2026-06-05T05:30:19.780727+00:00", "subscription_tier": "enterprise"}	2026-06-05 05:30:20.549563+00
4fbc16aa-81ca-4c32-9a6e-bccdde14ccbb	{"id": "4fbc16aa-81ca-4c32-9a6e-bccdde14ccbb", "name": "TEST Org 1780638091", "slug": "test-org-1780638091", "type": "university", "settings": {"language": "en", "timezone": "Asia/Kolkata"}, "is_active": true, "created_at": "2026-06-05T05:41:32.732831+00:00", "updated_at": "2026-06-05T05:41:32.732831+00:00", "subscription_tier": "trial"}	2026-06-05 05:41:33.510393+00
83693a6a-5de2-49af-b75b-55efaffaacc0	{"id": "83693a6a-5de2-49af-b75b-55efaffaacc0", "name": "TEST Org 1780638829", "slug": "test-org-1780638829", "type": "university", "settings": {"language": "en", "timezone": "Asia/Kolkata"}, "is_active": true, "created_at": "2026-06-05T05:53:50.026932+00:00", "updated_at": "2026-06-05T05:53:50.026932+00:00", "subscription_tier": "trial"}	2026-06-05 05:53:50.799019+00
d895cc64-7fd2-4883-9d19-27619fc370d1	{"id": "d895cc64-7fd2-4883-9d19-27619fc370d1", "name": "tdhdbfhf ", "slug": "tdhdbfhf-", "type": "university", "settings": {"language": "en", "timezone": "Asia/Kolkata"}, "is_active": true, "created_at": "2026-06-07T13:00:00.978268+00:00", "updated_at": "2026-06-07T13:00:00.978268+00:00", "subscription_tier": "trial"}	2026-06-07 13:00:01.091626+00
7bab9ff2-c2fd-4dc2-b0c2-6ec6bd8bf129	{"id": "7bab9ff2-c2fd-4dc2-b0c2-6ec6bd8bf129", "name": "IIT Testopolis", "slug": "iit-testopolis", "type": "university", "created_at": "2026-06-07T13:42:47.143124+00:00", "updated_at": "2026-06-07T13:42:47.143124+00:00", "subscription_tier": "trial"}	2026-06-07 13:42:47.92174+00
\.


--
-- Data for Name: password_resets; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.password_resets (id, data, created_at) FROM stdin;
8abfd75a-f016-48c4-8713-020361f60683	{"id": "8abfd75a-f016-48c4-8713-020361f60683", "used": false, "token": "gQ1kpaaLtdm1L9kp9dPyNh7lVPG75mtVeD7lhYNDdNE", "user_id": "5b27c9dc-8ed6-4cb0-b255-b75b8e09bbf9", "created_at": "2026-06-05T05:53:20.887121+00:00", "expires_at": "2026-06-05T06:08:20.887075+00:00"}	2026-06-05 05:53:21.002011+00
a247b023-a546-4a06-8211-3231887b94d3	{"id": "a247b023-a546-4a06-8211-3231887b94d3", "used": false, "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T12:56:23.159442+00:00", "expires_at": "2026-06-07T13:11:23.159392+00:00", "token_hash": "bb8adfaa5b72269c13c4c493bb5e30aa162a234a58a08fddadc63df74208b281"}	2026-06-07 12:56:23.273008+00
ab17febf-20a5-40f5-a566-82193284b67e	{"id": "ab17febf-20a5-40f5-a566-82193284b67e", "used": false, "purpose": "invite", "user_id": "489a236e-7abe-4219-8ebf-4ec7d378533f", "created_at": "2026-06-07T12:56:32.327754+00:00", "expires_at": "2026-06-08T12:56:33.202669+00:00", "token_hash": "4f7fc2107bd7190019e3d73e490ba9b196da6fecb6b15f8c0af372b50a812c57"}	2026-06-07 12:56:33.3163+00
187ce8d0-491c-44a4-a5f2-b01fb2ca223e	{"id": "187ce8d0-491c-44a4-a5f2-b01fb2ca223e", "used": false, "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T12:59:17.463343+00:00", "expires_at": "2026-06-07T13:14:17.463295+00:00", "token_hash": "4bbfc4a36f2ce2ad7ac0b5653cfd1c1c6e0899ae7cb90520a684b287975a1f6b"}	2026-06-07 12:59:17.577322+00
b2526447-8036-4cbc-964c-84285cee7c60	{"id": "b2526447-8036-4cbc-964c-84285cee7c60", "used": false, "purpose": "invite", "user_id": "d955f6c1-27db-40ae-9c04-117e180f328a", "created_at": "2026-06-07T12:59:27.025818+00:00", "expires_at": "2026-06-08T12:59:27.900030+00:00", "token_hash": "4d0199462e19e4fe3ab303ab3fb65dcb0db642f743af3e5af68807e18f40a1e3"}	2026-06-07 12:59:28.014072+00
c901a9d9-441b-43d5-9b89-09b5c81b2441	{"id": "c901a9d9-441b-43d5-9b89-09b5c81b2441", "used": true, "used_at": "2026-06-07T12:59:57.678970+00:00", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T12:59:53.943135+00:00", "expires_at": "2026-06-07T13:14:53.943087+00:00", "token_hash": "881ae26b4b348be824be2c04c6ec213b8491748f562f9590bb4e4880a0c6e887"}	2026-06-07 12:59:54.057179+00
5bf52845-5fb1-457c-b5e6-172f739c9f3a	{"id": "5bf52845-5fb1-457c-b5e6-172f739c9f3a", "used": false, "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T13:04:03.507568+00:00", "expires_at": "2026-06-07T13:19:03.507522+00:00", "token_hash": "b1d4e9596df995c1c1a5e2b826408906e614641628c2c42ab8f83c729c5ff089"}	2026-06-07 13:04:03.620646+00
5f3977da-464e-4c01-997f-29e5fdd4be8d	{"id": "5f3977da-464e-4c01-997f-29e5fdd4be8d", "used": false, "purpose": "invite", "user_id": "f4a02762-9920-4c96-81e1-adf6c1288880", "created_at": "2026-06-07T13:04:13.220013+00:00", "expires_at": "2026-06-08T13:04:14.098544+00:00", "token_hash": "65e19b7fc6d4bafce4f0bd5bab0d40aac6c5958106f6279faddb5e98cb6a066c"}	2026-06-07 13:04:14.211781+00
5d9a783e-81dd-4edb-acfb-0e34e5aa4918	{"id": "5d9a783e-81dd-4edb-acfb-0e34e5aa4918", "used": false, "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T13:30:47.464270+00:00", "expires_at": "2026-06-07T13:45:47.464223+00:00", "token_hash": "32e836fc6fcfb7153b5fd67c31065f3452975c65641b5d1e68d5172786c2f17d"}	2026-06-07 13:30:47.577531+00
c196edc3-434a-4d17-9b40-d08f3e776698	{"id": "c196edc3-434a-4d17-9b40-d08f3e776698", "used": false, "purpose": "invite", "user_id": "aac58d6b-53d1-4ab6-a261-4cbc755945a4", "created_at": "2026-06-07T13:30:57.156208+00:00", "expires_at": "2026-06-08T13:30:58.036059+00:00", "token_hash": "ab8675d1fdcaa88b225e437f4f0a56fe92304a156bdd6a2196e5b6b51b6e8db9"}	2026-06-07 13:30:58.149174+00
\.


--
-- Data for Name: policies; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.policies (id, data, created_at) FROM stdin;
92076049-7f54-4357-a151-b3d1bf84178c	{"id": "92076049-7f54-4357-a151-b3d1bf84178c", "title": "Incident Response Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "draft", "content_md": "# Incident Response Policy\\n\\n## Purpose\\nThis policy establishes baseline requirements for incident_response.\\n\\n## Scope\\nAll personnel, students, contractors and systems of the University.\\n\\n## Policy Statements\\n1. The University commits to protecting personal data per the DPDP Act 2023.\\n2. Information security is governed by ISO/IEC 27001:2022.\\n\\n## Roles and Responsibilities\\nCISO is accountable. DPO is responsible.\\n\\n## Review\\nReviewed annually by the Information Security Committee.\\n", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:30:58.695838+00:00", "approved_by": null, "policy_type": "incident_response", "review_date": "2027-06-05T05:32:08.206803+00:00", "effective_date": "2026-06-05T05:30:58.695838+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "version_number": 1, "is_ai_generated": false}	2026-06-05 05:32:08.321008+00
9a570615-cc96-4d47-a331-bdf2d9951744	{"id": "9a570615-cc96-4d47-a331-bdf2d9951744", "title": "Information Security Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "draft", "content_md": "# Information Security Policy\\n\\n**Organization:** Rajasthan University of Technology\\n**Framework Alignment:** ISO 27001:2022 A.5.1\\n**Status:** DRAFT (AI-Generated)\\n**Version:** 1.0\\n**Effective Date:** 2026-06-05\\n\\n## 1. Purpose\\nEstablish baseline requirements for protection of the confidentiality, integrity and availability of institutional information assets.\\n\\n## 2. Scope\\nThis policy applies to all employees, contractors, students, vendors and any third party with access to institutional information assets.\\n\\n## 3. Definitions\\n- **Personal Data** as defined under the DPDP Act 2023.\\n- **Information Asset** any data, document or system that supports institutional operations.\\n\\n## 4. Policy Statements\\n1. Information shall be classified per its sensitivity and protected with controls commensurate with risk.\\n2. Access to information systems shall be granted on a least-privilege basis with quarterly access reviews.\\n3. All systems shall log security-relevant events to a central log aggregator with 12-month retention.\\n4. Backups shall be performed daily, encrypted, and restore-tested at least quarterly.\\n5. Cryptographic controls shall comply with NIST SP 800-175B.\\n\\n## 5. Roles and Responsibilities\\n- **CISO** – Accountable for implementation and effectiveness.\\n- **DPO** – Responsible for privacy aspects.\\n- **Department Heads** – Responsible for compliance within their unit.\\n- **All Personnel** – Required to comply.\\n\\n## 6. Compliance and Enforcement\\nViolations may result in disciplinary action up to and including termination.\\n\\n## 7. Review\\nThis policy will be reviewed annually or upon significant change.\\n\\n## 8. Framework References\\nDPDP_ACT_2023, ISO_27001_2022\\n\\n## 9. Approval\\n| Role | Name | Date |\\n|------|------|------|\\n| Vice-Chancellor | _________ | _________ |\\n| CISO | _________ | _________ |\\n", "created_at": "2026-06-05T05:43:08.511342+00:00", "updated_at": "2026-06-05T05:43:08.511342+00:00", "approved_by": null, "policy_type": "information_security", "review_date": null, "effective_date": "2026-06-05T05:43:08.511342+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "version_number": 1, "is_ai_generated": true}	2026-06-05 05:43:08.626709+00
1d758f08-ed18-4a27-a17a-a4480ece3b4b	{"id": "1d758f08-ed18-4a27-a17a-a4480ece3b4b", "title": "Privacy Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "draft", "content_md": "# Privacy Policy\\n\\n**Organization:** Rajasthan University of Technology\\n**Framework Alignment:** DPDP Act 2023 Section 5 (Notice)\\n**Status:** DRAFT (AI-Generated)\\n**Version:** 1.0\\n**Effective Date:** 2026-06-05\\n\\n## 1. Purpose\\nInform Data Principals (students, faculty, staff, alumni) of how the institution processes personal data in compliance with the DPDP Act 2023.\\n\\n## 2. Scope\\nThis policy applies to all employees, contractors, students, vendors and any third party with access to institutional information assets.\\n\\n## 3. Definitions\\n- **Personal Data** as defined under the DPDP Act 2023.\\n- **Information Asset** any data, document or system that supports institutional operations.\\n\\n## 4. Policy Statements\\n1. Personal data is processed only on the basis of consent or legitimate use under Section 7.\\n2. A privacy notice is published in English and the languages listed in the Eighth Schedule.\\n3. Data Principals may exercise rights of access, correction, erasure and grievance redressal via the published DPO contact.\\n4. Cross-border transfers are documented with appropriate safeguards.\\n5. Children's data is processed only with verifiable parental consent.\\n\\n## 5. Roles and Responsibilities\\n- **CISO** – Accountable for implementation and effectiveness.\\n- **DPO** – Responsible for privacy aspects.\\n- **Department Heads** – Responsible for compliance within their unit.\\n- **All Personnel** – Required to comply.\\n\\n## 6. Compliance and Enforcement\\nViolations may result in disciplinary action up to and including termination.\\n\\n## 7. Review\\nThis policy will be reviewed annually or upon significant change.\\n\\n## 8. Framework References\\nDPDP_ACT_2023, ISO_27001_2022\\n\\n## 9. Approval\\n| Role | Name | Date |\\n|------|------|------|\\n| Vice-Chancellor | _________ | _________ |\\n| CISO | _________ | _________ |\\n", "created_at": "2026-06-05T05:43:11.194521+00:00", "updated_at": "2026-06-05T05:43:11.194521+00:00", "approved_by": null, "policy_type": "privacy", "review_date": null, "effective_date": "2026-06-05T05:43:11.194521+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "version_number": 1, "is_ai_generated": true}	2026-06-05 05:43:11.309852+00
4465c968-03c8-4553-9ce8-9db59d03c14f	{"id": "4465c968-03c8-4553-9ce8-9db59d03c14f", "title": "Information Security Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "approved", "content_md": "# Updated TEST 1780638204\\n\\nUpdated content.", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:43:26.621325+00:00", "approved_by": null, "policy_type": "information_security", "review_date": "2027-06-05T05:32:06.893775+00:00", "effective_date": "2026-06-05T05:30:58.695838+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "version_number": 2, "is_ai_generated": false}	2026-06-05 05:32:07.007946+00
9523ab29-9134-4684-a082-c056777c9ba0	{"id": "9523ab29-9134-4684-a082-c056777c9ba0", "title": "Privacy Policy (DPDP)", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "review", "content_md": "# Updated TEST 1780638961\\n\\nUpdated content.", "created_at": "2026-06-05T05:30:58.695838+00:00", "updated_at": "2026-06-05T05:56:03.508374+00:00", "approved_by": null, "policy_type": "privacy", "review_date": "2027-06-05T05:32:07.552654+00:00", "effective_date": "2026-06-05T05:30:58.695838+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "version_number": 2, "is_ai_generated": false}	2026-06-05 05:32:07.666855+00
b622dadf-3476-441c-9ad1-0af526b8f2cd	{"id": "b622dadf-3476-441c-9ad1-0af526b8f2cd", "title": "Incident Response Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "draft", "content_md": "# Incident Response Policy\\n\\n**Organization:** Rajasthan University of Technology\\n**Framework Alignment:** ISO 27001 A.5.24 / NIST RS.MA-01 / DPDP S.8(6)\\n**Status:** DRAFT (AI-Generated)\\n**Version:** 1.0\\n**Effective Date:** 2026-06-05\\n\\n## 1. Purpose\\nDefine how the institution prepares for, detects, responds to and recovers from information security incidents.\\n\\n## 2. Scope\\nThis policy applies to all employees, contractors, students, vendors and any third party with access to institutional information assets.\\n\\n## 3. Definitions\\n- **Personal Data** as defined under the DPDP Act 2023.\\n- **Information Asset** any data, document or system that supports institutional operations.\\n\\n## 4. Policy Statements\\n1. An Incident Response Team led by the CISO is on call 24x7.\\n2. All incidents are triaged per a documented severity matrix.\\n3. Personal-data breaches are notified to the Data Protection Board within the prescribed time.\\n4. Tabletop exercises are conducted at least annually.\\n5. Post-incident reviews capture lessons learned and corrective actions.\\n\\n## 5. Roles and Responsibilities\\n- **CISO** – Accountable for implementation and effectiveness.\\n- **DPO** – Responsible for privacy aspects.\\n- **Department Heads** – Responsible for compliance within their unit.\\n- **All Personnel** – Required to comply.\\n\\n## 6. Compliance and Enforcement\\nViolations may result in disciplinary action up to and including termination.\\n\\n## 7. Review\\nThis policy will be reviewed annually or upon significant change.\\n\\n## 8. Framework References\\nDPDP_ACT_2023, ISO_27001_2022\\n\\n## 9. Approval\\n| Role | Name | Date |\\n|------|------|------|\\n| Vice-Chancellor | _________ | _________ |\\n| CISO | _________ | _________ |\\n", "created_at": "2026-06-05T05:43:13.878232+00:00", "updated_at": "2026-06-05T05:43:13.878232+00:00", "approved_by": null, "policy_type": "incident_response", "review_date": null, "effective_date": "2026-06-05T05:43:13.878232+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "version_number": 1, "is_ai_generated": true}	2026-06-05 05:43:13.993727+00
b66e6a5e-fc63-4fdb-84f1-49668f64fdf5	{"id": "b66e6a5e-fc63-4fdb-84f1-49668f64fdf5", "title": "Access Control Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "draft", "content_md": "# Access Control Policy\\n\\n**Organization:** Rajasthan University of Technology\\n**Framework Alignment:** ISO 27001 A.8.3 / NIST PR.AA-01\\n**Status:** DRAFT (AI-Generated)\\n**Version:** 1.0\\n**Effective Date:** 2026-06-05\\n\\n## 1. Purpose\\nGovern the granting, review and revocation of access to information systems and physical facilities.\\n\\n## 2. Scope\\nThis policy applies to all employees, contractors, students, vendors and any third party with access to institutional information assets.\\n\\n## 3. Definitions\\n- **Personal Data** as defined under the DPDP Act 2023.\\n- **Information Asset** any data, document or system that supports institutional operations.\\n\\n## 4. Policy Statements\\n1. Access is granted on a need-to-know and least-privilege basis.\\n2. MFA is enforced for all privileged accounts and remote access.\\n3. Joiner-mover-leaver workflows complete within one business day.\\n4. Privileged access is reviewed quarterly by the system owner.\\n5. Shared accounts are prohibited except for emergency-break-glass accounts under strict logging.\\n\\n## 5. Roles and Responsibilities\\n- **CISO** – Accountable for implementation and effectiveness.\\n- **DPO** – Responsible for privacy aspects.\\n- **Department Heads** – Responsible for compliance within their unit.\\n- **All Personnel** – Required to comply.\\n\\n## 6. Compliance and Enforcement\\nViolations may result in disciplinary action up to and including termination.\\n\\n## 7. Review\\nThis policy will be reviewed annually or upon significant change.\\n\\n## 8. Framework References\\nDPDP_ACT_2023, ISO_27001_2022\\n\\n## 9. Approval\\n| Role | Name | Date |\\n|------|------|------|\\n| Vice-Chancellor | _________ | _________ |\\n| CISO | _________ | _________ |\\n", "created_at": "2026-06-05T05:43:16.566434+00:00", "updated_at": "2026-06-05T05:43:16.566434+00:00", "approved_by": null, "policy_type": "access_control", "review_date": null, "effective_date": "2026-06-05T05:43:16.566434+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "version_number": 1, "is_ai_generated": true}	2026-06-05 05:43:16.681755+00
e579a678-ddcb-4e47-8080-49c7bbd48745	{"id": "e579a678-ddcb-4e47-8080-49c7bbd48745", "title": "Vendor Risk Management Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "draft", "content_md": "# Vendor Risk Management Policy\\n\\n**Organization:** Rajasthan University of Technology\\n**Framework Alignment:** DPDP S.8(7) / ISO 27001 A.5.19\\n**Status:** DRAFT (AI-Generated)\\n**Version:** 1.0\\n**Effective Date:** 2026-06-05\\n\\n## 1. Purpose\\nGovern security and privacy risk arising from third-party suppliers and SaaS providers.\\n\\n## 2. Scope\\nThis policy applies to all employees, contractors, students, vendors and any third party with access to institutional information assets.\\n\\n## 3. Definitions\\n- **Personal Data** as defined under the DPDP Act 2023.\\n- **Information Asset** any data, document or system that supports institutional operations.\\n\\n## 4. Policy Statements\\n1. All suppliers handling personal data must execute a Data Processing Agreement.\\n2. Critical suppliers are assessed annually using a documented questionnaire.\\n3. Sub-processors are inventoried and require prior written approval.\\n4. Contracts include audit rights, breach-notification SLAs and data return / destruction obligations.\\n\\n## 5. Roles and Responsibilities\\n- **CISO** – Accountable for implementation and effectiveness.\\n- **DPO** – Responsible for privacy aspects.\\n- **Department Heads** – Responsible for compliance within their unit.\\n- **All Personnel** – Required to comply.\\n\\n## 6. Compliance and Enforcement\\nViolations may result in disciplinary action up to and including termination.\\n\\n## 7. Review\\nThis policy will be reviewed annually or upon significant change.\\n\\n## 8. Framework References\\nDPDP_ACT_2023, ISO_27001_2022\\n\\n## 9. Approval\\n| Role | Name | Date |\\n|------|------|------|\\n| Vice-Chancellor | _________ | _________ |\\n| CISO | _________ | _________ |\\n", "created_at": "2026-06-05T05:43:19.235772+00:00", "updated_at": "2026-06-05T05:43:19.235772+00:00", "approved_by": null, "policy_type": "vendor_risk", "review_date": null, "effective_date": "2026-06-05T05:43:19.235772+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "version_number": 1, "is_ai_generated": true}	2026-06-05 05:43:19.349792+00
81dd2a75-dd77-495f-b3e6-89d1bb97ae1a	{"id": "81dd2a75-dd77-495f-b3e6-89d1bb97ae1a", "title": "Data Retention Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "draft", "content_md": "# Data Retention Policy\\n\\n**Organization:** Rajasthan University of Technology\\n**Framework Alignment:** DPDP S.8(7), S.12\\n**Status:** DRAFT (AI-Generated)\\n**Version:** 1.0\\n**Effective Date:** 2026-06-05\\n\\n## 1. Purpose\\nDefine retention periods and disposal mechanisms for personal data across institutional systems.\\n\\n## 2. Scope\\nThis policy applies to all employees, contractors, students, vendors and any third party with access to institutional information assets.\\n\\n## 3. Definitions\\n- **Personal Data** as defined under the DPDP Act 2023.\\n- **Information Asset** any data, document or system that supports institutional operations.\\n\\n## 4. Policy Statements\\n1. Student records are retained for 5 years post-graduation unless statutory law requires longer.\\n2. Applicant records are deleted within 6 months of admission cycle close, unless converted to enrolment.\\n3. CCTV footage is retained for 30 days unless preserved by legal hold.\\n4. Erasure on withdrawal of consent is completed within 30 days.\\n\\n## 5. Roles and Responsibilities\\n- **CISO** – Accountable for implementation and effectiveness.\\n- **DPO** – Responsible for privacy aspects.\\n- **Department Heads** – Responsible for compliance within their unit.\\n- **All Personnel** – Required to comply.\\n\\n## 6. Compliance and Enforcement\\nViolations may result in disciplinary action up to and including termination.\\n\\n## 7. Review\\nThis policy will be reviewed annually or upon significant change.\\n\\n## 8. Framework References\\nDPDP_ACT_2023, ISO_27001_2022\\n\\n## 9. Approval\\n| Role | Name | Date |\\n|------|------|------|\\n| Vice-Chancellor | _________ | _________ |\\n| CISO | _________ | _________ |\\n", "created_at": "2026-06-05T05:43:21.906831+00:00", "updated_at": "2026-06-05T05:43:21.906831+00:00", "approved_by": null, "policy_type": "data_retention", "review_date": null, "effective_date": "2026-06-05T05:43:21.906831+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "version_number": 1, "is_ai_generated": true}	2026-06-05 05:43:22.022283+00
b3217cb3-8159-4b97-8883-d180d5003d43	{"id": "b3217cb3-8159-4b97-8883-d180d5003d43", "title": "Privacy Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "draft", "ai_model": "intake-template-v1", "content_md": "# Privacy Policy\\n\\n**Organization:** Rajasthan University of Technology\\n**Framework Alignment:** DPDP Act 2023 Section 5 (Notice) · ISO/IEC 27701:2019 · DPDP_ACT_2023, ISO_27001_2022\\n**Status:** Draft  ·  **Version:** 1.0  ·  **Effective Date:** 2026-06-05\\n\\n## 1. Purpose\\nRajasthan University of Technology (\\"the Institution\\") publishes this Privacy Policy to inform Data Principals — students, applicants, faculty, staff, alumni, parents and visitors — about how their personal data is processed under the Digital Personal Data Protection Act, 2023.\\n\\n## 2. Scope\\nThis policy covers all personal data processed by the Institution, including: **student PII, faculty/staff PII, biometric attendance data**.\\n\\n## 3. Languages\\nThis notice is published in: **English**. Translations into other languages listed in the Eighth Schedule are available on request.\\n\\n## 4. Policy Statements\\n1. **Lawful Basis** — Personal data is processed under consent (Sec. 6) or specified legitimate uses (Sec. 7).\\n2. **Notice** — A clear, plain-language notice is presented before or with every request for consent.\\n3. **Children's Data** — Verifiable parental consent is obtained for Data Principals under 18; behavioural tracking is disabled.\\n4. **Data Principal Rights** — Rights to access, correction, erasure, grievance redressal and nomination are exercisable via a self-service portal with a 30-day SLA.\\n5. **Cross-Border Transfers** — Foreign sub-processors are inventoried with country and contractual safeguards.\\n6. **Retention** — Retention is governed by the Data Retention Policy on the basis of: **statutory + academic record**.\\n7. **Security** — Encryption, access control and breach notification per the Information Security Policy.\\n8. **Breach Notification** — The Data Protection Board of India and affected Data Principals will be notified within prescribed timelines.\\n\\n## 5. Data Principal Contact\\n- **Grievance Officer / DPO:** dpo@rajasthanuniversityo.edu.in\\n- **Postal:** Office of the Registrar, Rajasthan University of Technology\\n- **Self-service portal:** https://privacy.rajasthan.edu.in (planned)\\n\\n## 6. Definitions\\n\\"Personal Data\\", \\"Data Principal\\", \\"Data Fiduciary\\", \\"Consent\\", \\"Significant Data Fiduciary\\" — as defined under the DPDP Act 2023.\\n\\n## 7. Roles and Responsibilities\\n- **DPO** — Operational accountability.\\n- **Registrar / Dean of Students** — Sponsor.\\n- **Heads of Departments** — Local compliance.\\n\\n## 8. Review\\nAnnually, or following any material change to processing or regulation.\\n\\n## 9. Framework References\\nDPDP_ACT_2023, ISO_27001_2022\\n\\n## 10. Approval\\n| Role | Name | Date |\\n|------|------|------|\\n| Vice-Chancellor | _________________ | _________ |\\n| DPO | _________________ | _________ |\\n", "created_at": "2026-06-05T05:53:10.663471+00:00", "updated_at": "2026-06-05T05:53:10.663471+00:00", "approved_by": null, "policy_type": "privacy", "review_date": null, "effective_date": "2026-06-05T05:53:10.663471+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "intake_answers": {"q1": "All students", "q2": "DPDP", "q3": "3 years", "q4": "DPO"}, "version_number": 1, "is_ai_generated": true}	2026-06-05 05:53:10.777998+00
17a39f9c-b593-4c0d-9580-0376b59970e6	{"id": "17a39f9c-b593-4c0d-9580-0376b59970e6", "title": "Information Security Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "draft", "content_md": "# Information Security Policy\\n\\n**Organization:** Rajasthan University of Technology\\n**Framework Alignment:** ISO 27001:2022 A.5.1\\n**Status:** DRAFT (AI-Generated)\\n**Version:** 1.0\\n**Effective Date:** 2026-06-05\\n\\n## 1. Purpose\\nEstablish baseline requirements for protection of the confidentiality, integrity and availability of institutional information assets.\\n\\n## 2. Scope\\nThis policy applies to all employees, contractors, students, vendors and any third party with access to institutional information assets.\\n\\n## 3. Definitions\\n- **Personal Data** as defined under the DPDP Act 2023.\\n- **Information Asset** any data, document or system that supports institutional operations.\\n\\n## 4. Policy Statements\\n1. Information shall be classified per its sensitivity and protected with controls commensurate with risk.\\n2. Access to information systems shall be granted on a least-privilege basis with quarterly access reviews.\\n3. All systems shall log security-relevant events to a central log aggregator with 12-month retention.\\n4. Backups shall be performed daily, encrypted, and restore-tested at least quarterly.\\n5. Cryptographic controls shall comply with NIST SP 800-175B.\\n\\n## 5. Roles and Responsibilities\\n- **CISO** – Accountable for implementation and effectiveness.\\n- **DPO** – Responsible for privacy aspects.\\n- **Department Heads** – Responsible for compliance within their unit.\\n- **All Personnel** – Required to comply.\\n\\n## 6. Compliance and Enforcement\\nViolations may result in disciplinary action up to and including termination.\\n\\n## 7. Review\\nThis policy will be reviewed annually or upon significant change.\\n\\n## 8. Framework References\\nDPDP_ACT_2023, ISO_27001_2022\\n\\n## 9. Approval\\n| Role | Name | Date |\\n|------|------|------|\\n| Vice-Chancellor | _________ | _________ |\\n| CISO | _________ | _________ |\\n", "created_at": "2026-06-05T05:55:45.230156+00:00", "updated_at": "2026-06-05T05:55:45.230156+00:00", "approved_by": null, "policy_type": "information_security", "review_date": null, "effective_date": "2026-06-05T05:55:45.230156+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "version_number": 1, "is_ai_generated": true}	2026-06-05 05:55:45.343879+00
0e0deeb4-7b8c-4c24-9334-ce93c0574b25	{"id": "0e0deeb4-7b8c-4c24-9334-ce93c0574b25", "title": "Privacy Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "draft", "content_md": "# Privacy Policy\\n\\n**Organization:** Rajasthan University of Technology\\n**Framework Alignment:** DPDP Act 2023 Section 5 (Notice)\\n**Status:** DRAFT (AI-Generated)\\n**Version:** 1.0\\n**Effective Date:** 2026-06-05\\n\\n## 1. Purpose\\nInform Data Principals (students, faculty, staff, alumni) of how the institution processes personal data in compliance with the DPDP Act 2023.\\n\\n## 2. Scope\\nThis policy applies to all employees, contractors, students, vendors and any third party with access to institutional information assets.\\n\\n## 3. Definitions\\n- **Personal Data** as defined under the DPDP Act 2023.\\n- **Information Asset** any data, document or system that supports institutional operations.\\n\\n## 4. Policy Statements\\n1. Personal data is processed only on the basis of consent or legitimate use under Section 7.\\n2. A privacy notice is published in English and the languages listed in the Eighth Schedule.\\n3. Data Principals may exercise rights of access, correction, erasure and grievance redressal via the published DPO contact.\\n4. Cross-border transfers are documented with appropriate safeguards.\\n5. Children's data is processed only with verifiable parental consent.\\n\\n## 5. Roles and Responsibilities\\n- **CISO** – Accountable for implementation and effectiveness.\\n- **DPO** – Responsible for privacy aspects.\\n- **Department Heads** – Responsible for compliance within their unit.\\n- **All Personnel** – Required to comply.\\n\\n## 6. Compliance and Enforcement\\nViolations may result in disciplinary action up to and including termination.\\n\\n## 7. Review\\nThis policy will be reviewed annually or upon significant change.\\n\\n## 8. Framework References\\nDPDP_ACT_2023, ISO_27001_2022\\n\\n## 9. Approval\\n| Role | Name | Date |\\n|------|------|------|\\n| Vice-Chancellor | _________ | _________ |\\n| CISO | _________ | _________ |\\n", "created_at": "2026-06-05T05:55:47.922191+00:00", "updated_at": "2026-06-05T05:55:47.922191+00:00", "approved_by": null, "policy_type": "privacy", "review_date": null, "effective_date": "2026-06-05T05:55:47.922191+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "version_number": 1, "is_ai_generated": true}	2026-06-05 05:55:48.035851+00
2ac3c510-c089-4a66-b06f-0244432c343a	{"id": "2ac3c510-c089-4a66-b06f-0244432c343a", "title": "Incident Response Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "draft", "content_md": "# Incident Response Policy\\n\\n**Organization:** Rajasthan University of Technology\\n**Framework Alignment:** ISO 27001 A.5.24 / NIST RS.MA-01 / DPDP S.8(6)\\n**Status:** DRAFT (AI-Generated)\\n**Version:** 1.0\\n**Effective Date:** 2026-06-05\\n\\n## 1. Purpose\\nDefine how the institution prepares for, detects, responds to and recovers from information security incidents.\\n\\n## 2. Scope\\nThis policy applies to all employees, contractors, students, vendors and any third party with access to institutional information assets.\\n\\n## 3. Definitions\\n- **Personal Data** as defined under the DPDP Act 2023.\\n- **Information Asset** any data, document or system that supports institutional operations.\\n\\n## 4. Policy Statements\\n1. An Incident Response Team led by the CISO is on call 24x7.\\n2. All incidents are triaged per a documented severity matrix.\\n3. Personal-data breaches are notified to the Data Protection Board within the prescribed time.\\n4. Tabletop exercises are conducted at least annually.\\n5. Post-incident reviews capture lessons learned and corrective actions.\\n\\n## 5. Roles and Responsibilities\\n- **CISO** – Accountable for implementation and effectiveness.\\n- **DPO** – Responsible for privacy aspects.\\n- **Department Heads** – Responsible for compliance within their unit.\\n- **All Personnel** – Required to comply.\\n\\n## 6. Compliance and Enforcement\\nViolations may result in disciplinary action up to and including termination.\\n\\n## 7. Review\\nThis policy will be reviewed annually or upon significant change.\\n\\n## 8. Framework References\\nDPDP_ACT_2023, ISO_27001_2022\\n\\n## 9. Approval\\n| Role | Name | Date |\\n|------|------|------|\\n| Vice-Chancellor | _________ | _________ |\\n| CISO | _________ | _________ |\\n", "created_at": "2026-06-05T05:55:50.594278+00:00", "updated_at": "2026-06-05T05:55:50.594278+00:00", "approved_by": null, "policy_type": "incident_response", "review_date": null, "effective_date": "2026-06-05T05:55:50.594278+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "version_number": 1, "is_ai_generated": true}	2026-06-05 05:55:50.707978+00
331877d4-a969-431d-9cf3-74f10ccd67dd	{"id": "331877d4-a969-431d-9cf3-74f10ccd67dd", "title": "Access Control Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "draft", "content_md": "# Access Control Policy\\n\\n**Organization:** Rajasthan University of Technology\\n**Framework Alignment:** ISO 27001 A.8.3 / NIST PR.AA-01\\n**Status:** DRAFT (AI-Generated)\\n**Version:** 1.0\\n**Effective Date:** 2026-06-05\\n\\n## 1. Purpose\\nGovern the granting, review and revocation of access to information systems and physical facilities.\\n\\n## 2. Scope\\nThis policy applies to all employees, contractors, students, vendors and any third party with access to institutional information assets.\\n\\n## 3. Definitions\\n- **Personal Data** as defined under the DPDP Act 2023.\\n- **Information Asset** any data, document or system that supports institutional operations.\\n\\n## 4. Policy Statements\\n1. Access is granted on a need-to-know and least-privilege basis.\\n2. MFA is enforced for all privileged accounts and remote access.\\n3. Joiner-mover-leaver workflows complete within one business day.\\n4. Privileged access is reviewed quarterly by the system owner.\\n5. Shared accounts are prohibited except for emergency-break-glass accounts under strict logging.\\n\\n## 5. Roles and Responsibilities\\n- **CISO** – Accountable for implementation and effectiveness.\\n- **DPO** – Responsible for privacy aspects.\\n- **Department Heads** – Responsible for compliance within their unit.\\n- **All Personnel** – Required to comply.\\n\\n## 6. Compliance and Enforcement\\nViolations may result in disciplinary action up to and including termination.\\n\\n## 7. Review\\nThis policy will be reviewed annually or upon significant change.\\n\\n## 8. Framework References\\nDPDP_ACT_2023, ISO_27001_2022\\n\\n## 9. Approval\\n| Role | Name | Date |\\n|------|------|------|\\n| Vice-Chancellor | _________ | _________ |\\n| CISO | _________ | _________ |\\n", "created_at": "2026-06-05T05:55:53.261608+00:00", "updated_at": "2026-06-05T05:55:53.261608+00:00", "approved_by": null, "policy_type": "access_control", "review_date": null, "effective_date": "2026-06-05T05:55:53.261608+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "version_number": 1, "is_ai_generated": true}	2026-06-05 05:55:53.375345+00
746b148d-e72c-46dd-b769-e95bed12eb89	{"id": "746b148d-e72c-46dd-b769-e95bed12eb89", "title": "Vendor Risk Management Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "draft", "content_md": "# Vendor Risk Management Policy\\n\\n**Organization:** Rajasthan University of Technology\\n**Framework Alignment:** DPDP S.8(7) / ISO 27001 A.5.19\\n**Status:** DRAFT (AI-Generated)\\n**Version:** 1.0\\n**Effective Date:** 2026-06-05\\n\\n## 1. Purpose\\nGovern security and privacy risk arising from third-party suppliers and SaaS providers.\\n\\n## 2. Scope\\nThis policy applies to all employees, contractors, students, vendors and any third party with access to institutional information assets.\\n\\n## 3. Definitions\\n- **Personal Data** as defined under the DPDP Act 2023.\\n- **Information Asset** any data, document or system that supports institutional operations.\\n\\n## 4. Policy Statements\\n1. All suppliers handling personal data must execute a Data Processing Agreement.\\n2. Critical suppliers are assessed annually using a documented questionnaire.\\n3. Sub-processors are inventoried and require prior written approval.\\n4. Contracts include audit rights, breach-notification SLAs and data return / destruction obligations.\\n\\n## 5. Roles and Responsibilities\\n- **CISO** – Accountable for implementation and effectiveness.\\n- **DPO** – Responsible for privacy aspects.\\n- **Department Heads** – Responsible for compliance within their unit.\\n- **All Personnel** – Required to comply.\\n\\n## 6. Compliance and Enforcement\\nViolations may result in disciplinary action up to and including termination.\\n\\n## 7. Review\\nThis policy will be reviewed annually or upon significant change.\\n\\n## 8. Framework References\\nDPDP_ACT_2023, ISO_27001_2022\\n\\n## 9. Approval\\n| Role | Name | Date |\\n|------|------|------|\\n| Vice-Chancellor | _________ | _________ |\\n| CISO | _________ | _________ |\\n", "created_at": "2026-06-05T05:55:55.930297+00:00", "updated_at": "2026-06-05T05:55:55.930297+00:00", "approved_by": null, "policy_type": "vendor_risk", "review_date": null, "effective_date": "2026-06-05T05:55:55.930297+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "version_number": 1, "is_ai_generated": true}	2026-06-05 05:55:56.044023+00
1e4b8fa6-4760-4dc0-a970-7ef6fcb68a64	{"id": "1e4b8fa6-4760-4dc0-a970-7ef6fcb68a64", "title": "Data Retention Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "draft", "content_md": "# Data Retention Policy\\n\\n**Organization:** Rajasthan University of Technology\\n**Framework Alignment:** DPDP S.8(7), S.12\\n**Status:** DRAFT (AI-Generated)\\n**Version:** 1.0\\n**Effective Date:** 2026-06-05\\n\\n## 1. Purpose\\nDefine retention periods and disposal mechanisms for personal data across institutional systems.\\n\\n## 2. Scope\\nThis policy applies to all employees, contractors, students, vendors and any third party with access to institutional information assets.\\n\\n## 3. Definitions\\n- **Personal Data** as defined under the DPDP Act 2023.\\n- **Information Asset** any data, document or system that supports institutional operations.\\n\\n## 4. Policy Statements\\n1. Student records are retained for 5 years post-graduation unless statutory law requires longer.\\n2. Applicant records are deleted within 6 months of admission cycle close, unless converted to enrolment.\\n3. CCTV footage is retained for 30 days unless preserved by legal hold.\\n4. Erasure on withdrawal of consent is completed within 30 days.\\n\\n## 5. Roles and Responsibilities\\n- **CISO** – Accountable for implementation and effectiveness.\\n- **DPO** – Responsible for privacy aspects.\\n- **Department Heads** – Responsible for compliance within their unit.\\n- **All Personnel** – Required to comply.\\n\\n## 6. Compliance and Enforcement\\nViolations may result in disciplinary action up to and including termination.\\n\\n## 7. Review\\nThis policy will be reviewed annually or upon significant change.\\n\\n## 8. Framework References\\nDPDP_ACT_2023, ISO_27001_2022\\n\\n## 9. Approval\\n| Role | Name | Date |\\n|------|------|------|\\n| Vice-Chancellor | _________ | _________ |\\n| CISO | _________ | _________ |\\n", "created_at": "2026-06-05T05:55:58.602297+00:00", "updated_at": "2026-06-05T05:55:58.602297+00:00", "approved_by": null, "policy_type": "data_retention", "review_date": null, "effective_date": "2026-06-05T05:55:58.602297+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "version_number": 1, "is_ai_generated": true}	2026-06-05 05:55:58.715991+00
f4b810bc-b183-42d8-b286-c5743afaf037	{"id": "f4b810bc-b183-42d8-b286-c5743afaf037", "title": "Test policy for approval", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "approved", "content_md": "# stub", "created_at": "2026-06-07T13:29:45.074735+00:00", "updated_at": "2026-06-07T13:29:50.920112+00:00", "approved_at": "2026-06-07T13:29:50.920112+00:00", "approved_by": null, "policy_type": "info_security", "review_date": null, "approved_by_id": "5b27c9dc-8ed6-4cb0-b255-b75b8e09bbf9", "effective_date": "2026-06-07T13:29:45.074735+00:00", "framework_refs": [], "version_number": 1, "is_ai_generated": false, "approved_by_email": "reviewer@rut.edu.in"}	2026-06-07 13:29:45.187899+00
85c8c27a-0dd7-4260-bb1e-86f764738c62	{"id": "85c8c27a-0dd7-4260-bb1e-86f764738c62", "title": "OrgB Policy", "org_id": "7bab9ff2-c2fd-4dc2-b0c2-6ec6bd8bf129", "status": "draft", "content_md": "# OrgB only", "created_at": "2026-06-07T13:42:47.143124+00:00", "updated_at": "2026-06-07T13:42:47.143124+00:00", "policy_type": "information_security", "framework_refs": [], "version_number": 1}	2026-06-07 13:42:56.395226+00
9d5f8a67-2953-4da9-831d-9730bb151317	{"id": "9d5f8a67-2953-4da9-831d-9730bb151317", "title": "Test policy for approval", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "approved", "content_md": "# stub", "created_at": "2026-06-07T13:44:29.346108+00:00", "updated_at": "2026-06-07T13:44:35.173493+00:00", "approved_at": "2026-06-07T13:44:35.173493+00:00", "approved_by": null, "policy_type": "info_security", "review_date": null, "approved_by_id": "5b27c9dc-8ed6-4cb0-b255-b75b8e09bbf9", "effective_date": "2026-06-07T13:44:29.346108+00:00", "framework_refs": [], "version_number": 1, "is_ai_generated": false, "approved_by_email": "reviewer@rut.edu.in"}	2026-06-07 13:44:29.459916+00
66df77ba-b1ac-4a50-a6c6-f5a04431b623	{"id": "66df77ba-b1ac-4a50-a6c6-f5a04431b623", "title": "Information Security Policy", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "draft", "ai_model": "intake-template-v1", "content_md": "# Information Security Policy\\n\\n**Organization:** Rajasthan University of Technology\\n**Framework Alignment:** ISO/IEC 27001:2022 Clause 5.2 · DPDP_ACT_2023, ISO_27001_2022\\n**Status:** Draft\\n**Version:** 1.0  ·  **Effective Date:** 2026-06-07\\n\\n## 1. Purpose\\nThis policy establishes the Rajasthan University of Technology's commitment to protecting the confidentiality, integrity and availability of all information assets in scope: **all institutional systems and departments**.\\n\\n## 2. Scope\\nThis policy applies to: **all institutional systems and departments**. It governs all employees, students, contractors and third parties who access institutional information.\\n\\n## 3. Risk Appetite\\nThe Governing Council has declared a **moderate** risk appetite for cybersecurity. Decisions affecting risk posture shall be made against this benchmark.\\n\\n## 4. Regulatory Drivers\\nThis policy is informed by: **DPDP Act 2023, UGC IT guidelines, CERT-In**.\\n\\n## 5. Policy Statements\\n1. **Information Classification** — All information shall be classified as Public, Internal, Confidential or Restricted and handled per the classification scheme.\\n2. **Access Control** — Access shall be granted on a least-privilege basis with quarterly reviews by system owners.\\n3. **Cryptography** — Data-in-transit shall use TLS 1.2 or higher; data-at-rest containing personal data shall be encrypted using AES-256.\\n4. **Backups** — Critical systems shall be backed up daily, encrypted, and restore-tested at least quarterly.\\n5. **Vulnerability Management** — Internet-facing systems shall be scanned monthly; criticals patched within 14 days.\\n6. **Awareness Training** — All personnel shall complete annual security awareness training; completion ≥ 90% is mandatory.\\n7. **Incident Response** — Security incidents shall be reported within 1 hour; the Incident Response Policy governs subsequent actions.\\n8. **Supplier Security** — All suppliers handling personal data shall execute a DPA aligned to DPDP Act 2023 Section 8(7).\\n9. **Continuous Monitoring** — A SIEM (or equivalent log aggregator) shall be operational with 12-month retention.\\n10. **Policy Exceptions** — Exceptions require CISO sign-off, are time-bound, and recorded in the exceptions register.\\n\\n## 6. Roles and Responsibilities\\n- **Vice-Chancellor / Governing Council** — Accountable for institutional risk posture.\\n- **CISO / Information Security Officer** — Owns implementation and operations.\\n- **Department Heads** — Responsible for compliance within their units.\\n- **All Personnel** — Required to comply and report incidents.\\n\\n## 7. Compliance and Enforcement\\nViolations may result in disciplinary action up to and including termination of employment or expulsion. Suspected criminal violations will be referred to the appropriate authorities.\\n\\n## 8. Review\\nThis policy shall be reviewed **annual** by the Information Security Committee or following any significant security incident.\\n\\n## 9. Framework References\\nDPDP_ACT_2023, ISO_27001_2022\\n\\n## 10. Institutional Intake\\nThe following intake was captured during drafting:\\n- **Scope:** all institutional systems and departments\\n- **Risk Appetite:** moderate\\n- **Regulatory Drivers:** DPDP Act 2023, UGC IT guidelines, CERT-In\\n- **Review Cycle:** annual\\n\\n## 11. Approval\\n| Role | Name | Date |\\n|------|------|------|\\n| Vice-Chancellor | _________________ | _________ |\\n| Registrar | _________________ | _________ |\\n| CISO | _________________ | _________ |\\n", "created_at": "2026-06-07T18:26:03.694267+00:00", "updated_at": "2026-06-07T18:26:03.694267+00:00", "approved_by": null, "policy_type": "information_security", "review_date": null, "effective_date": "2026-06-07T18:26:03.694267+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"], "intake_answers": {}, "version_number": 1, "is_ai_generated": true}	2026-06-07 18:26:03.767255+00
\.


--
-- Data for Name: policy_approvals; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.policy_approvals (id, data, created_at) FROM stdin;
\.


--
-- Data for Name: policy_sessions; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.policy_sessions (id, data, created_at) FROM stdin;
88c6f763-ac94-4a0f-876b-4fb563402196	{"id": "88c6f763-ac94-4a0f-876b-4fb563402196", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "finalized", "answers": {"q1": "All students", "q2": "DPDP", "q3": "3 years", "q4": "DPO"}, "used_ai": false, "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "policy_id": "b3217cb3-8159-4b97-8883-d180d5003d43", "questions": [{"id": "data_categories", "question": "Which categories of personal data do you process? (student PII, biometric, health, financial)"}, {"id": "languages", "question": "Which languages does your privacy notice need to be available in? (e.g., 'English, Hindi, Marathi')"}, {"id": "dpo_contact", "question": "Designated DPO contact email / office?"}, {"id": "retention_basis", "question": "Primary retention basis: statutory (UGC/AICTE), academic record, or alumni engagement?"}], "created_at": "2026-06-05T05:53:07.212800+00:00", "policy_type": "privacy", "finalized_at": "2026-06-05T05:53:10.663471+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"]}	2026-06-05 05:53:07.327266+00
c914b177-a05b-4ead-bae6-5cf2c569976d	{"id": "c914b177-a05b-4ead-bae6-5cf2c569976d", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "intake", "answers": {}, "user_id": "56ba859d-20d6-4470-974f-33d3165c9833", "questions": [{"id": "scope", "question": "Which systems / departments should be in scope? (e.g., 'ERP, LMS, IT, Examination, Library')"}, {"id": "risk_appetite", "question": "What is your institution's risk appetite: low, moderate, or high?"}, {"id": "regulatory_drivers", "question": "Any specific regulatory drivers beyond DPDP and ISO? (UGC IT cell guidelines, CERT-In, etc.)"}, {"id": "review_cycle", "question": "Annual or biennial review cycle?"}], "created_at": "2026-06-05T06:39:32.653338+00:00", "policy_type": "data_protection", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"]}	2026-06-05 06:39:32.767549+00
6d0a7a6e-bf45-48f0-a071-0b11d86df748	{"id": "6d0a7a6e-bf45-48f0-a071-0b11d86df748", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "intake", "answers": {}, "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "questions": [{"id": "scope", "question": "Which systems / departments should be in scope? (e.g., 'ERP, LMS, IT, Examination, Library')"}, {"id": "risk_appetite", "question": "What is your institution's risk appetite: low, moderate, or high?"}, {"id": "regulatory_drivers", "question": "Any specific regulatory drivers beyond DPDP and ISO? (UGC IT cell guidelines, CERT-In, etc.)"}, {"id": "review_cycle", "question": "Annual or biennial review cycle?"}], "created_at": "2026-06-07T15:27:00.839454+00:00", "policy_type": "information_security", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"]}	2026-06-07 15:27:00.952436+00
ac96bf03-0c7e-45d1-b84d-6920a04290eb	{"id": "ac96bf03-0c7e-45d1-b84d-6920a04290eb", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "finalized", "answers": {}, "used_ai": false, "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "policy_id": "66df77ba-b1ac-4a50-a6c6-f5a04431b623", "questions": [{"id": "scope", "question": "Which systems / departments should be in scope? (e.g., 'ERP, LMS, IT, Examination, Library')"}, {"id": "risk_appetite", "question": "What is your institution's risk appetite: low, moderate, or high?"}, {"id": "regulatory_drivers", "question": "Any specific regulatory drivers beyond DPDP and ISO? (UGC IT cell guidelines, CERT-In, etc.)"}, {"id": "review_cycle", "question": "Annual or biennial review cycle?"}], "created_at": "2026-06-07T18:25:55.162999+00:00", "policy_type": "information_security", "finalized_at": "2026-06-07T18:26:03.694267+00:00", "framework_refs": ["DPDP_ACT_2023", "ISO_27001_2022"]}	2026-06-07 18:25:55.224006+00
\.


--
-- Data for Name: policy_versions; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.policy_versions (id, data, created_at) FROM stdin;
a3dd5b6f-089e-4750-b975-46f7ec429083	{"id": "a3dd5b6f-089e-4750-b975-46f7ec429083", "policy_id": "4465c968-03c8-4553-9ce8-9db59d03c14f", "changed_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "content_md": "# Information Security Policy\\n\\n## Purpose\\nThis policy establishes baseline requirements for information_security.\\n\\n## Scope\\nAll personnel, students, contractors and systems of the University.\\n\\n## Policy Statements\\n1. The University commits to protecting personal data per the DPDP Act 2023.\\n2. Information security is governed by ISO/IEC 27001:2022.\\n\\n## Roles and Responsibilities\\nCISO is accountable. DPO is responsible.\\n\\n## Review\\nReviewed annually by the Information Security Committee.\\n", "created_at": "2026-06-05T05:43:25.958778+00:00", "change_summary": "Edit", "version_number": 1}	2026-06-05 05:43:26.074039+00
970aa24b-1997-4591-91a7-7cc77ed37b02	{"id": "970aa24b-1997-4591-91a7-7cc77ed37b02", "policy_id": "9523ab29-9134-4684-a082-c056777c9ba0", "changed_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "content_md": "# Privacy Policy (DPDP)\\n\\n## Purpose\\nThis policy establishes baseline requirements for privacy.\\n\\n## Scope\\nAll personnel, students, contractors and systems of the University.\\n\\n## Policy Statements\\n1. The University commits to protecting personal data per the DPDP Act 2023.\\n2. Information security is governed by ISO/IEC 27001:2022.\\n\\n## Roles and Responsibilities\\nCISO is accountable. DPO is responsible.\\n\\n## Review\\nReviewed annually by the Information Security Committee.\\n", "created_at": "2026-06-05T05:56:02.850703+00:00", "change_summary": "Edit", "version_number": 1}	2026-06-05 05:56:02.964472+00
\.


--
-- Data for Name: remediation_tasks; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.remediation_tasks (id, data, created_at) FROM stdin;
cfd75f61-f010-4bb7-b9ae-a9471becec7a	{"id": "cfd75f61-f010-4bb7-b9ae-a9471becec7a", "notes": "", "title": "Remediate: Backup restore not tested in last 12 months", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "in_progress", "due_date": "2026-07-20T05:32:16.070051+00:00", "priority": "high", "created_at": "2026-06-05T05:30:58.695838+00:00", "finding_id": "483ab799-7684-4be7-a8a4-a1b7c3f95468", "updated_at": "2026-06-05T05:30:58.695838+00:00", "assigned_to": null, "completion_evidence": null}	2026-06-05 05:32:16.184258+00
414ce5b4-f7dc-4f9d-85b3-81d726e54537	{"id": "414ce5b4-f7dc-4f9d-85b3-81d726e54537", "notes": "", "title": "Remediate: Vendor risk assessments outdated", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "todo", "due_date": "2026-07-20T05:32:17.378822+00:00", "priority": "high", "created_at": "2026-06-05T05:30:58.695838+00:00", "finding_id": "fabb829a-a85a-482c-a376-9bfce10ab7ed", "updated_at": "2026-06-05T05:30:58.695838+00:00", "assigned_to": null, "completion_evidence": null}	2026-06-05 05:32:17.492962+00
fb338ed9-0795-4107-ad3a-c352476fdcad	{"id": "fb338ed9-0795-4107-ad3a-c352476fdcad", "notes": "", "title": "Remediate: Awareness training completion under 60%", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "todo", "due_date": "2026-07-20T05:32:18.687796+00:00", "priority": "medium", "created_at": "2026-06-05T05:30:58.695838+00:00", "finding_id": "12470fd0-ed30-4e98-ac5d-b74d5092e7b7", "updated_at": "2026-06-05T05:30:58.695838+00:00", "assigned_to": null, "completion_evidence": null}	2026-06-05 05:32:18.802101+00
f82e42e8-78e1-4fdd-9f6f-c4f04a152e17	{"id": "f82e42e8-78e1-4fdd-9f6f-c4f04a152e17", "notes": "", "title": "Remediate: No documented DPDP consent management workflow", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "in_progress", "due_date": "2026-07-20T05:32:13.448017+00:00", "priority": "critical", "created_at": "2026-06-05T05:30:58.695838+00:00", "finding_id": "335a6d5b-8039-4754-a9c7-fc2bb6953b38", "updated_at": "2026-06-05T05:42:59.342066+00:00", "assigned_to": null, "completion_evidence": null}	2026-06-05 05:32:13.562227+00
b76995cc-42d1-4307-aa0c-d53dcc8918e1	{"id": "b76995cc-42d1-4307-aa0c-d53dcc8918e1", "notes": "", "title": "Remediate: Privileged accounts without MFA on ERP", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "in_progress", "due_date": "2026-07-20T05:32:14.761630+00:00", "priority": "critical", "created_at": "2026-06-05T05:30:58.695838+00:00", "finding_id": "8359f7f0-036b-40c7-a43c-042cfe17ceda", "updated_at": "2026-06-05T05:55:34.515043+00:00", "assigned_to": null, "completion_evidence": null}	2026-06-05 05:32:14.875825+00
06697087-3b70-44b1-9fc1-4a01b5490022	{"id": "06697087-3b70-44b1-9fc1-4a01b5490022", "title": "OrgB Task", "org_id": "7bab9ff2-c2fd-4dc2-b0c2-6ec6bd8bf129", "status": "todo", "priority": "medium", "created_at": "2026-06-07T13:42:47.143124+00:00", "updated_at": "2026-06-07T13:42:47.143124+00:00", "assigned_to": "0c272a62-9d99-4461-a4ef-c5545f1bdf77"}	2026-06-07 13:42:57.725071+00
\.


--
-- Data for Name: risk_treatments; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.risk_treatments (id, data, created_at) FROM stdin;
f372080c-1e0d-486b-b657-cdf00e3b884e	{"id": "f372080c-1e0d-486b-b657-cdf00e3b884e", "status": "planned", "risk_id": "6adc9487-0bd8-4243-8e46-039240b77172", "due_date": null, "created_at": "2026-06-05T05:47:33.127259+00:00", "updated_at": "2026-06-05T05:47:33.127259+00:00", "description": "TEST", "cost_estimate": 0.0, "treatment_type": "mitigate"}	2026-06-05 05:47:33.240602+00
1d8b312a-56b7-4f87-be84-5451007c6d74	{"id": "1d8b312a-56b7-4f87-be84-5451007c6d74", "status": "planned", "risk_id": "1f147371-9490-406d-96ef-8faeebe4190f", "due_date": null, "created_at": "2026-06-05T05:55:16.518669+00:00", "updated_at": "2026-06-05T05:55:16.518669+00:00", "description": "TEST", "cost_estimate": 0.0, "treatment_type": "mitigate"}	2026-06-05 05:55:16.632586+00
\.


--
-- Data for Name: risks; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.risks (id, data, created_at) FROM stdin;
b72c66f7-c3c0-4ed7-8a0c-430eb33923f0	{"id": "b72c66f7-c3c0-4ed7-8a0c-430eb33923f0", "title": "Student SIS data breach via SQL injection", "impact": 5, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "technical", "owner_id": null, "created_at": "2026-06-05T05:30:58.695838+00:00", "department": "IT", "likelihood": 3, "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Student SIS data breach via SQL injection", "review_date": "2026-09-03T05:31:59.693267+00:00", "inherent_score": 15, "residual_score": 8.25, "treatment_plan": "Apply layered controls and quarterly review."}	2026-06-05 05:31:59.807612+00
03e92135-03f9-4098-92a7-42cf12ac9561	{"id": "03e92135-03f9-4098-92a7-42cf12ac9561", "title": "Ransomware on academic file servers", "impact": 5, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "technical", "owner_id": null, "created_at": "2026-06-05T05:30:58.695838+00:00", "department": "IT", "likelihood": 3, "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Ransomware on academic file servers", "review_date": "2026-09-03T05:32:00.350222+00:00", "inherent_score": 15, "residual_score": 8.25, "treatment_plan": "Apply layered controls and quarterly review."}	2026-06-05 05:32:00.464396+00
5bbb6cf9-c7cb-4b01-9ea2-6a07273c12a5	{"id": "5bbb6cf9-c7cb-4b01-9ea2-6a07273c12a5", "title": "Third-party LMS vendor data leak", "impact": 4, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "operational", "owner_id": null, "created_at": "2026-06-05T05:30:58.695838+00:00", "department": "Academic", "likelihood": 2, "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Third-party LMS vendor data leak", "review_date": "2026-09-03T05:32:01.004331+00:00", "inherent_score": 8, "residual_score": 4.4, "treatment_plan": "Apply layered controls and quarterly review."}	2026-06-05 05:32:01.118505+00
3d41f1ee-4aaf-494b-8823-7b447a4fcb87	{"id": "3d41f1ee-4aaf-494b-8823-7b447a4fcb87", "title": "Research data theft (USB exfiltration)", "impact": 5, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "operational", "owner_id": null, "created_at": "2026-06-05T05:30:58.695838+00:00", "department": "Research", "likelihood": 2, "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Research data theft (USB exfiltration)", "review_date": "2026-09-03T05:32:01.658782+00:00", "inherent_score": 10, "residual_score": 5.5, "treatment_plan": "Apply layered controls and quarterly review."}	2026-06-05 05:32:01.772971+00
65327b78-a177-4df0-a786-b252301fae47	{"id": "65327b78-a177-4df0-a786-b252301fae47", "title": "Faculty payroll exposure (HR share drive)", "impact": 3, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "operational", "owner_id": null, "created_at": "2026-06-05T05:30:58.695838+00:00", "department": "HR", "likelihood": 2, "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Faculty payroll exposure (HR share drive)", "review_date": "2026-09-03T05:32:02.312876+00:00", "inherent_score": 6, "residual_score": 3.3, "treatment_plan": "Apply layered controls and quarterly review."}	2026-06-05 05:32:02.427072+00
55ca587c-9bdc-42d6-9eca-ba172a98fdb5	{"id": "55ca587c-9bdc-42d6-9eca-ba172a98fdb5", "title": "Phishing-led account takeover", "impact": 3, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "technical", "owner_id": null, "created_at": "2026-06-05T05:30:58.695838+00:00", "department": "IT", "likelihood": 4, "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Phishing-led account takeover", "review_date": "2026-09-03T05:32:02.967782+00:00", "inherent_score": 12, "residual_score": 6.6, "treatment_plan": "Apply layered controls and quarterly review."}	2026-06-05 05:32:03.082165+00
7375f871-c7a1-4e21-baad-a4dde6b2463a	{"id": "7375f871-c7a1-4e21-baad-a4dde6b2463a", "title": "Hostel CCTV footage retention violation", "impact": 3, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "legal", "owner_id": null, "created_at": "2026-06-05T05:30:58.695838+00:00", "department": "Hostel", "likelihood": 3, "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Hostel CCTV footage retention violation", "review_date": "2026-09-03T05:32:03.621904+00:00", "inherent_score": 9, "residual_score": 4.95, "treatment_plan": "Apply layered controls and quarterly review."}	2026-06-05 05:32:03.736117+00
e1d105de-6e98-4746-8c02-b44ff82f750d	{"id": "e1d105de-6e98-4746-8c02-b44ff82f750d", "title": "Cloud data sovereignty (foreign-hosted LMS)", "impact": 4, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "in_treatment", "category": "legal", "owner_id": null, "created_at": "2026-06-05T05:30:58.695838+00:00", "department": "Academic", "likelihood": 3, "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Cloud data sovereignty (foreign-hosted LMS)", "review_date": "2026-09-03T05:32:04.275936+00:00", "inherent_score": 12, "residual_score": 6.6, "treatment_plan": "Apply layered controls and quarterly review."}	2026-06-05 05:32:04.390306+00
cce29914-e9c4-4d97-8ac4-63d4b0ac1639	{"id": "cce29914-e9c4-4d97-8ac4-63d4b0ac1639", "title": "Accreditation evidence integrity (NAAC)", "impact": 5, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "reputational", "owner_id": null, "created_at": "2026-06-05T05:30:58.695838+00:00", "department": "IQAC", "likelihood": 2, "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Accreditation evidence integrity (NAAC)", "review_date": "2026-09-03T05:32:04.930244+00:00", "inherent_score": 10, "residual_score": 5.5, "treatment_plan": "Apply layered controls and quarterly review."}	2026-06-05 05:32:05.044386+00
c0c8efa9-6628-4a34-95eb-49201ba78bc1	{"id": "c0c8efa9-6628-4a34-95eb-49201ba78bc1", "title": "Lost laptop with student grades", "impact": 4, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "operational", "owner_id": null, "created_at": "2026-06-05T05:30:58.695838+00:00", "department": "Examination", "likelihood": 3, "updated_at": "2026-06-05T05:30:58.695838+00:00", "description": "Lost laptop with student grades", "review_date": "2026-09-03T05:32:05.584836+00:00", "inherent_score": 12, "residual_score": 6.6, "treatment_plan": "Apply layered controls and quarterly review."}	2026-06-05 05:32:05.699067+00
2d649450-863b-480f-8093-e560e275c1e5	{"id": "2d649450-863b-480f-8093-e560e275c1e5", "title": "Test PG migration risk", "impact": 4, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "technical", "owner_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T05:33:42.546468+00:00", "department": "IT", "likelihood": 3, "updated_at": "2026-06-05T05:33:42.546468+00:00", "description": "Verify writes work", "review_date": null, "inherent_score": 12, "residual_score": 6.6, "treatment_plan": null}	2026-06-05 05:33:42.660706+00
823b0e0a-cc55-468e-9beb-0702f544a746	{"id": "823b0e0a-cc55-468e-9beb-0702f544a746", "title": "TEST Risk 1780638156", "impact": 3, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "operational", "owner_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T05:42:37.237552+00:00", "department": "IT", "likelihood": 2, "updated_at": "2026-06-05T05:42:41.237774+00:00", "description": "test risk", "review_date": null, "inherent_score": 6, "residual_score": 3.3, "treatment_plan": null}	2026-06-05 05:42:37.35243+00
6adc9487-0bd8-4243-8e46-039240b77172	{"id": "6adc9487-0bd8-4243-8e46-039240b77172", "title": "TEST Risk 1780638444", "impact": 3, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "operational", "owner_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T05:47:24.975769+00:00", "department": "IT", "likelihood": 2, "updated_at": "2026-06-05T05:47:28.944117+00:00", "description": "test risk", "review_date": null, "inherent_score": 6, "residual_score": 3.3, "treatment_plan": null}	2026-06-05 05:47:25.089132+00
1f147371-9490-406d-96ef-8faeebe4190f	{"id": "1f147371-9490-406d-96ef-8faeebe4190f", "title": "TEST Risk 1780638907", "impact": 3, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "operational", "owner_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-05T05:55:08.323981+00:00", "department": "IT", "likelihood": 2, "updated_at": "2026-06-05T05:55:12.304744+00:00", "description": "test risk", "review_date": null, "inherent_score": 6, "residual_score": 3.3, "treatment_plan": null}	2026-06-05 05:55:08.437876+00
f2b65dac-9c4e-4f0e-88a7-58645c77ec53	{"id": "f2b65dac-9c4e-4f0e-88a7-58645c77ec53", "title": "RBAC test risk", "impact": 2, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "technical", "owner_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T13:25:04.370166+00:00", "department": null, "likelihood": 2, "updated_at": "2026-06-07T13:25:04.370166+00:00", "description": "x", "review_date": null, "inherent_score": 4, "residual_score": 2.2, "treatment_plan": null}	2026-06-07 13:25:04.483922+00
19e798f3-42c4-4b4a-9b85-1aecce5dca6e	{"id": "19e798f3-42c4-4b4a-9b85-1aecce5dca6e", "title": "RBAC test risk", "impact": 2, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "technical", "owner_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T13:29:39.270589+00:00", "department": null, "likelihood": 2, "updated_at": "2026-06-07T13:29:39.270589+00:00", "description": "x", "review_date": null, "inherent_score": 4, "residual_score": 2.2, "treatment_plan": null}	2026-06-07 13:29:39.383758+00
2cb74fbf-e457-426d-a62d-d08b562ef98f	{"id": "2cb74fbf-e457-426d-a62d-d08b562ef98f", "title": "OrgB Risk", "impact": 3, "org_id": "7bab9ff2-c2fd-4dc2-b0c2-6ec6bd8bf129", "status": "open", "category": "technical", "owner_id": "0c272a62-9d99-4461-a4ef-c5545f1bdf77", "created_at": "2026-06-07T13:42:47.143124+00:00", "department": "OrgBDept", "likelihood": 3, "updated_at": "2026-06-07T13:42:47.143124+00:00", "description": "Org B only", "inherent_score": 9, "residual_score": 4.95}	2026-06-07 13:42:55.064926+00
1cb5dea0-fa17-4bc2-8ba4-64b4aec14b30	{"id": "1cb5dea0-fa17-4bc2-8ba4-64b4aec14b30", "title": "RBAC test risk", "impact": 2, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "technical", "owner_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T13:44:23.520044+00:00", "department": null, "likelihood": 2, "updated_at": "2026-06-07T13:44:23.520044+00:00", "description": "x", "review_date": null, "inherent_score": 4, "residual_score": 2.2, "treatment_plan": null}	2026-06-07 13:44:23.633728+00
fdccdb06-a9a4-4e54-9419-0ec9d1eab1eb	{"id": "fdccdb06-a9a4-4e54-9419-0ec9d1eab1eb", "title": "RBAC test risk", "impact": 2, "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "status": "open", "category": "technical", "owner_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "created_at": "2026-06-07T15:41:37.798697+00:00", "department": null, "likelihood": 2, "updated_at": "2026-06-07T15:41:37.798697+00:00", "description": "x", "review_date": null, "inherent_score": 4, "residual_score": 2.2, "treatment_plan": null}	2026-06-07 15:41:37.912564+00
\.


--
-- Data for Name: user_preferences; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.user_preferences (id, data, created_at) FROM stdin;
5b856b8d-369c-40df-976b-34aa47cc6892	{"id": "5b856b8d-369c-40df-976b-34aa47cc6892", "theme": "light", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "user_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "updated_at": "2026-06-17T07:42:45.137348+00:00", "notify_policy_approval": true, "notify_critical_findings": true, "notify_assessment_completed": false}	2026-06-05 05:33:44.645567+00
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.users (id, data, created_at) FROM stdin;
9bfcb16a-1df0-4c93-a69f-9b8f6383feca	{"id": "9bfcb16a-1df0-4c93-a69f-9b8f6383feca", "role": "pending", "email": "sec-test-1@example.com", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Eve", "is_active": true, "created_at": "2026-06-07T13:02:30.072138+00:00", "department": null, "last_login": null, "updated_at": "2026-06-07T13:02:30.072138+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$J2FGMRmgiBmF7PBSNJf/nelyYLb0/Ew79Gm.9kccRayVOgQO/bNTK"}	2026-06-07 13:02:31.056266+00
56ba859d-20d6-4470-974f-33d3165c9833	{"id": "56ba859d-20d6-4470-974f-33d3165c9833", "role": "compliance_officer", "email": "ciso@rut.edu.in", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Rohan Kapoor", "is_active": true, "created_at": "2026-06-05T05:30:19.780727+00:00", "department": "IT Security", "last_login": "2026-06-11T09:03:50.020959+00:00", "updated_at": "2026-06-05T05:30:19.780727+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$yXcb5lY7W0yyUbybaVkzG.JmP2f08LoYI3MfsaIoduf0nGMqhhN/2"}	2026-06-05 05:30:23.619948+00
c8f13c16-2605-4395-9f8c-181ab04d48ce	{"id": "c8f13c16-2605-4395-9f8c-181ab04d48ce", "role": "department_reviewer", "email": "library@rut.edu.in", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Kavita Rao", "is_active": true, "created_at": "2026-06-05T06:22:33.049378+00:00", "department": "Library", "last_login": "2026-06-07T15:40:09.009282+00:00", "updated_at": "2026-06-05T06:22:33.049378+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$uftQ4.j2UgiBZhOnJYovceF0vXJ.X/0ppXU6FxH0JhKBUAyF7ZQV6"}	2026-06-05 06:22:40.394151+00
c1875549-56b3-4685-82a6-81580c677006	{"id": "c1875549-56b3-4685-82a6-81580c677006", "role": "auditor", "email": "auditor@rut.edu.in", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Priya Iyer", "is_active": true, "created_at": "2026-06-05T05:30:19.780727+00:00", "department": "Internal Audit", "last_login": "2026-06-07T15:41:14.006260+00:00", "updated_at": "2026-06-05T05:30:19.780727+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$H1bzimhbf3syBH.RmeFYpu.eeN7OjHOhWjqWa92lQ.g7D0TfHqRLS"}	2026-06-05 05:30:25.169401+00
90bd228d-5c5f-4f61-9559-bd1faec1f7e4	{"id": "90bd228d-5c5f-4f61-9559-bd1faec1f7e4", "role": "readonly_assessor", "email": "board@rut.edu.in", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Prof. Sunita Roy", "is_active": true, "created_at": "2026-06-05T06:22:33.049378+00:00", "department": "Board", "last_login": "2026-06-07T15:41:16.452616+00:00", "updated_at": "2026-06-05T06:22:33.049378+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$J.U63tEdaCj3gDMm.WkcDOrPyGn/jQMxA9dKRl5C3tl18sswfokXO"}	2026-06-05 06:22:45.643598+00
13af9ac1-05d8-4a26-b4d7-d587b124a727	{"id": "13af9ac1-05d8-4a26-b4d7-d587b124a727", "role": "institution_admin", "email": "TEST_owner_1780638091@testorg.edu.in", "org_id": "4fbc16aa-81ca-4c32-9a6e-bccdde14ccbb", "full_name": "TEST Owner", "is_active": true, "created_at": "2026-06-05T05:41:32.732831+00:00", "department": null, "last_login": null, "updated_at": "2026-06-05T05:41:32.732831+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$TLNN0Vx7oko03U58ECffkumieEjXE53V7a11C1NV1Fn3vqFwsJgfC"}	2026-06-05 05:41:34.39742+00
5b27c9dc-8ed6-4cb0-b255-b75b8e09bbf9	{"id": "5b27c9dc-8ed6-4cb0-b255-b75b8e09bbf9", "role": "policy_approver", "email": "reviewer@rut.edu.in", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Meera Bhatt", "is_active": true, "created_at": "2026-06-05T05:30:19.780727+00:00", "department": "Quality", "last_login": "2026-06-07T15:41:54.011051+00:00", "updated_at": "2026-06-05T06:22:33.049378+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$Dq9Wf92bnE2vrT/EStmG1u1hthN.7ca.iiaz0.B89N2lOL8/4cNJy"}	2026-06-05 05:30:28.232264+00
2b51dec0-c04e-402a-891a-b742ab090ee2	{"id": "2b51dec0-c04e-402a-891a-b742ab090ee2", "role": "vendor_reviewer", "email": "vendor@rut.edu.in", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Arjun Desai", "is_active": true, "created_at": "2026-06-05T06:22:33.049378+00:00", "department": "Procurement", "last_login": "2026-06-05T06:37:55.264941+00:00", "updated_at": "2026-06-05T06:22:33.049378+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$ElJwhoyFSMK.PYHdx9ThJ.mMccRlHHkxozogl3snT9y/Os1LCOU1a"}	2026-06-05 06:22:41.92685+00
c2131b29-a963-4db6-a10d-b19bd565f8e6	{"id": "c2131b29-a963-4db6-a10d-b19bd565f8e6", "role": "it_security_officer", "email": "itsec@rut.edu.in", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Vikram Singh", "is_active": true, "created_at": "2026-06-05T06:22:33.049378+00:00", "department": "IT", "last_login": "2026-06-05T06:40:05.917826+00:00", "updated_at": "2026-06-05T06:22:33.049378+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$itbQaIWQq31FRNc5MBGETelWzPqw4LU2MSSMyTEPlhfveojBlNkSK"}	2026-06-05 06:22:36.017855+00
439dc834-306a-4057-a852-ebc302f1ff9e	{"id": "439dc834-306a-4057-a852-ebc302f1ff9e", "role": "institution_admin", "email": "TEST_owner_1780638829@testorg.edu.in", "org_id": "83693a6a-5de2-49af-b75b-55efaffaacc0", "full_name": "TEST Owner", "is_active": true, "created_at": "2026-06-05T05:53:50.026932+00:00", "department": null, "last_login": null, "updated_at": "2026-06-05T05:53:50.026932+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$SPqW1UKazwyA.gKtFCLRMeCCSY9QC2hmDU/Avl1Po74PytyHcsshe"}	2026-06-05 05:53:51.679242+00
43ecd490-38ca-4b13-8dbd-96a05a46bb97	{"id": "43ecd490-38ca-4b13-8dbd-96a05a46bb97", "role": "pending", "email": "hacker@example.com", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Eve", "is_active": true, "created_at": "2026-06-07T12:56:19.355957+00:00", "department": null, "last_login": null, "updated_at": "2026-06-07T12:56:19.355957+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$aujlg96UzPGN9ZzxPEfU/OZPF5uoAqYXII8O2VZDlvbRxHjUZZ.YW"}	2026-06-07 12:56:20.346762+00
489a236e-7abe-4219-8ebf-4ec7d378533f	{"id": "489a236e-7abe-4219-8ebf-4ec7d378533f", "role": "compliance_officer", "email": "newhire@rut.edu.in", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "New Hire", "is_active": true, "created_at": "2026-06-07T12:56:32.327754+00:00", "department": "Compliance", "last_login": null, "updated_at": "2026-06-07T12:56:32.327754+00:00", "mfa_enabled": false, "invited_by_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "invite_pending": true, "hashed_password": "$2b$12$JD7GfZSJtUttSKAQQnN3O.ehTyc8D6OXUsO3PF3oX/bUbN2JuXc0a", "invited_by_email": "admin@rut.edu.in"}	2026-06-07 12:56:32.663389+00
b7a9a801-39e1-435b-92f5-46dd7c76da07	{"id": "b7a9a801-39e1-435b-92f5-46dd7c76da07", "role": "pending", "email": "hacker2@example.com", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Eve2", "is_active": true, "created_at": "2026-06-07T12:59:12.572446+00:00", "department": null, "last_login": null, "updated_at": "2026-06-07T12:59:12.572446+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$r8QtOCQo9pdzcKGoocemyujqd73szJ.WmtrdsbCGDyqxwH/8Tp5mW"}	2026-06-07 12:59:13.558899+00
ecd1fd37-0d66-406d-90e6-d169b6cfcd04	{"id": "ecd1fd37-0d66-406d-90e6-d169b6cfcd04", "role": "pending", "email": "sec-test-a87dce95@example.com", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Eve", "is_active": true, "created_at": "2026-06-07T13:03:54.782461+00:00", "department": null, "last_login": null, "updated_at": "2026-06-07T13:03:54.782461+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$E/YWhYnWFo4LNXbEtZtJY.NjtdIEsTUueILzgwYCxsEscWOZCSPDi"}	2026-06-07 13:03:55.774322+00
d955f6c1-27db-40ae-9c04-117e180f328a	{"id": "d955f6c1-27db-40ae-9c04-117e180f328a", "role": "compliance_officer", "email": "newhire2@rut.edu.in", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "X", "is_active": true, "created_at": "2026-06-07T12:59:27.025818+00:00", "department": null, "last_login": null, "updated_at": "2026-06-07T12:59:27.025818+00:00", "mfa_enabled": false, "invited_by_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "invite_pending": true, "hashed_password": "$2b$12$ZW7drCEjhc/ag/63thCETO.qMPnF1LXUjIXZlnjVj4ITjB8T4/DXa", "invited_by_email": "admin@rut.edu.in"}	2026-06-07 12:59:27.362191+00
574dfd33-87bc-4508-8c18-cef661f0b515	{"id": "574dfd33-87bc-4508-8c18-cef661f0b515", "role": "pending", "email": "sec-test-d0993ef1@example.com", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Eve", "is_active": true, "created_at": "2026-06-07T13:03:58.524327+00:00", "department": null, "last_login": null, "updated_at": "2026-06-07T13:03:58.524327+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$bLNNpR4iPGr4OH3MXLrf5uU0Ma59.k9zCYyJHe3AvSbM1fv2qdgFy"}	2026-06-07 13:03:59.514998+00
d9a973d8-e19d-42e0-8e43-6f648928f1ab	{"id": "d9a973d8-e19d-42e0-8e43-6f648928f1ab", "role": "pending", "email": "dadsdsfsfdsf@gmai.cok", "org_id": "d895cc64-7fd2-4883-9d19-27619fc370d1", "full_name": "dghvas", "is_active": true, "created_at": "2026-06-07T13:00:00.978268+00:00", "department": "Administration", "last_login": null, "updated_at": "2026-06-07T13:00:00.978268+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$iPaxMC.v/.btRjnyqjJawO6EPXSdfOXSMVD4eDabAV9f3NItw8dnS"}	2026-06-07 13:00:02.00797+00
f4a02762-9920-4c96-81e1-adf6c1288880	{"id": "f4a02762-9920-4c96-81e1-adf6c1288880", "role": "compliance_officer", "email": "sec-invite-f97eff@rut.edu.in", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Hire", "is_active": true, "created_at": "2026-06-07T13:04:13.220013+00:00", "department": "Compliance", "last_login": null, "updated_at": "2026-06-07T13:04:13.220013+00:00", "mfa_enabled": false, "invited_by_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "invite_pending": true, "hashed_password": "$2b$12$7XQr6Uz6bD0/OWiGXRfEx.PrMuBdlw0KN4V2tuaA7Y5kiXZfGBDie", "invited_by_email": "admin@rut.edu.in"}	2026-06-07 13:04:13.55595+00
4749174f-ae7b-4b0e-818a-58bc2819f9fa	{"id": "4749174f-ae7b-4b0e-818a-58bc2819f9fa", "role": "pending", "email": "sec-test-c78c2c9b@example.com", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Eve", "is_active": true, "created_at": "2026-06-07T13:30:42.483868+00:00", "department": null, "last_login": null, "updated_at": "2026-06-07T13:30:42.483868+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$ABxun5Sj0Texx.JZ7a27leSDByYKgiPzECa.SlFtWnfyMtjzWkcbe"}	2026-06-07 13:30:43.475882+00
aac58d6b-53d1-4ab6-a261-4cbc755945a4	{"id": "aac58d6b-53d1-4ab6-a261-4cbc755945a4", "role": "compliance_officer", "email": "sec-invite-1e8c68@rut.edu.in", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Hire", "is_active": true, "created_at": "2026-06-07T13:30:57.156208+00:00", "department": "Compliance", "last_login": null, "updated_at": "2026-06-07T13:30:57.156208+00:00", "mfa_enabled": false, "invited_by_id": "dc4d7985-f933-4460-b13f-23b1054b196d", "invite_pending": true, "hashed_password": "$2b$12$Sx5pWbl3ZYSCpt1GEqOeXuYdXyL5Kf6Qhxc3Grn6.sL4ClKTqeNF6", "invited_by_email": "admin@rut.edu.in"}	2026-06-07 13:30:57.494389+00
b2284cc6-c822-4a71-8ac5-23bb1793258d	{"id": "b2284cc6-c822-4a71-8ac5-23bb1793258d", "role": "department_reviewer", "email": "reviewer@iit-testopolis.edu.in", "org_id": "7bab9ff2-c2fd-4dc2-b0c2-6ec6bd8bf129", "full_name": "Org B Reviewer", "is_active": true, "created_at": "2026-06-07T13:42:47.143124+00:00", "department": "OrgBDept", "updated_at": "2026-06-07T13:42:47.143124+00:00", "hashed_password": "$2b$12$Ga7mSXDL4SyMUDrpN7ryd.EZIcLpYoM95cgpX.ooDVSMDxM8NZqqq"}	2026-06-07 13:42:51.02623+00
dc4d7985-f933-4460-b13f-23b1054b196d	{"id": "dc4d7985-f933-4460-b13f-23b1054b196d", "role": "institution_admin", "email": "admin@rut.edu.in", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Dr. Anjali Mehra", "is_active": true, "created_at": "2026-06-05T05:30:19.780727+00:00", "department": "Administration", "last_login": "2026-06-17T07:41:48.033373+00:00", "updated_at": "2026-06-07T12:59:56.160035+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$P1sM.6SXQmZSz7HJcTZ4ROe3sllKfGyBvI1wSJZnRs7L/iMJNsRYW"}	2026-06-05 05:30:22.084144+00
70165d8e-092f-4b20-b446-4348d31589e8	{"id": "70165d8e-092f-4b20-b446-4348d31589e8", "role": "department_reviewer", "email": "registrar@rut.edu.in", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "full_name": "Suresh Nair", "is_active": true, "created_at": "2026-06-05T05:30:19.780727+00:00", "department": "Registrar", "last_login": "2026-06-07T15:40:06.573477+00:00", "updated_at": "2026-06-05T06:22:33.049378+00:00", "mfa_enabled": false, "hashed_password": "$2b$12$.dA1xYQBY2qqRjOPZMeNNucpPPlMJpRA4AOLcuowAZL0A86Oq6/ta"}	2026-06-05 05:30:26.699844+00
0c272a62-9d99-4461-a4ef-c5545f1bdf77	{"id": "0c272a62-9d99-4461-a4ef-c5545f1bdf77", "role": "institution_admin", "email": "admin@iit-testopolis.edu.in", "org_id": "7bab9ff2-c2fd-4dc2-b0c2-6ec6bd8bf129", "full_name": "Org B Admin", "is_active": true, "created_at": "2026-06-07T13:42:47.143124+00:00", "department": "Administration", "last_login": "2026-06-07T15:40:11.444217+00:00", "updated_at": "2026-06-07T13:42:47.143124+00:00", "hashed_password": "$2b$12$LU3FUFcODENHfb4bz/9ZXe4pSFp5K62E/0MohGkpaM90n1b3W2JRu"}	2026-06-07 13:42:49.474654+00
\.


--
-- Data for Name: vendor_assessments; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.vendor_assessments (id, data, created_at) FROM stdin;
27ad6095-7341-44fe-aca6-416ecb055349	{"id": "27ad6095-7341-44fe-aca6-416ecb055349", "score": 85, "findings": [], "vendor_id": "8ddf017f-dc02-4aa5-a18b-19e45ffc4ed2", "created_at": "2026-06-05T05:43:38.369756+00:00", "assessed_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "assessment_date": "2026-06-05T05:43:38.369756+00:00", "next_review_date": null}	2026-06-05 05:43:38.485098+00
e52cf9c5-8f6a-4ef9-9cca-231719556ac7	{"id": "e52cf9c5-8f6a-4ef9-9cca-231719556ac7", "score": 65, "findings": [], "vendor_id": "06b0d114-b3f1-470d-a304-cd20a75fa1b5", "created_at": "2026-06-05T05:56:19.415530+00:00", "assessed_by": "dc4d7985-f933-4460-b13f-23b1054b196d", "assessment_date": "2026-06-05T05:56:19.415530+00:00", "next_review_date": null}	2026-06-05 05:56:19.529373+00
\.


--
-- Data for Name: vendors; Type: TABLE DATA; Schema: cs; Owner: neondb_owner
--

COPY cs.vendors (id, data, created_at) FROM stdin;
236ffcd7-31e7-4d40-8860-9592bc38c80a	{"id": "236ffcd7-31e7-4d40-8860-9592bc38c80a", "name": "Turnitin", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "category": "Plagiarism", "risk_tier": "medium", "created_at": "2026-06-05T05:30:58.695838+00:00", "risk_score": 45, "updated_at": "2026-06-05T05:30:58.695838+00:00", "contact_info": {"email": "contact@turnitin.com"}, "contract_expiry": "2027-06-05T05:32:10.826317+00:00", "last_assessed_at": "2026-06-05T05:30:58.695838+00:00", "services_provided": "Plagiarism detection"}	2026-06-05 05:32:10.94047+00
a35ec13b-1487-48d9-a00e-7c74fa4b0fe7	{"id": "a35ec13b-1487-48d9-a00e-7c74fa4b0fe7", "name": "AWS Mumbai", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "category": "Cloud Infra", "risk_tier": "high", "created_at": "2026-06-05T05:30:58.695838+00:00", "risk_score": 65, "updated_at": "2026-06-05T05:30:58.695838+00:00", "contact_info": {"email": "contact@awsmumbai.com"}, "contract_expiry": "2027-06-05T05:32:11.480305+00:00", "last_assessed_at": "2026-06-05T05:30:58.695838+00:00", "services_provided": "Compute and storage"}	2026-06-05 05:32:11.594535+00
8ddf017f-dc02-4aa5-a18b-19e45ffc4ed2	{"id": "8ddf017f-dc02-4aa5-a18b-19e45ffc4ed2", "name": "EduERP Cloud", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "category": "ERP / SIS", "risk_tier": "critical", "created_at": "2026-06-05T05:30:58.695838+00:00", "risk_score": 85, "updated_at": "2026-06-05T05:30:58.695838+00:00", "contact_info": {"email": "contact@eduerpcloud.com"}, "contract_expiry": "2027-06-05T05:32:09.514385+00:00", "last_assessed_at": "2026-06-05T05:43:38.369756+00:00", "services_provided": "Student Information System hosting"}	2026-06-05 05:32:09.628824+00
06b0d114-b3f1-470d-a304-cd20a75fa1b5	{"id": "06b0d114-b3f1-470d-a304-cd20a75fa1b5", "name": "LearnSphere LMS", "org_id": "ecd3f0cc-533d-4b8a-b24d-f15041f3b26e", "category": "LMS", "risk_tier": "high", "created_at": "2026-06-05T05:30:58.695838+00:00", "risk_score": 65, "updated_at": "2026-06-05T05:30:58.695838+00:00", "contact_info": {"email": "contact@learnspherelms.com"}, "contract_expiry": "2027-06-05T05:32:10.171877+00:00", "last_assessed_at": "2026-06-05T05:56:19.415530+00:00", "services_provided": "Learning Management"}	2026-06-05 05:32:10.286058+00
f91a4b41-186a-4672-aff1-ae615a4184cd	{"id": "f91a4b41-186a-4672-aff1-ae615a4184cd", "name": "OrgB Vendor", "org_id": "7bab9ff2-c2fd-4dc2-b0c2-6ec6bd8bf129", "category": "saas", "risk_tier": "high", "created_at": "2026-06-07T13:42:47.143124+00:00", "risk_score": 65, "updated_at": "2026-06-07T13:42:47.143124+00:00", "contact_info": {}, "last_assessed_at": null, "services_provided": "Test"}	2026-06-07 13:42:53.731532+00
\.


--
-- Data for Name: ai_conversations; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.ai_conversations (conversation_id, institution_id, user_id, agent_type, messages, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.alembic_version (version_num) FROM stdin;
ce6cc3c74c3a
\.


--
-- Data for Name: assessment_responses; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.assessment_responses (id, assessment_id, control_id, response, notes, created_at) FROM stdin;
\.


--
-- Data for Name: assessments; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.assessments (id, org_id, framework_id, title, status, overall_score, maturity_level, due_date, created_by, created_at) FROM stdin;
\.


--
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.audit_logs (id, org_id, user_id, user_email, action, resource_type, resource_id, ip_address, metadata, created_at) FROM stdin;
\.


--
-- Data for Name: audit_observations; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.audit_observations (id, institution_id, audit_id, control_id, observed_by, observation_text, created_at) FROM stdin;
\.


--
-- Data for Name: audit_reports; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.audit_reports (id, institution_id, audit_id, generated_by, report_data, created_at) FROM stdin;
\.


--
-- Data for Name: audits; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.audits (id, org_id, title, framework_id, auditor_id, status, start_date, end_date, created_at) FROM stdin;
\.


--
-- Data for Name: chat_messages; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.chat_messages (id, session_id, user_id, role, content, created_at) FROM stdin;
\.


--
-- Data for Name: control_assignments; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.control_assignments (id, institution_id, control_id, assigned_to_user_id, department_id, status, due_date, created_at) FROM stdin;
\.


--
-- Data for Name: controls; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.controls (id, framework_id, control_id, title, domain, description, severity, keywords, evidence_required, maturity_weight, created_at) FROM stdin;
\.


--
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.departments (id, org_id, name, description, head_user_id, created_at) FROM stdin;
\.


--
-- Data for Name: document_analyses; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.document_analyses (id, org_id, user_id, filename, file_size, hash_sha256, storage_path, framework_key, analysis_md, used_ai, created_at) FROM stdin;
\.


--
-- Data for Name: evidence_documents; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.evidence_documents (id, institution_id, control_assignment_id, uploaded_by, file_path, file_name, mime_type, file_size, sha256, title, approval_status, approved_by, approved_at, created_at) FROM stdin;
\.


--
-- Data for Name: findings; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.findings (id, org_id, title, description, severity, status, source, control_ref, assigned_to, created_at) FROM stdin;
\.


--
-- Data for Name: frameworks; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.frameworks (id, org_id, name, version, type, is_active, created_at) FROM stdin;
\.


--
-- Data for Name: generated_policies; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.generated_policies (id, institution_id, title, content, policy_status, created_by, submitted_to, approved_by, approved_at, rejection_reason, parent_policy_id, version, created_at, updated_at) FROM stdin;
a3c3b0ae-cad1-4917-a9c5-e5eb4e9c7820	ecd3f0cc-533d-4b8a-b24d-f15041f3b26e	ORM Test Policy	# ORM	approved	dc4d7985-f933-4460-b13f-23b1054b196d	\N	dc4d7985-f933-4460-b13f-23b1054b196d	2026-06-07 14:02:03.966417+00	\N	\N	1	2026-06-07 14:01:49.685119+00	2026-06-07 14:02:03.966417+00
4d7e169f-2110-49da-a850-8a6cb667d804	ecd3f0cc-533d-4b8a-b24d-f15041f3b26e	Test policy for approval	# stub	approved	56ba859d-20d6-4470-974f-33d3165c9833	\N	5b27c9dc-8ed6-4cb0-b255-b75b8e09bbf9	2026-06-07 15:42:00.896036+00	\N	\N	1	2026-06-07 15:41:49.693703+00	2026-06-07 15:42:00.896036+00
\.


--
-- Data for Name: incidents; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.incidents (id, org_id, title, description, severity, status, reported_by, cert_in_notified, dpdp_notified, created_at) FROM stdin;
\.


--
-- Data for Name: institutions; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.institutions (id, name, slug, subscription_tier, is_active, created_at) FROM stdin;
ecd3f0cc-533d-4b8a-b24d-f15041f3b26e	Mirrored Institution	mirror-ecd3f0cc	trial	t	2026-06-07 14:01:21.429469+00
\.


--
-- Data for Name: mitigation_tasks; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.mitigation_tasks (id, institution_id, finding_id, assigned_to, status, due_date, completed_at, created_at) FROM stdin;
\.


--
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.notifications (id, user_id, org_id, type, title, message, is_read, created_at) FROM stdin;
\.


--
-- Data for Name: password_resets; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.password_resets (id, user_id, token_hash, expires_at, used, purpose, created_at) FROM stdin;
\.


--
-- Data for Name: permissions; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.permissions (id, name, description) FROM stdin;
\.


--
-- Data for Name: policies; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.policies (id, org_id, title, policy_type, status, content_md, framework_ref, created_by, approved_by, approved_at, created_at) FROM stdin;
\.


--
-- Data for Name: policy_versions; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.policy_versions (id, policy_id, version_number, content_md, change_note, created_by, created_at) FROM stdin;
\.


--
-- Data for Name: remediation_tasks; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.remediation_tasks (id, finding_id, org_id, title, description, status, assigned_to, due_date, created_at) FROM stdin;
\.


--
-- Data for Name: risk_treatments; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.risk_treatments (id, risk_id, treatment_type, description, created_by, created_at) FROM stdin;
\.


--
-- Data for Name: risks; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.risks (id, org_id, title, description, category, likelihood, impact, inherent_score, status, owner_id, created_at) FROM stdin;
\.


--
-- Data for Name: role_permissions; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.role_permissions (role_id, permission_id) FROM stdin;
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.roles (id, institution_id, name, is_system_role) FROM stdin;
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.users (id, institution_id, email, password_hash, full_name, is_active, created_at, failed_login_attempts, blocked_until) FROM stdin;
dc4d7985-f933-4460-b13f-23b1054b196d	ecd3f0cc-533d-4b8a-b24d-f15041f3b26e	admin@rut.edu.in	$2b$12$LKk09cdzAQYhSaSnBYGPyuOK1tnoQ3YvCozTeHloqNH1.zWkVd6qK	Dr. Anjali Mehra	t	2026-06-07 14:01:21.429469+00	0	\N
62e08a11-cc99-4a9a-9cc2-d6807296ddbd	ecd3f0cc-533d-4b8a-b24d-f15041f3b26e	orm-newuser@rut.edu.in	$2b$12$nzOzzt6Fbk9xadd1S5E2MuoaM9PMwkkodRzOPfpY/xjVUCYbYKbqe	ORM Test User	t	2026-06-07 14:01:27.171284+00	0	\N
56ba859d-20d6-4470-974f-33d3165c9833	ecd3f0cc-533d-4b8a-b24d-f15041f3b26e	ciso@rut.edu.in	$2b$12$3.dh9Z0oodx7Lq9gUTeaW.4eT6MjjqWjkhNk3PmDp.pHmLpXPic6a	Rohan Kapoor	t	2026-06-07 15:41:41.046225+00	0	\N
5b27c9dc-8ed6-4cb0-b255-b75b8e09bbf9	ecd3f0cc-533d-4b8a-b24d-f15041f3b26e	reviewer@rut.edu.in	$2b$12$AFV2h5HyrFG6rHYK3sdnh.ih55KLefGCvZyVlwq9XqPoAMOmUqzRC	Meera Bhatt	t	2026-06-07 15:41:58.182746+00	0	\N
\.


--
-- Data for Name: vendor_assessments; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vendor_assessments (id, vendor_id, org_id, score, findings, notes, assessed_by, assessment_date, next_review_date, created_at) FROM stdin;
\.


--
-- Data for Name: vendors; Type: TABLE DATA; Schema: public; Owner: neondb_owner
--

COPY public.vendors (id, org_id, name, category, contact_email, risk_level, status, created_at) FROM stdin;
\.


--
-- Name: assessment_responses assessment_responses_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.assessment_responses
    ADD CONSTRAINT assessment_responses_pkey PRIMARY KEY (id);


--
-- Name: assessments assessments_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.assessments
    ADD CONSTRAINT assessments_pkey PRIMARY KEY (id);


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: audits audits_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.audits
    ADD CONSTRAINT audits_pkey PRIMARY KEY (id);


--
-- Name: chat_messages chat_messages_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.chat_messages
    ADD CONSTRAINT chat_messages_pkey PRIMARY KEY (id);


--
-- Name: chat_sessions chat_sessions_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.chat_sessions
    ADD CONSTRAINT chat_sessions_pkey PRIMARY KEY (id);


--
-- Name: control_assignments control_assignments_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.control_assignments
    ADD CONSTRAINT control_assignments_pkey PRIMARY KEY (id);


--
-- Name: controls controls_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.controls
    ADD CONSTRAINT controls_pkey PRIMARY KEY (id);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- Name: document_analyses document_analyses_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.document_analyses
    ADD CONSTRAINT document_analyses_pkey PRIMARY KEY (id);


--
-- Name: evidence evidence_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.evidence
    ADD CONSTRAINT evidence_pkey PRIMARY KEY (id);


--
-- Name: findings findings_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.findings
    ADD CONSTRAINT findings_pkey PRIMARY KEY (id);


--
-- Name: frameworks frameworks_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.frameworks
    ADD CONSTRAINT frameworks_pkey PRIMARY KEY (id);


--
-- Name: incidents incidents_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.incidents
    ADD CONSTRAINT incidents_pkey PRIMARY KEY (id);


--
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.notifications
    ADD CONSTRAINT notifications_pkey PRIMARY KEY (id);


--
-- Name: organizations organizations_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.organizations
    ADD CONSTRAINT organizations_pkey PRIMARY KEY (id);


--
-- Name: password_resets password_resets_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.password_resets
    ADD CONSTRAINT password_resets_pkey PRIMARY KEY (id);


--
-- Name: policies policies_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.policies
    ADD CONSTRAINT policies_pkey PRIMARY KEY (id);


--
-- Name: policy_approvals policy_approvals_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.policy_approvals
    ADD CONSTRAINT policy_approvals_pkey PRIMARY KEY (id);


--
-- Name: policy_sessions policy_sessions_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.policy_sessions
    ADD CONSTRAINT policy_sessions_pkey PRIMARY KEY (id);


--
-- Name: policy_versions policy_versions_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.policy_versions
    ADD CONSTRAINT policy_versions_pkey PRIMARY KEY (id);


--
-- Name: remediation_tasks remediation_tasks_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.remediation_tasks
    ADD CONSTRAINT remediation_tasks_pkey PRIMARY KEY (id);


--
-- Name: risk_treatments risk_treatments_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.risk_treatments
    ADD CONSTRAINT risk_treatments_pkey PRIMARY KEY (id);


--
-- Name: risks risks_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.risks
    ADD CONSTRAINT risks_pkey PRIMARY KEY (id);


--
-- Name: user_preferences user_preferences_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.user_preferences
    ADD CONSTRAINT user_preferences_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: vendor_assessments vendor_assessments_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.vendor_assessments
    ADD CONSTRAINT vendor_assessments_pkey PRIMARY KEY (id);


--
-- Name: vendors vendors_pkey; Type: CONSTRAINT; Schema: cs; Owner: neondb_owner
--

ALTER TABLE ONLY cs.vendors
    ADD CONSTRAINT vendors_pkey PRIMARY KEY (id);


--
-- Name: ai_conversations ai_conversations_pkey; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.ai_conversations
    ADD CONSTRAINT ai_conversations_pkey PRIMARY KEY (conversation_id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: assessment_responses pk_assessment_responses; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.assessment_responses
    ADD CONSTRAINT pk_assessment_responses PRIMARY KEY (id);


--
-- Name: assessments pk_assessments; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT pk_assessments PRIMARY KEY (id);


--
-- Name: audit_logs pk_audit_logs; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT pk_audit_logs PRIMARY KEY (id);


--
-- Name: audit_observations pk_audit_observations; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audit_observations
    ADD CONSTRAINT pk_audit_observations PRIMARY KEY (id);


--
-- Name: audit_reports pk_audit_reports; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audit_reports
    ADD CONSTRAINT pk_audit_reports PRIMARY KEY (id);


--
-- Name: audits pk_audits; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audits
    ADD CONSTRAINT pk_audits PRIMARY KEY (id);


--
-- Name: chat_messages pk_chat_messages; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT pk_chat_messages PRIMARY KEY (id);


--
-- Name: control_assignments pk_control_assignments; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.control_assignments
    ADD CONSTRAINT pk_control_assignments PRIMARY KEY (id);


--
-- Name: controls pk_controls; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.controls
    ADD CONSTRAINT pk_controls PRIMARY KEY (id);


--
-- Name: departments pk_departments; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT pk_departments PRIMARY KEY (id);


--
-- Name: document_analyses pk_document_analyses; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.document_analyses
    ADD CONSTRAINT pk_document_analyses PRIMARY KEY (id);


--
-- Name: evidence_documents pk_evidence_documents; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.evidence_documents
    ADD CONSTRAINT pk_evidence_documents PRIMARY KEY (id);


--
-- Name: findings pk_findings; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.findings
    ADD CONSTRAINT pk_findings PRIMARY KEY (id);


--
-- Name: frameworks pk_frameworks; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.frameworks
    ADD CONSTRAINT pk_frameworks PRIMARY KEY (id);


--
-- Name: generated_policies pk_generated_policies; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.generated_policies
    ADD CONSTRAINT pk_generated_policies PRIMARY KEY (id);


--
-- Name: incidents pk_incidents; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT pk_incidents PRIMARY KEY (id);


--
-- Name: institutions pk_institutions; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.institutions
    ADD CONSTRAINT pk_institutions PRIMARY KEY (id);


--
-- Name: mitigation_tasks pk_mitigation_tasks; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.mitigation_tasks
    ADD CONSTRAINT pk_mitigation_tasks PRIMARY KEY (id);


--
-- Name: notifications pk_notifications; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT pk_notifications PRIMARY KEY (id);


--
-- Name: password_resets pk_password_resets; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT pk_password_resets PRIMARY KEY (id);


--
-- Name: permissions pk_permissions; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT pk_permissions PRIMARY KEY (id);


--
-- Name: policies pk_policies; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.policies
    ADD CONSTRAINT pk_policies PRIMARY KEY (id);


--
-- Name: policy_versions pk_policy_versions; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.policy_versions
    ADD CONSTRAINT pk_policy_versions PRIMARY KEY (id);


--
-- Name: remediation_tasks pk_remediation_tasks; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.remediation_tasks
    ADD CONSTRAINT pk_remediation_tasks PRIMARY KEY (id);


--
-- Name: risk_treatments pk_risk_treatments; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.risk_treatments
    ADD CONSTRAINT pk_risk_treatments PRIMARY KEY (id);


--
-- Name: risks pk_risks; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.risks
    ADD CONSTRAINT pk_risks PRIMARY KEY (id);


--
-- Name: role_permissions pk_role_permissions; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT pk_role_permissions PRIMARY KEY (role_id, permission_id);


--
-- Name: roles pk_roles; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT pk_roles PRIMARY KEY (id);


--
-- Name: users pk_users; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT pk_users PRIMARY KEY (id);


--
-- Name: vendor_assessments pk_vendor_assessments; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vendor_assessments
    ADD CONSTRAINT pk_vendor_assessments PRIMARY KEY (id);


--
-- Name: vendors pk_vendors; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vendors
    ADD CONSTRAINT pk_vendors PRIMARY KEY (id);


--
-- Name: assessment_responses uq_assessment_responses_assessment_id_control_id; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.assessment_responses
    ADD CONSTRAINT uq_assessment_responses_assessment_id_control_id UNIQUE (assessment_id, control_id);


--
-- Name: departments uq_departments_org_id_name; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT uq_departments_org_id_name UNIQUE (org_id, name);


--
-- Name: policy_versions uq_policy_versions_policy_id_version_number; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.policy_versions
    ADD CONSTRAINT uq_policy_versions_policy_id_version_number UNIQUE (policy_id, version_number);


--
-- Name: roles uq_roles_institution_id_name; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT uq_roles_institution_id_name UNIQUE (institution_id, name);


--
-- Name: users uq_users_email; Type: CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT uq_users_email UNIQUE (email);


--
-- Name: idx_assess_fw; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_assess_fw ON cs.assessments USING btree (((data ->> 'framework_id'::text)));


--
-- Name: idx_assessment_responses_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_assessment_responses_created ON cs.assessment_responses USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_assessment_responses_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_assessment_responses_org ON cs.assessment_responses USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_assessments_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_assessments_created ON cs.assessments USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_assessments_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_assessments_org ON cs.assessments USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_audit_action; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_audit_action ON cs.audit_logs USING btree (((data ->> 'action'::text)));


--
-- Name: idx_audit_logs_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_audit_logs_created ON cs.audit_logs USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_audit_logs_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_audit_logs_org ON cs.audit_logs USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_audits_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_audits_created ON cs.audits USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_audits_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_audits_org ON cs.audits USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_chat_messages_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_chat_messages_created ON cs.chat_messages USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_chat_messages_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_chat_messages_org ON cs.chat_messages USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_chat_session; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_chat_session ON cs.chat_messages USING btree (((data ->> 'session_id'::text)));


--
-- Name: idx_chat_sessions_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_chat_sessions_created ON cs.chat_sessions USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_chat_sessions_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_chat_sessions_org ON cs.chat_sessions USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_control_assignments_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_control_assignments_created ON cs.control_assignments USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_control_assignments_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_control_assignments_org ON cs.control_assignments USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_controls_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_controls_created ON cs.controls USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_controls_ctrl; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_controls_ctrl ON cs.controls USING btree (((data ->> 'control_id'::text)));


--
-- Name: idx_controls_fw; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_controls_fw ON cs.controls USING btree (((data ->> 'framework_id'::text)));


--
-- Name: idx_controls_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_controls_org ON cs.controls USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_departments_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_departments_created ON cs.departments USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_departments_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_departments_org ON cs.departments USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_document_analyses_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_document_analyses_created ON cs.document_analyses USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_document_analyses_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_document_analyses_org ON cs.document_analyses USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_evidence_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_evidence_created ON cs.evidence USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_evidence_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_evidence_org ON cs.evidence USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_findings_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_findings_created ON cs.findings USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_findings_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_findings_org ON cs.findings USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_frameworks_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_frameworks_created ON cs.frameworks USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_frameworks_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_frameworks_org ON cs.frameworks USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_incidents_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_incidents_created ON cs.incidents USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_incidents_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_incidents_org ON cs.incidents USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_notif_user; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_notif_user ON cs.notifications USING btree (((data ->> 'user_id'::text)));


--
-- Name: idx_notifications_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_notifications_created ON cs.notifications USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_notifications_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_notifications_org ON cs.notifications USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_organizations_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_organizations_created ON cs.organizations USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_organizations_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_organizations_org ON cs.organizations USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_password_resets_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_password_resets_created ON cs.password_resets USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_password_resets_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_password_resets_org ON cs.password_resets USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_policies_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_policies_created ON cs.policies USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_policies_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_policies_org ON cs.policies USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_policy_approvals_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_policy_approvals_created ON cs.policy_approvals USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_policy_approvals_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_policy_approvals_org ON cs.policy_approvals USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_policy_sessions_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_policy_sessions_created ON cs.policy_sessions USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_policy_sessions_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_policy_sessions_org ON cs.policy_sessions USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_policy_versions_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_policy_versions_created ON cs.policy_versions USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_policy_versions_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_policy_versions_org ON cs.policy_versions USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_remediation_tasks_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_remediation_tasks_created ON cs.remediation_tasks USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_remediation_tasks_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_remediation_tasks_org ON cs.remediation_tasks USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_risk_treatments_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_risk_treatments_created ON cs.risk_treatments USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_risk_treatments_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_risk_treatments_org ON cs.risk_treatments USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_risks_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_risks_created ON cs.risks USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_risks_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_risks_org ON cs.risks USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_user_preferences_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_user_preferences_created ON cs.user_preferences USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_user_preferences_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_user_preferences_org ON cs.user_preferences USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_users_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_users_created ON cs.users USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_users_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_users_org ON cs.users USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_vendor_assessments_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_vendor_assessments_created ON cs.vendor_assessments USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_vendor_assessments_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_vendor_assessments_org ON cs.vendor_assessments USING btree (((data ->> 'org_id'::text)));


--
-- Name: idx_vendors_created; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_vendors_created ON cs.vendors USING btree (((data ->> 'created_at'::text)) DESC);


--
-- Name: idx_vendors_org; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE INDEX idx_vendors_org ON cs.vendors USING btree (((data ->> 'org_id'::text)));


--
-- Name: uix_orgs_slug; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE UNIQUE INDEX uix_orgs_slug ON cs.organizations USING btree (((data ->> 'slug'::text)));


--
-- Name: uix_users_email; Type: INDEX; Schema: cs; Owner: neondb_owner
--

CREATE UNIQUE INDEX uix_users_email ON cs.users USING btree (((data ->> 'email'::text)));


--
-- Name: idx_ai_conversations_type; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_ai_conversations_type ON public.ai_conversations USING btree (agent_type);


--
-- Name: idx_ai_conversations_user; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_ai_conversations_user ON public.ai_conversations USING btree (user_id);


--
-- Name: idx_users_blocked_until; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX idx_users_blocked_until ON public.users USING btree (blocked_until) WHERE (blocked_until IS NOT NULL);


--
-- Name: ix_assessment_responses_assessment_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_assessment_responses_assessment_id ON public.assessment_responses USING btree (assessment_id);


--
-- Name: ix_assessment_responses_control_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_assessment_responses_control_id ON public.assessment_responses USING btree (control_id);


--
-- Name: ix_assessments_framework_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_assessments_framework_id ON public.assessments USING btree (framework_id);


--
-- Name: ix_assessments_org_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_assessments_org_id ON public.assessments USING btree (org_id);


--
-- Name: ix_audit_logs_action; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audit_logs_action ON public.audit_logs USING btree (action);


--
-- Name: ix_audit_logs_created_at; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audit_logs_created_at ON public.audit_logs USING btree (created_at);


--
-- Name: ix_audit_logs_org_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audit_logs_org_id ON public.audit_logs USING btree (org_id);


--
-- Name: ix_audit_logs_resource_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audit_logs_resource_id ON public.audit_logs USING btree (resource_id);


--
-- Name: ix_audit_logs_resource_type; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audit_logs_resource_type ON public.audit_logs USING btree (resource_type);


--
-- Name: ix_audit_logs_user_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audit_logs_user_id ON public.audit_logs USING btree (user_id);


--
-- Name: ix_audit_observations_audit_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audit_observations_audit_id ON public.audit_observations USING btree (audit_id);


--
-- Name: ix_audit_observations_control_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audit_observations_control_id ON public.audit_observations USING btree (control_id);


--
-- Name: ix_audit_observations_institution_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audit_observations_institution_id ON public.audit_observations USING btree (institution_id);


--
-- Name: ix_audit_reports_audit_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audit_reports_audit_id ON public.audit_reports USING btree (audit_id);


--
-- Name: ix_audit_reports_institution_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audit_reports_institution_id ON public.audit_reports USING btree (institution_id);


--
-- Name: ix_audits_framework_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audits_framework_id ON public.audits USING btree (framework_id);


--
-- Name: ix_audits_org_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_audits_org_id ON public.audits USING btree (org_id);


--
-- Name: ix_chat_messages_session_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_chat_messages_session_id ON public.chat_messages USING btree (session_id);


--
-- Name: ix_chat_messages_user_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_chat_messages_user_id ON public.chat_messages USING btree (user_id);


--
-- Name: ix_control_assignments_assigned_to_user_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_control_assignments_assigned_to_user_id ON public.control_assignments USING btree (assigned_to_user_id);


--
-- Name: ix_control_assignments_control_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_control_assignments_control_id ON public.control_assignments USING btree (control_id);


--
-- Name: ix_control_assignments_department_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_control_assignments_department_id ON public.control_assignments USING btree (department_id);


--
-- Name: ix_control_assignments_institution_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_control_assignments_institution_id ON public.control_assignments USING btree (institution_id);


--
-- Name: ix_controls_control_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_controls_control_id ON public.controls USING btree (control_id);


--
-- Name: ix_controls_framework_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_controls_framework_id ON public.controls USING btree (framework_id);


--
-- Name: ix_departments_org_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_departments_org_id ON public.departments USING btree (org_id);


--
-- Name: ix_document_analyses_hash_sha256; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_document_analyses_hash_sha256 ON public.document_analyses USING btree (hash_sha256);


--
-- Name: ix_document_analyses_org_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_document_analyses_org_id ON public.document_analyses USING btree (org_id);


--
-- Name: ix_evidence_documents_control_assignment_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_evidence_documents_control_assignment_id ON public.evidence_documents USING btree (control_assignment_id);


--
-- Name: ix_evidence_documents_institution_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_evidence_documents_institution_id ON public.evidence_documents USING btree (institution_id);


--
-- Name: ix_findings_org_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_findings_org_id ON public.findings USING btree (org_id);


--
-- Name: ix_findings_status; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_findings_status ON public.findings USING btree (status);


--
-- Name: ix_frameworks_org_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_frameworks_org_id ON public.frameworks USING btree (org_id);


--
-- Name: ix_generated_policies_institution_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_generated_policies_institution_id ON public.generated_policies USING btree (institution_id);


--
-- Name: ix_generated_policies_parent_policy_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_generated_policies_parent_policy_id ON public.generated_policies USING btree (parent_policy_id);


--
-- Name: ix_generated_policies_policy_status; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_generated_policies_policy_status ON public.generated_policies USING btree (policy_status);


--
-- Name: ix_incidents_org_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_incidents_org_id ON public.incidents USING btree (org_id);


--
-- Name: ix_incidents_status; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_incidents_status ON public.incidents USING btree (status);


--
-- Name: ix_institutions_slug; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ix_institutions_slug ON public.institutions USING btree (slug);


--
-- Name: ix_mitigation_tasks_assigned_to; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_mitigation_tasks_assigned_to ON public.mitigation_tasks USING btree (assigned_to);


--
-- Name: ix_mitigation_tasks_finding_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_mitigation_tasks_finding_id ON public.mitigation_tasks USING btree (finding_id);


--
-- Name: ix_mitigation_tasks_institution_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_mitigation_tasks_institution_id ON public.mitigation_tasks USING btree (institution_id);


--
-- Name: ix_notifications_is_read; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_notifications_is_read ON public.notifications USING btree (is_read);


--
-- Name: ix_notifications_org_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_notifications_org_id ON public.notifications USING btree (org_id);


--
-- Name: ix_notifications_user_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_notifications_user_id ON public.notifications USING btree (user_id);


--
-- Name: ix_password_resets_token_hash; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ix_password_resets_token_hash ON public.password_resets USING btree (token_hash);


--
-- Name: ix_password_resets_user_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_password_resets_user_id ON public.password_resets USING btree (user_id);


--
-- Name: ix_permissions_name; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE UNIQUE INDEX ix_permissions_name ON public.permissions USING btree (name);


--
-- Name: ix_policies_org_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_policies_org_id ON public.policies USING btree (org_id);


--
-- Name: ix_policies_status; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_policies_status ON public.policies USING btree (status);


--
-- Name: ix_policy_versions_policy_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_policy_versions_policy_id ON public.policy_versions USING btree (policy_id);


--
-- Name: ix_remediation_tasks_finding_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_remediation_tasks_finding_id ON public.remediation_tasks USING btree (finding_id);


--
-- Name: ix_remediation_tasks_org_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_remediation_tasks_org_id ON public.remediation_tasks USING btree (org_id);


--
-- Name: ix_risk_treatments_risk_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_risk_treatments_risk_id ON public.risk_treatments USING btree (risk_id);


--
-- Name: ix_risks_org_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_risks_org_id ON public.risks USING btree (org_id);


--
-- Name: ix_risks_status; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_risks_status ON public.risks USING btree (status);


--
-- Name: ix_roles_institution_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_roles_institution_id ON public.roles USING btree (institution_id);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_institution_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_users_institution_id ON public.users USING btree (institution_id);


--
-- Name: ix_vendor_assessments_org_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_vendor_assessments_org_id ON public.vendor_assessments USING btree (org_id);


--
-- Name: ix_vendor_assessments_vendor_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_vendor_assessments_vendor_id ON public.vendor_assessments USING btree (vendor_id);


--
-- Name: ix_vendors_org_id; Type: INDEX; Schema: public; Owner: neondb_owner
--

CREATE INDEX ix_vendors_org_id ON public.vendors USING btree (org_id);


--
-- Name: ai_conversations ai_conversations_institution_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.ai_conversations
    ADD CONSTRAINT ai_conversations_institution_id_fkey FOREIGN KEY (institution_id) REFERENCES public.institutions(id);


--
-- Name: ai_conversations ai_conversations_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.ai_conversations
    ADD CONSTRAINT ai_conversations_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: assessment_responses fk_assessment_responses_assessment_id_assessments; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.assessment_responses
    ADD CONSTRAINT fk_assessment_responses_assessment_id_assessments FOREIGN KEY (assessment_id) REFERENCES public.assessments(id) ON DELETE CASCADE;


--
-- Name: assessment_responses fk_assessment_responses_control_id_controls; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.assessment_responses
    ADD CONSTRAINT fk_assessment_responses_control_id_controls FOREIGN KEY (control_id) REFERENCES public.controls(id) ON DELETE RESTRICT;


--
-- Name: assessments fk_assessments_created_by_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT fk_assessments_created_by_users FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: assessments fk_assessments_framework_id_frameworks; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT fk_assessments_framework_id_frameworks FOREIGN KEY (framework_id) REFERENCES public.frameworks(id) ON DELETE RESTRICT;


--
-- Name: assessments fk_assessments_org_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.assessments
    ADD CONSTRAINT fk_assessments_org_id_institutions FOREIGN KEY (org_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: audit_logs fk_audit_logs_org_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT fk_audit_logs_org_id_institutions FOREIGN KEY (org_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: audit_logs fk_audit_logs_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT fk_audit_logs_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: audit_observations fk_audit_observations_institution_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audit_observations
    ADD CONSTRAINT fk_audit_observations_institution_id_institutions FOREIGN KEY (institution_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: audit_observations fk_audit_observations_observed_by_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audit_observations
    ADD CONSTRAINT fk_audit_observations_observed_by_users FOREIGN KEY (observed_by) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: audit_reports fk_audit_reports_generated_by_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audit_reports
    ADD CONSTRAINT fk_audit_reports_generated_by_users FOREIGN KEY (generated_by) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: audit_reports fk_audit_reports_institution_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audit_reports
    ADD CONSTRAINT fk_audit_reports_institution_id_institutions FOREIGN KEY (institution_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: audits fk_audits_auditor_id_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audits
    ADD CONSTRAINT fk_audits_auditor_id_users FOREIGN KEY (auditor_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: audits fk_audits_framework_id_frameworks; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audits
    ADD CONSTRAINT fk_audits_framework_id_frameworks FOREIGN KEY (framework_id) REFERENCES public.frameworks(id) ON DELETE SET NULL;


--
-- Name: audits fk_audits_org_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.audits
    ADD CONSTRAINT fk_audits_org_id_institutions FOREIGN KEY (org_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: chat_messages fk_chat_messages_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.chat_messages
    ADD CONSTRAINT fk_chat_messages_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: control_assignments fk_control_assignments_assigned_to_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.control_assignments
    ADD CONSTRAINT fk_control_assignments_assigned_to_user_id_users FOREIGN KEY (assigned_to_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: control_assignments fk_control_assignments_institution_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.control_assignments
    ADD CONSTRAINT fk_control_assignments_institution_id_institutions FOREIGN KEY (institution_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: controls fk_controls_framework_id_frameworks; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.controls
    ADD CONSTRAINT fk_controls_framework_id_frameworks FOREIGN KEY (framework_id) REFERENCES public.frameworks(id) ON DELETE CASCADE;


--
-- Name: departments fk_departments_head_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT fk_departments_head_user_id_users FOREIGN KEY (head_user_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: departments fk_departments_org_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT fk_departments_org_id_institutions FOREIGN KEY (org_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: document_analyses fk_document_analyses_org_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.document_analyses
    ADD CONSTRAINT fk_document_analyses_org_id_institutions FOREIGN KEY (org_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: document_analyses fk_document_analyses_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.document_analyses
    ADD CONSTRAINT fk_document_analyses_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: evidence_documents fk_evidence_documents_approved_by_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.evidence_documents
    ADD CONSTRAINT fk_evidence_documents_approved_by_users FOREIGN KEY (approved_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: evidence_documents fk_evidence_documents_control_assignment_id_control_assignments; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.evidence_documents
    ADD CONSTRAINT fk_evidence_documents_control_assignment_id_control_assignments FOREIGN KEY (control_assignment_id) REFERENCES public.control_assignments(id) ON DELETE SET NULL;


--
-- Name: evidence_documents fk_evidence_documents_institution_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.evidence_documents
    ADD CONSTRAINT fk_evidence_documents_institution_id_institutions FOREIGN KEY (institution_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: evidence_documents fk_evidence_documents_uploaded_by_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.evidence_documents
    ADD CONSTRAINT fk_evidence_documents_uploaded_by_users FOREIGN KEY (uploaded_by) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: findings fk_findings_assigned_to_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.findings
    ADD CONSTRAINT fk_findings_assigned_to_users FOREIGN KEY (assigned_to) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: findings fk_findings_org_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.findings
    ADD CONSTRAINT fk_findings_org_id_institutions FOREIGN KEY (org_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: frameworks fk_frameworks_org_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.frameworks
    ADD CONSTRAINT fk_frameworks_org_id_institutions FOREIGN KEY (org_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: generated_policies fk_generated_policies_approved_by_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.generated_policies
    ADD CONSTRAINT fk_generated_policies_approved_by_users FOREIGN KEY (approved_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: generated_policies fk_generated_policies_created_by_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.generated_policies
    ADD CONSTRAINT fk_generated_policies_created_by_users FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE RESTRICT;


--
-- Name: generated_policies fk_generated_policies_institution_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.generated_policies
    ADD CONSTRAINT fk_generated_policies_institution_id_institutions FOREIGN KEY (institution_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: generated_policies fk_generated_policies_parent_policy_id_generated_policies; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.generated_policies
    ADD CONSTRAINT fk_generated_policies_parent_policy_id_generated_policies FOREIGN KEY (parent_policy_id) REFERENCES public.generated_policies(id) ON DELETE SET NULL;


--
-- Name: generated_policies fk_generated_policies_submitted_to_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.generated_policies
    ADD CONSTRAINT fk_generated_policies_submitted_to_users FOREIGN KEY (submitted_to) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: incidents fk_incidents_org_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT fk_incidents_org_id_institutions FOREIGN KEY (org_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: incidents fk_incidents_reported_by_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.incidents
    ADD CONSTRAINT fk_incidents_reported_by_users FOREIGN KEY (reported_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: mitigation_tasks fk_mitigation_tasks_assigned_to_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.mitigation_tasks
    ADD CONSTRAINT fk_mitigation_tasks_assigned_to_users FOREIGN KEY (assigned_to) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: mitigation_tasks fk_mitigation_tasks_institution_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.mitigation_tasks
    ADD CONSTRAINT fk_mitigation_tasks_institution_id_institutions FOREIGN KEY (institution_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: notifications fk_notifications_org_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT fk_notifications_org_id_institutions FOREIGN KEY (org_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: notifications fk_notifications_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.notifications
    ADD CONSTRAINT fk_notifications_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: password_resets fk_password_resets_user_id_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT fk_password_resets_user_id_users FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: policies fk_policies_approved_by_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.policies
    ADD CONSTRAINT fk_policies_approved_by_users FOREIGN KEY (approved_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: policies fk_policies_created_by_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.policies
    ADD CONSTRAINT fk_policies_created_by_users FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: policies fk_policies_org_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.policies
    ADD CONSTRAINT fk_policies_org_id_institutions FOREIGN KEY (org_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: policy_versions fk_policy_versions_created_by_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.policy_versions
    ADD CONSTRAINT fk_policy_versions_created_by_users FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: policy_versions fk_policy_versions_policy_id_policies; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.policy_versions
    ADD CONSTRAINT fk_policy_versions_policy_id_policies FOREIGN KEY (policy_id) REFERENCES public.policies(id) ON DELETE CASCADE;


--
-- Name: remediation_tasks fk_remediation_tasks_assigned_to_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.remediation_tasks
    ADD CONSTRAINT fk_remediation_tasks_assigned_to_users FOREIGN KEY (assigned_to) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: remediation_tasks fk_remediation_tasks_finding_id_findings; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.remediation_tasks
    ADD CONSTRAINT fk_remediation_tasks_finding_id_findings FOREIGN KEY (finding_id) REFERENCES public.findings(id) ON DELETE CASCADE;


--
-- Name: remediation_tasks fk_remediation_tasks_org_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.remediation_tasks
    ADD CONSTRAINT fk_remediation_tasks_org_id_institutions FOREIGN KEY (org_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: risk_treatments fk_risk_treatments_created_by_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.risk_treatments
    ADD CONSTRAINT fk_risk_treatments_created_by_users FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: risk_treatments fk_risk_treatments_risk_id_risks; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.risk_treatments
    ADD CONSTRAINT fk_risk_treatments_risk_id_risks FOREIGN KEY (risk_id) REFERENCES public.risks(id) ON DELETE CASCADE;


--
-- Name: risks fk_risks_org_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.risks
    ADD CONSTRAINT fk_risks_org_id_institutions FOREIGN KEY (org_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: risks fk_risks_owner_id_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.risks
    ADD CONSTRAINT fk_risks_owner_id_users FOREIGN KEY (owner_id) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: role_permissions fk_role_permissions_permission_id_permissions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT fk_role_permissions_permission_id_permissions FOREIGN KEY (permission_id) REFERENCES public.permissions(id) ON DELETE CASCADE;


--
-- Name: role_permissions fk_role_permissions_role_id_roles; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT fk_role_permissions_role_id_roles FOREIGN KEY (role_id) REFERENCES public.roles(id) ON DELETE CASCADE;


--
-- Name: roles fk_roles_institution_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT fk_roles_institution_id_institutions FOREIGN KEY (institution_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: users fk_users_institution_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_users_institution_id_institutions FOREIGN KEY (institution_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: vendor_assessments fk_vendor_assessments_assessed_by_users; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vendor_assessments
    ADD CONSTRAINT fk_vendor_assessments_assessed_by_users FOREIGN KEY (assessed_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: vendor_assessments fk_vendor_assessments_org_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vendor_assessments
    ADD CONSTRAINT fk_vendor_assessments_org_id_institutions FOREIGN KEY (org_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: vendor_assessments fk_vendor_assessments_vendor_id_vendors; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vendor_assessments
    ADD CONSTRAINT fk_vendor_assessments_vendor_id_vendors FOREIGN KEY (vendor_id) REFERENCES public.vendors(id) ON DELETE CASCADE;


--
-- Name: vendors fk_vendors_org_id_institutions; Type: FK CONSTRAINT; Schema: public; Owner: neondb_owner
--

ALTER TABLE ONLY public.vendors
    ADD CONSTRAINT fk_vendors_org_id_institutions FOREIGN KEY (org_id) REFERENCES public.institutions(id) ON DELETE CASCADE;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON SEQUENCES TO neon_superuser WITH GRANT OPTION;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: cloud_admin
--

ALTER DEFAULT PRIVILEGES FOR ROLE cloud_admin IN SCHEMA public GRANT ALL ON TABLES TO neon_superuser WITH GRANT OPTION;


--
-- PostgreSQL database dump complete
--

\unrestrict JnNdsgfJUEZ8hbldk8ZQbIcxrxwQqzHk4bUtVeTdTmAwepxDfZHxOBtgTile5i5

