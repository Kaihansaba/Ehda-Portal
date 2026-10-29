# Diagrams

## Project: Ehda Portal — Online Blood Donation Platform

### 1. Purpose

This folder contains the project's UML diagrams:

- **Sequence diagrams** show the interactions between users, the application and the database in the order they happen, for the main workflows.
- **Use case diagrams** give a high-level view of the system's functional scope: which actors use which functions.

Files are named `Sprint-N - Topic (Author)` so each diagram can be matched to its sprint and its author.

### 2. Sequence Diagrams

| Sprint | Diagram | Author |
|---|---|---|
| 1 | [Registration, login and profile](Sequence-Diagrams/Sprint-1%20-%20Registration,%20Login%20and%20Profile%20%28Samira%20Azizi%29.png) | Samira Azizi |
| 2 | [Search donors by blood type and distance](Sequence-Diagrams/Sprint-2%20-%20Search%20Donors%20by%20Blood%20Type%20and%20Distance%20%28Ahmad%20Kaihan%20Saba%29.svg) | Ahmad Kaihan Saba |
| 3 | [Blood requests and messaging](Sequence-Diagrams/Sprint-3%20-%20Blood%20Requests%20and%20Messaging%20%28Shafiqa%20Taraki%29.jpg) | Shafiqa Taraki |
| 4 | [Donation history and account](Sequence-Diagrams/Sprint-4%20-%20Donation%20History%20and%20Account%20%28Samira%20Azizi%29.png) | Samira Azizi |

### 3. Use Case Diagrams

| Sprint | Diagram | Author |
|---|---|---|
| 1 | [Registration, login and profile](Use-Case-Diagrams/Sprint-1%20-%20Registration,%20Login%20and%20Profile%20%28Samira%20Azizi%29.png) | Samira Azizi |
| 2 | [Donor search and map](Use-Case-Diagrams/Sprint-2%20-%20Donor%20Search%20and%20Map%20%28Ahmad%20Kaihan%20Saba%29.svg) | Ahmad Kaihan Saba |
| 3–4 | [Requests, messaging and admin](Use-Case-Diagrams/Sprint-3-4%20-%20Requests,%20Messaging%20and%20Admin%20%28Shafiqa%20Taraki%29.png) | Shafiqa Taraki |
| 4 | [Donation history and account](Use-Case-Diagrams/Sprint-4%20-%20Donation%20History%20and%20Account%20%28Samira%20Azizi%29.png) | Samira Azizi |

### 4. Main Actors

- **Donor:** registers, manages a donor profile, blood type and availability, receives blood requests and responds to them.
- **Blood seeker:** searches for potential donors and sends blood requests. In the implemented system, hospitals act as blood seekers.
- **Administrator:** manages users, hospitals and donation centres, reviews reported accounts and monitors platform activity.

### 5. Notes

- Some diagrams show planned features that are not fully implemented yet, such as in-app messaging (#014) and sending a request to one selected donor (#010). See the feature status table in the [root README](../README.md).
- Donor privacy: diagrams and the system use approximate donor locations only, never exact home addresses.
