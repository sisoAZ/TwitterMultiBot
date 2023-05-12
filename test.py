test_list = ["a", "b", "c", "d", "e"]
test_list2 = ["b", "c", "d", "e", "f"]

diff_list = list(set(test_list2) - set(test_list))
print(diff_list)