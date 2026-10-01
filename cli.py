
import requests

BASE_URL = "http://127.0.0.1:5000"


def show_inventory():
    try:
        response = requests.get(f"{BASE_URL}/inventory", timeout=10)
        response.raise_for_status()
        items = response.json()

        if not items:
            print("The inventory is empty.")
            return

        for item in items:
            print(
                f"ID: {item['id']} | "
                f"Name: {item['name']} | "
                f"Price: KSh {item['price']} | "
                f"Quantity: {item['quantity']} | "
                f"Brand: {item['brand']}"
            )

    except requests.RequestException as error:
        print(f"Could not connect to the API: {error}")


def add_item():
    try:
        name = input("Product name: ").strip()
        price = float(input("Price in KSh: "))
        quantity = int(input("Quantity in stock: "))
        barcode = input("Barcode (optional): ").strip()
        brand = input("Brand (optional): ").strip()

        data = {
            "name": name,
            "price": price,
            "quantity": quantity,
            "barcode": barcode,
            "brand": brand
        }

        response = requests.post(
            f"{BASE_URL}/inventory",
            json=data,
            timeout=10
        )

        print("Status:", response.status_code)
        print(response.text)

    except ValueError:
        print("Enter a valid price and whole-number quantity.")
    except requests.RequestException as error:
        print(f"Could not connect to the API: {error}")


def update_item():
    try:
        item_id = int(input("Enter the item ID: "))

        print("1. Update price")
        print("2. Update quantity")
        print("3. Update name")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            data = {"price": float(input("New price: "))}
        elif choice == "2":
            data = {"quantity": int(input("New quantity: "))}
        elif choice == "3":
            data = {"name": input("New name: ").strip()}
        else:
            print("Invalid option.")
            return

        response = requests.patch(
            f"{BASE_URL}/inventory/{item_id}",
            json=data,
            timeout=10
        )

        print("Status:", response.status_code)
        print(response.text)

    except ValueError:
        print("Enter a valid ID, price, or quantity.")
    except requests.RequestException as error:
        print(f"Could not connect to the API: {error}")


def delete_item():
    try:
        item_id = int(input("Enter the item ID to delete: "))
        confirm = input("Type yes to confirm deletion: ").strip().lower()

        if confirm != "yes":
            print("Deletion cancelled.")
            return

        response = requests.delete(
            f"{BASE_URL}/inventory/{item_id}",
            timeout=10
        )

        if response.status_code == 204:
            print("Item deleted successfully.")
        else:
            print("Status:", response.status_code)
            print(response.text)

    except ValueError:
        print("Enter a valid item ID.")
    except requests.RequestException as error:
        print(f"Could not connect to the API: {error}")


def find_product():
    print("1. Search by barcode")
    print("2. Search by product name")
    print("3. Import product by barcode")

    choice = input("Choose an option: ").strip()

    try:
        if choice == "1":
            barcode = input("Enter barcode: ").strip()

            response = requests.get(
                f"{BASE_URL}/external/barcode/{barcode}",
                timeout=15
            )

        elif choice == "2":
            name = input("Enter product name: ").strip()

            response = requests.get(
                f"{BASE_URL}/external/search",
                params={"name": name},
                timeout=15
            )

        elif choice == "3":
            barcode = input("Enter barcode to import: ").strip()

            response = requests.post(
                f"{BASE_URL}/external/import/{barcode}",
                timeout=15
            )

        else:
            print("Invalid option.")
            return

        print("Status:", response.status_code)
        print(response.text)

    except requests.RequestException as error:
        print(f"Could not connect to the API: {error}")


def main():
    while True:
        print("\n=== INVENTORY MANAGEMENT SYSTEM ===")
        print("1. View inventory")
        print("2. Add product")
        print("3. Update product")
        print("4. Delete product")
        print("5. Search or import OpenFoodFacts product")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            show_inventory()
        elif choice == "2":
            add_item()
        elif choice == "3":
            update_item()
        elif choice == "4":
            delete_item()
        elif choice == "5":
            find_product()
        elif choice == "6":
            print("Thank you for using the inventory system!")
            break
        else:
            print("Invalid choice. Enter a number from 1 to 6.")



if __name__ == "__main__":
    main()