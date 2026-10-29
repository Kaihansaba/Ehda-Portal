# Ehda Portal: Online Blood Donation Platform
## Product Backlog Document

**Prepared by:** Madina Pasun (Product Owner)  
**Course:** Software Engineering  
**Date:** October 08, 2026

## 1. Introduction

The Product Backlog is the main list of work required to develop the Ehda Portal: Online Blood Donation Platform. It contains the functional features, technical tasks, and quality requirements needed to build a platform that connects people seeking blood with potential donors, hospitals, and blood donation centers.

The backlog contains 20 user stories and 5 technical or quality-related items. Each item includes a description, acceptance criteria, priority, story points, status, sprint assignment, and responsible team member or members.

The Product Owner is responsible for maintaining and prioritizing the backlog, while the development team is responsible for estimating and implementing the selected work. The backlog will be reviewed and updated throughout the project as the team identifies problems, receives feedback, and clarifies requirements.

## 2. Functional Backlog Items (User Stories)

| ID | User Story | Acceptance Criteria | Priority | Estimation | Sprint | Responsible |
|---|---|---|---|---:|---|---|
| #001 | As a new user, I want to create an account so that I can access the platform’s features. | Registration accepts valid required information; required fields are validated; duplicate accounts are rejected; the account is created successfully. | Critical | 3 | Sprint 1 | Samira Azizi |
| #002 | As a user, I want to log in and log out so that I can access and protect my account. | Registered users can log in with correct credentials; invalid credentials are rejected; users can log out; protected pages cannot be accessed after logout without logging in again. | Critical | 3 | Sprint 1 | Samira Azizi |
| #003 | As a donor, I want to create and update my donor profile so that people who need blood can find information about me. | Donors can create and update their profiles; entered information is saved; updated information is displayed correctly; private information is not exposed to unauthorized users. | Critical | 5 | Sprint 1 | Samira Azizi |
| #004 | As a donor, I want to specify my blood type and availability so that blood seekers can identify potential donors. | Donors can select their blood type and availability status; the information appears in their profiles; changes are saved and displayed correctly. | Critical | 2 | Sprint 1 | Samira Azizi |
| #005 | As a donor, I want to control my availability status so that others know whether I am currently available. | Donors can set and update their availability; the current status appears in relevant search results; available and unavailable donors are clearly distinguished. | High | 2 | Sprint 1 | Samira Azizi |
| #006 | As a blood seeker, I want to search for donors by blood type so that I can find potential donors with the blood type I need. | Users can select a required blood type; results display donors with the selected blood type; relevant donor information and availability are shown. | Critical | 5 | Sprint 2 | Ahmad Kaihan Saba |
| #007 | As a blood seeker, I want to search for donors by location and distance so that I can find potential donors nearby. | Users can enter or select a search location; users can specify a search distance when supported; results match the location criteria and are ordered by proximity where distance data is available. | Critical | 5 | Sprint 2 | Ahmad Kaihan Saba |
| #008 | As a user, I want to view a map of nearby donors, hospitals, and donation centers so that I can identify relevant locations. | Users can open the map; available hospital and donation-center locations are displayed; donor markers use approximate locations; users can interact with the map and view available location information. | High | 8 | Sprint 3 | Ahmad Kaihan Saba |
| #009 | As a donor, I want to share my approximate location instead of my exact home address so that my privacy is protected. | Exact home addresses are not shown in public search results or on the map; approximate locations are displayed where appropriate; location information is accessible only according to the platform’s privacy rules. | High | 3 | Sprint 2 | Ahmad Kaihan Saba |
| #010 | As a blood seeker, I want to send a blood request to a donor so that I can ask for help when I need blood. | Users can select a donor and submit the required request information; the system records the request; the selected donor can view the request; the request has a clear status, such as pending, accepted, or declined. | Critical | 5 | Sprint 3 | Shafiqa Taraki |
| #011 | As a donor, I want to receive notifications about blood requests so that I know when someone needs my help. | A notification is generated when a blood request is received; the notification identifies the relevant request; the donor can open and review the request. | High | 3 | Sprint 3 | Shafiqa Taraki |
| #012 | As a donor, I want to accept or decline a blood request so that I can decide whether I am able to respond. | Donors can view pending requests; donors can accept or decline a request; the system saves the response and updates the request status; the blood seeker can see the response. | High | 3 | Sprint 3 | Shafiqa Taraki |
| #013 | As a blood seeker, I want to view a donor’s response so that I know whether the donor has responded to my request. | Blood seekers can view their submitted requests; each request displays its current status; accepted and declined requests are distinguishable; the seeker is informed when the donor responds. | High | 2 | Sprint 3 | Shafiqa Taraki |
| #014 | As a donor or blood seeker, I want to exchange messages after a request is accepted so that we can discuss the donation. | Messaging becomes available after a request is accepted; both participants can send and view messages; previous messages remain visible in the conversation; users cannot message through this feature before acceptance. | High | 5 | Sprint 3 | Shafiqa Taraki |
| #015 | As a donor, I want to record my blood donations so that I can keep track of my donation history. | Donors can add donation records; required donation information is validated; previous records are displayed in chronological order; donors can update their own records; donation history is private. | Medium | 3 | Sprint 4 | Samira Azizi |
| #016 | As a user, I want to manage my account information so that my personal information remains up to date. | Users can view and update permitted account information; updated information is validated and saved; changes appear correctly; sensitive information is protected. | Medium | 3 | Sprint 4 | Samira Azizi |
| #017 | As an administrator, I want to view and manage registered users so that I can maintain the platform properly. | Authorized administrators can view and search registered users; they can review relevant account information and manage accounts using permitted actions; unauthorized users cannot access these functions. | Medium | 5 | Sprint 4 | Shafiqa Taraki |
| #018 | As an administrator, I want to manage hospitals and blood donation centers so that users can access accurate location information. | Authorized administrators can add and update hospital and donation-center information; saved details are displayed correctly; only authorized administrators can manage these records. | Medium | 5 | Sprint 4 | Shafiqa Taraki |
| #019 | As an administrator, I want to review reported accounts and take appropriate action so that the platform remains safe. | Users can submit account reports; administrators can view reports and their details; administrators can review reported accounts and take permitted action; report status is recorded where applicable. | Medium | 5 | Sprint 4 | Shafiqa Taraki |
| #020 | As an administrator, I want to monitor blood requests and platform activities so that I can help maintain proper operation of the system. | Authorized administrators can view recorded blood requests and their statuses; request activity is displayed clearly; administrative monitoring functions are restricted to authorized users. | Medium | 8 | Sprint 4 | Shafiqa Taraki |

