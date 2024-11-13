#!/bin/python3

import math
import os
import random
import re
import sys


#
# Complete the 'dynamicArray' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts following parameters:
#  1. INTEGER n
#  2. 2D_INTEGER_ARRAY queries
#

def dynamicArray(n, queries):
    # Write your code here
    a = 0
    arr = []
    for i in range(n):
        arr.append([])
    r = []
    for q in queries:
        i = (q[1] ^ a) % n
        if q[0] == 1:
            print(arr)
            arr[i].append(q[2])
            print(i, arr[i])
            print(arr)
            break
        else:
            i2 = q[2] % len(arr[i])
            a = arr[i][i2]
            r.append(a)
    return r


if __name__ == '__main__':
    first_multiple_input = input().rstrip().split()

    n = int(first_multiple_input[0])

    q = int(first_multiple_input[1])

    queries = []

    for _ in range(q):
        queries.append(list(map(int, input().rstrip().split())))

    result = dynamicArray(n, queries)

    print('\n'.join(map(str, result)))
