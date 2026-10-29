# Acceptance Criteria

## Project: Ehda Portal — Online Blood Donation Platform

### 1. Purpose

This document defines the acceptance criteria for the 20 user stories of Ehda Portal. Acceptance criteria describe the conditions that must be satisfied for a feature to meet its specified requirements.

These criteria support development, testing, sprint reviews, and product evaluation. Each criterion should be verified against the implemented system where the feature is available.

**Important:** A feature should only be marked as accepted or completed after the relevant criteria have been verified. Planned functionality that has not been implemented or tested must remain identified as incomplete.

---

## US-001 — User Registration

**Acceptance Criteria**

1. The system shall allow a new user to enter the required registration information.
2. The system shall validate required fields and reject missing or invalid information.
3. The system shall prevent registration using an email address that is already registered.
4. The system shall securely store the user's account information, including a protected password representation rather than a plain-text password.
5. The system shall display a success message after successful registration.
6. The registered user shall be able to use their credentials to log in.
7. If registration fails, the system shall display an appropriate error message without creating an invalid account.

## US-002 — Login and Logout

**Acceptance Criteria**

1. The system shall allow registered users to enter their email address and password.
2. The system shall verify the submitted credentials before granting access.
3. The system shall display an appropriate error message when the credentials are incorrect.
4. Users with valid credentials shall be able to access their authorized account pages.
5. The system shall provide a logout option to authenticated users.
6. After logout, the system shall invalidate or terminate the active session.
7. After logout, protected pages and account information shall not remain accessible through the previous authenticated session.

## US-003 — Donor Profile

**Acceptance Criteria**

1. A registered donor shall be able to create a donor profile.
2. The system shall allow the donor to enter the profile information required by the application.
3. The donor shall be able to update existing profile information.
4. The system shall save valid changes and display the updated information.
5. The system shall validate profile fields where applicable.
6. The donor shall be able to control the visibility of supported profile information.
7. Other users shall only be able to view profile information that the system permits them to access.

## US-004 — Blood Type and Donation Information

**Acceptance Criteria**

1. The donor shall be able to select a blood type from the available options.
2. The donor shall be able to provide the donation-related information supported by the system.
3. The selected blood type shall be displayed in the donor's profile.
4. The donor shall be able to update blood type or donation information when necessary.
5. The system shall validate the selected values and save valid updates.
6. Updated information shall be reflected wherever the relevant information is displayed.
7. The platform shall not present a donor's self-reported blood type as medically verified unless a verification process has actually been implemented.

## US-005 — Availability Status

**Acceptance Criteria**

1. The donor shall be able to set their availability status to **Available** or **Unavailable**.
2. The donor shall be able to change their availability status at any time when authenticated.
3. The system shall save the updated availability status.
4. Donor search results shall display availability status when that information is available and permitted to be shown.
5. Unavailable donors shall be clearly distinguished from available donors.
6. The system shall not present an unavailable donor as currently available.

## US-006 — Search by Blood Type

**Acceptance Criteria**

1. A blood seeker shall be able to select the required blood type.
2. The system shall return donors whose recorded blood type matches the selected search criterion.
3. Search results shall display relevant and permitted donor information, including blood type and availability where available.
4. The system shall handle searches with no matching results by displaying an appropriate message.
5. The system shall not expose private donor information in search results.
6. Search results shall reflect the latest saved donor information available to the system.

## US-007 — Search by Location or Distance

**Acceptance Criteria**

1. A blood seeker shall be able to provide or select a search location using the location options supported by the system.
2. The blood seeker shall be able to specify a search radius when distance-based filtering is supported.
3. The system shall display donors whose available location information falls within the selected search area.
4. When distance-based sorting is implemented, results shall be ordered according to calculated distance.
5. The system shall display an appropriate message when no donors match the location criteria.
6. The system shall use approximate donor locations in public-facing search features rather than exposing exact home addresses.
7. The system shall handle missing or unavailable location information without displaying misleading distance results.

## US-008 — Interactive Map

**Acceptance Criteria**

