# Software Requirements Specification (SRS)

**Project:** Ehda Portal – Online Blood Donation Platform

**Date:** 18.10.2026

**Prepared by:** The Scrum Team

(Madina Pasun, Madina Afshar, Samira Azizi, Ahmad Kaihan Saba, Shafiqa Taraki)

---

## 1. Introduction

### 1.1 Purpose

The purpose of this document is to describe all the functional and non-functional requirements of Ehda Portal, an online web-based blood donation platform.

This document shows the expected system behavior, challenges, features, user interactions, interface requirements, design limitations, performance expectations, and quality attributes. It is a reference for the Product Owner, Scrum Master, developers, and testers throughout the software development process.

The Software Requirement Specification will help the team with the implementation of the application, and verify that the system meets the project requirements.

### 1.2 Scope

Ehda portal aims to provide a centralized online platform that connects people who are seeking blood with potential blood donors, hospitals, and other blood donation centers.

The system intends to support donor registration, profile management, blood-type and location-based searches, blood requests, request responses, notifications, messaging, donation history, and administrative management.

The main objectives of this platform are:

- To make blood donors easier to find.
- To organize donor information and availability in a centralized platform.
- To support searches based on location and blood type.
- To simplify tracking of blood requests.
- To improve communication between donors and blood seekers.
- To provide administrators with tools to manage users, hospitals, and other platform activities.
- To protect user information through privacy and security controls.

### 1.3 Definitions and Acronyms

| Acronym | Definition |
|---|---|
| SRS | Software Requirement Specification |
| FR | Functional Requirement |
| NFR | Non-Functional Requirement |
| PO | Product Owner |
| SM | Scrum Master |
| UI | User Interface |

---

## 2. General Description

### 2.1 Product Perspectives

Ehda portal is a web-based blood donation platform that aims to provide a centralized environment for discovering blood donors and coordinating blood requests.

The application consists of a user interface, application logic, data storage, authentication and authorization mechanisms, and location-based functionality.

The system will support three main user groups:

1. Blood donors
2. Blood seekers
3. Administrators

### 2.2 User Characteristics

#### 2.2.1 Blood Donors

Blood donors are users who provide information about their blood type, contact details, approximate location, and availability.

They should be able to manage their profiles, update their availability status, receive requests, and accept or decline requests they have received.

#### 2.2.2 Blood Seekers

Blood seekers are users looking for blood donors.

They should be able to search for donors, view profile information, create blood requests, check request responses, and communicate with donors after the request has been accepted.

#### 2.2.3 Administrators

Administrators are authorized users responsible for managing platform functions.

They should be able to manage registered accounts and healthcare facilities, review reported accounts, and monitor blood requests and platform activity.

Administrative actions should be restricted to authorized accounts only.

#### 2.2.4 Constraints

- Development must remain within the project scope.
- The technology stack must be selected and documented by the team.
- The application must protect credentials and private user information.
- Donor locations must not be exact residential addresses.
- Map functionality may depend on an external map provider.
- Notification functionality depends on the notification mechanism selected by the team.
- Source code and project documentation must be maintained in the GitHub repository.
- Features must be tested before marking as complete.
- The project should be submitted by November 1.

---

## 3. Functional Requirements (FR)

| ID | Functional Requirement |
|---|---|
| FR-001 | The system shall allow users to create accounts using valid registration information |
| FR-002 | The system shall allow registered users to log in and log out securely. |
| FR-003 | The system shall enforce role-based permission for donors, blood seekers, and administrators. |
| FR-004 | The system shall allow donors to create and update their donor profiles. |
| FR-005 | The system shall allow donors to specify their blood type. |
| FR-006 | The system shall allow donors to set and update their availability status. |
| FR-007 | The system shall allow users to manage account information they are authorized to change. |
| FR-008 | The system shall allow users to view and maintain their donation history according to the supported workflow. |
| FR-009 | The system shall allow users to search for potential blood donors based on blood type. |
| FR-010 | The system shall allow users to search for potential blood donors based on location or distance. |
| FR-011 | The system shall display approximate donor location rather than exact one to maintain privacy. |
| FR-012 | The system shall display relevant donors, hospitals, and blood donation centers on a map when the required data and mapping functionality are available. |
| FR-013 | The system shall allow a blood seeker to create a blood request. |
| FR-014 | The system shall send the blood request to the selected donor. |
| FR-015 | The system shall store and manage request information, including request ID, seeker ID, donor ID, status, and timestamp. |
| FR-016 | The system shall allow donors to accept or decline blood requests directed to them. |
| FR-017 | The system shall update the request status to pending, accepted, or declined. |
| FR-018 | The system shall notify donors when they receive blood requests. |
| FR-019 | The system shall notify blood seekers when the request is accepted or declined. |
| FR-020 | The system shall manage notifications including administrative alerts and platform updates. |
| FR-021 | The system shall enable communication between donors and blood seekers once a blood request has been accepted. |
| FR-022 | The system shall allow users to send and receive messages in real time. |
| FR-023 | The system shall store and display message history to the relevant authorized participants. |
| FR-024 | The system shall allow administrators to view and manage registered users. |
| FR-025 | The system shall allow administrators to manage hospitals and blood donation centers. |
| FR-026 | The system shall allow administrators to review reported accounts and take appropriate actions. |
| FR-027 | The system shall allow administrators to monitor and manage blood requests and platform activities. |
| FR-028 | The system shall validate user input and display appropriate error messages when information is invalid or incomplete. |

