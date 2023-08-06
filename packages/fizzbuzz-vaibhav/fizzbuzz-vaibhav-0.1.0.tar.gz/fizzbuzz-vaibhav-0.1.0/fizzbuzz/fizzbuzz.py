def fizzbuzz(n):
    def _fizzbuzz(i):
        if i % 3 == 0 and i % 5 == 0:
            return 'FizzBuzz'
        elif i % 3 == 0:
            return 'Fizz'
        elif i % 5 == 0:
            return 'Buzz'
        else:
            return str(i)
    print("\n".join(_fizzbuzz(i+1) for i in range(n)))
