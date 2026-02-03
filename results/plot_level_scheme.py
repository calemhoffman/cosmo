#!/usr/bin/env python3
"""
Plot nuclear level scheme from ASCII GLS file format.
Parses level and gamma transition data and creates a visual representation.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch
import numpy as np
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Level:
    """Represents a nuclear energy level."""
    number: int
    energy: float
    energy_err: float
    jpi: str
    k: int
    band: int
    level_flag: int
    label_flag: int
    enlabel_flag: int
    
    def format_jpi(self) -> str:
        """Format J^pi for display."""
        return self.jpi.strip()


@dataclass
class Gamma:
    """Represents a gamma-ray transition."""
    number: int
    energy: float
    energy_err: float
    multipolarity: str
    initial_level: int
    final_level: int
    intensity: float
    intensity_err: float
    conv_coef: float
    
    def format_multipolarity(self) -> str:
        """Format multipolarity for display."""
        return self.multipolarity.strip()


class LevelSchemeParser:
    """Parser for ASCII GLS format files."""
    
    def __init__(self, filename: str):
        self.filename = filename
        self.z = 0
        self.nlevels = 0
        self.ngammas = 0
        self.nbands = 0
        self.levels: List[Level] = []
        self.gammas: List[Gamma] = []
        self.bands = {}
        
    def parse(self):
        """Parse the GLS file."""
        with open(self.filename, 'r') as f:
            lines = f.readlines()
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Parse header with Z, Nlevels, Ngammas, Nbands
            if line.startswith('**') and 'Nlevels' in line:
                i += 1
                parts = lines[i].split()
                self.z = int(parts[0])
                self.nlevels = int(parts[1])
                self.ngammas = int(parts[2])
                self.nbands = int(parts[3])
            
            # Parse levels
            elif line.startswith('** Level') and 'Energy' in line:
                i += 2  # Skip the ++ line
                for _ in range(self.nlevels):
                    level_line = lines[i].strip()
                    if level_line.startswith('++'):
                        i += 1
                        continue
                    
                    parts = level_line.split()
                    level = Level(
                        number=int(parts[0]),
                        energy=float(parts[1]),
                        energy_err=float(parts[2]),
                        jpi=parts[3],
                        k=int(parts[4]),
                        band=int(parts[5]),
                        level_flag=int(parts[6]),
                        label_flag=int(parts[7]),
                        enlabel_flag=int(parts[8])
                    )
                    self.levels.append(level)
                    i += 2  # Skip the ++ line
                continue
            
            # Parse bands
            elif line.startswith('** Band') and 'Name' in line:
                i += 1
                for _ in range(self.nbands):
                    band_line = lines[i].strip()
                    parts = band_line.split()
                    band_num = int(parts[0])
                    band_name = parts[1]
                    self.bands[band_num] = band_name
                    i += 1
                continue
            
            # Parse gamma transitions
            elif line.startswith('** Gamma') and 'Energy' in line:
                i += 2  # Skip the ++ lines describing format
                gamma_count = 0
                while gamma_count < self.ngammas and i < len(lines):
                    gamma_line = lines[i].strip()
                    
                    # Skip empty lines or ++ lines at start
                    if not gamma_line or gamma_line.startswith('**'):
                        i += 1
                        continue
                    
                    # This should be the main gamma line
                    if not gamma_line.startswith('++'):
                        parts = gamma_line.split()
                        
                        # Multipolarity can be "M 1", "E 2", etc. (two parts) or just "M1", "E1" (one part)
                        # Need to combine them and adjust indices accordingly
                        # Format: number energy err mult [mult_num] ILev FLev intensity intensity_err
                        
                        # Check if parts[4] is a number (multipolarity number) or ILev
                        try:
                            # If parts[4] is a small integer (1-4), it's likely the multipolarity number
                            mult_num = int(parts[4])
                            if mult_num <= 4:  # M1, E1, M2, E2, etc.
                                multipolarity = f"{parts[3]} {parts[4]}"
                                ilev_idx = 5
                                flev_idx = 6
                                intensity_idx = 7
                                intensity_err_idx = 8
                            else:
                                # It's actually ILev (level numbers are > 4)
                                multipolarity = parts[3]
                                ilev_idx = 4
                                flev_idx = 5
                                intensity_idx = 6
                                intensity_err_idx = 7
                        except (ValueError, IndexError):
                            # Not a number, so multipolarity is just parts[3]
                            multipolarity = parts[3]
                            ilev_idx = 4
                            flev_idx = 5
                            intensity_idx = 6
                            intensity_err_idx = 7
                        
                        gamma = Gamma(
                            number=int(parts[0]),
                            energy=float(parts[1]),
                            energy_err=float(parts[2]),
                            multipolarity=multipolarity,
                            initial_level=int(parts[ilev_idx]),
                            final_level=int(parts[flev_idx]),
                            intensity=float(parts[intensity_idx]),
                            intensity_err=float(parts[intensity_err_idx]),
                            conv_coef=0.0  # Will be updated from next line
                        )
                        
                        # Next line should be ++ with conversion coefficient
                        i += 1
                        if i < len(lines):
                            conv_line = lines[i].strip()
                            if conv_line.startswith('++'):
                                conv_parts = conv_line.split()
                                if len(conv_parts) > 1:
                                    gamma.conv_coef = float(conv_parts[1])
                        
                        # Next line should be ++ with position data
                        i += 1
                        
                        self.gammas.append(gamma)
                        gamma_count += 1
                    
                    i += 1
                continue
            
            i += 1


class LevelSchemePlotter:
    """Create visual representation of nuclear level scheme."""
    
    def __init__(self, parser: LevelSchemeParser):
        self.parser = parser
        self.fig = None
        self.ax = None
        
        # Visual parameters
        self.level_width = 1.0
        self.band_spacing = 2.5
        self.energy_scale = 0.001  # Scale factor for vertical spacing
        
    def _assign_columns(self):
        """Intelligently assign levels to columns based on energy and connections."""
        # Strategy: Create columns based on energy ranges and minimize crossing transitions
        # Start with low energy levels in leftmost columns
        
        sorted_levels = sorted(self.parser.levels, key=lambda l: l.energy)
        
        # Assign columns - try to group levels that are connected
        level_columns = {}
        num_columns = 4  # Start with 4 columns
        
        # Simple strategy: distribute levels across columns by energy
        levels_per_column = len(sorted_levels) // num_columns + 1
        
        for i, level in enumerate(sorted_levels):
            col = min(i // levels_per_column, num_columns - 1)
            level_columns[level.number] = col
        
        return level_columns, num_columns
    
    def plot(self, output_file: Optional[str] = None):
        """Create the level scheme plot."""
        # Create figure with larger size for better readability
        self.fig, self.ax = plt.subplots(figsize=(18, 20))
        
        # Assign levels to columns intelligently
        level_columns, num_columns = self._assign_columns()
        
        # Calculate x-positions for each column
        column_spacing = 3.0
        column_x_positions = {i: i * column_spacing for i in range(num_columns)}
        
        # Calculate intensity range for arrow width scaling
        intensities = [g.intensity for g in self.parser.gammas]
        max_intensity = max(intensities) if intensities else 100.0
        min_intensity = min(intensities) if intensities else 1.0
        
        # Plot levels
        level_positions = {}
        for level in self.parser.levels:
            col = level_columns[level.number]
            x_pos = column_x_positions[col]
            y_pos = level.energy * self.energy_scale
            level_positions[level.number] = (x_pos, y_pos)
            
            # Draw level line
            self.ax.plot([x_pos - self.level_width/2, x_pos + self.level_width/2],
                       [y_pos, y_pos], 'k-', linewidth=2.5, zorder=3)
            
            # Add level energy label (left side)
            energy_label = f"{level.energy:.1f}"
            self.ax.text(x_pos - self.level_width/2 - 0.15, y_pos, energy_label,
                       ha='right', va='center', fontsize=8, fontweight='bold', zorder=4)
            
            # Add J^pi label (right side)
            jpi_label = level.format_jpi()
            self.ax.text(x_pos + self.level_width/2 + 0.15, y_pos, jpi_label,
                       ha='left', va='center', fontsize=8, fontweight='bold', zorder=4)
        
        # Plot gamma transitions with intensity-based widths
        for idx, gamma in enumerate(self.parser.gammas):
            if gamma.initial_level in level_positions and gamma.final_level in level_positions:
                x_i, y_i = level_positions[gamma.initial_level]
                x_f, y_f = level_positions[gamma.final_level]
                
                # Calculate arrow width based on relative intensity
                # Scale from 0.5 to 3.0 based on intensity
                if max_intensity > min_intensity:
                    intensity_fraction = (gamma.intensity - min_intensity) / (max_intensity - min_intensity)
                else:
                    intensity_fraction = 0.5
                arrow_width = 0.5 + 2.5 * intensity_fraction
                
                # Determine arrow position offset for multiple transitions
                if x_i == x_f:
                    # Count how many transitions we've already drawn from this level
                    same_level_count = sum(1 for g in self.parser.gammas[:idx] 
                                          if g.initial_level == gamma.initial_level 
                                          and level_positions.get(g.final_level, (None, None))[0] == x_f)
                    offset = 0.08 * (same_level_count % 5 - 2)
                else:
                    offset = 0
                
                # Draw arrow for transition with intensity-based width
                arrow = FancyArrowPatch(
                    (x_i + offset, y_i),
                    (x_f + offset, y_f),
                    arrowstyle='->,head_width=0.15,head_length=0.2',
                    color='red',
                    linewidth=arrow_width,
                    alpha=0.6,
                    zorder=2
                )
                self.ax.add_patch(arrow)
        
        # Set axis properties
        self.ax.set_xlabel('', fontsize=12)
        self.ax.set_ylabel('Energy (keV)', fontsize=16, fontweight='bold')
        self.ax.set_title(f'$^{{38}}$Cl Level Scheme', fontsize=18, fontweight='bold', pad=20)
        
        # Set y-axis to show actual energies
        self.ax.yaxis.set_major_locator(plt.MaxNLocator(20))
        y_ticks = self.ax.get_yticks()
        self.ax.set_yticklabels([f'{int(y/self.energy_scale)}' for y in y_ticks])
        
        # Remove x-axis ticks
        self.ax.set_xticks([])
        
        # Set limits with some padding
        all_x = [pos[0] for pos in level_positions.values()]
        self.ax.set_xlim(min(all_x) - 1.5, max(all_x) + 1.5)
        
        max_energy = max(level.energy for level in self.parser.levels)
        y_top = max_energy * self.energy_scale
        self.ax.set_ylim(-0.5, y_top + 0.5)
        
        # Grid
        self.ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
        
        # Add legend for intensity
        legend_x = max(all_x) + 0.5
        legend_y_start = y_top * 0.9
        self.ax.text(legend_x, legend_y_start, 'Intensity', 
                   fontsize=10, fontweight='bold', ha='left')
        
        # Draw sample arrows for legend
        for i, (label, fraction) in enumerate([('High', 1.0), ('Medium', 0.5), ('Low', 0.1)]):
            y_pos = legend_y_start - (i + 1) * 0.8
            width = 0.5 + 2.5 * fraction
            self.ax.plot([legend_x, legend_x + 0.5], [y_pos, y_pos], 
                       'r-', linewidth=width, alpha=0.6)
            self.ax.text(legend_x + 0.6, y_pos, label, 
                       fontsize=8, va='center', ha='left')
        
        plt.tight_layout()
        
        # Save or show
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Level scheme saved to {output_file}")
        else:
            plt.show()


def main():
    """Main function to parse and plot level scheme."""
    import sys
    
    # Input file
    input_file = '/Users/calemhoffman/Documents/GitHub/cosmo/results/38Cl_yjc.txt'
    output_file = '/Users/calemhoffman/Documents/GitHub/cosmo/results/38Cl_level_scheme.png'
    
    # Parse the file
    print(f"Parsing {input_file}...")
    parser = LevelSchemeParser(input_file)
    parser.parse()
    
    print(f"Found {len(parser.levels)} levels and {len(parser.gammas)} gamma transitions")
    print(f"Bands: {parser.bands}")
    
    # Create plot
    print("Creating level scheme plot...")
    plotter = LevelSchemePlotter(parser)
    plotter.plot(output_file)
    
    print("Done!")


if __name__ == '__main__':
    main()
