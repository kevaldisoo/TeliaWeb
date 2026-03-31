--
-- PostgreSQL database dump
--

\restrict 3BJBW40tu17OG6orAE2xuurNKzScgqUHciTEhdyfwMitb3LCe8RtkmKwkUsWReX

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- Name: experience_level; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.experience_level AS ENUM (
    'junior',
    'mid',
    'senior'
);


--
-- Name: project_duration; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.project_duration AS ENUM (
    'short',
    'medium',
    'long'
);


--
-- Name: tech_stack; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE public.tech_stack AS ENUM (
    'backend',
    'frontend',
    'fullstack',
    'data',
    'devops',
    'mobile'
);


--
-- Name: rls_auto_enable(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.rls_auto_enable() RETURNS event_trigger
    LANGUAGE plpgsql SECURITY DEFINER
    SET search_path TO 'pg_catalog'
    AS $$
DECLARE
  cmd record;
BEGIN
  FOR cmd IN
    SELECT *
    FROM pg_event_trigger_ddl_commands()
    WHERE command_tag IN ('CREATE TABLE', 'CREATE TABLE AS', 'SELECT INTO')
      AND object_type IN ('table','partitioned table')
  LOOP
     IF cmd.schema_name IS NOT NULL AND cmd.schema_name IN ('public') AND cmd.schema_name NOT IN ('pg_catalog','information_schema') AND cmd.schema_name NOT LIKE 'pg_toast%' AND cmd.schema_name NOT LIKE 'pg_temp%' THEN
      BEGIN
        EXECUTE format('alter table if exists %s enable row level security', cmd.object_identity);
        RAISE LOG 'rls_auto_enable: enabled RLS on %', cmd.object_identity;
      EXCEPTION
        WHEN OTHERS THEN
          RAISE LOG 'rls_auto_enable: failed to enable RLS on %', cmd.object_identity;
      END;
     ELSE
        RAISE LOG 'rls_auto_enable: skip % (either system schema or not in enforced list: %.)', cmd.object_identity, cmd.schema_name;
     END IF;
  END LOOP;
END;
$$;


--
-- Name: set_updated_at(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.set_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
  BEGIN
      NEW.updated_at = now();
      RETURN NEW;
  END;
  $$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: employee_project_selections; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employee_project_selections (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    employee_id uuid NOT NULL,
    project_id uuid NOT NULL,
    selected_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: employees; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.employees (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    full_name text NOT NULL,
    email text NOT NULL,
    experience_level public.experience_level NOT NULL,
    tech_stack public.tech_stack NOT NULL,
    preferred_duration public.project_duration NOT NULL,
    additional_skills text,
    availability_confirmed boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: projects; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.projects (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name text NOT NULL,
    description text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Data for Name: employee_project_selections; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employee_project_selections (id, employee_id, project_id, selected_at) FROM stdin;
b56a0aeb-bef1-4f9d-93a4-5df573d86fda	e8972049-876f-475a-903c-2e818136ded5	e5239c4b-daad-4bb6-a18b-09e73a8e067c	2026-03-29 19:05:38.258838+00
3b5f04c3-094d-4c3f-8902-43c36af0de04	e8972049-876f-475a-903c-2e818136ded5	1ba1da57-5794-45d8-b8f5-ecce36347172	2026-03-29 19:05:38.258838+00
5cf6f4ad-cb17-44f6-95c8-bf3a02d0781d	e8972049-876f-475a-903c-2e818136ded5	95d578d2-5e16-4e82-ae85-4f63110ea6d1	2026-03-29 19:05:38.258838+00
\.


--
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.employees (id, full_name, email, experience_level, tech_stack, preferred_duration, additional_skills, availability_confirmed, created_at, updated_at) FROM stdin;
e8972049-876f-475a-903c-2e818136ded5	test	test@test.com	junior	frontend	short	as	t	2026-03-29 18:41:28.72906+00	2026-03-29 19:05:37.980412+00
\.


--
-- Data for Name: projects; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.projects (id, name, description, is_active, created_at) FROM stdin;
65b49885-5342-483b-9528-56b70f47bebe	Customer Portal Redesign	\N	t	2026-03-29 18:15:41.468087+00
9ca9a991-05db-4251-89a8-192b0248cd16	Data Pipeline Migration	\N	t	2026-03-29 18:15:41.468087+00
3700902a-b0aa-460c-9997-065155a1bea8	Mobile App Enhancement	\N	t	2026-03-29 18:15:41.468087+00
1ba1da57-5794-45d8-b8f5-ecce36347172	Internal Analytics Dashboard	\N	t	2026-03-29 18:15:41.468087+00
9b71d3ba-f5b2-4d76-94ad-8117b51d8e75	API Gateway Implementation	\N	t	2026-03-29 18:15:41.468087+00
bf4fd3e6-d564-4189-a667-e225e076b568	Cloud Infrastructure Setup	\N	t	2026-03-29 18:15:41.468087+00
e5239c4b-daad-4bb6-a18b-09e73a8e067c	E-commerce Platform Update	\N	t	2026-03-29 18:15:41.468087+00
e667ec2c-f7f1-405e-bde2-0d4e98aefc5a	Reporting System Automation	\N	t	2026-03-29 18:15:41.468087+00
95d578d2-5e16-4e82-ae85-4f63110ea6d1	Microservices Architecture Transition	\N	t	2026-03-29 18:15:41.468087+00
7ee75d00-7b72-40ca-b0ab-275253e6465b	Customer Data Platform Integration	\N	t	2026-03-29 18:15:41.468087+00
\.


--
-- Name: employee_project_selections employee_project_selections_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_project_selections
    ADD CONSTRAINT employee_project_selections_pkey PRIMARY KEY (id);


--
-- Name: employees employees_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_email_key UNIQUE (email);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: idx_eps_employee; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_eps_employee ON public.employee_project_selections USING btree (employee_id);


--
-- Name: idx_eps_project; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_eps_project ON public.employee_project_selections USING btree (project_id);


--
-- Name: employees employees_set_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER employees_set_updated_at BEFORE UPDATE ON public.employees FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();


--
-- Name: employee_project_selections employee_project_selections_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_project_selections
    ADD CONSTRAINT employee_project_selections_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: employee_project_selections employee_project_selections_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.employee_project_selections
    ADD CONSTRAINT employee_project_selections_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: employee_project_selections Enable read access for all users; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Enable read access for all users" ON public.employee_project_selections FOR SELECT USING (true);


--
-- Name: employees Enable read access for all users; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Enable read access for all users" ON public.employees FOR SELECT USING (true);


--
-- Name: projects Enable read access for all users; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY "Enable read access for all users" ON public.projects FOR SELECT USING (true);


--
-- Name: employee_project_selections; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.employee_project_selections ENABLE ROW LEVEL SECURITY;

--
-- Name: employees; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.employees ENABLE ROW LEVEL SECURITY;

--
-- Name: employees employees_insert; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY employees_insert ON public.employees FOR INSERT WITH CHECK (true);


--
-- Name: employees employees_update; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY employees_update ON public.employees FOR UPDATE USING (true) WITH CHECK (true);


--
-- Name: employee_project_selections eps_delete; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY eps_delete ON public.employee_project_selections FOR DELETE USING (true);


--
-- Name: employee_project_selections eps_insert; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY eps_insert ON public.employee_project_selections FOR INSERT WITH CHECK (true);


--
-- Name: projects; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.projects ENABLE ROW LEVEL SECURITY;

--
-- PostgreSQL database dump complete
--

\unrestrict 3BJBW40tu17OG6orAE2xuurNKzScgqUHciTEhdyfwMitb3LCe8RtkmKwkUsWReX

