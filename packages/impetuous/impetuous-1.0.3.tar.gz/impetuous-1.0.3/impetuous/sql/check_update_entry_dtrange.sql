CREATE TRIGGER check_update_entry_dtrange
BEFORE UPDATE OF start, end ON entry
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, "entry start end overlap")
    WHERE EXISTS (
        SELECT 1 FROM entry e
        WHERE e.id is not new.id
            AND (e.start <= NEW.start AND e.end   > NEW.start
             OR  e.end   >  NEW.start AND e.start < NEW.end)
    );
END;
