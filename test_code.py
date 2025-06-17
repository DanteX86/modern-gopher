#!/usr/bin/env python3

def old_function_name():
    print("This function has an old name")
    return "old result"

def another_old_function():
    x = old_function_name()
    print(f"Called old function: {x}")

class TestClass:
    def method_with_old_name(self):
        return old_function_name()

# Some more code
if __name__ == "__main__":
    old_function_name()
    another_old_function()

