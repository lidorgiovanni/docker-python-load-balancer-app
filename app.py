from flask import Flask, request, make_response
import mysql.connector
import socket
import datetime

app = Flask(__name__)

# Global counter
counter = 0

# DB connection
def get_db_connection():
    return mysql.connector.connect(
        host='db',  # MySQL container name in Docker Compose
        user='root',
        password='password',
        database='app_db'
    )

@app.route('/')
def home():
    global counter
    # Increment the counter
    counter += 1

    # Get internal IP of the container
    internal_ip = socket.gethostbyname(socket.gethostname())

    # Get the client's IP address
    client_ip = request.remote_addr

    # Record access log to DB
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS access_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            access_time DATETIME,
            client_ip VARCHAR(255),
            internal_ip VARCHAR(255)
        )
    """)
    cursor.execute("INSERT INTO access_log (access_time, client_ip, internal_ip) VALUES (%s, %s, %s)",
                   (datetime.datetime.now(), client_ip, internal_ip))
    conn.commit()

    # Set a cookie for the internal IP
    resp = make_response(f"Internal IP: {internal_ip}")
    resp.set_cookie('internal_ip', internal_ip, max_age=5*60)  # 5 minutes expiration

    return resp

@app.route('/showcount')
def showcount():
    return f"Global counter: {counter}"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
