def max_two_args(num1, num2):
    return num1 if num1 >= num2 else num2

def max_three_args(num1, num2, num3):
    return max_two_args(num1, max_two_args(num2, num3))

if __name__ == "__main__":
    try:
        num1 = int(input("First number: "))
        num2 = int(input("Second number: "))
        num3 = int(input("Third number: "))

        print(max_three_args(num1, num2, num3))
    except ValueError:
        print("Input error!")