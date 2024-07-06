# plot_gallery.py - different types of plots for comparing versions
# RMM, 19 Jun 2024
#
# This file collects together some of the more interesting plots that can
# be generated by python-control and puts them into a PDF file that can be
# used to compare what things look like between different versions of the
# library.  It is mainly intended for uses by developers to make sure there
# are no unexpected changes in plot formats, but also has some interest
# examples of things you can plot.

import os
import sys
from math import pi

import matplotlib.pyplot as plt
import numpy as np

import control as ct

# Don't save figures if we are running CI tests
savefigs = 'PYCONTROL_TEST_EXAMPLES' not in os.environ
if savefigs:
    # Create a pdf file for storing the results
    import subprocess
    from matplotlib.backends.backend_pdf import PdfPages
    from datetime import date
    git_info = subprocess.check_output(['git', 'describe'], text=True).strip()
    pdf = PdfPages(
        f'plot_gallery-{git_info}-{date.today().isoformat()}.pdf')

# Context manager to handle plotting
class create_figure(object):
    def __init__(self, name):
        self.name = name
    def __enter__(self):
        self.fig = plt.figure()
        print(f"Generating {self.name} as Figure {self.fig.number}")
        return self.fig
    def __exit__(self, type, value, traceback):
        if type is not None:
            print(f"Exception: {type=}, {value=}, {traceback=}")
        if savefigs:
            pdf.savefig()
        if hasattr(sys, 'ps1'):
            # Show the figures on the screen
            plt.show(block=False)
        else:
            plt.close()

# Define systems to use throughout
sys1 = ct.tf([1], [1, 2, 1], name='sys1')
sys2 = ct.tf([1, 0.2], [1, 1, 3, 1, 1], name='sys2')
sys_mimo1 = ct.tf2ss(
    [[[1], [0.1]], [[0.2], [1]]],
    [[[1, 0.6, 1], [1, 1, 1]], [[1, 0.4, 1], [1, 2, 1]]], name="sys_mimo1")
sys_mimo2 = ct.tf2ss(
    [[[1], [0.1]], [[0.2], [1]]],
    [[[1, 0.2, 1], [1, 24, 22, 5]], [[1, 4, 16, 21], [1, 0.1]]],
    name="sys_mimo2")
sys_frd = ct.frd(
    [[np.array([10 + 0j, 5 - 5j, 1 - 1j, 0.5 - 1j, -.1j]),
      np.array([1j, 0.5 - 0.5j, -0.5, 0.1 - 0.1j, -.05j]) * 0.1],
     [np.array([10 + 0j, -20j, -10, 2j, 1]),
      np.array([10 + 0j, 5 - 5j, 1 - 1j, 0.5 - 1j, -.1j]) * 0.01]],
    np.logspace(-2, 2, 5))
sys_frd.name = 'frd'            # For backward compatibility

# Close all existing figures
plt.close('all')

# bode
with create_figure("Bode plot"):
    try:
        ct.bode_plot([sys_mimo1, sys_mimo2])
    except AttributeError:
        print("  - falling back to earlier method")
        plt.clf()
        ct.bode_plot(sys_mimo1)
        ct.bode_plot(sys_mimo2)

# describing function
with create_figure("Describing function plot"):
    H = ct.tf([1], [1, 2, 2, 1]) * 8
    F = ct.descfcn.saturation_nonlinearity(1)
    amp = np.linspace(1, 4, 10)
    ct.describing_function_response(H, F, amp).plot()

# nichols
with create_figure("Nichols chart"):
    response = ct.frequency_response([sys1, sys2])
    ct.nichols_plot(response)

# nyquist
with create_figure("Nyquist plot"):
    ct.nyquist_plot([sys1, sys2])

# phase plane
with create_figure("Phase plane plot"):
    def invpend_update(t, x, u, params):
        m, l, b, g = params['m'], params['l'], params['b'], params['g']
        return [x[1], -b/m * x[1] + (g * l / m) * np.sin(x[0]) + u[0]/m]
    invpend = ct.nlsys(invpend_update, states=2, inputs=1, name='invpend')
    ct.phase_plane_plot(
        invpend, [-2*pi, 2*pi, -2, 2], 5,
        gridtype='meshgrid', gridspec=[5, 8], arrows=3,
        plot_separatrices={'gridspec': [12, 9]},
        params={'m': 1, 'l': 1, 'b': 0.2, 'g': 1})

# pole zero map
with create_figure("Pole/zero map"):
    T = ct.tf(
        [-9.0250000e-01, -4.7200750e+01, -8.6812900e+02,
         +5.6261850e+03, +2.1258472e+05, +8.4724600e+05,
         +1.0192000e+06, +2.3520000e+05],
        [9.02500000e-03, 9.92862812e-01, 4.96974094e+01,
         1.35705659e+03, 2.09294163e+04, 1.64898435e+05,
         6.54572220e+05, 1.25274600e+06, 1.02420000e+06,
         2.35200000e+05], name='T')
    ct.pole_zero_plot([T, sys2])

# root locus
with create_figure("Root locus plot") as fig:
    ax1, ax2 = fig.subplots(2, 1)
    sys1 = ct.tf([1, 2], [1, 2, 3], name='sys1')
    sys2 = ct.tf([1, 0.2], [1, 1, 3, 1, 1], name='sys2')
    ct.root_locus_plot([sys1, sys2], grid=True, ax=ax1)
    ct.root_locus_plot([sys1, sys2], grid=False, ax=ax2)
    ct.suptitle("Root locus plots (w/ specified axes)")
    print("  -- BUG: should have 2 x 1 array of plots")

# sisotool
with create_figure("sisotool"):
    s = ct.tf('s')
    H = (s+0.3)/(s**4 + 4*s**3 + 6.25*s**2)
    ct.sisotool(H)

# step response
with create_figure("step response") as fig:
    try:
        ct.step_response([sys_mimo1, sys_mimo2]).plot()
    except ValueError:
        print("  - falling back to earlier method")
        fig.clf()
        ct.step_response(sys_mimo1).plot()
        ct.step_response(sys_mimo2).plot()

# time response
with create_figure("time response"):
    timepts = np.linspace(0, 10)
    
    U = np.vstack([np.sin(timepts), np.cos(2*timepts)])
    resp1 = ct.input_output_response(sys_mimo1, timepts, U)

    U = np.vstack([np.cos(2*timepts), np.sin(timepts)])
    resp2 = ct.input_output_response(sys_mimo1, timepts, U)

    resp = ct.combine_time_responses(
        [resp1, resp2], trace_labels=["resp1", "resp2"])
    resp.plot(transpose=True)

# Show the figures if running in interactive mode
if savefigs:
    pdf.close()