1. Authorized users shall be able to open and view the interactive map.
2. The map shall display supported nearby hospitals and donation centers when location data is available.
3. Donors shall be represented using approximate locations rather than exact home addresses.
4. Users shall be able to interact with the map using the implemented controls, such as viewing markers and selecting locations.
5. Selecting a map marker shall display the relevant information that the user is authorized to view.
6. The map shall provide appropriate feedback when location data is unavailable or no relevant locations are found.
7. Map information shall be consistent with the system's available location records.

## US-009 — Location Privacy

**Acceptance Criteria**

1. The system shall not display a donor's exact home address to other ordinary users.
2. The system shall use approximate donor locations in map and search features intended for other users.
3. The system shall restrict access to private location information to authorized operations and roles.
4. The system shall validate authorization before providing protected location information.
5. The system shall not expose exact addresses through public-facing results or map markers.
6. Location information shall be handled using appropriate access controls and secure data practices.
7. Location-based features shall remain usable without requiring the donor's exact home address to be publicly displayed.

## US-010 — Blood Request

**Acceptance Criteria**

1. An authenticated blood seeker shall be able to select a donor from the available search results.
2. The blood seeker shall be able to enter the required blood request information.
3. The system shall validate the required request fields before submission.
4. The system shall record each successfully submitted request and associate it with the relevant seeker and donor.
5. The intended donor shall be able to view the submitted request.
6. Each request shall have a status, such as **Pending**, **Accepted**, or **Declined**.
7. The system shall prevent invalid or incomplete requests from being submitted.
8. The system shall provide confirmation when a request is submitted successfully.

## US-011 — Blood Request Notifications

**Acceptance Criteria**

1. The system shall notify the intended donor when a new blood request is successfully received, using the notification mechanism implemented by the platform.
2. The notification shall indicate that a blood request has been received.
3. The donor shall be able to open or access the corresponding request from the notification when supported by the interface.
4. The system shall associate the notification with the correct request.
5. The donor shall be able to view the current status of the request.
6. Notification information shall be updated or supplemented when the request status changes, where supported.
7. The system shall not create notifications for requests that were not successfully recorded.

## US-012 — Accept or Decline a Request

**Acceptance Criteria**

1. An authenticated donor shall be able to view their pending blood requests.
2. The donor shall be able to accept a pending request.
3. The donor shall be able to decline a pending request.
4. The system shall update the request status after a valid response.
5. The updated status shall be visible to the relevant users according to their permissions.
6. The blood seeker shall be notified of the donor's response through the implemented notification mechanism.
7. The system shall prevent unauthorized users from responding to another donor's requests.
8. The system shall not allow a request that has already received a final response to be treated as pending without a valid system-supported status change.

## US-013 — Request Response

**Acceptance Criteria**

1. An authenticated blood seeker shall be able to view the blood requests they have submitted.
2. The system shall display the status of each request clearly.
3. The blood seeker shall be able to identify whether a request is pending, accepted, or declined.
4. The system shall make the donor's response available to the relevant blood seeker.
5. The blood seeker shall receive a notification of the response when the notification feature is available.
6. The displayed status shall correspond to the latest saved request status.
7. Users shall not be able to view request details that they are not authorized to access.

## US-014 — Messaging

**Acceptance Criteria**

1. The messaging option shall become available to the relevant donor and blood seeker after the associated blood request has been accepted.
2. Both the donor and the blood seeker shall be able to send messages within the permitted conversation.
3. The system shall display sent messages in the correct conversation.
4. Authorized conversation participants shall be able to view previous messages retained by the system.
5. The system shall prevent messaging through a request-related conversation before the request has been accepted.
6. Only the participants authorized for a conversation shall be able to access its messages.
7. The system shall provide appropriate feedback if a message cannot be sent.
8. Message content shall be stored and accessed according to the platform's security and privacy requirements.

## US-015 — Donation History

**Acceptance Criteria**

1. An authenticated donor shall be able to add a donation record using the information fields supported by the system.
2. The system shall validate required donation record fields before saving.
3. The donor shall be able to view their previously saved donation records.
4. Donation records shall be displayed in chronological order using the recorded donation dates.
5. The donor shall be able to update an existing record when permitted by the system.
6. The system shall save valid changes and display the updated record.
7. Donation history shall be accessible only to the donor and other specifically authorized roles or operations.
8. The system shall not expose a donor's private donation history to ordinary users.

