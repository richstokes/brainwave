import ollama

# Example usage:
response = ollama.chat(
    model="gpt-oss", messages=[{"role": "user", "content": "Hello!"}]
)
print(response["message"]["content"])


def main():
    print("Hello World")


if __name__ == "__main__":
    main()
