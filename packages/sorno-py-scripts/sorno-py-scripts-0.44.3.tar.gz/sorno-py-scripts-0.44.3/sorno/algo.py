def min_edit_distance_dp(s1, s2):
    if len(s1) < len(s2):
        # longer string at the left
        s1, s2 = s2, s1

    dists = [0] * (1 + len(s2))
    dists2 = [0] * (1 + len(s2))

    for i in range(len(s1) + 1):
        for j in range(len(s2) + 1):
            if i == 0:
                dists[j] = j
            elif j == 0:
                dists[j] = i
            else:
                if s1[i - 1] == s2[j - 1]:
                    dists[j] = dists2[j - 1]
                else:
                    dists[j] = 1 + min([
                        dists2[j],
                        dists[j - 1],
                        dists2[j - 1],
                    ])
        dists, dists2 = dists2, dists

    return dists2[-1]
