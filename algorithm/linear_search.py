def linear_search(A, x):
    for i in range(0, len(A)):
        if A[i] == x:
            return i
    return -1
