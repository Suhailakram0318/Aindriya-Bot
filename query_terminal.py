import requests

BASE_URL = "http://localhost:8001"

def ask_question(user_id, username):
    question = input("\nAsk your question:\n")
    payload = {
        "question": question,
        "user_id": user_id,
        "username": username
    }
    response = requests.post(f"{BASE_URL}/ask", json=payload)
    
    if response.status_code == 200:
        answer = response.json().get("answer", "❌ No answer returned.")
        print("\nAnswer:")
        print(answer)
    else:
        print("\n❌ Error:", response.json())

def main():
    print("Welcome to the Chat Terminal! 🚀")

    # Ask for user_id and username once at the beginning
    user_id = input("Enter your User ID: ").strip()
    username = input("Enter your Username: ").strip()

    while True:
        print("\n--- OPTIONS ---")
        print("1. Ask a Question")
        print("2. Exit")

        choice = input("Choose an option (1-2): ").strip()

        if choice == "1":
            ask_question(user_id, username)
        elif choice == "2":
            print("Goodbye 👋")
            break
        else:
            print("❌ Invalid option. Try again.")

if __name__ == "__main__":
    main()
