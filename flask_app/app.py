"""Flask entry point for the t2 sports e-commerce analytics API."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, send_from_directory

from .blueprints import marketing, ml, overview, product, sales, user
from .config import API_PREFIX, DEBUG, PORT, ROOT


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)
    app.config["JSON_AS_ASCII"] = False

    for bp in (overview.bp, sales.bp, product.bp, user.bp, marketing.bp, ml.bp):
        app.register_blueprint(bp, url_prefix=API_PREFIX)

    @app.after_request
    def cors(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        return response

    @app.errorhandler(Exception)
    def handle_error(exc):
        return jsonify({"code": 500, "msg": f"{type(exc).__name__}: {exc}", "data": None}), 200

    dashboard = ROOT / "dashboard"
    static = dashboard / "static"

    @app.get("/")
    def index():
        return send_from_directory(dashboard, "dashboard_t2.html")

    @app.get("/<path:filename>")
    def dashboard_assets(filename):
        return send_from_directory(dashboard, filename)

    @app.get("/static/<path:filename>")
    def dashboard_static(filename):
        return send_from_directory(static, filename)

    @app.get("/health")
    def health():
        return jsonify({"code": 0, "msg": "ok", "data": {"service": "t2-sports-analytics", "port": PORT}})

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=DEBUG)
