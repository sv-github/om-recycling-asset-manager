from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.customer import Customer
from app.models.customer_location import CustomerLocation
from app.models.collection import Collection
from app.models.collection_item import CollectionItem
from app.models.asset import Asset
from app.models.asset_inspection import AssetInspection
from app.models.asset_processing import AssetProcessing


def seed_development_data(db: Session) -> None:
    """
    Create the canonical development/test dataset.

    This dataset is intentionally deterministic so that development
    databases on different machines contain the same records and IDs.
    """

    # ------------------------------------------------------------------
    # Customer
    # ------------------------------------------------------------------

    customer = db.get(Customer, 1)

    if customer is None:
        customer = Customer(
            id=1,
            customer_code="TEST-CUSTOMER-001",
            company_name="OM Recycling Development Customer",
            legal_name="OM Recycling Development Customer Pvt Ltd",
            gstin=None,
            primary_contact_name="Development Contact",
            primary_contact_email="test@example.com",
            primary_contact_phone="9999999999",
            address="Development Test Address",
            notes="Canonical development/test customer.",
            is_active=True,
        )
        db.add(customer)

    # ------------------------------------------------------------------
    # Customer Location
    # ------------------------------------------------------------------

    location = db.get(CustomerLocation, 1)

    if location is None:
        location = CustomerLocation(
            id=1,
            customer_id=1,
            location_code="TEST-LOC-001",
            location_name="Development Test Location",
            address="Development Test Location Address",
            contact_name="Receiving Contact",
            contact_email="receiving@example.com",
            contact_phone="9999999999",
            notes="Canonical development/test location.",
            is_active=True,
        )
        db.add(location)

    db.flush()

    # ------------------------------------------------------------------
    # Collection
    # ------------------------------------------------------------------

    collection = db.get(Collection, 1)

    if collection is None:
        collection = Collection(
            id=1,
            collection_code="TEST-COLLECTION-001",
            customer_id=1,
            location_id=1,
            collection_date=datetime.now(timezone.utc).date(),
            pickup_receipt_number="TEST-PICKUP-001",
            source_type="customer",
            status="completed",
            expected_item_count=5,
            transport_reference="TEST-TRANSPORT-001",
            notes="Canonical development/test collection.",
            is_active=True,
        )
        db.add(collection)

    db.flush()

    # ------------------------------------------------------------------
    # Collection Item
    # ------------------------------------------------------------------

    collection_item = db.get(CollectionItem, 1)

    if collection_item is None:
        collection_item = CollectionItem(
            id=1,
            collection_id=1,
            category="Laptop",
            manufacturer="Dell",
            model="Latitude 7410",
            description="Development/test laptop collection item.",
            expected_quantity=5,
            notes="Canonical development/test collection item.",
        )
        db.add(collection_item)

    db.flush()

    # ------------------------------------------------------------------
    # Assets
    # ------------------------------------------------------------------

    assets = {
        1: {
            "asset_code": "TEST-ASSET-001",
            "serial_number": "FULL-INTAKE-TEST-001",
            "status": "received",
            "data_wipe_status": "passed",
            "data_wipe_method": "Secure Erase",
            "data_wipe_reference": "WIPE-TEST-00001",
            "description": (
                "Fully processed development asset ready for "
                "final disposition testing."
            ),
        },
        2: {
            "asset_code": "TEST-ASSET-002",
            "serial_number": "TEST-RECEIVED-002",
            "status": "received",
            "data_wipe_status": "not_started",
            "data_wipe_method": None,
            "data_wipe_reference": None,
            "description": "Received asset awaiting initial inspection.",
        },
        3: {
            "asset_code": "TEST-ASSET-003",
            "serial_number": "TEST-INSPECTED-003",
            "status": "received",
            "data_wipe_status": "not_started",
            "data_wipe_method": None,
            "data_wipe_reference": None,
            "description": "Inspected asset awaiting data sanitization.",
        },
        4: {
            "asset_code": "TEST-ASSET-004",
            "serial_number": "TEST-SANITIZED-004",
            "status": "received",
            "data_wipe_status": "passed",
            "data_wipe_method": "Secure Erase",
            "data_wipe_reference": "WIPE-TEST-00004",
            "description": "Sanitized asset awaiting processing.",
        },
        5: {
            "asset_code": "TEST-ASSET-005",
            "serial_number": "TEST-REFURB-005",
            "status": "received",
            "data_wipe_status": "passed",
            "data_wipe_method": "Secure Erase",
            "data_wipe_reference": "WIPE-TEST-00005",
            "description": "Refurbished asset ready for disposition testing.",
        },
    }

    for asset_id, values in assets.items():
        asset = db.get(Asset, asset_id)

        if asset is None:
            asset = Asset(
                id=asset_id,
                asset_code=values["asset_code"],
                serial_number=values["serial_number"],
                collection_id=1,
                collection_item_id=1,
                asset_category="Laptop",
                manufacturer="Dell",
                model="Latitude 7410",
                description=values["description"],
                status=values["status"],
                received_by="Development Receiving Staff",
                receiving_notes="Canonical development/test asset.",
                data_wipe_status=values["data_wipe_status"],
                data_wipe_method=values["data_wipe_method"],
                data_wipe_date=(
                    datetime.now(timezone.utc)
                    if values["data_wipe_status"] == "passed"
                    else None
                ),
                data_wipe_reference=values["data_wipe_reference"],
                final_disposition=None,
                notes="Canonical development/test data.",
            )
            db.add(asset)

    db.flush()

    # ------------------------------------------------------------------
    # Initial Inspection - Asset 1
    # ------------------------------------------------------------------

    inspection = db.get(AssetInspection, 1)

    if inspection is None:
        inspection = AssetInspection(
            id=1,
            asset_id=1,
            inspection_type="initial",
            inspected_by="Receiving Staff",
            working_status="working",
            overall_condition="good",
            display_condition="good",
            body_condition="fair",
            keyboard_condition="good",
            touchpad_condition="good",
            hinge_condition="good",
            ports_condition="good",
            battery_condition="fair",
            charger_status="present",
            ram_status="present",
            storage_status="present",
            cpu_status="present",
            gpu_status="not_applicable",
            accessories="Original charger",
            inspection_notes=(
                "Canonical development inspection. "
                "Device powers on and appears functional."
            ),
        )
        db.add(inspection)

    # ------------------------------------------------------------------
    # Initial Inspection - Asset 3
    # ------------------------------------------------------------------

    inspection = db.get(AssetInspection, 2)

    if inspection is None:
        inspection = AssetInspection(
            id=2,
            asset_id=3,
            inspection_type="initial",
            inspected_by="Receiving Staff",
            working_status="working",
            overall_condition="good",
            display_condition="good",
            body_condition="good",
            keyboard_condition="good",
            touchpad_condition="good",
            hinge_condition="good",
            ports_condition="good",
            battery_condition="fair",
            charger_status="present",
            ram_status="present",
            storage_status="present",
            cpu_status="present",
            gpu_status="not_applicable",
            accessories="Original charger",
            inspection_notes="Inspected; awaiting data sanitization.",
        )
        db.add(inspection)

    # ------------------------------------------------------------------
    # Initial Inspection - Asset 4
    # ------------------------------------------------------------------

    inspection = db.get(AssetInspection, 3)

    if inspection is None:
        inspection = AssetInspection(
            id=3,
            asset_id=4,
            inspection_type="initial",
            inspected_by="Receiving Staff",
            working_status="working",
            overall_condition="good",
            display_condition="good",
            body_condition="good",
            keyboard_condition="good",
            touchpad_condition="good",
            hinge_condition="good",
            ports_condition="good",
            battery_condition="fair",
            charger_status="present",
            ram_status="present",
            storage_status="present",
            cpu_status="present",
            gpu_status="not_applicable",
            accessories="Original charger",
            inspection_notes="Inspection completed.",
        )
        db.add(inspection)

    # ------------------------------------------------------------------
    # Initial Inspection - Asset 5
    # ------------------------------------------------------------------

    inspection = db.get(AssetInspection, 4)

    if inspection is None:
        inspection = AssetInspection(
            id=4,
            asset_id=5,
            inspection_type="initial",
            inspected_by="Receiving Staff",
            working_status="working",
            overall_condition="good",
            display_condition="good",
            body_condition="fair",
            keyboard_condition="good",
            touchpad_condition="good",
            hinge_condition="good",
            ports_condition="good",
            battery_condition="fair",
            charger_status="present",
            ram_status="present",
            storage_status="present",
            cpu_status="present",
            gpu_status="not_applicable",
            accessories="Original charger",
            inspection_notes="Inspection completed for refurbishment.",
        )
        db.add(inspection)

    db.flush()

    # ------------------------------------------------------------------
    # Processing - Asset 1 grading
    # ------------------------------------------------------------------

    processing = db.get(AssetProcessing, 1)

    if processing is None:
        processing = AssetProcessing(
            id=1,
            asset_id=1,
            processing_type="grading",
            grade="B",
            refurbishment_status="not_required",
            processor="Processing Technician",
            condition_summary="Good working condition.",
            repairs_performed=None,
            parts_replaced=None,
            testing_notes="Functional testing completed.",
            processing_reference="GRADE-TEST-00001",
            cost=Decimal("0.00"),
            notes="Canonical development grading record.",
        )
        db.add(processing)

    # ------------------------------------------------------------------
    # Processing - Asset 5 grading
    # ------------------------------------------------------------------

    processing = db.get(AssetProcessing, 2)

    if processing is None:
        processing = AssetProcessing(
            id=2,
            asset_id=5,
            processing_type="grading",
            grade="B",
            refurbishment_status="not_required",
            processor="Processing Technician",
            condition_summary="Good condition before refurbishment.",
            repairs_performed=None,
            parts_replaced=None,
            testing_notes="Initial grading completed.",
            processing_reference="GRADE-TEST-00005",
            cost=Decimal("0.00"),
            notes="Canonical development grading record.",
        )
        db.add(processing)

    db.flush()

    # ------------------------------------------------------------------
    # Processing - Asset 1 refurbishment
    # ------------------------------------------------------------------

    processing = db.get(AssetProcessing, 3)

    if processing is None:
        processing = AssetProcessing(
            id=3,
            asset_id=1,
            processing_type="refurbishment",
            grade="B",
            refurbishment_status="completed",
            processor="Refurbishment Technician",
            condition_summary="Good overall condition after refurbishment.",
            repairs_performed=(
                "Cleaned internal and external surfaces; "
                "replaced worn components as required."
            ),
            parts_replaced="None",
            testing_notes="Post-refurbishment functional testing passed.",
            processing_reference="REFURB-TEST-00001",
            cost=Decimal("1500.00"),
            notes="Canonical development refurbishment record.",
        )
        db.add(processing)

    # ------------------------------------------------------------------
    # Processing - Asset 5 refurbishment
    # ------------------------------------------------------------------

    processing = db.get(AssetProcessing, 4)

    if processing is None:
        processing = AssetProcessing(
            id=4,
            asset_id=5,
            processing_type="refurbishment",
            grade="B",
            refurbishment_status="completed",
            processor="Refurbishment Technician",
            condition_summary="Good overall condition after refurbishment.",
            repairs_performed="Cleaned and serviced.",
            parts_replaced="None",
            testing_notes="Post-refurbishment testing passed.",
            processing_reference="REFURB-TEST-00005",
            cost=Decimal("1200.00"),
            notes="Canonical development refurbishment record.",
        )
        db.add(processing)

    db.flush()

    # ------------------------------------------------------------------
    # Reset PostgreSQL sequences after deterministic ID insertion
    # ------------------------------------------------------------------

    sequence_tables = [
        ("customers", "customers_id_seq"),
        ("customer_locations", "customer_locations_id_seq"),
        ("collections", "collections_id_seq"),
        ("collection_items", "collection_items_id_seq"),
        ("assets", "assets_id_seq"),
        ("asset_inspections", "asset_inspections_id_seq"),
        ("asset_processing", "asset_processing_id_seq"),
        ("asset_dispositions", "asset_dispositions_id_seq"),
    ]

    for table_name, sequence_name in sequence_tables:
        db.execute(
            text(
                f"""
                SELECT setval(
                    '{sequence_name}',
                    COALESCE((SELECT MAX(id) FROM {table_name}), 1),
                    true
                )
                """
            )
        )

    db.commit()


def main() -> None:
    db = SessionLocal()

    try:
        seed_development_data(db)
        print("Development seed completed successfully.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()