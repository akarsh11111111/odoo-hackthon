"""Driver management service layer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from src.core.exceptions import BusinessRuleException, ConflictException, NotFoundException
from src.models.driver import Driver, DriverStatus
from src.repositories.driver import DriverActivityLogRepository, DriverRepository
from src.schemas.driver import DriverCreateRequest, DriverRead, DriverUpdateRequest


@dataclass(slots=True)
class DriverService:
    """Coordinates driver management business logic and auditing."""

    driver_repository: DriverRepository
    activity_log_repository: DriverActivityLogRepository | None = None

    async def create(self, payload: DriverCreateRequest, *, created_by: str | None = None) -> DriverRead:
        normalized_license = payload.license_number.strip().upper()
        existing_driver = await self.driver_repository.get_by_license_number(normalized_license)
        if existing_driver is not None:
            raise ConflictException("Driver license number already exists")

        if payload.license_expiry < date.today():
            raise BusinessRuleException("License expiry must be in the future")

        driver = await self.driver_repository.create(
            license_number=normalized_license,
            first_name=payload.first_name.strip(),
            last_name=payload.last_name.strip(),
            phone=payload.phone,
            email=payload.email,
            address=payload.address.strip() if payload.address else None,
            date_of_birth=payload.date_of_birth,
            license_expiry=payload.license_expiry,
            safety_score=payload.safety_score,
            driver_status=payload.driver_status,
            region=payload.region.strip(),
            documents=list(payload.documents or []),
            years_of_experience=payload.years_of_experience,
            is_active=True,
            created_by=created_by,
            updated_by=created_by,
        )
        await self._log_activity(driver_id=driver.id, action="Driver Created", message=f"Driver {driver.license_number} created", performed_by=created_by)
        return self._to_read(driver)

    async def list(
        self,
        *,
        page: int = 1,
        size: int = 20,
        filters: dict[str, object] | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        search: str | None = None,
    ) -> dict[str, object]:
        skip = (page - 1) * size
        items, total = await self.driver_repository.list(
            skip=skip,
            limit=size,
            filters=filters,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
        )
        return {
            "items": [self._to_read(driver) for driver in items],
            "total": total,
            "page": page,
            "size": size,
        }

    async def get_by_id(self, driver_id: str) -> DriverRead:
        driver = await self.driver_repository.get_by_id(driver_id)
        if driver is None:
            raise NotFoundException("Driver not found")
        return self._to_read(driver)

    async def update(self, driver_id: str, payload: DriverUpdateRequest, *, updated_by: str | None = None) -> DriverRead:
        existing_driver = await self.driver_repository.get_by_id(driver_id)
        if existing_driver is None:
            raise NotFoundException("Driver not found")

        if payload.driver_status is not None and payload.driver_status == DriverStatus.SUSPENDED:
            raise BusinessRuleException("Suspended drivers cannot be updated to active dispatch status")

        if payload.license_expiry is not None and payload.license_expiry < date.today():
            raise BusinessRuleException("License expiry must be in the future")

        update_data = payload.model_dump(exclude_unset=True)
        if update_data.get("license_number") is not None:
            normalized_license = str(update_data["license_number"]).strip().upper()
            duplicate_driver = await self.driver_repository.get_by_license_number(normalized_license)
            if duplicate_driver is not None and str(duplicate_driver.id) != driver_id:
                raise ConflictException("Driver license number already exists")
            update_data["license_number"] = normalized_license

        if update_data.get("first_name") is not None:
            update_data["first_name"] = str(update_data["first_name"]).strip()

        if update_data.get("last_name") is not None:
            update_data["last_name"] = str(update_data["last_name"]).strip()

        if update_data.get("region") is not None:
            update_data["region"] = str(update_data["region"]).strip()

        if update_data.get("address") is not None:
            update_data["address"] = str(update_data["address"]).strip()

        update_data["updated_by"] = updated_by
        driver = await self.driver_repository.update(driver_id, **update_data)
        await self._log_activity(driver_id=driver.id, action="Driver Updated", message=f"Driver {driver.license_number} updated", performed_by=updated_by)
        return self._to_read(driver)

    async def delete(self, driver_id: str, *, deleted_by: str | None = None) -> dict[str, str]:
        driver = await self.driver_repository.get_by_id(driver_id)
        if driver is None:
            raise NotFoundException("Driver not found")

        await self.driver_repository.delete(driver_id)
        await self._log_activity(driver_id=driver.id, action="Driver Deleted", message=f"Driver {driver.license_number} deleted", performed_by=deleted_by)
        return {"detail": "Driver deleted successfully"}

    async def search(self, *, query: str, page: int = 1, size: int = 20) -> dict[str, object]:
        return await self.list(page=page, size=size, search=query)

    async def list_available(self, *, page: int = 1, size: int = 20) -> dict[str, object]:
        items = await self.driver_repository.list_available()
        total = len(items)
        start = (page - 1) * size
        paginated = items[start : start + size]
        return {
            "items": [self._to_read(driver) for driver in paginated],
            "total": total,
            "page": page,
            "size": size,
        }

    async def _log_activity(self, *, driver_id: object, action: str, message: str, performed_by: str | None = None) -> None:
        if self.activity_log_repository is None:
            return
        await self.activity_log_repository.create(
            driver_id=driver_id,
            action=action,
            message=message,
            performed_by=performed_by,
        )

    @staticmethod
    def _to_read(driver: Driver) -> DriverRead:
        return DriverRead(
            id=str(driver.id),
            license_number=driver.license_number,
            first_name=driver.first_name,
            last_name=driver.last_name,
            phone=driver.phone,
            email=driver.email,
            address=driver.address,
            date_of_birth=driver.date_of_birth,
            license_expiry=driver.license_expiry,
            safety_score=driver.safety_score,
            driver_status=driver.driver_status,
            region=driver.region,
            documents=driver.documents,
            years_of_experience=driver.years_of_experience,
            is_active=driver.is_active,
            created_at=driver.created_at,
            updated_at=driver.updated_at,
            created_by=driver.created_by,
            updated_by=driver.updated_by,
        )


def get_driver_service() -> DriverService:
    """Build a driver service with concrete repositories."""

    return DriverService(
        driver_repository=DriverRepository(),
        activity_log_repository=DriverActivityLogRepository(),
    )
