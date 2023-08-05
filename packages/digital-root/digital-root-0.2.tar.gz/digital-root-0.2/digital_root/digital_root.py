def digital_root(n):
    sum = 0
    while len(str(n)) > 1:
        sum += n % 10
        n = n // 10
    sum += n
    if len(str(sum)) > 1:
        return digital_root(sum)
    return sum


def main():
    user_input = input('Enter the number you want to calculate digital root for:\n')
    try:
        print(digital_root(int(user_input)))
    except ValueError:
        print('You can only calculate digital root of an integer number')


if __name__ == '__main__':
    main()
