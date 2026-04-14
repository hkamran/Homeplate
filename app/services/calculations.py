def calc_so_pct(strikeouts, plate_appearances):
    """Calculate strikeout percentage: SO / PA."""
    if plate_appearances is None or plate_appearances == 0:
        return None
    return round(strikeouts / plate_appearances * 100, 1)


def calc_bb_pct(walks, plate_appearances):
    """Calculate walk percentage: BB / PA."""
    if plate_appearances is None or plate_appearances == 0:
        return None
    return round(walks / plate_appearances * 100, 1)
