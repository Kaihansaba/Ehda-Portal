# Use Case Diagrams

## Project: Ehda Portal — Online Blood Donation Platform

### 1. Purpose

This folder contains the UML use case diagrams for the Ehda Portal online blood donation platform. Use case diagrams describe the interactions between external actors and the system's main functions. They provide a high-level view of the system's functional scope.

### 2. System Overview

Ehda Portal aims to connect people seeking blood with potential donors and support communication about blood requests. The platform also provides administrative functions for managing users and monitoring system activity.

### 3. Main Actors

- **Donor:** Registers an account, manages a donor profile, specifies blood type and availability, receives blood requests, responds to requests, and communicates with seekers when permitted.
- **Blood Seeker:** Registers an account, searches for potential donors, views permitted donor information, sends blood requests, receives responses, and communicates with donors after request acceptance.
- **Administrator:** Manages registered users, maintains hospital and donation-center information, reviews reported accounts, and monitors platform activity.

### 4. Main Use Cases

The use case diagram should represent the following system functions:

**Account Management**
- Register an account
- Log in and log out
- Update account information
- Manage donor profile

**Donor Search and Location**
- Search donors by blood type
- Search donors by location or distance
- View available donor location information
- Protect donor location privacy

**Blood Request Management**
- Send a blood request
- Receive request notifications
- Accept or decline a request
- View request responses
- Exchange messages after request acceptance

**Donation History**
- Record previous donations
- View donation history

**Administrative Functions**
- Manage registered users
- Manage hospitals and donation centers
- Review reported accounts
- Monitor blood requests and platform activity

### 5. Design Considerations

- Actors must remain outside the system boundary.
- Use cases must be represented inside the system boundary.
- Actor-to-use-case associations should clearly show which functions each actor can perform.
- The diagram should match the project's functional requirements and user stories.
- Donor privacy must be considered when displaying location information.
- Any include or extend relationships should be used only when justified by the system's behavior.

### 6. Diagram Files

The completed use case diagram and its editable source file will be stored in this folder.

