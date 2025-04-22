-- Table: public.login

-- DROP TABLE IF EXISTS public.login;

CREATE TABLE IF NOT EXISTS public.login
(
    user_id integer NOT NULL DEFAULT nextval('login_user_id_seq'::regclass),
    username character varying(50) COLLATE pg_catalog."default" NOT NULL,
    password character varying(100) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT login_pkey PRIMARY KEY (user_id),
    CONSTRAINT login_username_key UNIQUE (username)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.login
    OWNER to admin;