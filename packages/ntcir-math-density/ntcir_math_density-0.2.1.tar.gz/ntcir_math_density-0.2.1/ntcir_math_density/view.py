"""
These are the plotting functions for the NTCIR Math Density Estimator package.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa:E402


ESTIMATE_TITLES = [
    "$\\hat P$(relevant)", "$\\hat p$(position)", "$\\hat p$(position | relevant)",
    "$\\hat P$(position, relevant)", "$\\hat P$(relevant | position)"]
FIGURE_HEIGHT = 4
LINE_COLOR = (0.8, 0.8, 0.8)
LINE_WIDTH = 4
SUBPLOT_WIDTH = 8


def plot_estimates(positions, estimates):
    """
    Plots density, and probability estimates.

    Parameters
    ----------
    positions : iterable of float
        Paragraph positions for which densities, and probabilities were estimated.
    estimates : six-tuple of (sequence of float)
        Estimates of P(relevant), p(position), p(position | relevant), P(position, relevant), and
        P(relevant | position).

    Returns
    -------
    matplotlib.figure.Figure
        The plotted figure.
    """
    x = list(positions)
    fig = plt.figure(figsize=(SUBPLOT_WIDTH * len(estimates), FIGURE_HEIGHT))
    for i, (title, y) in enumerate(zip(ESTIMATE_TITLES, estimates)):
        ax = fig.add_subplot(1, len(estimates), i + 1)
        ax.plot(x, y, linewidth=LINE_WIDTH, c=LINE_COLOR)
        ax.title.set_text(title)
        ax.set_xlim(0, 1)
        ax.set_xlabel("position")
        ax.set_ylabel("$\\hat P$")
        ax.grid()
    return fig
