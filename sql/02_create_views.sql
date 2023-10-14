
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
  WHERE marketplace."when" IS NOT NULL AND marketplace.lowest_price IS NOT NULL AND artist_release.artist_rank = 0 AND label_release.label_rank = 0
  ORDER BY artists.name, releases.release_id, marketplace."when";

ALTER TABLE public.prices
    OWNER TO dsnyder;



-- View: public.last_price

-- DROP VIEW public.last_price;

CREATE OR REPLACE VIEW public.last_price
 AS
 SELECT DISTINCT ON (marketplace.release_id) marketplace.release_id,
    marketplace.lowest_price,
    marketplace.num_for_sale,
    marketplace."when",
    releases.title,
    artists.name AS artist,
    labels.name AS label,
    releases.catno,
    releases.year,
    releases.image,
    releases.country,
    releases.format,
    releases.format_details
   FROM marketplace
     JOIN releases ON releases.release_id = marketplace.release_id
     JOIN artist_release ON artist_release.release_id = marketplace.release_id
     JOIN artists ON artists.artist_id = artist_release.artist_id
     JOIN label_release ON label_release.release_id = marketplace.release_id
     JOIN labels ON labels.label_id = label_release.label_id
  ORDER BY marketplace.release_id, marketplace."when" DESC, artist_release.artist_rank, label_release.label_rank;

ALTER TABLE public.last_price
    OWNER TO dsnyder;


-- View: public.label_by_release

-- DROP VIEW public.label_by_release;

CREATE OR REPLACE VIEW public.label_by_release
 AS
 SELECT releases.release_id,
    releases.title,
    label_release.label_id,
    labels.name AS label_name,
    label_release.label_rank
   FROM releases
     JOIN label_release ON label_release.release_id = releases.release_id
     JOIN labels ON labels.label_id = label_release.label_id
  ORDER BY releases.release_id, label_release.label_rank;

ALTER TABLE public.label_by_release
    OWNER TO dsnyder;


-- View: public.artist_by_release

-- DROP VIEW public.artist_by_release;

CREATE OR REPLACE VIEW public.artist_by_release
 AS
 SELECT releases.release_id,
    releases.title,
    artists.artist_id,
    artists.name AS artist_name,
    artist_release.artist_rank
   FROM releases
     JOIN artist_release ON releases.release_id = artist_release.release_id
     JOIN artists ON artists.artist_id = artist_release.artist_id
  ORDER BY releases.release_id, artist_release.artist_rank;

ALTER TABLE public.artist_by_release
    OWNER TO dsnyder;


-- View: public.unique_releases

-- DROP VIEW public.unique_releases;

CREATE OR REPLACE VIEW public.unique_releases
 AS
 SELECT marketplace.release_id,
    count(*) AS count
   FROM marketplace
  GROUP BY marketplace.release_id;

ALTER TABLE public.unique_releases
    OWNER TO dsnyder;

