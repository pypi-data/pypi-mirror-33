
def exp_func(number, power):
    return number ** power


if __name__ == '__main__':
    num = int(input('Input number: '))
    power = int(input('Input power: '))

    print(exp_func(num, power))
