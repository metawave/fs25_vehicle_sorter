# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FS25 Vehicle Sorter is a Python desktop application that allows Farming Simulator 2025 players to reorder vehicles in their savegame. The app modifies the `vehicles.xml` file in the savegame folder to change the TAB-cycling order of vehicles in the game.

## Architecture

### Core Components

1. **main.py** - GUI application entry point using FreeSimpleGUI. Handles all UI events, vehicle selection, and movement operations. The main event loop processes user interactions and updates the vehicle list display.

2. **vehicle_xml.py (VehiclesXml class)** - Core business logic for loading/saving savegames and manipulating vehicle order. This class:
   - Parses the `vehicles.xml` file from savegame folders
   - Maintains `vehicles_list` (list of Vehicle objects) representing the current order
   - Provides `move_up()` and `move_down()` methods to reposition vehicles in the list
   - On save, reassigns vehicle IDs based on list order and updates all references via OrderNotifier
   - Creates timestamped backups before overwriting `vehicles.xml`

3. **model.py** - Data models for Vehicle, Attachments, and Attachment classes. Each extends BaseModel and participates in the observer pattern through OrderNotifier. The `changed_id()` method allows each object to update its XML node when vehicle IDs are reassigned.

4. **order_notifier.py (OrderNotifier class)** - Observer pattern implementation. When vehicles are reordered and saved, it broadcasts ID changes to all registered models (vehicles and attachments) so they can update their XML references.

### Key Design Pattern

The ID reassignment system uses an observer pattern:
- All model objects register with OrderNotifier on initialization
- When `save_savegame()` is called, new IDs are assigned sequentially based on list order
- `OrderNotifier.notify_new_id()` broadcasts each ID change to all registered listeners
- Each model updates its own XML node attributes to reflect the new IDs
- This ensures attachment relationships remain valid after reordering

## Development Commands

This project uses [uv](https://docs.astral.sh/uv/) for Python version and dependency management.

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
uv run pyinstaller "FS25 Vehicle Sorter.spec"
```

## Platform-specific Notes

The app detects the platform and sets default savegame locations:
- **Windows**: `~\Documents\My Games\FarmingSimulator2025`
- **macOS**: `~/Library/Application Support/FarmingSimulator2025`

## Important Implementation Details

- Vehicle IDs must remain consistent with attachment references. The OrderNotifier pattern ensures all `attachmentId` and `rootVehicleId` values in the XML are updated when vehicles are reordered.
- The XML root element is sorted by ID and rootVehicleId after ID reassignment (vehicle_xml.py:50-52) to maintain proper structure.
- Always reload the savegame after saving (vehicle_xml.py:60) to refresh the in-memory state.