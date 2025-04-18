# wix_adapter.py
from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# DB 連線設定
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
    return jsonify({"status": "ok"})

@app.route("/schema", methods=["GET"])
def schema():
    return jsonify({
        "collections": {
            "feedbacks": {
                "fields": {
                    "id": {"type": "number"},
                    "user_id": {"type": "text"},
                    "feedback": {"type": "text"}
                },
                "primaryKey": "id"
            }
        }
    })


@app.route("/find", methods=["POST"])
def find():
    body = request.get_json()
    collection = body.get("collectionName")

    if collection != "feedbacks":
        return jsonify({"items": []})

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, feedback FROM feedbacks")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    data = [{"id": r[0], "user_id": r[1], "feedback": r[2]} for r in rows]
    return jsonify({"items": data})


# 可以再加 /insert, /update, /delete routes

if __name__ == "__main__":
    app.run()
