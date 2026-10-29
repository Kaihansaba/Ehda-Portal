# Roles and Responsibilities

**Course:** Software Engineering Project  
**Project Name:** Ehda Portal: An Online Blood Donation Platform

**Prepared by:**
- Madina Afshar
- Madina Pasun
- Samira Azizi
- Shafiqa Taraki
- Ahmad Kaihan Saba

---

## 1. Introduction

This document defines the roles, responsibilities, and areas of contribution of each team member working on the Ehda Portal project. The team follows the Scrum framework, which organizes the work into manageable Sprints and encourages collaboration, continuous improvement, and regular progress reviews.

The team consists of a Product Owner, a Scrum Master, and three Developers. Each member has a specific area of responsibility while also contributing to shared activities, including requirements analysis, system modeling, documentation, testing, and project reviews, as appropriate to their role.

## 2. Team Structure

| No. | Team Member | Scrum Role | Specific Responsibilities | General Responsibilities |
|---|---|---|---|---|
| 1 | Madina Pasun | Product Owner | Product backlog management, requirements, priorities, user stories, acceptance criteria, and product feedback | Representing user needs, maintaining project scope, clarifying requirements, and reviewing completed features against acceptance criteria |
| 2 | Madina Afshar | Scrum Master | Daily Scrum facilitation, Sprint coordination, time management, blocker identification, and Scrum process support | Encouraging collaboration, monitoring progress, maintaining meeting records, and helping the team follow Scrum practices |
| 3 | Samira Azizi | Developer 1 | Authentication, user management, donor profiles, and donation history | Requirements analysis support, system modeling, implementation, database work, testing, debugging, documentation, and code maintenance |
| 4 | Ahmad Kaihan Saba | Developer 2 | Donor search, interactive map, and location-based features | Requirements analysis support, system modeling, implementation, database queries, testing, debugging, documentation, and code maintenance |
| 5 | Shafiqa Taraki | Developer 3 | Blood requests, notifications, messaging, and admin dashboard | Requirements analysis support, system modeling, implementation, database work, testing, debugging, documentation, and code maintenance |

## 3. Product Owner

### 3.1 Role

The Product Owner is responsible for maximizing the value of the product by representing user needs, clarifying product requirements, and ensuring that the team works on the most important features. The Product Owner manages the Product Backlog and communicates priorities and expected outcomes to the Scrum Team.

**Assigned team member:** Madina Pasun

### 3.2 Responsibilities

The Product Owner is responsible for:

- Creating, organizing, and maintaining the Product Backlog.
- Identifying and documenting product requirements.
- Defining user stories based on the needs of donors, blood seekers, hospitals, and administrators.
- Prioritizing backlog items according to importance, user value, dependencies, and project scope.
- Defining clear and testable acceptance criteria for user stories.
- Explaining requirements and expected outcomes to the Developers.
- Clarifying questions about requirements during implementation.
- Collaborating with the Scrum Master and Developers during Sprint Planning.
- Participating in Sprint Reviews and providing feedback on completed features.
- Reviewing completed work against the agreed acceptance criteria.
- Managing changes to requirements and maintaining the agreed project scope.
- Ensuring that the project continues to address the needs of its intended users.
- Maintaining product-related documentation, including user stories and backlog records.

The Product Owner does not need to perform the Developers' coding tasks. The focus of this role is product value, requirements, priorities, and acceptance.

## 4. Scrum Master

### 4.1 Role

The Scrum Master is responsible for helping the team understand and follow Scrum principles and practices. The Scrum Master facilitates collaboration, supports effective Scrum events, and helps the team identify and address obstacles that interfere with progress.

**Assigned team member:** Madina Afshar

### 4.2 Responsibilities

The Scrum Master is responsible for:

