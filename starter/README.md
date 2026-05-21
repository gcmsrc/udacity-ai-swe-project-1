# Udatracker Starter Code

This directory contains the starter code for the Udatracker project. The initial structure of directories and files is described below.

## Run with Docker

From this directory (`starter/`):

```bash
docker compose up --build -d && ./scripts/print-next-steps.sh
```

Or use the helper script (same thing):

```bash
./up.sh
```

The banner shows where to open the UI and how to stop the stack. You can also see it in the container logs: `docker compose logs udatracker`.

Without Compose:

```bash
docker build -t udatracker .
docker run --rm -p 8888:8888 udatracker
```

Set `FLASK_DEBUG=true` in `docker-compose.yml` or `docker run -e FLASK_DEBUG=true` for local-style debug mode inside the container.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```

# Additional Notes

## `OrderTracker`

* For the `list_all_orders` and `list_orders_by_status` methods I opted to ruturn flat lists where the `order_id` is just one of the keys in the dictionary of each order (insated of having a nested dictionary with `order_id` first and then the data). This is is aligned with the "tabular" view we see in the UI
* I decided to move the possible statuses of an order as an attribute of the `OrderTracker` class. In the tests fixture I set the valid statuses to `["pending", "shipped"]`. When testing the UI, I found out, luckily, there was another status (`"processing"`) that I did not think of. I added it to the `OrderTracker` class but ketp the same unchanged. This gives me flexiblity in testing the core logic independently of the possible statuses (even if, in the future, some statuses may require dedicated business logic).
* I also had to change the `add_order` method in `OrderTracker` to accept the status as an argument while setting it to `"pending"` by default. In my mind, I thought that adding an order would have always resulted in a `"pending"` status one (this is also what happens in the UI). However, I understand the flexibility of back-adding an order that, for example, has already been shipped.

## API
At the endpoint `/api/help` I have added the API Swagger documentation.
