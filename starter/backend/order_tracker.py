# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.


class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """

    def __init__(
        self, storage, valid_statuses: list[str] = ["pending", "processing", "shipped"]
    ):
        required_methods = ["save_order", "get_order", "get_all_orders"]
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(
                    f"Storage object must implement a callable '{method}' method."
                )
        self.storage = storage
        self.valid_statuses = valid_statuses

    def add_order(
        self,
        order_id: str,
        item_name: str,
        quantity: int,
        customer_id: str,
        status: str = "pending",
    ):
        """Add an order to the storage."""
        if any(arg is None for arg in [order_id, item_name, quantity, customer_id]):
            raise ValueError(
                "Order ID, item name, quantity and customer ID are required"
            )

        if self.storage.get_order(order_id):
            raise ValueError(f"Order with ID '{order_id}' already exists.")

        if quantity < 1 or type(quantity) != int:
            raise ValueError(
                "Order quantity is invalid! It must be greater than 0 and integer"
            )

        self.storage.save_order(
            order_id=order_id,
            order_data=dict(
                item_name=item_name,
                quantity=quantity,
                customer_id=customer_id,
                status=status,
            ),
        )

    def get_order_by_id(self, order_id: str):
        """Get an order by its ID."""
        if not order_id:
            raise ValueError("Order ID must be a non-null string")
        else:
            order = self.storage.get_order(order_id)
            if order is None:
                raise KeyError(
                    f"Order with ID '{order_id}' not found / invalid")
            return order

    def update_order_status(self, order_id: str, new_status: str):
        """Update the status of an order."""
        if new_status not in self.valid_statuses:
            raise ValueError(
                f"Invalid status. Must be one of: {', '.join(self.valid_statuses)}"
            )
        order = self.get_order_by_id(order_id).copy()
        if order["status"] == new_status:
            raise ValueError(f"Order status is already '{new_status}'")
        else:
            order["status"] = new_status
            self.storage.save_order(
                order_id=order_id,
                order_data=order,  # save the updated order
            )

    def list_all_orders(self):
        """List all orders."""
        return [
            {
                "order_id": order_id,
                "item_name": order["item_name"],
                "quantity": order["quantity"],
                "customer_id": order["customer_id"],
                "status": order["status"],
            }
            for order_id, order in self.storage.get_all_orders().items()
        ]

    def list_orders_by_status(self, status: str):
        if status not in self.valid_statuses:
            raise ValueError(
                f"Invalid status. Must be one of: {', '.join(self.valid_statuses)}"
            )
        return [order for order in self.list_all_orders() if order["status"] == status]
