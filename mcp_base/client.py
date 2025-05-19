import requests

BASE_URL = "http://127.0.0.1:8000"

def test_list_items():
    resp = requests.post(f"{BASE_URL}/tool/list_items", json={})
    print("list_items:", resp.json())

def test_new_item(title):
    resp = requests.post(f"{BASE_URL}/tool/new_item", json={"title": title})
    print("new_item:", resp.json())

def test_complete_item(id):
    resp = requests.post(f"{BASE_URL}/tool/complete_item", json={"id": id})
    print("complete_item:", resp.json())

if __name__ == "__main__":
    test_list_items()
    test_new_item("Finish MCP integration")
    test_list_items()
    test_complete_item(1)
    test_list_items()
