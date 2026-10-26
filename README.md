## Conversational Analytics Assistant

A safety-first text-to-SQL portfolio project using **LangGraph, LangChain, Python and SQLite**.
I used OLLAMA in the project due to it being locally stored and free.

## Workflow

Business question -> SQL generation -> SQL validation -> read-only execution -> plain-English summary.

## Guardrails

- SELECT/WITH only
- Blocks INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, ATTACH, PRAGMA and similar statements
- Single SQL statement
- Only the approved `sales` table is exposed
- Automatic `LIMIT 50`
- Database connection is read-only
- Audit logging to `logs/audit.jsonl`
- Retry loop for rejected/failed queries

## Example questions

- What were total sales by region?
- Which product generated the most revenue?
- What is the average order value by salesperson?
- How many units were sold in the North region?

## Portfolio result

The included database contains 1,000 synthetic sales transactions.

> Evaluated on 20 business questions: 20/20 answered correctly.

## Architecture

```text
Business Question
       |
       v
+------------------+
| Generate SQL     |
| schema-aware     |
+------------------+
       |
       v
+------------------+
| Validate SQL     |
| SELECT-only      |
| allow-list       |
| row limit        |
+------------------+
       |
   invalid? ---> retry
       |
       v
+------------------+
| Read-only DB     |
+------------------+
       |
       v
+------------------+
| Summarize Result |
+------------------+
       |
       v
 Plain-English Answer
```
