
# Inventory Management System

## Project Description

This is a beginner-friendly inventory management system built
using Python and Flask.

The system allows employees to view, add, update, and delete
inventory products. It also connects to the OpenFoodFacts API
to search for product information by barcode or name.

Employees can import products from OpenFoodFacts into the
inventory list using the command-line interface.

## Technologies Used

- Python
- Flask
- Requests
- OpenFoodFacts API
- Pytest
- Git and GitHub

## Project Structure

```text
inventory-management-system/
├── app.py
├── cli.py
├── test_app.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd inventory-management-system
```

Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

On Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Start the API

```bash
python app.py
```

The API runs at:

http://127.0.0.1:5000

## Start the CLI

Open a second terminal and activate the virtual environment.

Run:

```bash
python cli.py
```

Follow the menu to manage inventory products.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Welcome message |
| GET | /inventory | View all products |
| GET | /inventory/<id> | View one product |
| POST | /inventory | Add a product |
| PATCH | /inventory/<id> | Update a product |
| DELETE | /inventory/<id> | Delete a product |
| GET | /external/barcode/<barcode> | Search by barcode |
| GET | /external/search?name=milk | Search by name |
| POST | /external/import/<barcode> | Import a product |

## Example JSON

Use this JSON to add a product:

```json
{
  "name": "Rice",
  "price": 200,
  "quantity": 15,
  "barcode": "",
  "brand": "Local Store"
}
```

## Run Unit Tests

```bash
pytest -v
```

The tests check CRUD operations, validation, and external
API interactions using mocked responses.

## Storage

This project uses a Python list as temporary storage.
Changes will be lost when the Flask server restarts.

A database such as SQLite could be added in the future.

## External API

OpenFoodFacts provides product details such as product names,
brands, ingredients, and barcodes.

Website: https://world.openfoodfacts.org/

Internet access is required for live product searches.

## Author

Anord Wakaba