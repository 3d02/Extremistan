import pytest
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from unittest.mock import patch, MagicMock
from market_monitor.ui.dashboard import MatplotlibDashboard

def test_dashboard_render_smoke():
    """
    Smoke test to verify that MatplotlibDashboard.render executes without error
    given valid input data.
    """
    # Create dummy data
    dates = pd.date_range(start='2020-01-01', periods=100)
    df = pd.DataFrame(index=dates)
    df['SPX'] = np.random.uniform(3000, 4000, size=100)
    df['VIX'] = np.random.uniform(10, 30, size=100)
    df['Slope'] = np.random.uniform(-1, 2, size=100)
    df['Log_Return'] = np.random.normal(0, 0.01, size=100)
    df['Drawdown'] = np.random.uniform(-0.1, 0, size=100)

    # Introduce some outliers
    df.iloc[10, df.columns.get_loc('Log_Return')] = 0.06 # Likely > 5 sigma
    df.iloc[20, df.columns.get_loc('Log_Return')] = 0.12 # Likely > 10 sigma

    context = {
        'lifetime_sigma': 0.01,
        'lifetime_mad': 0.008
    }

    dashboard = MatplotlibDashboard()

    # Mock plt.show so we don't actually open a window
    with patch('matplotlib.pyplot.show') as mock_show:
        dashboard.render(df, context)

        # Verify show was called
        mock_show.assert_called_once()

    # Close figures to avoid memory leaks
    plt.close('all')

if __name__ == "__main__":
    test_dashboard_render_smoke()
