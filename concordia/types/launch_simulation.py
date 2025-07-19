"""
SimulationLauncher: A modular class for launching and logging Concordia simulations.
"""

import os
from typing import List, Dict, Any, Optional, Union


class SimulationLauncher:
    """
    A class to handle launching simulations and logging their outputs.
    
    This class provides a modular way to launch simulations, capture their outputs,
    and save the logs in various formats. It is designed to be scalable and extensible
    as the Concordia framework evolves.
    """
    
    def __init__(
        self,
        simulation_instance: Any,
        simulation_name: str,
        log_dir: Optional[str] = None,
        auto_create_log_dir: bool = True,
    ):
        """
        Initialize the SimulationLauncher.
        
        Args:
            simulation_instance: The instantiated simulation object to run
            simulation_name: String name to use for log files (required)
            log_dir: Directory path where logs should be saved
                     (default: concordia/logs/examples)
            auto_create_log_dir: Whether to automatically create the log directory if it doesn't exist
        """
        self.simulation_instance = simulation_instance
        self.simulation_name = simulation_name
        
        # Set default log directory if not specified
        if log_dir is None:
            # Assuming this is run from a script in the Concordia package
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            self.log_dir = os.path.join(base_dir, 'logs', 'examples')
        else:
            self.log_dir = log_dir
            
        # Create log directory if it doesn't exist and auto_create_log_dir is True
        if auto_create_log_dir:
            os.makedirs(self.log_dir, exist_ok=True)
    
    def run_simulation(
        self, 
        print_terminal_output: bool = True,
        save_terminal_log: bool = True,
        save_html_log: bool = True,
        terminal_log_suffix: str = 'terminal.log',
        html_log_suffix: str = 'html',
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run the simulation and handle logging.
        
        Args:
            print_terminal_output: Whether to print the terminal output during execution
            save_terminal_log: Whether to save terminal logs to a file
            save_html_log: Whether to save HTML logs to a file
            terminal_log_suffix: Suffix for terminal log filenames
            html_log_suffix: Suffix for HTML log filenames
            **kwargs: Additional arguments to pass to the simulation's play method
            
        Returns:
            A dictionary containing:
                - raw_log: List of raw log entries
                - results_log: HTML formatted results log
                - terminal_log_path: Path to saved terminal log (if saved)
                - html_log_path: Path to saved HTML log (if saved)
        """
        # Initialize empty raw_log list to capture terminal output
        raw_log = []
        
        # Run the simulation
        results_log = self.simulation_instance.play(
            raw_log=raw_log,
            **kwargs
        )
        
        # Prepare return dictionary
        return_data = {
            'raw_log': raw_log,
            'results_log': results_log,
        }
        
        # Save the terminal log if requested
        if save_terminal_log:
            # Use the provided simulation_name for the log file
            terminal_log_path = os.path.join(
                self.log_dir, f'{self.simulation_name}_{terminal_log_suffix}'
            )
            with open(terminal_log_path, 'w', encoding='utf-8') as f:
                for entry in raw_log:
                    f.write(str(entry) + '\n')
            return_data['terminal_log_path'] = terminal_log_path
        
        # Print the terminal output if requested
        if print_terminal_output:
            for entry in raw_log:
                print(entry)
        
        # Save the HTML log if requested
        if save_html_log:
            html_log_path = os.path.join(
                self.log_dir, f'{self.simulation_name}.{html_log_suffix}'
            )
            with open(html_log_path, 'w', encoding='utf-8') as f:
                f.write(results_log)
            return_data['html_log_path'] = html_log_path
        
        # Print file locations
        if save_terminal_log:
            print(f"\nTerminal log saved to: {return_data['terminal_log_path']}")
        if save_html_log:
            print(f"HTML log saved to: {return_data['html_log_path']}")
        
        return return_data
