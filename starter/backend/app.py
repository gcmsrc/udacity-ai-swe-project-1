from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

OPENAPI_YAML_PATH = Path(__file__).resolve().parent / "openapi.yaml"

app = Flask(__name__, static_folder="../frontend")
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


@app.route("/api/help/openapi.yaml")
def openapi_yaml():
    """Source-of-truth OpenAPI document."""
    return send_from_directory(
        OPENAPI_YAML_PATH.parent,
        OPENAPI_YAML_PATH.name,
        mimetype="application/yaml",
    )


@app.route("/api/help")
def api_help():
    """Interactive API docs (Swagger UI) backed by the OpenAPI spec."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Udatracker API</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"/>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({{
      url: "/api/help/openapi.yaml",
      dom_id: "#swagger-ui",
    }});
  </script>
</body>
</html>"""


@app.route("/api/orders", methods=["POST"])
def add_order_api():
    """Add an order to the order tracker."""
    order_data = request.json
    try:
        order_tracker.add_order(
            order_id=order_data["order_id"],
            item_name=order_data["item_name"],
            quantity=order_data["quantity"],
            customer_id=order_data["customer_id"],
            # default status is pending
            status=order_data.get("status", "pending"),
        )
        return (
            jsonify(
                {
                    "order_id": order_data["order_id"],
                    "message": "Order added successfully",
                }
            ),
            201,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # In case of invalid order data


@app.route("/api/orders/<string:order_id>", methods=["GET"])
def get_order_api(order_id):
    """Get order from storage by ID."""
    try:
        order = order_tracker.get_order_by_id(order_id)
        return jsonify({"order_id": order_id, "order_data": order}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # In case of invalid order ID
    except KeyError as e:
        return jsonify({"error": str(e)}), 404  # In case of order not found


@app.route("/api/orders/<string:order_id>/status", methods=["PUT"])
def update_order_status_api(order_id):
    """Update an order status."""
    try:
        order_tracker.update_order_status(order_id, request.json["new_status"])
        return (
            jsonify(
                {
                    "order_id": order_id,
                    "status": request.json["new_status"],
                    "message": "Order status updated successfully",
                }
            ),
            200,
        )
    except ValueError as e:
        # In case of invalid order status
        return jsonify({"error": str(e)}), 400


@app.route("/api/orders", methods=["GET"])
def list_orders_api():
    """Get all the oders. If status is provided, filter the orders by status."""
    try:
        status = request.args.get("status")
        if status:
            orders = order_tracker.list_orders_by_status(status)
        else:
            orders = order_tracker.list_all_orders()
        return jsonify(orders), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400  # In case of invalid status


if __name__ == "__main__":
    import os

    debug = os.environ.get(
        "FLASK_DEBUG", "true").lower() in ("1", "true", "yes")
    port = int(os.environ.get("PORT", "8888"))
    app.run(host="0.0.0.0", debug=debug, port=port)
