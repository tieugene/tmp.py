"""Explore signals"""
import sys
from typing import Optional

import comtrade


def _ps_mult(sig_cfg):
    if sig_cfg.pors.lower() == 'p':  # primary default
        return 1, sig_cfg.secondary / sig_cfg.primary
    else:  # secondary default
        return sig_cfg.primary / sig_cfg.secondary, 1


def pors(data: comtrade.Comtrade, sig_num: int = 0, lines: Optional[int] = None):
    """View primary/secondary values. QC OK"""
    ch_cfg = data.cfg.analog_channels[sig_num]
    ch_data = data.analog[sig_num]
    if lines is None:
        lines = len(ch_data)
    pri, sec = _ps_mult(ch_cfg)
    print("Name: ", ch_cfg.name)
    print("Raw\tPri\tSec\n===\t===\t===")
    for v in ch_data[:lines]:
        print("%.3f\t%.3f\t%.3f" % (v, v * pri, v * sec))


def mid(data: comtrade.Comtrade, sig_num: int, lines: Optional[int] = None):
    """View moving average values (numpy.ma.average)"""
    import numpy as np
    ch_cfg = data.cfg.analog_channels[sig_num]
    ch_data = data.analog[sig_num]
    if lines is None:
        lines = len(ch_data)
    pri, sec = _ps_mult(ch_cfg)
    tpp = round(data.cfg.sample_rates[0][0] / data.cfg.frequency)  # ticks per period
    # np.convolve(ch_data, np.ones(__tpp) / __tpp, mode='valid')  # all array
    print("Name: ", ch_cfg.name)
    # print("Orig: ", ch_data)
    mx, mn = max(ch_data), min(ch_data)
    print("Max: %.3f, Min: %.3f, D: %.3f, Mid: %.3f" % (mx, mn, mx-mn, (mx+mn)/2))
    print("#\tOriginal\tPrimary\tSecondary\n===\t====\t====\t====")
    norm = (max(ch_data) - min(ch_data)) / 4
    for i in range(lines):
        a = ch_data[i+1-tpp:i+1] if i+1 >= tpp else np.pad(ch_data[:i+1], (tpp-i-1, 0))
        # m = np.sum(ch_data[max(i-__tpp+1, 0):i+1]) / __tpp  # runnig mid
        # m = np.std(a)  # effective
        m = np.fft.fft(a)
        # print(np.around(m, 3))
        # print(i, np.around(np.absolute(m) / norm, 3)[:5])
        print(i, len(m), np.around(np.degrees(np.angle(m))[:5], 3))
        # print("%d\t%.3f\t%.3f\t%.3f" % (i, m, m * pri, m * sec))


def fft(data: comtrade.Comtrade, sig_num: int, lines: Optional[int] = None):
    """FFT"""
    def prepare_test() -> tuple:
        t = np.arange(256)  # int[256] of 0..255
        v = np.sin(t)  # float[256] of 0..1
        s: int = t.shape[-1]  # == 256
        f = np.fft.fftfreq(s)  # float[256] sample freqs of -0.5..0.5
        return v, f

    def show_it(d, f):
        import matplotlib.pyplot as plt
        plt.plot(f, d.real, f, d.imag)  #
        plt.show()

    import numpy as np
    ch_cfg = data.cfg.analog_channels[sig_num]
    ch_data = data.analog[sig_num]
    if lines is None:
        lines = len(ch_data)
    pri, sec = _ps_mult(ch_cfg)
    tpp = round(data.cfg.sample_rates[0][0] / data.cfg.frequency)  # ticks per period
    #
    val = data.analog[sig_num]  # 40 samples by 120Hz
    # val, frq = prepare_test()
    sp = np.fft.fft(val, 20)
    # frq = np.fft.fftfreq(len(val), 1.0/2400.0)  # d=1/2400 => -1200..1200 by 60
    # print(frq)  # 0, 60...1140, -1200..-60
    # print(val)
    print(sp.real)
    print(sp.imag)
    # show_it(sp, frq)


def main():
    if len(sys.argv) != 2:
        sys.exit(f"Usage: {sys.argv[0]} <comtrade_file>")
    rec = comtrade.Comtrade()
    rec.load(sys.argv[1])
    # go
    # pors(rec, 0, 5)
    mid(rec, 0)
    # fft(rec, 0)


if __name__ == '__main__':
    main()
