CREATE TRIGGER check_insert_entry_dtrange
BEFORE INSERT ON entry
FOR EACH ROW
BEGIN
    SELECT RAISE(ABORT, "entry start end overlap")
    WHERE EXISTS (
        SELECT 1 FROM entry e
        WHERE e.start <= NEW.start AND e.end   > NEW.start
           OR e.end   >  NEW.start AND e.start < NEW.end
    );
END;
