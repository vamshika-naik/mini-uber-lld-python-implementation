from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import math

# Excpetions


class InvalidStateTransitionError(Exception):
    pass


class NoDriverAvailableError(Exception):
    pass

# Status


class DriverStatus(Enum):
    AVAILABLE = "AVAILABLE"
    ON_TRIP = "ON_TRIP"
    OFFLINE = "OFFLINE"


class TripStatus(Enum):
    REQUESTED = "REQUESTED"
    ACCEPTED = "ACCEPTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

# Core Entities


@dataclass(frozen=True)
class Location:
    x: float
    y: float

    def distance_to(self, other: 'Location') -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass
class Rider:
    id: str
    name: str
    contact: str
    rating: float
    wallet_balance: float = 500.0


@dataclass
class Driver:
    id: str
    name: str
    vehicle: str
    location: str
    status: DriverStatus = DriverStatus.OFFLINE
    rating: float = 5.0
    earnings: float = 0.0


@dataclass
class Vehicle:
    reg_no: str
    vehicle_type: str
    capacity: int
    rate_multiplier: float


@dataclass
class Trip:
    trip_id: str
    rider: Rider
    driver: Driver
    pickup: Location
    drop: Location
    fare: float
    status: TripStatus = TripStatus.REQUESTED

    def update_status(self, new_status: TripStatus):
        valid_transitions = {
            TripStatus.REQUESTED: [TripStatus.ACCEPTED, TripStatus.CANCELLED],
            TripStatus.ACCEPTED: [TripStatus.IN_PROGRESS, TripStatus.CANCELLED],
            TripStatus.IN_PROGRESS: [TripStatus.COMPLETED],
            TripStatus.COMPLETED: [],
            TripStatus.CANCELLED: []
        }
        if new_status not in valid_transitions.get(self.status, []):
            raise InvalidStateTransitionError(
                f"Invalid transition from {self.status} to {new_status}")
        self.status = new_status

# Strategies


class DriverMatchingStrategy(ABC):
    @abstractmethod
    def match(self, pickup: Location, drivers: list[Driver]) -> Driver:
        pass


class ClosestDriverStrategy(DriverMatchingStrategy):
    def match(self, pickup: Location, drivers: list[Driver]) -> Driver:
        available = [d for d in drivers if d.status == DriverStatus.AVAILABLE]
        if not available:
            raise NoDriverAvailableError("No drivers available!")
        return min(available, key=lambda d: d.location.distance_to(pickup))


class PricingStrategy(ABC):
    @abstractmethod
    def calculate(self, distance: float, vehicle: Vehicle) -> float:
        pass


class StandardPricing(PricingStrategy):
    def calculate(self, distance: float, vehicle: Vehicle) -> float:
        base_fare = 50.0
        per_km_rate = 15.0
        return round((base_fare + (distance * per_km_rate)) * vehicle.rate_multiplier, 2)


class RideServiceManager:
    def __init__(self):
        self.riders = {}
        self.drivers = {}
        self.trips = {}
        self.matching_strategy = ClosestDriverStrategy()
        self.pricing_strategy = StandardPricing()

    def register_rider(self, rider: Rider):
        self.riders[rider.id] = rider

    def register_driver(self, driver: Driver):
        self.drivers[driver.id] = driver

    def request_ride(self, trip_id: str, rider_id: str, pickup: Location, drop: Location) -> Trip:
        rider = self.riders[rider_id]

        # Match drive
        driver = self.matching_strategy.match(
            pickup, list(self.drivers.values()))
        distance = pickup.distance_to(drop)
        fare = self.pricing_strategy.calculate(distance, driver.vehicle)

        # Create trip
        trip = Trip(trip_id, rider, driver, pickup, drop, fare)
        self.trips[trip_id] = trip
        return trip

    def accept_trip(self, trip_id: str):
        trip = self.trips[trip_id]
        trip.update_status(TripStatus.ACCEPTED)
        trip.driver.status = DriverStatus.ON_TRIP

    def cancel_trip(self, trip_id: str, penalty_fee: float = 50.0):
        trip = self.trips[trip_id]
        if trip.status == TripStatus.ACCEPTED:
            trip.rider.wallet_balance -= penalty_fee
            trip.driver.earnings += penalty_fee
            trip.update_status(TripStatus.CANCELLED)
            print(f"Ride Cancelled! Status: {trip.status.value}")
            print(
                f"[Ledger] Trip cancelled in ACCEPTED state. ${penalty_fee} penalty charged to rider and credited to driver.")
        trip.driver.status = DriverStatus.AVAILABLE

    def rate_driver(self, trip_id: str, rating: float):
        trip = self.trips[trip_id]
        if trip.status != TripStatus.COMPLETED:
            raise Exception("Cannot rate a trip that is not completed.")

        driver = trip.driver
        # Simple incremental rolling average formula
        driver.rating = round((driver.rating + rating) / 2, 2)
        print(
            f"[Feedback] Driver {driver.name} rating updated to {driver.rating} stars.")


