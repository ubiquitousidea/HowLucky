-- Database: dsnyder

-- DROP DATABASE IF EXISTS dsnyder;

CREATE DATABASE dsnyder
    WITH
    OWNER = dsnyder
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;


-- Role: dsnyder
-- DROP ROLE IF EXISTS dsnyder;

CREATE ROLE dsnyder WITH
  LOGIN
  SUPERUSER
  INHERIT
  CREATEDB
  CREATEROLE
  NOREPLICATION
  ENCRYPTED PASSWORD 'md533396353073c2e3358f7fb9f02a401c5';


-- SEQUENCE: public.marketplace_qid_seq

-- DROP SEQUENCE IF EXISTS public.marketplace_qid_seq;

CREATE SEQUENCE IF NOT EXISTS public.marketplace_qid_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1
    OWNED BY marketplace.qid;

ALTER SEQUENCE public.marketplace_qid_seq
    OWNER TO dsnyder;


-- Table: public.releases

-- DROP TABLE IF EXISTS public.releases;

CREATE TABLE IF NOT EXISTS public.releases
(
    release_id bigint NOT NULL,
    title text COLLATE pg_catalog."default",
    artist text COLLATE pg_catalog."default",
    artist_id bigint,
    year bigint,
    country text COLLATE pg_catalog."default",
    master_id bigint,
    CONSTRAINT releases_pkey PRIMARY KEY (release_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.releases
    OWNER to dsnyder;

-- Table: public.marketplace

-- DROP TABLE IF EXISTS public.marketplace;

CREATE TABLE IF NOT EXISTS public.marketplace
(
    release_id bigint NOT NULL,
    lowest_price numeric(20,2),
    currency character varying(16) COLLATE pg_catalog."default",
    num_for_sale bigint,
    "when" timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    qid bigint NOT NULL DEFAULT nextval('marketplace_qid_seq'::regclass),
    owned boolean,
    CONSTRAINT marketplace_pkey PRIMARY KEY (qid)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.marketplace
    OWNER to dsnyder;


-- View: public.prices

-- DROP VIEW public.prices;

CREATE OR REPLACE VIEW public.prices
 AS
 SELECT marketplace.release_id,
    releases.artist,
    releases.title,
    releases.year,
    releases.country,
    marketplace.lowest_price,
    marketplace.currency,
    marketplace.num_for_sale,
    marketplace."when",
    marketplace.owned,
    releases.artist_id,
    releases.master_id
   FROM marketplace
     JOIN releases USING (release_id)
  ORDER BY releases.artist, releases.title, marketplace."when";

ALTER TABLE public.prices
    OWNER TO dsnyder;

