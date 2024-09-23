def divide_list(lst, n):
    k, m = divmod(len(lst), n)
    return [lst[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]

a = [1, 2, 3, 4, 5, 6, 7, 8]
b = 3
c = divide_list(a, b)
print(c)
