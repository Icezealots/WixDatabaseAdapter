# wix_adapter.py
from flask import Flask, request, jsonify, abort
import psycopg2
import uuid
from datetime import datetime

app = Flask(__name__)

# Wix Secret Key 驗證
MY_WIX_SECRET = "sdMUpozNTsUhq1bG5Kzs1d5Lq0FsbtDX"

def check_secret():
    incoming_secret = request.headers.get("x-wix-secrets")
    if incoming_secret != MY_WIX_SECRET:
        abort(403, description="Forbidden: Secret key is invalid")

# PostgreSQL 資料庫連線設定
def get_conn():
    return psycopg2.connect(
        host="dpg-d014hq2dbo4c73drlss0-a.oregon-postgres.render.com",
        port="5432",
        database="soulv_db",
        user="soulv",
        password="sdMUpozNTsUhq1bG5Kzs1d5Lq0FsbtDX"
    )

@app.route("/ping", methods=["GET"])
def ping():
    check_secret()
    return jsonify({"status": "ok"})

@app.route("/schema", methods=["GET"])
def schema():
    check_secret()
    return jsonify({
        "collections": {
            "feedbacks": {
                "fields": {
                    "_id": {"type": "text"},
                    "_createdDate": {"type": "datetime"},
                    "_updatedDate": {"type": "datetime"},
                    "_owner": {"type": "text"},
                    "user_id": {"type": "text"},
                    "feedback": {"type": "text"}
                },
                "primaryKey": "_id"
            }
        }
    })

@app.route("/insert", methods=["POST"])
def insert():
    check_secret()
    body = request.get_json()
    collection = body.get("collectionName")
    item = body.get("item", {})

    if collection != "feedbacks":
        return jsonify({"inserted": False})

    _id = item.get("_id") or str(uuid.uuid4())
    _owner = item.get("_owner", "anonymous")
    user_id = item.get("user_id")
    feedback = item.get("feedback")

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO feedbacks (_id, _createdDate, _updatedDate, _owner, user_id, feedback)
        VALUES (%s, NOW(), NOW(), %s, %s, %s)
    """, (_id, _owner, user_id, feedback))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"inserted": True})

@app.route("/find", methods=["POST"])
def find():
    check_secret()
    body = request.get_json()
    collection = body.get("collectionName")

    if collection != "feedbacks":
        return jsonify({"items": []})

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT _id, _createdDate, _updatedDate, _owner, user_id, feedback
        FROM feedbacks
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    data = [
        {
            "_id": r[0],
            "_createdDate": r[1].isoformat() if isinstance(r[1], datetime) else r[1],
            "_updatedDate": r[2].isoformat() if isinstance(r[2], datetime) else r[2],
            "_owner": r[3],
            "user_id": r[4],
            "feedback": r[5]
        }
        for r in rows
    ]
    return jsonify({"items": data})

if __name__ == "__main__":
    app.run()
