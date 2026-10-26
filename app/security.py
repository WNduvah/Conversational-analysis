import re

FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|ATTACH|DETACH|PRAGMA|VACUUM|REINDEX|REPLACE|TRUNCATE|GRANT|REVOKE)\b",
    re.IGNORECASE,
)

def validate_sql(sql):
    sql = sql.strip()

    if not sql:
        return False, "SQL is empty."

    if ";" in sql.rstrip(";"):
        return False, "Multiple SQL statements are not allowed."

    if not re.match(r"^(SELECT|WITH)\b", sql, re.IGNORECASE):
        return False, "Only SELECT/WITH queries are allowed."

    if FORBIDDEN.search(sql):
        return False, "Potentially mutating or administrative SQL is blocked."

    tables = re.findall(
        r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)",
        sql,
        re.IGNORECASE,
    )
    if any(t.lower() != "sales" for t in tables):
        return False, "Only the approved sales table may be queried."

    if not re.search(r"\bLIMIT\s+\d+\b", sql, re.IGNORECASE):
        sql = sql.rstrip(";") + " LIMIT 50"

    return True, sql
