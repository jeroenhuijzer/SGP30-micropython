import machine
import time
from sgp30 import SGP30

scl = machine.Pin(22)
sda = machine.Pin(21)

i2c = machine.SoftI2C(scl, sda)

sensor = SGP30(i2c)

# test cases
SGP30_TVOC_BASELINE = 0x8000
SGP30_IAQ_BASELINE = 0x80018002
MIN_VALUE_TVOC = 0
MAX_VALUE_TVOC = 60000
MIN_VALUE_CO2 = 0
MAX_VALUE_CO2 = 60000
MIN_VALUE_ETHANOL = 0
MAX_VALUE_ETHANOL = 60000
MIN_VALUE_H2 = 0
MAX_VALUE_H2 = 60000
MAX_VALUE_HUMIDITY = 256000
MEASUREMENT_DURATION_USEC = 50000

def test():
    print("SGP30_no_humi_compensation")
    test_setup()
    sensor.sgp30_set_absolute_humidity(0)
    sgp30_run_tests()
    print("SGP30_with_humi_compensation")
    test_setup()
    sensor.sgp30_set_absolute_humidity(MAX_VALUE_HUMIDITY)
    sgp30_run_tests()
    print("SGP30_too_much_humidity")
    test_setup()
    try:
        sensor.sgp30_set_absolute_humidity(MAX_VALUE_HUMIDITY + 1)
        assert False
    except RuntimeError:
        assert True

def test_setup():
    sensor.sgp30_probe()


def sgp30_run_tests():
    serial = sensor.sgp30_get_serial_id()
    print('SGP30 serial:', serial)
    fs_version, product_type = sensor.sgp30_get_feature_set_version()
    print('FS: ', hex(fs_version), 'Type', product_type)

    # initialize IAQ
    sensor.sgp30_iaq_init()

    # For FS > 0x20: Set tvoc baseline to inceptive baseline
    if fs_version > 0x20:
        tvoc_baseline = sensor.sgp30_get_tvoc_inceptive_baseline()
        if tvoc_baseline == 0:
            tvoc_baseline = SGP30_TVOC_BASELINE
        sensor.sgp30_set_tvoc_baseline(tvoc_baseline)

    # Set IAQ baseline to SGP30_IAQ_BASELINE. Then get it back and check
    # if it is indeed set to this value
    sensor.sgp30_set_iaq_baseline(SGP30_IAQ_BASELINE)
    iaq_baseline = sensor.sgp30_get_iaq_baseline()
    assert iaq_baseline == SGP30_IAQ_BASELINE, "sgp30_get_iaq_baseline mismatch"

    # check sensor for defects
    test_result = sensor.sgp30_measure_test()
    assert test_result is True

    # iaq measurements (tvoc and co2)
    tvoc_ppb, co2_ppm = sensor.sgp30_measure_iaq_blocking_read()
    assert MIN_VALUE_TVOC <= tvoc_ppb <= MAX_VALUE_TVOC
    assert MIN_VALUE_CO2 <= co2_ppm <= MAX_VALUE_CO2
    print("TVOC: ", tvoc_ppb, "CO2: ", co2_ppm)

    sensor.sgp30_measure_iaq()
    time.sleep_us(MEASUREMENT_DURATION_USEC)
    tvoc_ppb, co2_ppm = sensor.sgp30_read_iaq()
    assert MIN_VALUE_TVOC <= tvoc_ppb <= MAX_VALUE_TVOC
    assert MIN_VALUE_CO2 <= co2_ppm <= MAX_VALUE_CO2
    print("TVOC: ", tvoc_ppb, "CO2: ", co2_ppm)

    # tvoc measurements
    tvoc_ppb = sensor.sgp30_measure_tvoc_blocking_read()
    assert MIN_VALUE_TVOC <= tvoc_ppb <= MAX_VALUE_TVOC
    print("TVOC: ", tvoc_ppb)

    sensor.sgp30_measure_tvoc()
    time.sleep_us(MEASUREMENT_DURATION_USEC)
    tvoc_ppb = sensor.sgp30_read_tvoc()
    assert MIN_VALUE_TVOC <= tvoc_ppb <= MAX_VALUE_TVOC
    print("TVOC: ", tvoc_ppb)

    # co2 measurements
    co2_ppm = sensor.sgp30_measure_co2_eq_blocking_read()
    assert MIN_VALUE_CO2 <= co2_ppm <= MAX_VALUE_CO2
    print("CO2: ", co2_ppm)

    sensor.sgp30_measure_co2_eq()
    time.sleep_us(MEASUREMENT_DURATION_USEC)
    co2_ppm = sensor.sgp30_read_co2_eq()
    assert MIN_VALUE_CO2 <= co2_ppm <= MAX_VALUE_CO2
    print("CO2: ", co2_ppm)

    # raw measurements
    ethanol_raw, h2_raw = sensor.sgp30_measure_raw_blocking_read()
    assert MIN_VALUE_ETHANOL <= ethanol_raw <= MAX_VALUE_ETHANOL
    assert MIN_VALUE_H2 <= h2_raw <= MAX_VALUE_H2
    print("ethanol: ", ethanol_raw, "h2: ", h2_raw)

    sensor.sgp30_measure_raw()
    time.sleep_us(MEASUREMENT_DURATION_USEC)
    ethanol_raw, h2_raw = sensor.sgp30_read_raw()
    assert MIN_VALUE_ETHANOL <= ethanol_raw <= MAX_VALUE_ETHANOL
    assert MIN_VALUE_H2 <= h2_raw <= MAX_VALUE_H2
    print("ethanol: ", ethanol_raw, "h2: ", h2_raw)

test()