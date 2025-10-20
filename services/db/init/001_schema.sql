-- Tabla de eventos de orquestación
CREATE TABLE IF NOT EXISTS events (
  id           BIGSERIAL PRIMARY KEY,
  ts           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  from_email   TEXT,
  subject      TEXT,
  items_json   JSONB NOT NULL,
  availability_json JSONB NOT NULL,
  pricing_json JSONB NOT NULL,
  currency     TEXT NOT NULL DEFAULT 'USD',
  status       TEXT NOT NULL,                 -- created | incomplete | error
  missing_json JSONB,
  quote_id     TEXT,
  latency_ms   INTEGER
);

-- Índices útiles
CREATE INDEX IF NOT EXISTS idx_events_ts        ON events (ts);
CREATE INDEX IF NOT EXISTS idx_events_status    ON events (status);
CREATE INDEX IF NOT EXISTS idx_events_quote_id  ON events (quote_id);
CREATE INDEX IF NOT EXISTS idx_events_items_gin ON events USING GIN (items_json);
CREATE INDEX IF NOT EXISTS idx_events_missing_gin ON events USING GIN (missing_json);
