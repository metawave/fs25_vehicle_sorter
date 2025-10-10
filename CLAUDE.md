# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FS25 Vehicle Sorter is a Python desktop application that allows Farming Simulator 2025 players to reorder vehicles in their savegame. The app modifies the `vehicles.xml` file in the savegame folder to change the TAB-cycling order of vehicles in the game.

## Architecture

### Project Structure

The project follows the modern Python src/ layout:
- **main.py** - Root-level entry point that imports and runs the application
- **src/fs25_vehicle_sorter/** - Main package containing all application code
- **pyproject.toml** - Modern Python project configuration with dependency groups

### Core Components

1. **src/fs25_vehicle_sorter/main.py** - GUI application entry point using FreeSimpleGUI. Handles all UI events, vehicle selection, and movement operations. The main event loop processes user interactions and updates the vehicle list display.

2. **src/fs25_vehicle_sorter/vehicle_xml.py (VehiclesXml class)** - Core business logic for loading/saving savegames and manipulating vehicle order. This class:
   - Parses the `vehicles.xml` file from savegame folders
   - Maintains `vehicles_list` (list of Vehicle objects) representing the current order
   - Provides `move_up()` and `move_down()` methods to reposition vehicles in the list
   - On save, reorders XML `<vehicle>` elements to match the vehicles_list order
   - Creates timestamped backups before overwriting `vehicles.xml`

3. **src/fs25_vehicle_sorter/model.py (Vehicle class)** - Simple data model representing a vehicle with properties:
   - `unique_id` - FS25's hash-based vehicle identifier (e.g., "vehicle18dfe4fe5acb6b8413a82c48a4ef62db")
   - `name` - Extracted from filename, with mod name if applicable
   - `operating_time` - Converted to hours
   - `license_plates` - Character string from licensePlates element
   - `get_attached_vehicle_ids()` - Returns list of uniqueIds for attached implements

### FS25 Format Changes

FS25 significantly changed the vehicles.xml format from FS22:

**Key differences:**
- ✅ **No numeric IDs** - Uses hash-based `uniqueId` strings instead
- ✅ **No ID reassignment** - Vehicle order is determined by XML element order, not ID values
- ✅ **Inline attachments** - Uses `<attacherJoints>/<attachedImplement>` instead of separate `<attachments>` section
- ✅ **Simpler approach** - Just reorder XML elements, no complex ID tracking needed

**How it works:**
- TAB cycling order = order of `<vehicle>` elements in XML
- To reorder vehicles, we simply reorder the XML elements
- Attachment references use `attachedVehicleUniqueId` pointing to other vehicles' `uniqueId`
- No need to update references when reordering (they remain valid)

## Development Commands

This project uses [uv](https://docs.astral.sh/uv/) for Python version and dependency management. PyInstaller is configured as a dev dependency.

### Installing dependencies
```bash
uv sync
```

### Running the application
```bash
uv run python main.py
```

### Building the executable (PyInstaller)
```bash
uv run pyinstaller --onefile --name "FS25 Vehicle Sorter" --windowed main.py
```

### Code quality (Ruff)
```bash
# Check for linting issues
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Run both fix and format
uv run ruff check --fix . && uv run ruff format .
```

### Pre-commit hooks
Pre-commit hooks automatically run ruff before each commit:
```bash
# Install the hooks (one-time setup)
uv run pre-commit install

# Manually run hooks on all files
uv run pre-commit run --all-files

# Skip hooks for a specific commit (not recommended)
git commit --no-verify
```

## Platform-specific Notes

The app detects the platform and sets default savegame locations:
- **Windows**: `~\Documents\My Games\FarmingSimulator2025`
- **macOS**: `~/Library/Application Support/FarmingSimulator2025`

## Important Implementation Details

- **XML Element Ordering**: TAB order is determined by the order of `<vehicle>` elements in the XML file. When saving, we reorder these elements to match the vehicles_list order (src/fs25_vehicle_sorter/vehicle_xml.py:50-53).
- **Attachment Tracking**: Uses `uniqueId` references via `attachedVehicleUniqueId` attribute. These remain valid when reordering since we don't modify the uniqueId values.
- **Backup Creation**: Always creates a timestamped backup before saving (src/fs25_vehicle_sorter/vehicle_xml.py:56-59).
- **Reload After Save**: Always reload the savegame after saving (src/fs25_vehicle_sorter/vehicle_xml.py:65) to refresh the in-memory state.
- **Package Structure**: Uses relative imports (e.g., `from .model import Vehicle`) within the src/fs25_vehicle_sorter directory.