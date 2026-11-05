from sqlalchemy import text


def test_database_has_schema(db_session):
    tables = {r[0] for r in db_session.execute(text("select tablename from pg_tables where schemaname='public'"))}
    assert {"users", "subjects", "documents", "document_chunks", "conversations", "messages", "message_sources"} <= tables


def test_fixtures_create_users(teacher, student):
    assert teacher.user.role == "teacher"
    assert student.headers["Authorization"].startswith("Bearer ")