## 3. Technical and Enhancement Tasks

The following items support the implementation, security, reliability, and testing of the platform.

| ID | Task | Acceptance Criteria | Priority | Estimation | Sprint | Responsible |
|---|---|---|---|---:|---|---|
| #021 | Establish the project structure, database connection, and initial database schema for users, donor profiles, and related platform data. | The project structure is organized; the application connects to the database; required tables and relationships are defined; the application can run with the database connection. | Critical | 5 | Sprint 1 | Samira Azizi |
| #022 | Implement security controls for authentication, password storage, sessions, and role-based access. | Passwords are securely hashed; protected features require authentication; administrative functions require the correct role; users cannot access another user’s private information without authorization. | Critical | 5 | Sprint 1 | Samira Azizi |
| #023 | Protect donor privacy throughout profiles, search results, and location features. | Exact home addresses and private account information are not exposed in public results; approximate donor locations are used where appropriate; access to private information follows the platform’s authorization rules. | Critical | 3 | Sprints 1–2 | Samira Azizi and Ahmad Kaihan Saba |
| #024 | Validate user input and handle errors consistently. | Required fields and invalid inputs are checked; invalid data is not accepted; users receive clear error messages; errors do not expose sensitive technical information. | High | 3 | Sprints 1–4 | All Developers |
| #025 | Prepare and execute test cases, fix defects, and retest affected features. | Test cases and results are documented; defects are recorded; fixes are retested; important failures are addressed before the affected features are considered complete. | Critical | 5 | Sprints 1–4 | All Developers |

