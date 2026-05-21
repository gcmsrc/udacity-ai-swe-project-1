import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---


@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock


@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage, valid_statuses=["pending", "shipped"])


#
# --- TODO: add test functions below this line ---


### ADD ORDER TESTS ###
def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""

    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once_with(
        order_id="ORD001",
        order_data={
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": "pending",  # check the default status is pending
        },
    )


def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(
        ValueError, match="Order with ID 'ORD_EXISTING' already exists."
    ):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")


@pytest.mark.parametrize("quantity", [(-20), (0), (12.5)])
def test_add_order_raises_error_if_quantity_invalid(order_tracker, quantity):
    """Tests invalid quantities are not allowed (negative, non-int and zero)"""
    with pytest.raises(
        ValueError,
        match="Order quantity is invalid! It must be greater than 0 and integer",
    ):
        order_tracker.add_order("ORD001", "Laptop", quantity, "CUST001")


@pytest.mark.parametrize(
    "order_id, item_name, quantity, customer_id",
    [
        (None, "Laptop", 1, "CUST001"),
        ("ORD001", None, 1, "CUST001"),
        ("ORD001", "Laptop", None, "CUST001"),
        ("ORD001", "Laptop", 1, None),
    ],
)
def test_add_order_raises_error_if_missing_required_fields(
    order_tracker, order_id, item_name, quantity, customer_id
):
    """Tests that adding an order with missing required fields raises a ValueError."""
    with pytest.raises(
        ValueError,
        match="Order ID, item name, quantity and customer ID are required",
    ):
        order_tracker.add_order(order_id, item_name, quantity, customer_id)


