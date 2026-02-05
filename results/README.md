# Spectroscopy Data Viewer

Interactive web-based tool for visualizing nuclear spectroscopic factors from shell model calculations.

## Requirements

- **Python 3.x** (any version)
- **Web browser** (Chrome, Firefox, Safari, or Edge)

## Quick Start

1. **Extract the files** to a folder containing:
   - `theory_viewer.html`
   - `theory_data.json`

2. **Start a local web server** in the folder:
   ```bash
   python3 -m http.server 8000
   ```

3. **Open your browser** and navigate to:
   ```
   http://localhost:8000/theory_viewer.html
   ```

4. **Stop the server** when done:
   - Press `Ctrl+C` in the terminal

## Features

- **Interactive filtering** by parent state, daughter state, angular momentum (L), and energy ranges
- **Multiple plot modes**: SF, G, and normalized versions
- **Searchable data table** with all calculated values
- **Live statistics** showing record counts and unique states
- **Export plots** as PNG images using the Plotly toolbar

## Data

Current dataset: **³⁵Cl(d,p)³⁴Cl** spectroscopic factors
- 179 transitions to ground state (3+) and first excited state (0+)
- Calculated using FSU9 interaction

## Regenerating Data

To process new data files, use `theory_mg.py`:

```bash
python3 theory_mg.py
```

This will create a new `theory_data.json` file. Refresh the browser to see updated data.

---

**Note**: The viewer must be accessed through a local server (not by opening the HTML file directly) due to browser security restrictions on loading JSON files.