if __name__ == "__main__":
    app = RideServiceManager()

    # Rider Registration
    app.register_rider(Rider("R1", "Alice", "12345", 4.9))
    app.register_rider(Rider("R2", "Charlie", "222-222", 4.8))

    # Driver Registration
    car1 = Vehicle("KA01AB1234", "Sedan", 4, 1.2)
    app.register_driver(
        Driver("D1", "Bob", car1, Location(1.0, 1.0), DriverStatus.AVAILABLE))

    car2 = Vehicle("KA02CD5678", "SUV", 6, 1.5)
    app.register_driver(
        Driver("D2", "David", car2, Location(5.0, 5.0), DriverStatus.AVAILABLE))

    pickup_loc = Location(0.0, 0.0)
    drop_loc = Location(3.0, 4.0)

    print(f"Starting Ride 1 ")
    trip = app.request_ride("T1", "R1", pickup_loc, drop_loc)
    print(
        f"Ride Requested! Rider: {trip.rider.name}, Status: {trip.status.value}")

    app.accept_trip("T1")
    print(
        f"Ride Booked! Driver: {trip.driver.name}, Fare: ${trip.fare}, Status: {trip.status.value}")

    print(f" ")
    print(f"Starting Ride 2 ")
    try:
        trip1 = app.request_ride("T2", "R2", pickup_loc, drop_loc)
        print(
            f"Ride Requested! Rider: {trip1.rider.name} Status: {trip1.status.value}")
        app.accept_trip("T2")
        print(
            f"Ride Booked! Driver: {trip1.driver.name}, Fare: ${trip1.fare}, Status: {trip1.status.value}")

        trip1.update_status(TripStatus.IN_PROGRESS)
        print(f"Trip Status: {trip1.status.value}")
        trip1.update_status(TripStatus.COMPLETED)
        print(f"Trip Status: {trip1.status.value}")
        trip1.driver.status = DriverStatus.AVAILABLE
    except NoDriverAvailableError as e:
        print(f"[Caught Expected Exception]: {e}")

    print(f" ")
    print(f"Continuing with Ride 1 ")
    trip.update_status(TripStatus.IN_PROGRESS)
    print(f"Trip Status: {trip.status.value}")

    trip.update_status(TripStatus.COMPLETED)
    print(f"Trip Status: {trip.status.value}")

    trip.driver.status = DriverStatus.AVAILABLE

    app.rate_driver("T1", 4.0)

    print(f" ")
    print(f"Starting Ride 3")

    trip2 = app.request_ride("T3", "R1", pickup_loc, drop_loc)
    print(
        f"Ride Requested! Rider: {trip2.rider.name} Status: {trip2.status.value}")

    app.accept_trip("T3")
    print(
        f"Ride Booked! Driver: {trip2.driver.name}, Fare: ${trip2.fare}, Status: {trip2.status.value}")

    app.cancel_trip("T3")
    print(f"Rider Wallet Balance after penalty: ${trip2.rider.wallet_balance}")
    print(f"Driver Earnings after penalty: ${trip2.driver.earnings}\n")
