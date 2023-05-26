from multiprocessing import Process,Pool,current_process,cpu_count
import os
import time
import logging

def factorize(number):
    ###print("process: ", os.getpid())
    logging.debug(f"pid={current_process().pid}, x={number}")
    divisor = 1
    divisors = []
    while divisor <= number:
        if number%divisor == 0:
            divisors.append(divisor)
        divisor +=1
    return divisors

def factorization(numbers):
    output = []
    for number in numbers:
        output.append(factorize(number))
    return output

if __name__=="__main__":
    #####print(cpu_count())
    logging.basicConfig(level=logging.DEBUG, format='%(processName)s %(message)s')

    numbers = [128, 255, 99999, 10651060]


    start = time.time()
    output = factorization(numbers)
    print("------------------------------------------------------------------------------------------------")
    for i in range(len(numbers)):
        print(numbers[i],output[i])
    print("------------------------------------------------------------------------------------------------")

    end = time.time()
    print("synchronous calculation elapsed time, sec: ", end - start)



    print(f"\n Calculations including all {cpu_count()} CPUs \n")
    start = time.time()
    with Pool(processes  = cpu_count()) as pool:
        result = pool.map(factorize,numbers)

    output = factorization(numbers)
    print("------------------------------------------------------------------------------------------------")
    for i in range(len(numbers)):
        print(numbers[i],output[i])
    print("------------------------------------------------------------------------------------------------")
    end = time.time()

    print(f"all {cpu_count()} CPUs included calculation elapsed time, sec: ", end - start)

