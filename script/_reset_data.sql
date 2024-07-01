BEGIN;
SET session_replication_role = 'replica';

TRUNCATE TABLE public.client_bottle_transaction RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.bottle RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.bottle_brand RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.client RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.user_token RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.user RESTART IDENTITY CASCADE;

SET session_replication_role = 'origin';

INSERT INTO public.user (username, email, password, full_name, created_at)
VALUES ('Braum', 'mtbraum@gmail.com', '$2a$12$obLG9LxAFpC8L6D/Xyhg.uF0zCBzccLKaqqHZv4yFgNm1CwK9/Xo2', 'Braum - Test', CURRENT_TIMESTAMP AT TIME ZONE 'America/Sao_Paulo');

CREATE OR REPLACE FUNCTION _reinicia_sequences() RETURNS VOID AS
$$
DECLARE
    query_row RECORD;
BEGIN
    FOR query_row IN
        SELECT
            FORMAT(
                'SELECT setval(pg_get_serial_sequence(''"%s"'', ''%s''), coalesce(max(%s),0) + 1, false) FROM "%s";',
                tablename, idname, idname, tablename
            ) AS query_row
        FROM
            (
                SELECT
                    tablename,
                    (
                        SELECT a.attname
                        FROM
                            pg_index i
                            JOIN pg_attribute a ON a.attrelid = i.indrelid
                                AND a.attnum = ANY (i.indkey)
                        WHERE i.indrelid = tablename::REGCLASS AND i.indisprimary
                    ) AS idname
                FROM
                    pg_catalog.pg_tables
                WHERE schemaname = 'public' AND tablename != 'alembic_version'
            ) _
        LOOP
            EXECUTE query_row.query_row;
        END LOOP;
END;
$$ LANGUAGE plpgsql;

SELECT _reinicia_sequences();

COMMIT;