## US-016 — Account Management

**Acceptance Criteria**

1. An authenticated user shall be able to view their own account information.
2. The user shall be able to update the account fields supported by the system.
3. The system shall validate updated information before saving changes.
4. The system shall save valid changes and display the updated account information.
5. The system shall provide an appropriate error message when an update is invalid or unsuccessful.
6. Sensitive account information shall be protected from unauthorized access.
7. Users shall not be able to modify another user's account through ordinary account-management functions.

## US-017 — User Management

**Acceptance Criteria**

1. An authorized administrator shall be able to view the registered users.
2. The administrator shall be able to search for users using the search options implemented by the system.
3. The administrator shall be able to view the account information permitted by their administrative role.
4. The administrator shall be able to perform the account-management actions supported by the platform.
5. The system shall restrict user-management functions to authorized administrators.
6. Unauthorized users shall not be able to access administrative user-management pages or perform administrative actions.
7. The system shall provide appropriate feedback when an administrative action succeeds or fails.

## US-018 — Hospital and Donation Center Management

**Acceptance Criteria**

1. An authorized administrator shall be able to add a hospital or donation center.
2. The administrator shall be able to update the information of an existing hospital or donation center.
3. The system shall validate required location and facility information before saving.
4. Saved facility information shall be displayed correctly in the relevant system views and map features.
5. The system shall prevent unauthorized users from adding or modifying facility records.
6. The system shall display appropriate feedback when facility information is saved or an operation fails.
7. Updated facility information shall be reflected in the relevant views after the changes are saved.

## US-019 — Reported Accounts

**Acceptance Criteria**

1. An authenticated user shall be able to submit a report about an account using the reporting options provided by the system.
2. The system shall record a successfully submitted report and associate it with the reported account.
3. An authorized administrator shall be able to view submitted account reports.
4. The administrator shall be able to review the report information available to their role.
5. The administrator shall be able to take the supported action on a report, such as updating its review status.
6. The system shall record the updated report status when an administrative action is completed.
7. Only authorized administrators shall be able to access restricted report-management functions.
8. The system shall provide appropriate feedback when a report is submitted or reviewed.

## US-020 — Platform Monitoring

**Acceptance Criteria**

1. An authorized administrator shall be able to view the blood request activity supported by the administrative interface.
2. The system shall display the current recorded status of blood requests.
3. The administrator shall be able to distinguish pending, accepted, and declined requests.
4. The displayed activity information shall be based on the records available in the system.
5. The system shall restrict platform-monitoring functions to authorized administrators.
6. The system shall display appropriate feedback when monitoring information is unavailable or cannot be loaded.
7. Monitoring features shall not expose private user information beyond what is necessary and authorized for the administrative function.

---

## 2. General Acceptance and Verification Rules

The following rules apply to all user stories where relevant:

1. **Requirement alignment:** The implemented feature must match the documented user story and its acceptance criteria.
2. **Input validation:** Required fields and supported data formats must be validated before information is saved.
3. **Access control:** Users must only be able to access functions and information permitted by their roles.
4. **Data persistence:** Successfully saved information must remain available when the relevant page or view is reopened, subject to the system's intended behavior.
5. **Error handling:** The system should provide understandable feedback when an operation fails or input is invalid.
6. **Privacy and security:** Personal information, account credentials, donor locations, messages, and donation history must be protected according to their access requirements.
7. **Testing evidence:** Where a feature is implemented, its acceptance criteria should be checked through appropriate tests or a documented demonstration.
8. **Honest status reporting:** A user story must not be marked as complete or accepted solely because its documentation has been written.

## 3. Acceptance Review

During a sprint review, the Product Owner and relevant team members should review the completed work against the applicable acceptance criteria. Any unmet criteria, defects, or incomplete functionality should be documented and addressed through the team's backlog process.

A user story may be considered accepted only when the required behavior has been implemented and the applicable acceptance criteria have been verified. Any changes to the agreed requirements should be documented and reflected in the relevant project artifacts.

