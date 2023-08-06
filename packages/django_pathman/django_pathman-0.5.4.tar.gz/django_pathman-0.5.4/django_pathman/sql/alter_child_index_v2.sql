CREATE OR REPLACE FUNCTION alter_child_index(parent_table text, itable text=NULL, is_debug boolean=false) RETURNS VOID AS $$
DECLARE
    has_pathman BOOLEAN;
    new_idx_name text;
    new_idx_def text;
    tbl REGCLASS;
    diff_idx RECORD;
    max_index_name_length int := 63;
    schema_name varchar(255);
BEGIN
    SELECT EXISTS(SELECT to_regclass('pathman_partition_list')) INTO has_pathman;
    IF (has_pathman) THEN
    ELSE
        RAISE WARNING 'Install and enable pg_pathman first';
        RETURN;
    END IF;
    schema_name := current_schema();

    IF(itable IS NULL) THEN
        IF(is_debug) THEN RAISE INFO '----- [Detecting partitions...] -----'; END IF;
        FOR tbl IN SELECT partition FROM pathman_partition_list WHERE parent = parent_table::regclass
        LOOP
            IF(is_debug) THEN RAISE INFO '----- [Detect child "%.%"] -----', schema_name, tbl; END IF;
            PERFORM alter_child_index(parent_table, tbl::text, is_debug);
        END LOOP;
        RETURN;
    END IF;

    IF(is_debug) THEN
        RAISE INFO '----- [Working with table "%.%"] -----', schema_name, itable;
        RAISE INFO 'Checking indexes...';
    END IF;

    FOR diff_idx IN SELECT schemaname, tablename, indexname, indexdef FROM
        (SELECT *, COUNT(*) OVER (PARTITION BY indexdefcut) as index_cnt FROM
            (SELECT *, replace(replace(indexdef, indexname, ''), tablename, '') as indexdefcut FROM pg_indexes WHERE tablename IN (parent_table, itable)) as t1
        ) as t2 WHERE index_cnt = 1
    LOOP
        IF (diff_idx.tablename = parent_table) THEN
            new_idx_name := replace(diff_idx.indexname, parent_table, itable);
            IF (new_idx_name = diff_idx.indexname) THEN
                new_idx_name := new_idx_name || '_' || substring(md5(random()::text) from 1 for 10);
            END IF;
            new_idx_name := substring(new_idx_name from 1 for max_index_name_length);
            new_idx_def := regexp_replace(diff_idx.indexdef, 'CREATE (UNIQUE |)INDEX (' || diff_idx.indexname || ') ON (' || parent_table || ') ', 'CREATE \1INDEX ' || new_idx_name || ' ON ' || itable || ' ');
            IF(is_debug) THEN
                RAISE INFO 'Creating index "%" ON "%.%"...', new_idx_name, schema_name, itable;
                RAISE INFO '%s', new_idx_def;
            END IF;
            EXECUTE new_idx_def;
        ELSE
            IF(is_debug) THEN RAISE INFO 'Dropping old index "%" ON "%.%", converting to constraint...', diff_idx.indexname, schema_name, itable; END IF;
            EXECUTE 'DROP INDEX ' || diff_idx.indexname || ';';
        END IF;
    END LOOP;
    RETURN;
END;
$$ LANGUAGE plpgsql;