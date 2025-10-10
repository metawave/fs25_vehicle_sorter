import datetime
import os.path
from xml.etree import cElementTree as ET
from xml.etree.ElementTree import ElementTree, Element

from .model import Vehicle


class VehiclesXml:
    """Handles loading and saving FS25 savegame vehicles.xml files.

    FS25 Format:
    - Uses uniqueId (hash strings) instead of numeric IDs
    - TAB order is determined by vehicle element order in XML
    - Attachments are inline via attacherJoints/attachedImplement
    - No separate attachments section
    """
    savegame_folder: str
    vehicle_xml_tree: ElementTree
    vehicle_root: Element
    all_vehicles: list[Vehicle] = []  # All vehicles (for lookups)
    vehicles_list: list[Vehicle] = []  # Displayed vehicles (tabbable by default)
    show_all_vehicles: bool = False

    def load_savegame(self, savegame_folder: str):
        """Load vehicles from savegame folder."""
        self.all_vehicles = []
        self.vehicles_list = []
        self.savegame_folder = savegame_folder
        vehicle_xml_path = os.path.join(savegame_folder, "vehicles.xml")
        if not os.path.exists(vehicle_xml_path):
            raise FileNotFoundError

        self.vehicle_xml_tree = ET.parse(vehicle_xml_path)
        self.vehicle_root = self.vehicle_xml_tree.getroot()

        # Parse all vehicles in order
        for vehicle_node in self.vehicle_root.findall("vehicle"):
            vehicle = Vehicle(vehicle_node)
            self.all_vehicles.append(vehicle)
            # Only add tabbable vehicles to the display list by default
            if self.show_all_vehicles or vehicle.is_tabbable:
                self.vehicles_list.append(vehicle)

        return self

    def save_savegame(self):
        """Save vehicles back to XML in the current list order.

        FS25 determines TAB order by vehicle element order in XML,
        so we simply reorder the XML elements to match all_vehicles order.
        Note: We need to reorder ALL vehicles, not just tabbable ones.
        """
        # Create a mapping of uniqueId to position in all_vehicles
        vehicle_order = {v.unique_id: idx for idx, v in enumerate(self.all_vehicles)}

        # Reorder XML elements based on all_vehicles order
        self.vehicle_root[:] = sorted(
            self.vehicle_root,
            key=lambda child: vehicle_order.get(child.get("uniqueId"), 999999)
        )

        # Make a backup copy of the old vehicles.xml
        current_datetime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        backup_path = os.path.join(self.savegame_folder, "vehicles_" + current_datetime + ".xml")
        original_path = os.path.join(self.savegame_folder, "vehicles.xml")
        os.rename(original_path, backup_path)

        # Write the updated XML
        self.vehicle_xml_tree.write(original_path, xml_declaration=True, encoding="utf-8")

        # Reload to refresh in-memory state
        self.load_savegame(self.savegame_folder)

    def sort_vehicles_by_name(self):
        """Sort vehicles alphabetically by name.

        Updates both vehicles_list and all_vehicles to maintain consistency.
        """
        # Sort the display list
        self.vehicles_list = sorted(self.vehicles_list, key=lambda v: v.name.lower())

        # Rebuild all_vehicles with tabbable vehicles in sorted order
        # Keep non-tabbable vehicles in their original positions
        tabbable_sorted = {v.unique_id: idx for idx, v in enumerate(self.vehicles_list)}

        def sort_key(vehicle):
            if vehicle.is_tabbable:
                # Use sorted order for tabbable vehicles
                return (0, tabbable_sorted.get(vehicle.unique_id, 9999))
            else:
                # Keep non-tabbable at the beginning (they come before tabbable ones)
                return (-1, self.all_vehicles.index(vehicle))

        self.all_vehicles = sorted(self.all_vehicles, key=sort_key)

    def get_attached_to(self, vehicle: Vehicle) -> Vehicle | None:
        """Find which vehicle (if any) this vehicle is attached to.

        In FS25, vehicle A is attached to vehicle B if B's attacherJoints
        contains an attachedImplement with attachedVehicleUniqueId = A's uniqueId.
        """
        for potential_parent in self.all_vehicles:
            attached_ids = potential_parent.get_attached_vehicle_ids()
            if vehicle.unique_id in attached_ids:
                return potential_parent
        return None

    def get_attached_vehicles(self, vehicle: Vehicle) -> list[Vehicle]:
        """Get list of vehicles attached TO this vehicle."""
        attached_ids = vehicle.get_attached_vehicle_ids()
        attached_vehicles = []
        for v in self.all_vehicles:
            if v.unique_id in attached_ids:
                attached_vehicles.append(v)
        return attached_vehicles

    def move_up(self, vehicle: Vehicle, positions: int = 1) -> int:
        """Move vehicle up in the list (earlier TAB order).

        Updates both vehicles_list (display) and all_vehicles (save order).
        """
        # Move in display list
        current_index = self.vehicles_list.index(vehicle)
        if current_index - positions < 0:
            positions = min(current_index, positions)

        moved_vehicle = self.vehicles_list.pop(current_index)
        new_index = current_index - positions
        self.vehicles_list.insert(new_index, moved_vehicle)

        # Update all_vehicles: find the correct position based on neighboring tabbable vehicles
        self.all_vehicles.remove(vehicle)

        if new_index == 0:
            # Moving to first position - find first tabbable in all_vehicles and insert before it
            for i, v in enumerate(self.all_vehicles):
                if v.is_tabbable:
                    self.all_vehicles.insert(i, vehicle)
                    break
            else:
                # No other tabbable vehicles, insert at start
                self.all_vehicles.insert(0, vehicle)
        else:
            # Insert after the previous vehicle in vehicles_list
            prev_vehicle = self.vehicles_list[new_index - 1]
            prev_all_index = self.all_vehicles.index(prev_vehicle)
            self.all_vehicles.insert(prev_all_index + 1, vehicle)

        return new_index

    def move_down(self, vehicle: Vehicle, positions: int = 1) -> int:
        """Move vehicle down in the list (later TAB order).

        Updates both vehicles_list (display) and all_vehicles (save order).
        """
        # Move in display list
        current_index = self.vehicles_list.index(vehicle)
        if current_index + positions > len(self.vehicles_list) - 1:
            positions = min(len(self.vehicles_list) - 1 - current_index, positions)

        moved_vehicle = self.vehicles_list.pop(current_index)
        new_index = current_index + positions
        self.vehicles_list.insert(new_index, moved_vehicle)

        # Update all_vehicles: find the correct position based on neighboring tabbable vehicles
        self.all_vehicles.remove(vehicle)

        if new_index >= len(self.vehicles_list) - 1:
            # Moving to last position - find last tabbable in all_vehicles and insert after it
            for i in range(len(self.all_vehicles) - 1, -1, -1):
                if self.all_vehicles[i].is_tabbable:
                    self.all_vehicles.insert(i + 1, vehicle)
                    break
            else:
                # No other tabbable vehicles, insert at end
                self.all_vehicles.append(vehicle)
        else:
            # Insert before the next vehicle in vehicles_list
            next_vehicle = self.vehicles_list[new_index + 1]
            next_all_index = self.all_vehicles.index(next_vehicle)
            self.all_vehicles.insert(next_all_index, vehicle)

        return new_index