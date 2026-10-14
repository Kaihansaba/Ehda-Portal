from .constants import APPROXIMATE_DECIMALS


def approximate(latitude, longitude):
    """Round a point to about 1 km so a donor's exact spot is hidden."""
    return (
        round(float(latitude), APPROXIMATE_DECIMALS),
        round(float(longitude), APPROXIMATE_DECIMALS),
    )
