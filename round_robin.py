def rotate(elements: list, n=1, length=None, clockwise=True):
    """Rotates a list of elements n positions

    >>> rotate([1, 2, 3], n=1, clockwise=True)
    [3, 1, 2]
    >>> rotate([1, 2, 3], n=-1, clockwise=False)
    [3, 1, 2]
    >>> rotate([1, 2, 3], n=1, clockwise=False)
    [2, 3, 1]
    >>> rotate([1, 2, 3], n=-1, clockwise=True)
    [2, 3, 1]
    """
    if not elements:
        return elements
    if length is None:
        length = len(elements)
    if length < 2:
        return elements
    n %= length
    direction = -1 if clockwise else 1
    return elements[direction * n :] + elements[: direction * n]


def circle_method(teams, pivot=0, length=None):

    if length is None:
        length = len(teams)

    half = length // 2
    pivot %= length
    fixed = [teams[pivot]]

    circle = teams[:pivot] + teams[pivot + 1 :]
    for _ in range(length - 1):

        current = circle[:pivot] + fixed + circle[pivot:]

        pairings = [
            (player, opponent)
            for (player, opponent) in zip(current[:half], current[: half - 2 : -1])
        ]
        yield pairings

        circle = rotate(circle, n=1, length=length, clockwise=True)


def berger_tables(teams, length=None, pivot=-1):
    if length is None:
        length = len(teams)

    pivot %= length
    indexes = list(range(length))
    half = length // 2
    pivot_pos = pivot if pivot < half else pivot - length + 1
    pivot_free_indices = [i for i in indexes if i != pivot]

    for i in range(length - 1):
        pairings = [
            (teams[i], teams[j])
            for (i, j) in zip(indexes[:half], indexes[: half - 2 : -1])
        ]

        if i % 2:
            pairings[pivot_pos] = tuple(reversed(pairings[pivot_pos]))

        for k in pivot_free_indices:
            indexes[k] += half
            indexes[k] %= length - 1

        yield pairings


def round_robin(teams, method="circle", offsett_msg="break", *args, **kwargs):
    if not teams:
        yield [(None, None)]
        return
    elif (length := len(teams)) < 2:
        yield [(teams[0], None)]
        return
    elif length % 2:
        teams.append(offsett_msg)
    if "circ" in method:
        yield from circle_method(teams, *args, **kwargs, length=length)
    elif "berg" in method or "table" in method:
        yield from berger_tables(teams, *args, **kwargs, length=length)
