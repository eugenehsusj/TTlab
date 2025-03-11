import ttlab

def test_info():
    expected_output = "TTLAB Semiconductor analysis and simulation package"
    assert ttlab.info() == expected_output, f"Expected '{expected_output}', but got '{ttlab.info()}'"

if __name__ == "__main__":
    test_info()
    print("All tests passed.")