-- ============================================================
-- Siledje — Script SQL complet pour Supabase
-- ============================================================
-- Recrée TOUTES les tables nécessaires à la synchronisation
-- cloud (catalogue + historique des ventes).
-- À exécuter dans le SQL Editor de Supabase (Dashboard > SQL Editor).
-- Idempotent : peut être relancé sans risque (create if not exists).
--
-- Utile si tu recrées un nouveau projet Supabase de zéro : ce
-- fichier seul suffit à reconstruire tout le schéma distant.
--
-- Schéma déduit des adaptateurs de synchro (cloud_data_sync_manager.py)
-- et confirmé contre le nombre de colonnes observé sur Supabase :
--   categories (9), suppliers (12), products (18), stock_movements (8).
-- ============================================================


-- ────────────────────────────────────────────────────────────
-- CATALOGUE (LWW : dernière écriture gagne, via updated_at)
-- ────────────────────────────────────────────────────────────

create table if not exists categories (
    sync_uuid uuid primary key default gen_random_uuid(),
    parent_id uuid references categories(sync_uuid),
    name text not null,
    description text,
    icon text,
    color text,
    sort_order integer default 0,
    is_active boolean default true,
    updated_at timestamptz default now()
);

create table if not exists suppliers (
    sync_uuid uuid primary key default gen_random_uuid(),
    name text not null,
    contact_name text,
    email text,
    phone text,
    phone2 text,
    address text,
    city text,
    payment_terms text,
    notes text,
    is_active boolean default true,
    updated_at timestamptz default now()
);

create table if not exists products (
    sync_uuid uuid primary key default gen_random_uuid(),
    category_id uuid references categories(sync_uuid),
    supplier_id uuid references suppliers(sync_uuid),
    name text not null,
    description text,
    buy_price numeric,
    sell_price numeric,
    min_stock_threshold integer default 10,
    packaging_type text default 'unitaire',
    units_per_pack integer default 1,
    location text,
    image_path text,
    sku text,
    tax_rate numeric default 0,
    is_active boolean default true,
    is_book boolean default false,
    notes text,
    updated_at timestamptz default now()
);

-- stock_quantity n'est PAS synchronisé (reconstruit uniquement via
-- stock_movements côté desktop, jamais copié tel quel depuis le distant).


-- ────────────────────────────────────────────────────────────
-- MOUVEMENTS DE STOCK (append-only, fusion additive, bidirectionnel)
-- ────────────────────────────────────────────────────────────

create table if not exists stock_movements (
    sync_uuid uuid primary key default gen_random_uuid(),
    product_id uuid references products(sync_uuid),
    movement_type text,
    quantity integer,
    reason text,
    unit_cost numeric,
    notes text,
    created_at timestamptz
);


-- ────────────────────────────────────────────────────────────
-- VENTES (push-only depuis le desktop, journal de consultation
-- pour le mobile — jamais modifié ni créé à distance)
-- ────────────────────────────────────────────────────────────

create table if not exists clients (
    sync_uuid uuid primary key default gen_random_uuid(),
    name text not null,
    phone text,
    email text,
    address text,
    updated_at timestamptz default now()
);

create table if not exists payment_methods (
    sync_uuid uuid primary key default gen_random_uuid(),
    name text not null
);

create table if not exists sales (
    sync_uuid uuid primary key default gen_random_uuid(),
    invoice_number text,
    sale_date timestamptz,
    subtotal numeric,
    tax_amount numeric,
    discount_amount numeric,
    total_amount numeric,
    status text,
    notes text,
    client_name text,
    payment_method_name text,
    created_at timestamptz
);

create table if not exists sale_items (
    sync_uuid uuid primary key default gen_random_uuid(),
    sale_id uuid references sales(sync_uuid),
    product_id uuid references products(sync_uuid),
    quantity integer,
    unit_price numeric,
    discount numeric,
    total_price numeric,
    product_name_snap text,
    created_at timestamptz
);

create table if not exists sale_payments (
    sync_uuid uuid primary key default gen_random_uuid(),
    sale_id uuid references sales(sync_uuid),
    amount numeric,
    reference text,
    payment_method_name text,
    paid_at timestamptz
);

-- ============================================================
-- Fin du script.
-- ============================================================