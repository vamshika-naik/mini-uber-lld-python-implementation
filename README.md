# Mini-Uber Ride-Sharing System (Low-Level Design)

An object-oriented, in-memory backend engine for an on-demand ride-hailing service built with **Python 3.10+**[cite: 1]. This project translates complex business rules into a clean, modular architecture while avoiding monolithic "god classes"[cite: 1].

📄 You can view the full challenge requirements and specifications here: [Ride-Sharing System LLD Challenge PDF](./Ride-Sharing%20System%20-%20Low-Level%20Design%20Challenge.pdf)[cite: 1, 2].

---

## 🏗️ Architecture & Design Patterns

The system adheres strictly to object-oriented programming (OOP) principles and design patterns:
1. **Strategy Pattern**: Extracted algorithms for **Driver Matching** (Closest Distance Strategy) and **Fare Pricing** behind abstract base classes (`abc.ABC`), allowing them to be swapped dynamically at runtime[cite: 2].
2. **State / Lifecycle Guard**: Encapsulated trip lifecycle tracking inside a state machine dictionary to enforce strict, unidirectional transitions and prevent illegal state mutations[cite: 1, 2].
3. **Manager / Facade Pattern**: `RideServiceManager` acts as the central orchestrator coordinating user registries, trips, and strategy execution without cluttering business entities[cite: 2].

---

## 🧩 Core Entities & Responsibilities

* **Location**: Immutable coordinate value-object (`frozen=True`) that computes Euclidean distances to other points[cite: 1].
* **Rider**: Initiates ride requests, holds contact information, profile ratings, and wallet balances[cite: 1, 2].
* **Driver**: Maintains operational statuses (`AVAILABLE`, `ON_TRIP`, `OFFLINE`), links to a vehicle, and tracks rolling average ratings and earnings[cite: 1, 2].
* **Vehicle**: Encapsulates registration numbers, vehicle types, capacity, and rate multipliers[cite: 1, 2].
* **Trip**: Manages the lifecycle timeline timestamps, route coordinates, final fares, and state safety[cite: 1, 2].

---

## 🔄 Trip Lifecycle State Machine

Trips follow a strict unidirectional state sequence[cite: 1, 2]:
`REQUESTED` ➔ `ACCEPTED` ➔ `IN_PROGRESS` ➔ `COMPLETED` *(or `CANCELLED`)*[cite: 1, 2]

---

## 🌟 Advanced Bonus Features Implemented

* **Cancellation Fee Ledger**: Cancelling a trip during the `ACCEPTED` state automatically charges a penalty fee to the rider's wallet and credits it to the driver's earnings[cite: 2].
* **Bidirectional Driver Feedback**: Post-trip ratings incrementally update the driver's rolling average star rating[cite: 2].

---

## 🚀 How to Run

1. Ensure you have **Python 3.10+** installed[cite: 1].
2. Open your terminal in the project directory.
3. Run the script:
   ```bash
   python3 ride.py
