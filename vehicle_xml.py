import datetime
import os.path
from xml.etree import cElementTree as ET
from xml.etree.ElementTree import ElementTree, Element

from model import Vehicle, Attachments, Attachment
from order_notifier import OrderNotifier


class VehiclesXml:
    savegame_folder: str
    vehicle_xml_tree: ElementTree
    vehicle_root: Element

    order_notifier = OrderNotifier()

    vehicles_list: list[Vehicle] = []
    attachments_list: list[Attachments] = []
    attachment_list: list[Attachment] = []

    def load_savegame(self, savegame_folder: str):
        self.vehicles_list = []
        self.attachments_list = []
        self.savegame_folder = savegame_folder
        vehicle_xml_path = os.path.join(savegame_folder, "vehicles.xml")
        if not os.path.exists(vehicle_xml_path):
            raise FileNotFoundError

        self.vehicle_xml_tree = ET.parse(vehicle_xml_path)
        self.vehicle_root = self.vehicle_xml_tree.getroot()

        for vehicle in self.vehicle_root.iter("vehicle"):
            self.vehicles_list.append(Vehicle(self.order_notifier, vehicle))

        for attachments in self.vehicle_root.iter("attachments"):
            attachments_object = Attachments(self.order_notifier, attachments)
            self.attachments_list.append(attachments_object)
            self.attachment_list.extend(attachments_object.attachment_list)

        return self

    def save_savegame(self):
        # set the id according to the new order in the list
        i = 1
        for sorted_vehicle in self.vehicles_list:
            self.order_notifier.notify_new_id(sorted_vehicle.id, i)
            i = i + 1

        # reorder xml nodes to reflect the id order,
        self.vehicle_root[:] = sorted(self.vehicle_root, key=lambda child: (
            int(child.get("id")) if child.get("id") is not None else 888888,
            int(child.get("rootVehicleId")) if child.get("rootVehicleId") else 999999))

        # make a backup copy of the old vehicles.xml
        current_datetime = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        os.rename(os.path.join(self.savegame_folder, "vehicles.xml"),
                  os.path.join(self.savegame_folder, "vehicles_" + current_datetime + ".xml"))
        self.vehicle_xml_tree.write(os.path.join(self.savegame_folder, "vehicles.xml"), xml_declaration=True,
                                    encoding="utf-8")
        self.load_savegame(self.savegame_folder)

    def sort_vehicles_by_name(self):
        self.vehicles_list = sorted(self.vehicles_list, key=lambda v: v.name.lower())

    def get_attached_to(self, vehicle: Vehicle) -> Vehicle | None:
        for attachment in self.attachment_list:
            if attachment.attachment_id == vehicle.id:
                for v in self.vehicles_list:
                    if v.id == attachment.root_vehicle_id:
                        return v
        return None

    def move_up(self, vehicle: Vehicle, positions: int = 1) -> int:
        current_index = self.vehicles_list.index(vehicle)
        if current_index - positions < 0:
            positions = min(current_index, positions)

        moved_vehicle = self.vehicles_list.pop(current_index)
        self.vehicles_list.insert(current_index - positions, moved_vehicle)
        return current_index - positions

    def move_down(self, vehicle: Vehicle, positions: int = 1) -> int:
        current_index = self.vehicles_list.index(vehicle)
        if current_index + positions > len(self.vehicles_list) - 1:
            positions = min(len(self.vehicles_list) - 1 - current_index, positions)

        moved_vehicle = self.vehicles_list.pop(current_index)
        self.vehicles_list.insert(current_index + positions, moved_vehicle)
        return current_index + positions
