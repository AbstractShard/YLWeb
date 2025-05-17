def test_function():
    print("This is a test function.")
    return "Test function executed."


def test_function2():
    for i in range(5):
        print(i)


if __name__ == "__main__":
    print("Running test.py directly.")
    test_function()
    print(test_function())
    print(123)
    test_function2()
    print(test_function2())
    