### GET ORDER TESTS ###
def test_get_order_by_id_successfully(order_tracker, mock_storage):
    """Tests getting an order by its ID successfully."""
    mock_storage.get_order.return_value = {
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    order = order_tracker.get_order_by_id("ORD001")
    assert order["item_name"] == "Laptop"
    assert order["quantity"] == 1
    assert order["customer_id"] == "CUST001"
    assert order["status"] == "pending"


def test_get_order_by_id_raises_error_if_not_found(order_tracker, mock_storage):
    """Tests getting an order by its ID that does not exist raises a ValueError."""
    order_id = "ORD003"
    with pytest.raises(
        KeyError,
        match=f"Order with ID '{order_id}' not found / invalid",
    ):
        order_tracker.get_order_by_id(order_id)


def test_get_order_by_id_raises_error_if_order_id_is_null(order_tracker, mock_storage):
    """Tests getting an order by its ID that is null raises a ValueError."""
    order_id = None
    with pytest.raises(
        ValueError,
        match="Order ID must be a non-null string",
    ):
        order_tracker.get_order_by_id(order_id)


### UPDATE ORDER STATUS TESTS ###
def test_update_order_status_successfully(order_tracker, mock_storage):
    """Tests updating an order status successfully."""
    mock_storage.get_order.return_value = {
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    order_tracker.update_order_status("ORD001", "shipped")
    mock_storage.save_order.assert_called_once_with(
        order_id="ORD001",
        order_data={
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": "shipped",
        },
    )


def test_update_order_status_with_invalid_status(order_tracker, mock_storage):
    """Tests updating an order status with an invalid status raises a ValueError."""
    order_id = "ORD001"
    with pytest.raises(
        ValueError,
        match=f"Invalid status. Must be one of: {', '.join(order_tracker.valid_statuses)}",
    ):
        order_tracker.update_order_status(order_id, "in progress")


def test_update_order_status_if_order_id_is_null(order_tracker, mock_storage):
    """Tests updating an order status that is null raises a ValueError."""
    order_id = None

    # This test leverages the get_order_by_id logic
    with pytest.raises(
        ValueError,
        match="Order ID must be a non-null string",
    ):
        order_tracker.update_order_status(order_id, "shipped")


def test_update_order_status_with_same_status(order_tracker, mock_storage):
    """Tests updating an order status with the same status raises a ValueError."""
    order_id = "ORD001"
    new_status = "shipped"
    mock_storage.get_order.return_value = {
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": new_status,
    }
    with pytest.raises(ValueError, match=f"Order status is already '{new_status}'"):
        order_tracker.update_order_status(order_id, "shipped")


### LIST ALL ORDERS TESTS ###
def test_list_all_orders_successfully(order_tracker, mock_storage):
    """Tests listing all orders successfully."""
    mock_storage.get_all_orders.return_value = {
        "ORD001": {
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": order_tracker.valid_statuses[0],
        },
        "ORD002": {
            "item_name": "Phone",
            "quantity": 2,
            "customer_id": "CUST002",
            "status": order_tracker.valid_statuses[1],
        },
        "ORD003": {
            "item_name": "Tablet",
            "quantity": 3,
            "customer_id": "CUST003",
            "status": order_tracker.valid_statuses[0],
        },
    }
    orders = order_tracker.list_all_orders()

    mock_storage.get_all_orders.assert_called_once()
    assert len(orders) == 3
    assert [order["order_id"]
            for order in orders] == ["ORD001", "ORD002", "ORD003"]


### LIST ORDERS BY STATUS TESTS ###
@pytest.mark.parametrize(
    "status, expected_orders",
    [
        ("pending", ["ORD001", "ORD003"]),
        ("shipped", ["ORD002"]),
    ],
)
def test_list_orders_by_status_successfully(
    order_tracker, mock_storage, status, expected_orders
):
    """Tests listing orders by status successfully."""
    mock_storage.get_all_orders.return_value = {
        "ORD001": {
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": order_tracker.valid_statuses[0],
        },
        "ORD002": {
            "item_name": "Phone",
            "quantity": 2,
            "customer_id": "CUST002",
            "status": order_tracker.valid_statuses[1],
        },
        "ORD003": {
            "item_name": "Tablet",
            "quantity": 3,
            "customer_id": "CUST003",
            "status": order_tracker.valid_statuses[0],
        },
    }
    orders = order_tracker.list_orders_by_status(status)
    assert len(orders) == len(expected_orders)
    assert set([order["order_id"] for order in orders]) == set(expected_orders)


def test_list_orders_by_status_with_invalid_status(order_tracker, mock_storage):
    """Tests listing orders by status successfully."""
    mock_storage.get_all_orders.return_value = {
        "ORD001": {
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": order_tracker.valid_statuses[0],
        },
        "ORD002": {
            "item_name": "Phone",
            "quantity": 2,
            "customer_id": "CUST002",
            "status": order_tracker.valid_statuses[1],
        },
        "ORD003": {
            "item_name": "Tablet",
            "quantity": 3,
            "customer_id": "CUST003",
            "status": order_tracker.valid_statuses[0],
        },
    }
    with pytest.raises(
        ValueError,
        match=f"Invalid status. Must be one of: {', '.join(order_tracker.valid_statuses)}",
    ):
        order_tracker.list_orders_by_status("invalid-status")


def test_list_orders_by_status_with_no_orders_with_status(order_tracker, mock_storage):
    """Tests listing orders by status successfully."""
    mock_storage.get_all_orders.return_value = {
        "ORD001": {
            "item_name": "Laptop",
            "quantity": 1,
            "customer_id": "CUST001",
            "status": order_tracker.valid_statuses[0],
        },
        "ORD002": {
            "item_name": "Phone",
            "quantity": 2,
            "customer_id": "CUST002",
            "status": order_tracker.valid_statuses[0],
        },
        "ORD003": {
            "item_name": "Tablet",
            "quantity": 3,
            "customer_id": "CUST003",
            "status": order_tracker.valid_statuses[0],
        },
    }
    orders = order_tracker.list_orders_by_status(
        order_tracker.valid_statuses[1])
    assert len(orders) == 0
