-- SEQUENCE: public.marketplace_qid_seq

-- DROP SEQUENCE IF EXISTS public.marketplace_qid_seq;

CREATE SEQUENCE IF NOT EXISTS public.marketplace_qid_seq
    INCREMENT 1
    START 1
    MINVALUE 1
    MAXVALUE 9223372036854775807
    CACHE 1;

ALTER SEQUENCE public.marketplace_qid_seq
    OWNER TO dsnyder;

-- Table: public.releases

-- DROP TABLE IF EXISTS public.releases;

CREATE TABLE IF NOT EXISTS public.releases
(
    release_id bigint NOT NULL,
    title text COLLATE pg_catalog."default",
    year bigint,
    country text COLLATE pg_catalog."default",
    master_id bigint,
    format text COLLATE pg_catalog."default",
    catno character varying(32) COLLATE pg_catalog."default",
    image text COLLATE pg_catalog."default",
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
    CONSTRAINT marketplace_pkey PRIMARY KEY (qid)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.marketplace
    OWNER to dsnyder;


-- Table: public.labels

-- DROP TABLE IF EXISTS public.labels;

CREATE TABLE IF NOT EXISTS public.labels
(
    label_id bigint NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    image text COLLATE pg_catalog."default",
    CONSTRAINT labels_pkey PRIMARY KEY (label_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.labels
    OWNER to dsnyder;

COMMENT ON TABLE public.labels
    IS 'table for storing label information';


-- Table: public.label_release

-- DROP TABLE IF EXISTS public.label_release;

CREATE TABLE IF NOT EXISTS public.label_release
(
    release_id bigint NOT NULL,
    label_id bigint NOT NULL,
    CONSTRAINT label_release_pkey PRIMARY KEY (release_id, label_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.label_release
    OWNER to dsnyder;

COMMENT ON TABLE public.label_release
    IS 'table for connecting multiple releases to multiple record labels';


-- Table: public.artists

-- DROP TABLE IF EXISTS public.artists;

CREATE TABLE IF NOT EXISTS public.artists
(
    artist_id bigint NOT NULL,
    name text COLLATE pg_catalog."default" NOT NULL,
    image text COLLATE pg_catalog."default",
    CONSTRAINT artists_pkey PRIMARY KEY (artist_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.artists
    OWNER to dsnyder;

COMMENT ON TABLE public.artists
    IS 'table for storing artist information';


-- Table: public.artist_release

-- DROP TABLE IF EXISTS public.artist_release;

CREATE TABLE IF NOT EXISTS public.artist_release
(
    release_id bigint NOT NULL,
    artist_id bigint NOT NULL,
    CONSTRAINT artist_release_pkey PRIMARY KEY (release_id, artist_id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.artist_release
    OWNER to dsnyder;

COMMENT ON TABLE public.artist_release
    IS 'table for connecting multiple releases to multiple artists';


-- View: public.prices

-- DROP VIEW public.prices;

CREATE OR REPLACE VIEW public.prices
 AS
 SELECT marketplace.release_id,
    releases.title,
    releases.catno,
    releases.year,
    releases.country,
    releases.master_id,
    artists.name AS artist,
    artists.artist_id,
    labels.name AS label,
    labels.label_id,
    marketplace.lowest_price,
    marketplace.currency,
    marketplace.num_for_sale,
    marketplace."when"
   FROM marketplace
     JOIN releases ON releases.release_id = marketplace.release_id
     JOIN artist_release ON artist_release.release_id = marketplace.release_id
     JOIN label_release ON label_release.release_id = marketplace.release_id
     JOIN artists ON artists.artist_id = artist_release.artist_id
     JOIN labels ON label_release.label_id = labels.label_id
  WHERE marketplace."when" IS NOT NULL AND marketplace.lowest_price IS NOT NULL
  ORDER BY artists.name, releases.title, marketplace."when";

ALTER TABLE public.prices
    OWNER TO dsnyder;



-- View: public.last_price

-- DROP VIEW public.last_price;

CREATE OR REPLACE VIEW public.last_price
 AS
 SELECT DISTINCT ON (marketplace.release_id) marketplace.release_id,
    marketplace.lowest_price,
    marketplace.num_for_sale,
    marketplace."when"
   FROM marketplace
  ORDER BY marketplace.release_id, marketplace."when" DESC;

ALTER TABLE public.last_price
    OWNER TO dsnyder;


-- View: public.label_by_release

-- DROP VIEW public.label_by_release;

CREATE OR REPLACE VIEW public.label_by_release
 AS
 SELECT releases.release_id,
    releases.title,
    label_release.label_id,
    labels.name AS label_name
   FROM releases
     JOIN label_release ON label_release.release_id = releases.release_id
     JOIN labels ON labels.label_id = label_release.label_id;

ALTER TABLE public.label_by_release
    OWNER TO dsnyder;

