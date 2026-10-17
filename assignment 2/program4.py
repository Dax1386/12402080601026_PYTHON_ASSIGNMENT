"""Q4: Validate a JSON query specification and build safe parameterized SQL.
Tables assumed: Student(student_id,name,spi), Course(course_id,name),
CourseRegistration(student_id,course_id). Requires mysql-connector-python.
Input is JSON with columns, filters [{column,op,value}], order_by, direction, limit.
"""
import json, getpass, sys

try:
    import importlib
    mysql = importlib.import_module("mysql")
    importlib.import_module("mysql.connector")
    Error = mysql.connector.Error
except ImportError:  # pragma: no cover - dependency is optional at lint time
    mysql = None
    class Error(Exception):
        """Fallback error used when mysql-connector-python is unavailable."""
        pass

COLUMNS = {
 "student.id": "s.student_id", "student.name": "s.name", "student.spi": "s.spi",
 "course.id": "c.course_id", "course.name": "c.name",
 "registration.student_id": "r.student_id", "registration.course_id": "r.course_id"
}
OPS = {"=": "=", "<>": "<>", ">": ">", ">=": ">=", "<": "<", "<=": "<=", "LIKE": "LIKE"}
def build_query(spec):
    columns = spec.get("columns")
    if not isinstance(columns, list) or not columns or any(c not in COLUMNS for c in columns): raise ValueError("columns must be a nonempty list of whitelisted names")
    limit = spec.get("limit")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 1000: raise ValueError("limit must be an integer from 1 to 1000")
    direction = str(spec.get("direction", "ASC")).upper()
    if direction not in ("ASC", "DESC"): raise ValueError("direction must be ASC or DESC")
    order = spec.get("order_by")
    if order not in COLUMNS: raise ValueError("order_by must be a whitelisted column")
    filters = spec.get("filters", [])
    if not isinstance(filters, list): raise ValueError("filters must be a list")
    clauses, params = [], []
    for item in filters:
        if not isinstance(item, dict) or item.get("column") not in COLUMNS or item.get("op") not in OPS or "value" not in item: raise ValueError("Invalid filter; check column, operator, and value")
        clauses.append(f"{COLUMNS[item['column']]} {OPS[item['op']]} %s")
        params.append(item["value"])
    sql = ("SELECT " + ", ".join(COLUMNS[c] for c in columns) +
           " FROM Student s JOIN CourseRegistration r ON r.student_id=s.student_id "
           "JOIN Course c ON c.course_id=r.course_id")
    if clauses: sql += " WHERE " + " AND ".join(clauses)
    sql += f" ORDER BY {COLUMNS[order]} {direction} LIMIT %s"
    params.append(limit)
    return sql, params
def main():
    conn = None
    try:
        spec = json.loads(input("Query JSON: "))
        sql, params = build_query(spec)
        print("SQL:", sql); print("PARAMETERS:", repr(params))
        host=input("MySQL host [localhost]: ").strip() or "localhost"; user=input("MySQL user: ").strip(); password=getpass.getpass("MySQL password: "); database=input("Database: ").strip()
        conn=mysql.connector.connect(host=host,user=user,password=password,database=database)
        cur=conn.cursor(); cur.execute(sql, params)
        for row in cur: print(*row)
        cur.close()
    except (ValueError, json.JSONDecodeError, Error) as exc:
        print(f"Error: {exc}", file=sys.stderr); raise SystemExit(1)
    finally:
        if conn and conn.is_connected(): conn.close()
if __name__ == "__main__": main()