---

## 4. Interface Requirements

### 4.1 User Interface

The application shall provide a clear and consistent web interface for donors, blood seekers, and administrators.

The interface should:

- Provide understandable navigation and page labels.
- Include forms for registration, login, donor profiles, and blood requests.
- Identify required fields and explain validation errors.
- Display donor search results in a readable format.
- Show relevant requests statuses and responses.
- Provide access to the map and location-based results.
- Restrict protected pages and functions according to user permissions.
- Avoid displaying private information to unauthorized users.
- Remain usable on the screen sizes supported by the team.

### 4.2 Software Interface

The system may interact with the following software components:

- A web browser for user interaction
- An application backend for processing requests and enforcing business rules.
- A database for storing user profiles, blood requests, messages, and other required information.
- An authentication mechanism for account access and permissions.
- A mapping service for location-based functionality.
- A notification mechanism for request updates.
- Testing and development tools used by the team.

---

## 5. Non-Functional Requirements

| ID | Non-Functional Requirement |
|---|---|
| NFR-001 | Notifications shall be delivered within 5 seconds of a request being sent, under defined normal operating conditions. |
| NFR-002 | The messaging system shall support at least 100 concurrent conversations without significant delay under agreed test conditions. |
| NFR-003 | Donor search should return results within 3 seconds under defined normal test conditions, excluding delays caused by external services. |
| NFR-004 | All messages shall be encrypted in transit and protected against unauthorized access. |
| NFR-005 | Only authorized users shall be able to send or receive blood requests. |
| NFR-006 | Access to the admi dashboard shall be restricted to authorized administrators only. |
| NFR-007 | User passwords shall not be stored as plain text. |
| NFR-008 | Private requests, messages, and personal information shall be accessible only to authorized users. |
| NFR-009 | The blood request creation form shall be simple, requiring no more than 3 steps to complete a request. |
| NFR-010 | Notifications shall be displayed clearly in the user interface with distinct icons or visual indicators. |
| NFR-011 | The admin dashboard shall provide a clean interface with easy navigation menus. |
| NFR-012 | Forms shall use clear labels, identify required fields, and display understandable validation and error messages. |
| NFR-013 | The system shall target 99% uptime during active hours when deployed in its intended operating environment. |
| NFR-014 | The system shall be designed to support up to 10000 registered users. |
| NFR-015 | The system shall maintain data consistency among user accounts, donor profiles, blood requests, responses, and messages. |
| NFR-016 | The system shall handle errors gracefully and provide appropriate feedback without exposing sensitive technical information. |
| NFR-017 | The application shall be tested in supported browsers, including Chrome and Edge. |
| NFR-018 | The source code shall be organized and documented to support maintenance, testing, and future improvements. |
| NFR-019 | The team shall document and execute test cases, record identified defects, and retest corrected features. |

---

## 6. Requirement Review

The project team shall review this SRS to confirm that the requirements are clear, consistent, and aligned with the project objectives.

The review shall check that:

- Each requirement is understandable and testable.
- Functional requirements match the planned platform features.
- Non-functional requirements include measurable targets where possible.
- Requirements are represented in the product backlog.
- The team agrees on the scope and identifies any unresolved questions.

## 7. Related Project Documents

1. Project description and objectives
2. Roles and responsibilities document
3. Product backlog
4. Sprint backlog and sprint plans
5. Acceptance criteria
6. System design diagrams
7. Test cases and testing evidence
8. Sprint review and retrospective records

---

## PO Review and Approval

**Product Owner:** Madina Pasun

**Review Date:** 19 October 2026

“I confirm that the requirements in this document have been reviewed against the intended scope of Ehda portal. Any necessary changes will be recorded and agreed upon before the document is finalized. “

---

**Prepared by:** Scrum team

**Project:** Ehda Portal – Online Blood Donation Platform
