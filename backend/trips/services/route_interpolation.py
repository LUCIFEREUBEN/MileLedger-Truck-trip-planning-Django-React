from math import asin, cos, radians, sin, sqrt


def _distance(a: list[float], b: list[float]) -> float:
    lon1, lat1, lon2, lat2 = map(radians, [a[0], a[1], b[0], b[1]])
    dlon, dlat = lon2 - lon1, lat2 - lat1
    h = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 12_742_000 * asin(sqrt(h))


def interpolate_route(
    geometry: list[list[float]], route_distance_m: int, target_m: int
) -> list[float] | None:
    if not geometry:
        return None
    if len(geometry) == 1 or route_distance_m <= 0:
        return geometry[0]
    target_ratio = min(1.0, max(0.0, target_m / route_distance_m))
    lengths = [_distance(geometry[i - 1], geometry[i]) for i in range(1, len(geometry))]
    geometric_total = sum(lengths)
    target = geometric_total * target_ratio
    walked = 0.0
    for index, length in enumerate(lengths, 1):
        if walked + length >= target:
            ratio = 0 if length == 0 else (target - walked) / length
            a, b = geometry[index - 1], geometry[index]
            return [a[0] + (b[0] - a[0]) * ratio, a[1] + (b[1] - a[1]) * ratio]
        walked += length
    return geometry[-1]
