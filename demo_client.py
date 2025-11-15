from server import scan_code_impl

def main():
    with open("example_insecure.py", "r", encoding="utf-8") as f:
        code = f.read()

    result = scan_code_impl("python", code)

    print("=== PatchGuard MCP Demo ===")
    print(result["summary"])
    print()

    for issue in result["issues"]:
        print(
            f"[{issue['tool']}] {issue['kind'].upper()} {issue['severity']} "
            f"{issue['id']} at line {issue['line']}: {issue['message']}"
        )

if __name__ == "__main__":
    main()
