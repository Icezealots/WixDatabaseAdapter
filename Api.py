# wix_adapter.py
from flask import Flask, request, jsonify ,abort
import psycopg2


app = Flask(__name__)

MY_WIX_SECRET = "sdMUpozNTsUhq1bG5Kzs1d5Lq0FsbtDX"

def check_secret():
    incoming_secret = request.headers.get("x-wix-secrets")
    if incoming_secret != MY_WIX_SECRET:
        abort(403, description="Forbidden: Secret key is invalid")
        
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
    check_secret()
    return jsonify({"status": "ok"})

@app.route("/schema", methods=["GET"])
def schema():
    check_secret()
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
    check_secret()
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
