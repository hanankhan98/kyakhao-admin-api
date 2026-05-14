import sys

action = sys.argv[1] if len(sys.argv) > 1 else ""
if action == "get":
    lines = sys.stdin.read().strip().split("\n")
    is_github = any("host=github.com" in line for line in lines)
    if is_github:
        print("protocol=https")
        print("host=github.com")
        print("username=lalainfatima237")
        print("password=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")