- Facilitating Daily Scrum meetings.
- Preparing or coordinating meeting agendas when needed.
- Recording or ensuring the recording of meeting minutes and action items.
- Helping the team establish and maintain a realistic Sprint schedule.
- Monitoring Sprint progress and communicating potential delays.
- Identifying blockers and helping the team work toward resolving them.
- Encouraging communication and collaboration among team members.
- Helping the team understand and follow Scrum practices.
- Supporting the Product Owner in backlog refinement and clarification of user stories.
- Facilitating Sprint Planning, Sprint Reviews, and Sprint Retrospectives as appropriate.
- Encouraging team accountability and transparency regarding progress.
- Following up on action items agreed upon during meetings.
- Helping the team continuously improve its workflow.

The Scrum Master supports the team rather than assigning or controlling every technical task. Developers remain responsible for organizing their implementation work and communicating their progress.

## 5. Development Team

### 5.1 General Role

The Developers are responsible for designing, implementing, integrating, and testing the technical features of Ehda Portal. Each Developer has primary responsibility for specific modules, while all Developers collaborate to ensure that the modules work together as a complete system.

### 5.2 General Responsibilities

All Developers are responsible for:

- Implementing assigned requirements and features.
- Contributing technical information to the Software Requirements Specification (SRS) when needed.
- Participating in requirements analysis and system modeling.
- Developing and maintaining relevant UML diagrams, including Use Case and Sequence Diagrams.
- Designing and maintaining the database structures required for their modules.
- Writing, running, and documenting tests for assigned features.
- Identifying and fixing bugs and other implementation problems.
- Participating in Daily Scrum meetings, Sprint Planning, Sprint Reviews, and other relevant team activities.
- Reporting progress, completed work, and blockers accurately.
- Collaborating with the Product Owner to clarify requirements and acceptance criteria.
- Coordinating with other Developers on module dependencies and integration.
- Maintaining and updating source code in the GitHub repository.
- Following agreed coding, documentation, and version-control practices.
- Providing evidence of implemented and tested functionality when required.

## 6. Developer 1: Authentication, User Management, Donor Profiles, and Donation History

**Assigned team member:** Samira Azizi

Developer 1 is primarily responsible for user accounts, authentication, donor profile management, and donation history.

### 6.1 Authentication and User Management

Responsibilities include:

- Implementing user registration.
- Implementing login and logout functionality.
- Supporting password creation, updating, and recovery functionality as included in the project scope.
- Implementing authentication and session management.
- Managing user roles and access permissions.
- Supporting account management and profile access.
- Validating user inputs and handling invalid or incomplete data.
- Protecting passwords and other sensitive account information.
- Ensuring that restricted features are accessible only to authorized users.

### 6.2 Donor Profiles

Responsibilities include:

- Implementing donor profile creation and editing.
- Managing donor blood-type information.
- Managing donor contact information, including phone numbers.
- Managing donor location information and availability.
- Allowing donors to update their information.
- Ensuring that profile information is displayed according to the platform's privacy rules.
- Supporting the secure storage and retrieval of donor profile information.

### 6.3 Donation History

Responsibilities include:

- Implementing the donation-history functionality within the agreed project scope.
- Supporting the storage and retrieval of donation-history records.
- Allowing authorized users to view relevant history information.
- Ensuring that donation-history data is handled appropriately.

### 6.4 Additional Responsibilities

- Designing and maintaining database structures related to users, donor profiles, and donation history.
- Testing registration, login, profile management, and donation-history functionality.
- Identifying and fixing bugs in assigned modules.
- Coordinating with other Developers when their modules depend on user accounts or donor profile data.

## 7. Developer 2: Donor Search and Interactive Map

**Assigned team member:** Ahmad Kaihan Saba

Developer 2 is primarily responsible for helping users find potential blood donors and view relevant location-based information.

### 7.1 Blood Donor Search

Responsibilities include:

- Implementing donor searches based on blood type.
- Supporting location-based donor searches.
- Supporting distance-based searches where feasible.
- Implementing relevant search filters.
- Displaying search results in a clear and understandable format.
- Displaying only the donor information appropriate for the current user and purpose.
- Handling cases where no matching donors are found.
- Coordinating search functionality with the donor-profile and location data managed by other modules.

### 7.2 Interactive Map

Responsibilities include:

