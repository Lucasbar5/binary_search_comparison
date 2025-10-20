def binary_search_subvector_copies(A: list[int], x):
    n = len(A)
    if n <= 0:
        return -1
    mid = (0 + n-1) // 2
    if x == A[mid]:
        return mid
    elif x < A[mid]:
        return binary_search_subvector_copies(A[:mid], x)
    else:
        result = binary_search_subvector_copies(A[mid+1:], x)
        if result != -1:
            return result + mid + 1
        else:
            return -1
