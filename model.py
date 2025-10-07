from abc import abstractmethod
from xml.etree.ElementTree import Element

from order_notifier import OrderNotifier


class BaseModel:
    xml_node: Element

    def __init__(self, order_notifier: OrderNotifier, xml_node: Element):
        order_notifier.register(self)
        self.xml_node = xml_node

    @abstractmethod
    def changed_id(self, old_id: int, new_id: int):
        pass


class Vehicle(BaseModel):
    id: int
    name: str
    operating_time: float
    license_plates: str

    def __init__(self, order_notifier: OrderNotifier, xml_node: Element):
        super().__init__(order_notifier, xml_node)
        self.id = int(xml_node.get("id"))
        if xml_node.get("modName") is not None:
            self.name = xml_node.get("filename").split("/").pop().replace(".xml", "") + " (" + xml_node.get(
                "modName") + ")"
        else:
            self.name = xml_node.get("filename").split("/").pop().replace(".xml", "")
        self.operating_time = round(float(xml_node.get("operatingTime")) / 60 / 60, 1)
        license_plates_node = xml_node.find("licensePlates")
        if license_plates_node is not None:
            self.license_plates = license_plates_node.get("characters")
        else:
            self.license_plates = "[None]"

    def __str__(self):
        return str(self.id) + ': ' + self.name

    def changed_id(self, old_id: int, new_id: int):
        if self.id != old_id:
            return

        self.xml_node.set("id", str(new_id))


class Attachment(BaseModel):
    root_vehicle_id: int
    attachment_id: int

    def __init__(self, order_notifier: OrderNotifier, xml_node: Element, root_vehicle_id: int):
        super().__init__(order_notifier, xml_node)
        self.root_vehicle_id = root_vehicle_id
        self.attachment_id = int(xml_node.get("attachmentId"))

    def changed_id(self, old_id: int, new_id: int):
        if self.attachment_id != old_id:
            return

        self.xml_node.set("attachmentId", str(new_id))


class Attachments(BaseModel):
    root_vehicle_id: int
    attachment_list: list[Attachment] = []

    def __init__(self, order_notifier: OrderNotifier, xml_node: Element):
        super().__init__(order_notifier, xml_node)
        self.root_vehicle_id = int(xml_node.get("rootVehicleId"))

        for attachment in xml_node.iter("attachment"):
            self.attachment_list.append(Attachment(order_notifier, attachment, self.root_vehicle_id))

    def changed_id(self, old_id: int, new_id: int):
        if self.root_vehicle_id != old_id:
            return

        self.xml_node.set("rootVehicleId", str(new_id))