- Implementing the interactive map interface.
- Displaying approximate locations of potential donors.
- Displaying hospitals and blood donation centers when the required location data is available.
- Implementing location-based functionality.
- Integrating Leaflet and OpenStreetMap, as planned for the project.
- Displaying location information in a useful and understandable way.
- Supporting map markers and relevant location details.
- Applying location-privacy requirements to prevent unnecessary exposure of donors' exact home addresses.

### 7.3 Additional Responsibilities

- Developing and maintaining database queries needed for donor search, blood type, and location-based filtering.
- Coordinating with Developer 1 on donor profile and user data.
- Testing search filters, map markers, and location-based functionality.
- Identifying and fixing bugs in assigned modules.
- Verifying that map and search results are displayed correctly using available test data.

## 8. Developer 3: Blood Requests, Notifications, Messaging, and Admin Dashboard

**Assigned team member:** Shafiqa Taraki

Developer 3 is primarily responsible for the blood-request workflow, communication between users, notifications, and administrative functionality.

### 8.1 Blood Requests

Responsibilities include:

- Implementing the creation of blood requests.
- Supporting the delivery of requests to relevant donors.
- Managing blood-request information.
- Implementing request-status management.
- Allowing donors to accept or decline requests.
- Updating request statuses when responses are submitted.
- Displaying relevant request information to authorized users.
- Handling request states consistently throughout the workflow.

### 8.2 Notifications

Responsibilities include:

- Notifying donors when they receive blood requests.
- Notifying relevant users when requests are accepted or declined.
- Supporting other notifications included in the agreed project scope.
- Ensuring that notifications contain relevant information without unnecessarily exposing sensitive data.
- Testing notification behavior throughout the request workflow.

### 8.3 Messaging

Responsibilities include:

- Implementing communication between blood seekers and donors.
- Supporting the sending and receiving of messages.
- Maintaining message history as required by the project.
- Restricting message access to the appropriate participants.
- Coordinating messaging functionality with request statuses and user permissions.
- Testing message delivery and access control.

### 8.4 Admin Dashboard

Responsibilities include:

- Implementing the administrative dashboard.
- Supporting authorized administrators in managing user accounts.
- Supporting the management of hospital and blood donation center information.
- Providing functionality for reviewing reported accounts.
- Supporting administrative actions within the agreed project scope.
- Displaying relevant platform information to authorized administrators.
- Ensuring that administrative features are protected by appropriate access controls.

### 8.5 Additional Responsibilities

- Designing and maintaining database structures related to blood requests, messages, notifications, and administration.
- Testing the request, notification, messaging, and administrative workflows.
- Identifying and fixing bugs in assigned modules.
- Coordinating with other Developers to integrate user, donor-search, and request-related functionality.

## 9. Collaboration and Communication

Although each team member has a primary area of responsibility, the successful completion of Ehda Portal depends on collaboration across the team.

The team follows these practices:

- **Requirements communication:** The Product Owner clarifies product requirements and acceptance criteria.
- **Sprint coordination:** The Scrum Master facilitates Scrum events and helps the team address blockers.
- **Technical collaboration:** Developers coordinate dependencies, share relevant technical information, and integrate their modules.
- **Progress reporting:** Each team member communicates actual progress, completed work, and difficulties.
- **Documentation:** Team members maintain the project documents and technical records relevant to their responsibilities.
- **Version control:** Code and documentation are maintained in the shared GitHub repository.
- **Testing and review:** Developers test assigned features, while the team reviews the completed work against the agreed requirements.
- **Continuous improvement:** The team discusses problems and identifies practical improvements during appropriate review and retrospective activities.

## 10. Conclusion

The defined roles and responsibilities provide a clear division of work for the Ehda Portal project. The Product Owner focuses on product requirements, priorities, and acceptance; the Scrum Master supports the Scrum process and team collaboration; and the Developers design, implement, test, and maintain the assigned system modules.

By coordinating their responsibilities, communicating progress honestly, and maintaining the required documentation, the team aims to develop a functional, maintainable, and privacy-conscious online blood donation platform that addresses the needs of donors, blood seekers, hospitals, and administrators.
