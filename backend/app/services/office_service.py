from typing import List

from app.domain.models import Office, Device
from app.domain.repositories import OfficeRepository, DeviceRepository


class OfficeService:
    def __init__(self, office_repository: OfficeRepository, device_repository: DeviceRepository):
        self.office_repository = office_repository
        self.device_repository = device_repository

    async def start(self):
        pass

    async def stop(self):
        pass

    async def get_all_offices(self, return_components: bool = False) -> List[Office]:
        offices = await self.office_repository.get_all_offices()
        if return_components:
            devices = await self.device_repository.get_devices()
            # Group devices by office_id
            office_devices = {}
            for device in devices:
                if device.office_id not in office_devices:
                    office_devices[device.office_id] = []
                # Get components for each device
                device.sensors = await self.device_repository.get_sensors_by_device_id(device.id)
                device.actuators = await self.device_repository.get_actuators_by_device_id(device.id)
                office_devices[device.office_id].append(device)

            # Add devices to each office
            for office in offices:
                setattr(office, 'devices', office_devices.get(office.id, []))
        return offices

    async def get_office_by_id(self, office_id: int, return_components: bool = False) -> Office:
        office = await self.office_repository.get_office_by_id(office_id)
        if office and return_components:
            # Get all devices for this office
            devices = await self.device_repository.get_devices()
            office_devices = []
            for device in devices:
                if device.office_id == office_id:
                    # Get components for each device
                    device.sensors = await self.device_repository.get_sensors_by_device_id(device.id)
                    device.actuators = await self.device_repository.get_actuators_by_device_id(device.id)
                    office_devices.append(device)
            setattr(office, 'devices', office_devices)
        return office

    async def create_office(self, office: Office) -> Office:
        return await self.office_repository.create_office(office)

    async def update_office(self, office_id: int, office: Office) -> Office:
        return await self.office_repository.update_office(office_id, office)

    async def delete_office(self, office_id: int) -> bool:
        return await self.office_repository.delete_office(office_id)
