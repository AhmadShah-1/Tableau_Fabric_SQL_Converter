"""
Visualizer Module
=================

This module creates matplotlib-based visualizations of SQL conversion metrics,
displaying success rates, function type conversions, and error statistics in
separate popup windows.
"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import matplotlib.patches as mpatches
from datetime import datetime
import os


class ConversionVisualizer:
    """
    Creates visualizations for SQL conversion metrics using matplotlib.
    
    Generates bar charts and statistics showing conversion success rates,
    function type breakdowns, and error analysis in separate popup windows.
    """
    
    def __init__(self):
        """Initialize the visualizer with default settings."""
        # Set matplotlib style for better looking plots
        plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
        
        # Color scheme
        self.colors = {
            'success': '#2ecc71',  # Green
            'flagged': '#e74c3c',  # Red
            'warning': '#f39c12',  # Orange
            'info': '#3498db',     # Blue
            'date': '#9b59b6',     # Purple
            'string': '#1abc9c',   # Teal
            'aggregate': '#e67e22', # Dark Orange
            'logical': '#34495e',  # Dark Gray
            'mathematical': '#16a085', # Dark Teal
            'other': '#95a5a6'     # Light Gray
        }
    
    def visualize_conversion_metrics(self, metrics_dict, save_path=None):
        """
        Create comprehensive visualization of conversion metrics in a popup window.
        
        Args:
            metrics_dict (dict): Dictionary containing conversion metrics
            save_path (str, optional): Path to save the visualization as PNG
            
        Returns:
            Figure: The matplotlib figure object
        """
        # Create figure with subplots
        fig = plt.figure(figsize=(14, 10))
        fig.suptitle('Tableau to Fabric SQL Conversion Report', fontsize=16, fontweight='bold')
        
        # Create a 2x2 grid of subplots
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
        
        # Subplot 1: Overall Conversion Success Rate (top-left)
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_success_rate(ax1, metrics_dict)
        
        # Subplot 2: Function Type Breakdown (top-right)
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_function_breakdown(ax2, metrics_dict)
        
        # Subplot 3: Conversion Statistics (middle-left)
        ax3 = fig.add_subplot(gs[1, 0])
        self._plot_conversion_stats(ax3, metrics_dict)
        
        # Subplot 4: Flagged Items (middle-right)
        ax4 = fig.add_subplot(gs[1, 1])
        self._plot_flagged_items(ax4, metrics_dict)
        
        # Subplot 5: Summary Text (bottom, spanning both columns)
        ax5 = fig.add_subplot(gs[2, :])
        self._plot_summary_text(ax5, metrics_dict)
        
        # Add timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        fig.text(0.99, 0.01, f'Generated: {timestamp}', 
                ha='right', va='bottom', fontsize=8, style='italic')
        
        # Save if path provided
        if save_path:
            try:
                # Ensure directory exists
                directory = os.path.dirname(save_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory, exist_ok=True)
                
                plt.savefig(save_path, dpi=300, bbox_inches='tight')
            except Exception as e:
                print(f"Warning: Could not save visualization: {str(e)}")
        
        # Show the plot in a popup window
        plt.show(block=False)
        
        return fig
    
    def _plot_success_rate(self, ax, metrics_dict):
        """
        Plot overall conversion success rate as a horizontal bar.
        
        Args:
            ax: Matplotlib axes object
            metrics_dict (dict): Metrics dictionary
        """
        success_rate = metrics_dict.get('success_rate', 0)
        failure_rate = 100 - success_rate
        
        # Create horizontal bar
        bars = ax.barh(['Conversion'], [success_rate], color=self.colors['success'], 
                       label='Successful')
        ax.barh(['Conversion'], [failure_rate], left=[success_rate], 
               color=self.colors['flagged'], label='Flagged/Failed')
        
        # Add percentage labels
        ax.text(success_rate/2, 0, f'{success_rate:.1f}%', 
               ha='center', va='center', fontweight='bold', color='white')
        if failure_rate > 5:  # Only show if visible
            ax.text(success_rate + failure_rate/2, 0, f'{failure_rate:.1f}%', 
                   ha='center', va='center', fontweight='bold', color='white')
        
        ax.set_xlim(0, 100)
        ax.set_xlabel('Percentage (%)')
        ax.set_title('Overall Conversion Success Rate', fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(axis='x', alpha=0.3)
    
    def _plot_function_breakdown(self, ax, metrics_dict):
        """
        Plot function type conversion breakdown as a bar chart.
        
        Args:
            ax: Matplotlib axes object
            metrics_dict (dict): Metrics dictionary
        """
        function_conversions = metrics_dict.get('function_conversions', {})
        
        # Filter out zero values
        categories = [k for k, v in function_conversions.items() if v > 0]
        counts = [function_conversions[k] for k in categories]
        
        if not categories:
            ax.text(0.5, 0.5, 'No function conversions', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Function Type Conversions', fontweight='bold')
            return
        
        # Create color list based on category
        colors = [self.colors.get(cat.lower(), self.colors['other']) for cat in categories]
        
        # Create bar chart
        bars = ax.bar(categories, counts, color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)
        
        # Add count labels on top of bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{int(height)}',
                       ha='center', va='bottom', fontweight='bold')
        
        ax.set_ylabel('Number of Conversions')
        ax.set_title('Function Type Conversions', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    def _plot_conversion_stats(self, ax, metrics_dict):
        """
        Plot conversion statistics as a comparison bar chart.
        
        Args:
            ax: Matplotlib axes object
            metrics_dict (dict): Metrics dictionary
        """
        total = metrics_dict.get('total_statements', 0)
        successful = metrics_dict.get('successful_conversions', 0)
        flagged = metrics_dict.get('flagged_statements', 0)
        
        categories = ['Total\nStatements', 'Successful\nConversions', 'Flagged\nStatements']
        values = [total, successful, flagged]
        colors_list = [self.colors['info'], self.colors['success'], self.colors['flagged']]
        
        bars = ax.bar(categories, values, color=colors_list, alpha=0.8, 
                     edgecolor='black', linewidth=1.2)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontweight='bold', fontsize=12)
        
        ax.set_ylabel('Count')
        ax.set_title('Conversion Statistics', fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
    
    def _plot_flagged_items(self, ax, metrics_dict):
        """
        Plot information about flagged items.
        
        Args:
            ax: Matplotlib axes object
            metrics_dict (dict): Metrics dictionary
        """
        flagged_lines = metrics_dict.get('flagged_lines', [])
        unsupported_funcs = metrics_dict.get('unsupported_functions', [])
        
        # Turn off axis
        ax.axis('off')
        
        # Create text summary
        text_content = "Flagged Items for Manual Review\n" + "="*35 + "\n\n"
        
        if flagged_lines:
            text_content += f"Total Flagged Lines: {len(flagged_lines)}\n\n"
            text_content += "Sample Issues:\n"
            for i, (line_num, reason) in enumerate(flagged_lines[:5]):  # Show first 5
                text_content += f"  • Line {line_num}: {reason[:40]}...\n"
            if len(flagged_lines) > 5:
                text_content += f"  ... and {len(flagged_lines) - 5} more\n"
        else:
            text_content += "✓ No flagged lines\n\n"
        
        text_content += "\n"
        
        if unsupported_funcs:
            text_content += f"Unsupported Functions ({len(unsupported_funcs)}):\n"
            func_list = list(unsupported_funcs)[:8]  # Show first 8
            for func in func_list:
                text_content += f"  • {func}\n"
            if len(unsupported_funcs) > 8:
                text_content += f"  ... and {len(unsupported_funcs) - 8} more\n"
        else:
            text_content += "✓ All functions supported\n"
        
        # Display text
        ax.text(0.1, 0.9, text_content, transform=ax.transAxes,
               fontfamily='monospace', fontsize=9, verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        ax.set_title('Items Requiring Attention', fontweight='bold')
    
    def _plot_summary_text(self, ax, metrics_dict):
        """
        Plot summary text with key metrics.
        
        Args:
            ax: Matplotlib axes object
            metrics_dict (dict): Metrics dictionary
        """
        ax.axis('off')
        
        # Calculate summary statistics
        total = metrics_dict.get('total_statements', 0)
        successful = metrics_dict.get('successful_conversions', 0)
        success_rate = metrics_dict.get('success_rate', 0)
        total_functions = sum(metrics_dict.get('function_conversions', {}).values())
        
        # Create summary text
        summary = (
            f"CONVERSION SUMMARY\n"
            f"{'='*80}\n\n"
            f"Total SQL Statements Processed: {total}\n"
            f"Successfully Converted: {successful} ({success_rate:.1f}%)\n"
            f"Total Function Conversions: {total_functions}\n\n"
            f"Status: "
        )
        
        if success_rate >= 90:
            summary += "✓ EXCELLENT - Conversion completed with minimal issues"
            color = self.colors['success']
        elif success_rate >= 70:
            summary += "⚠ GOOD - Some items may need manual review"
            color = self.colors['warning']
        else:
            summary += "⚠ ATTENTION NEEDED - Multiple items require manual review"
            color = self.colors['flagged']
        
        ax.text(0.5, 0.5, summary, transform=ax.transAxes,
               fontfamily='monospace', fontsize=10, verticalalignment='center',
               horizontalalignment='center',
               bbox=dict(boxstyle='round', facecolor=color, alpha=0.2, pad=1))
    
    def create_comparison_visualization(self, tableau_sql, fabric_sql):
        """
        Create a side-by-side comparison visualization of Tableau and Fabric SQL.
        
        This displays the before/after SQL in a visual format.
        
        Args:
            tableau_sql (str): Original Tableau SQL
            fabric_sql (str): Converted Fabric SQL
            
        Returns:
            Figure: The matplotlib figure object
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))
        fig.suptitle('SQL Conversion Comparison', fontsize=16, fontweight='bold')
        
        # Display Tableau SQL
        ax1.axis('off')
        ax1.text(0.05, 0.95, 'TABLEAU SQL (Before)', transform=ax1.transAxes,
                fontsize=12, fontweight='bold', verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
        ax1.text(0.05, 0.88, tableau_sql[:1000], transform=ax1.transAxes,
                fontfamily='monospace', fontsize=8, verticalalignment='top',
                wrap=True)
        
        # Display Fabric SQL
        ax2.axis('off')
        ax2.text(0.05, 0.95, 'FABRIC SQL (After)', transform=ax2.transAxes,
                fontsize=12, fontweight='bold', verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
        ax2.text(0.05, 0.88, fabric_sql[:1000], transform=ax2.transAxes,
                fontfamily='monospace', fontsize=8, verticalalignment='top',
                wrap=True)
        
        plt.tight_layout()
        plt.show(block=False)
        
        return fig
    
    def close_all_plots(self):
        """Close all open matplotlib windows."""
        plt.close('all')

