from app.services.calculations import calc_bb_pct, calc_so_pct


class TestCalcSoPct:
    def test_normal_calculation(self):
        assert calc_so_pct(30, 200) == 15.0

    def test_zero_strikeouts(self):
        assert calc_so_pct(0, 200) == 0.0

    def test_zero_plate_appearances(self):
        assert calc_so_pct(10, 0) is None

    def test_none_plate_appearances(self):
        assert calc_so_pct(10, None) is None

    def test_rounds_to_one_decimal(self):
        # 97 / 633 = 15.3238...
        assert calc_so_pct(97, 633) == 15.3


class TestCalcBbPct:
    def test_normal_calculation(self):
        assert calc_bb_pct(50, 500) == 10.0

    def test_zero_walks(self):
        assert calc_bb_pct(0, 300) == 0.0

    def test_zero_plate_appearances(self):
        assert calc_bb_pct(10, 0) is None

    def test_none_plate_appearances(self):
        assert calc_bb_pct(10, None) is None

    def test_rounds_to_one_decimal(self):
        # 26 / 633 = 4.1074...
        assert calc_bb_pct(26, 633) == 4.1
