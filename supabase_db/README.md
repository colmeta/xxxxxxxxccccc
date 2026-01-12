# The Vault (Database)

This directory contains the database definitions for Clarity Pearl.

## Setup Instructions

1.  **Supabase:** Create a new Free Tier project on Supabase.
2.  **SQL Editor:** Copy the contents of `schema.sql` and paste it into the Supabase SQL Editor.
3.  **Run:** Click "Run" to build the tables and apply RLS policies.

## Tables Overview

*   `profiles`: User data (credits, tier). Linked to Supabase Auth.
*   `jobs`: The scraping requests. Status flow: `queued` -> `running` -> `completed`.
*   `results`: The scraped data (JSON).
*   `provenance_logs`: The legal audit trail for every record.
*   `opt_out_registry`: One-way hashes of people who said "Don't scrape me".

## Security

*   **RLS (Row Level Security):** Enabled on all tables. Users can ONLY see their own data.
*   **Opt-Out:** The `opt_out_registry` is checked before any data is inserted into `results`.