## 4. Non-Functional Requirements

The following quality requirements apply across the platform. They describe how the system should operate rather than introducing separate user-facing features.

| ID | Quality Requirement | Acceptance Criteria | Priority | Related Backlog Items | Responsible |
|---|---|---|---|---|---|
| NFR-001 | Security | Passwords are not stored as plain text; authenticated sessions are handled securely; private user data is protected from unauthorized access. | Critical | #001, #002, #022 | Samira Azizi |
| NFR-002 | Performance | Donor search and other common pages return results within an acceptable response time under normal usage conditions. | High | #006, #007, #008 | Ahmad Kaihan Saba |
| NFR-003 | Data Validation | Registration, profile, blood request, and other forms reject missing or invalid required information and provide understandable feedback. | High | #001, #003, #004, #010, #024 | All Developers |
| NFR-004 | Access Control | Only authorized administrators can access administrative functions; regular users can access only the features and information permitted for their roles. | Critical | #017, #018, #019, #020, #022 | Samira Azizi and Shafiqa Taraki |
| NFR-005 | Data Reliability | User profiles, donor availability, requests, messages, and other stored information can be saved and retrieved consistently. | High | #003, #005, #010, #014, #015, #021 | Samira Azizi |
| NFR-006 | Privacy | Exact donor home addresses and private account information are not publicly displayed; sensitive records are available only to authorized users. | Critical | #003, #009, #016, #023 | Samira Azizi and Ahmad Kaihan Saba |
| NFR-007 | Maintainability | Code is organized into understandable components, follows consistent naming practices, and is documented where needed to support future changes. | Medium | #021, #024, #025 | All Developers |
| NFR-008 | Usability | Main functions are clearly labeled, forms provide useful feedback, and users can navigate between important pages without unnecessary difficulty. | High | #001–#020 | All Developers |

## 5. Prioritization Strategy

Backlog items are prioritized according to their importance to the platform’s main purpose, user needs, security, and dependencies between features.

### Critical Priority

Critical items are necessary to establish the platform’s foundation and support its main purpose.

These include:

