from app.security import validate_sql

def test_select_is_allowed():
    ok, sql = validate_sql("SELECT region, SUM(revenue) FROM sales GROUP BY region")
    assert ok
    assert "LIMIT 50" in sql

def test_insert_is_blocked():
    ok, _ = validate_sql("INSERT INTO sales VALUES (1, 'x')")
    assert not ok

def test_delete_is_blocked():
    ok, _ = validate_sql("DELETE FROM sales")
    assert not ok

def test_unknown_table_is_blocked():
    ok, _ = validate_sql("SELECT * FROM customers")
    assert not ok

def test_multiple_statements_are_blocked():
    ok, _ = validate_sql("SELECT * FROM sales; DROP TABLE sales")
    assert not ok
