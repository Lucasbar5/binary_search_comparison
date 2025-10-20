def binary_search_recursive_indexes(A, x, i, j):
    if j < i:
        return -1
    mid = (i + j) // 2

    if x == A[mid]:
        return mid
    elif x < A[mid]:
        return binary_search_recursive_indexes(A, x, i, mid-1)
    else:
        return binary_search_recursive_indexes(A, x, mid+1, j)
