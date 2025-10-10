from xml.etree.ElementTree import Element


class Vehicle:
    """Represents a vehicle in FS25.

    FS25 uses uniqueId (hash strings) instead of numeric IDs.
    Vehicle order in the XML determines TAB-cycling order in game.
    """

    unique_id: str
    name: str
    operating_time: float
    license_plates: str
    is_tabbable: bool
    xml_node: Element

    def __init__(self, xml_node: Element):
        self.xml_node = xml_node
        self.unique_id = xml_node.get("uniqueId")

        # Extract vehicle name from filename
        if xml_node.get("modName") is not None:
            self.name = (
                xml_node.get("filename").split("/").pop().replace(".xml", "") + " (" + xml_node.get("modName") + ")"
            )
        else:
            self.name = xml_node.get("filename").split("/").pop().replace(".xml", "")

        self.operating_time = round(float(xml_node.get("operatingTime")) / 60 / 60, 1)

        # License plates
        license_plates_node = xml_node.find("licensePlates")
        if license_plates_node is not None:
            self.license_plates = license_plates_node.get("characters")
        else:
            self.license_plates = "[None]"

        # Check if vehicle can be tabbed to
        enterable = xml_node.find("enterable")
        if enterable is not None:
            self.is_tabbable = enterable.get("isTabbable", "false").lower() == "true"
        else:
            self.is_tabbable = False

    def __str__(self):
        return self.name

    def get_attached_vehicle_ids(self) -> list[str]:
        """Returns list of uniqueIds of vehicles attached to this one."""
        attached_ids = []
        attacher_joints = self.xml_node.find("attacherJoints")
        if attacher_joints is not None:
            for attached_implement in attacher_joints.findall("attachedImplement"):
                attached_id = attached_implement.get("attachedVehicleUniqueId")
                if attached_id:
                    attached_ids.append(attached_id)
        return attached_ids
