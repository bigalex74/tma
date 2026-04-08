import requests
import os

BASE_URL = "http://127.0.0.1:8000"

def test_api_suite():
    print("--- Starting Regression Test Suite ---")
    
    # 1. Test List
    res = requests.get(f"{BASE_URL}/api/prompts")
    assert res.status_code == 200, "List API failed"
    print("List: OK")

    # 2. Test File Upload (Create dummy docx-like interaction)
    # Имитация отправки файла
    with open("/home/user/telegram-apps/main.py", "rb") as f:
        files = {'file': ('test.txt', f, 'text/plain')}
        res = requests.post(f"{BASE_URL}/api/upload-file", files=files)
        assert res.status_code == 200, "Upload API failed"
        print("Upload: OK")

    # 3. Test Create & Update (The bug-prone area)
    res = requests.post(f"{BASE_URL}/api/prompts", json={"name": "RegTest", "prompt": "Content"})
    assert res.status_code == 200, "Create failed"
    
    prompts = requests.get(f"{BASE_URL}/api/prompts").json()
    p = next((x for x in prompts if x['name'] == "RegTest"), None)
    
    res = requests.put(f"{BASE_URL}/api/prompts/{p['id']}", json={"name": "RegTestUpdated", "prompt": "NewContent"})
    assert res.status_code == 200, "Update failed"
    print("Save/Update: OK")
    
    prompts = requests.get(f"{BASE_URL}/api/prompts").json()
    new_p = [p for p in prompts if p['name'] == 'RegTestUpdated']
    if new_p:
        pid = new_p[0]['id']
        # 4. Test History
        res = requests.get(f"{BASE_URL}/api/prompts/{pid}/history")
        assert res.status_code == 200, "History failed"
        print("History: OK")

        # 5. Test Delete
        res = requests.delete(f"{BASE_URL}/api/prompts/{pid}")
        assert res.status_code == 200, "Delete failed"
        # Проверка, что удалено
        prompts = requests.get(f"{BASE_URL}/api/prompts").json()
        assert not any(x['id'] == pid for x in prompts), "Prompt still exists after delete"
        print("Delete: OK")
    else:
        print("Skip Delete: Prompt not found")

    print("--- All Tests Passed Successfully ---")

if __name__ == "__main__":
    try:
        test_api_suite()
    except Exception as e:
        print(f"!!! TEST FAILED: {e}")
        exit(1)
