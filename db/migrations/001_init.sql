CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE stores (
  id         BIGSERIAL PRIMARY KEY,
  chain      TEXT NOT NULL,
  name       TEXT NOT NULL,
  address    TEXT,
  geom       GEOGRAPHY(Point, 4326) NOT NULL,
  UNIQUE (chain, name)
);
CREATE INDEX stores_geom_gix ON stores USING GIST (geom);

CREATE TABLE categories (
  id        SERIAL PRIMARY KEY,
  name      TEXT NOT NULL UNIQUE,
  parent_id INT REFERENCES categories(id)
);

CREATE TABLE products (
  id          BIGSERIAL PRIMARY KEY,
  name        TEXT NOT NULL,
  category_id INT REFERENCES categories(id),
  unit        TEXT,                 -- '1 l', '500 g' ...
  external_id TEXT,                 -- chain SKU, used by scrapers
  UNIQUE (name, unit)
);
CREATE INDEX products_name_trgm ON products USING GIN (name gin_trgm_ops);

-- Append-only: every scrape inserts a row; "current" price = newest row per (product, store)
CREATE TABLE prices_history (
  id         BIGSERIAL PRIMARY KEY,
  product_id BIGINT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  store_id   BIGINT NOT NULL REFERENCES stores(id)   ON DELETE CASCADE,
  price      NUMERIC(10,2) NOT NULL CHECK (price >= 0),
  currency   CHAR(3) NOT NULL DEFAULT 'UAH',
  scraped_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX prices_latest_ix ON prices_history (product_id, store_id, scraped_at DESC);

CREATE VIEW latest_prices AS
SELECT DISTINCT ON (product_id, store_id)
       product_id, store_id, price, currency, scraped_at
FROM prices_history
ORDER BY product_id, store_id, scraped_at DESC;

CREATE TABLE user_locations (
  telegram_id BIGINT PRIMARY KEY,
  geom        GEOGRAPHY(Point, 4326) NOT NULL,
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Cheapest matching products within radius (default 3 km). $1=lng $2=lat $3=radius_m $4=query $5=limit
-- ST_DWithin on geography uses meters and the GiST index; ST_MakePoint order is (lng, lat)!
-- Used by the API as a parameterised query:
--   SELECT p.id, p.name, p.unit, s.id AS store_id, s.chain, s.name AS store_name,
--          lp.price, lp.scraped_at,
--          ST_Distance(s.geom, pt.g) AS distance_m
--   FROM (SELECT ST_SetSRID(ST_MakePoint($1,$2),4326)::geography AS g) pt
--   JOIN stores s          ON ST_DWithin(s.geom, pt.g, $3)
--   JOIN latest_prices lp  ON lp.store_id = s.id
--   JOIN products p        ON p.id = lp.product_id
--   WHERE p.name ILIKE '%'||$4||'%' OR p.name % $4
--   ORDER BY lp.price ASC, distance_m ASC LIMIT $5;
