# Web Cloner & Analyzer

A powerful and modular Python framework designed to clone web assets, parse HTML/JS, analyze hidden API endpoints, and map workspace structures.

## Features

- **Interactive Domain Input**: Run the script with or without command-line arguments.
- **Resource Fetching & Saving**: Automatically downloads HTML and corresponding web assets locally.
- **API & Endpoint Discovery**: Static analysis of JavaScript and HTML files to find potential API routes.
- **API Verification**: Live verification of discovered endpoints to confirm activity.
- **Compiler Engine**: Generates a complete directory tree and exports structured intelligence reports of the cloned workspace.

## Project Structure

- `main.py` - The main entry point that orchestrates the execution flow.
- `mon/` - Core package housing the specific operational modules:
  - `fetcher.py` - Handles HTTP requests and retrieves raw HTML.
  - `saver.py` - Saves HTML and downloads assets to local directories.
  - `parser.py` - Extracts links, scripts, and media resources.
  - `api_analyzer.py` - Inspects JavaScript and source files to map endpoints.
  - `api_verifier.py` - Validates the responsiveness of identified APIs.
  - `explorer.py` - Scans local directories to build structured system trees.
  - `compiler_engine.py` - Organizes gathered telemetry and exports the final execution reports.
  - `utils.py` - Contains common utility functions used across the library.

## Installation

Install the required dependencies prior to running the cloner:

```bash
pip install requests beautifulsoup4