- Account registration and login (#001, #002)
- Donor profiles, blood types, and availability (#003, #004, #005)
- Searching for donors by blood type and location (#006, #007)
- Sending blood requests (#010)
- Project structure and database setup (#021)
- Authentication and access security (#022)
- Donor privacy protection (#023)
- Testing and defect correction (#025)

### High Priority

High-priority items provide important features for locating donors, protecting privacy, and supporting communication.

These include:

- Updating donor availability (#005)
- Viewing the map (#008)
- Sharing approximate donor locations (#009)
- Blood request notifications (#011)
- Accepting or declining requests (#012)
- Displaying request responses (#013)
- Messaging after request acceptance (#014)
- Input validation and error handling (#024)
- Important performance, validation, usability, and privacy requirements

### Medium Priority

Medium-priority items improve account management, donation records, and administrative operations.

These include:

- Recording donation history (#015)
- Managing account information (#016)
- Managing registered users (#017)
- Managing hospitals and donation centers (#018)
- Reviewing reported accounts (#019)
- Monitoring blood requests and platform activities (#020)

Priorities may be reviewed by the Product Owner as requirements become clearer. Changes should also consider dependencies. For example, request notifications and responses depend on the blood request feature being available.

## 6. Guidance on Sprint Planning

The project backlog is organized into four planned sprints. The team should confirm the selected items and their estimated workload during each sprint planning meeting. The following plan reflects the existing backlog assignments.

### Sprint 1: Platform Foundation and User Access

**Main Goal:** Establish the initial application structure and allow users to register, log in, and manage their basic donor information.

**Main Work:**

- #001 — Create an account
- #002 — Login and logout
- #003 — Create and update donor profiles
- #004 — Add blood type and availability information
- #005 — Change donor availability
- #021 — Set up the project structure and database
- #022 — Implement authentication and security controls
- #023 — Begin implementing donor privacy protections
- #024 — Validate input and handle errors
- #025 — Test implemented features

**Expected Increment:** A working foundation with user authentication, basic donor profiles, blood type and availability information, and an initial database.

### Sprint 2: Donor Search and Location Privacy

**Main Goal:** Allow blood seekers to find potential donors based on blood type and location while protecting donor privacy.

**Main Work:**

- #006 — Search donors by blood type
- #007 — Search donors by location and distance
- #009 — Display approximate donor locations
- #023 — Continue implementing donor privacy protections
- #024 — Validate search inputs and handle errors
- #025 — Test donor search and location-related features

**Expected Increment:** Users can search for potential donors using blood type and location criteria without publicly exposing exact donor home addresses.

### Sprint 3: Blood Requests and Communication

**Main Goal:** Enable blood seekers to send requests and allow donors to respond and communicate after accepting a request.

**Main Work:**

- #008 — Display nearby donors, hospitals, and donation centers on a map
- #010 — Send blood requests
- #011 — Notify donors about incoming requests
- #012 — Accept or decline requests
- #013 — Display request responses
- #014 — Enable messaging after request acceptance
- #024 — Validate request and messaging inputs
- #025 — Test and integrate related features

**Expected Increment:** A request-response workflow that allows users to send requests, view donor responses, and communicate after acceptance, alongside the planned map functionality.

### Sprint 4: Account Management and Administration

**Main Goal:** Complete account management and provide administrative tools for managing users, locations, reports, and platform activity.

**Main Work:**

- #015 — Record donation history
- #016 — Manage account information
- #017 — Manage registered users
- #018 — Manage hospitals and donation centers
- #019 — Review reported accounts
- #020 — Monitor blood requests and platform activities
- #024 — Complete input validation and error handling
- #025 — Complete testing, fix defects, and retest

**Expected Increment:** A more complete platform with donation history, account management, administrative features, and tested core workflows.

**Planning Note:** The sprint assignments are the current plan, not proof that the work has been completed. During each planning meeting, the team should review dependencies, confirm the work that can realistically be completed, and update the backlog when necessary.

## 7. Product Backlog Refinement

The Product Backlog will be reviewed and refined throughout development. The Product Owner is responsible for maintaining priorities and clarifying requirements with input from the Scrum Master and development team.

During refinement, the team may:

- Clarify user stories and acceptance criteria.
- Divide large features into smaller tasks when necessary.
- Review story-point estimates and technical dependencies.
- Change priorities when important user needs or technical issues are identified.
- Identify incomplete requirements and add missing tasks.
- Update item status and sprint assignments based on actual progress.
- Review testing needs and ensure privacy and security requirements are considered.

For example, if donor search does not protect private location information adequately, the team may prioritize the relevant privacy work before proceeding with map-related functionality. Similarly, if the blood request feature is incomplete, dependent features such as notifications, responses, and messaging may need to be adjusted.

Backlog updates should reflect actual team decisions and progress rather than assuming that planned work has already been completed.

## 8. Definition of Done

A backlog item will be considered Done when the following conditions applicable to that item have been satisfied:

- The feature or task has been implemented according to its description.
- All acceptance criteria have been met.
- The feature has been tested, and test results have been recorded where applicable.
- Important defects have been fixed and affected functionality has been retested.
- The code has been reviewed and integrated into the current project.
- Relevant security and privacy requirements have been checked.
- Required documentation has been updated.
- The work has been committed and pushed to the project’s GitHub repository.
- The Product Owner has reviewed the completed work against the agreed acceptance criteria.

An item should remain in progress or be marked as incomplete if important acceptance criteria have not been met. A planned task should not be marked Done solely because its sprint has ended.

---

**Prepared by:** Madina Pasun (Product Owner)  
**Project:** Ehda Portal: Online Blood Donation Platform  
**Course:** Software Engineering  
**Date:** October 08, 2026
