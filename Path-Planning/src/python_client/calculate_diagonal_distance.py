def calculate_diagonal_distance(source, destination):
    dx = abs(source.x - destination.x)
    dy = abs(source.y - destination.y)
    return 2 * min(dx, dy) + (max(dx, dy) - min(dx, dy))