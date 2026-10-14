# AI Travel Planner

AI Travel Planner suggests travel itineraries based on a traveler's interests, budget and available time. It builds an AI-curated day-wise plan, recommends local activities, generates a plan that fits a stated budget, and lists the transport options (flight, train, bus and cab) and hotels for the trip.

The project is developed for IT314 Software Engineering (Group 12). It recommends hotels and transport and links out to the providers where a link is available. It does not take bookings or payments.

## Contents

1. [Overview](#1-overview)
2. [Design decisions](#2-design-decisions)
3. [User flow](#3-user-flow)
4. [Requirements](#4-requirements)
5. [Failure handling](#5-failure-handling)
6. [Budget and validation rules](#6-budget-and-validation-rules)
7. [Architecture and technology stack](#7-architecture-and-technology-stack)
8. [Data model](#8-data-model)
9. [API](#9-api)
10. [Authentication and privacy](#10-authentication-and-privacy)
11. [Repository layout](#11-repository-layout)
12. [Testing](#12-testing)
13. [Scope and sprint plan](#13-scope-and-sprint-plan)

## 1. Overview

A traveler registers, logs in and creates a trip by entering a destination, departure city, dates or duration, number of travelers, total budget, interests, travel style (relaxed or fast-paced), and transportation and accommodation preferences. The system returns a day-wise itinerary with activities verified against real-world location data, hotel and transport options, an estimated cost and a budget check. The traveler can view the itinerary on an interactive map with optimized routes, customize it manually (add, remove, reorder or replace activities), track spending against the budget, and export the result as a PDF.

### Features

- Account registration and login, with trips private to their owner.
- Trip management: create, view, edit and delete trips, including budget, interests, travel style and preferences.
- AI-generated, day-wise itineraries personalized to the trip details, with regeneration after preferences change.
- Local activity and attraction suggestions ranked by interest, verified against real-world location data, with verified fallback recommendations.
- Hotel and transport recommendations, with comparison of transport options by estimated cost and travel time.
- Interactive map with markers, routes, distances and travel-time estimates between stops.
- Route optimization that groups nearby activities and reduces backtracking.
- Estimated trip cost with a category breakdown, planned daily budget, cost alerts and budget validation.
- Manual customization with automatic route, schedule and budget recalculation after every change.
- Schedule validation: durations, opening hours, overlaps and fit within the travel dates.
- PDF export of generated and customized itineraries.
- Graceful handling of AI-service and external API failures, with clear error messages and a retry option.

### Out of scope

In-app booking and payment, collaborative editing, price alerts, anonymous guest planning and public share links are not part of the current version.

### Project status

The project is under active development. Section 4 lists the functional requirements, non-functional requirements, user stories and domain rules, and section 13 shows what is planned for each of the five sprints.

## 2. Design decisions

| Topic | Decision |
| --- | --- |
| Accounts | Trip data is private. Users register and log in before creating trips, and every trip is owned by exactly one user. |
| Trip creation | Guided multi-step form that ends on a review screen. |
| Itinerary generation | The AI model produces a structured proposal. The backend validates its structure and the domain rules before anything is shown or saved. |
| Place verification | Every recommended place is checked against real-world location data (Google Places). If a place cannot be found, a verified fallback recommendation is offered. Unverified places are marked clearly in the itinerary and on the map. |
| Maps and routes | Google Maps JavaScript API displays the map. Google Routes API supplies distances and travel times. Route optimization runs in the backend. |
| Budget | The planner tries to meet the budget. It shows the estimated total, the daily budget and a category breakdown, warns when a threshold is reached or the budget is exceeded, and suggests lower-cost alternatives. The budget is never exceeded silently. |
| Customization | Users can add, remove, reorder and replace activities. After every change the backend revalidates the schedule, recalculates routes and updates the budget. |
| Travel products | Hotels and transport are recommended with estimated prices and external links where available. No bookings are made. |
| Data quality | Live data is used where available and everything else is labeled. Availability, schedules, opening hours and prices are never invented. Costs and travel times are always presented as estimates. |
| Backend responsibility | Validation, domain rules, budget calculation, route calculation, authorization and persistence run in the backend. Frontend checks and AI instructions are not relied on. |
| Failed generation | An incomplete or invalid itinerary is never saved as a successful result. |
| Export | PDF export is in scope. |
| Administrator | A protected area for account management, AI-quality review and reference data (user stories US-15 to US-17). Not part of the sprint deliverables; built after the core sprint items if time allows. |

### Data status labels

Every price, schedule, opening hour and availability value shown to the user carries one of these labels.

| Label | Meaning |
| --- | --- |
| Verified | Retrieved from a provider or a reference-data entry. The source and retrieval time are recorded. |
| Cached | Retrieved earlier and reused. The age is shown. |
| Estimated | Calculated or inferred without confirmation from a source. |
| Unverified | Availability, schedule or location has not been checked, or could not be checked. |
| Unavailable | Applied only when the provider confirms it. A provider timeout is not proof of unavailability. |

## 3. User flow

### Actors

| Actor | Role |
| --- | --- |
| Traveler | A registered, signed-in user who plans, customizes, saves and exports trips. |
| Administrator | A signed-in user with extra permissions, working in a separate protected interface. |
| AI model | Generates and revises itinerary proposals through a common LLM interface. |
| External APIs | Supply places, opening hours, routing, flight, hotel and transport data. |

### Trip form

| Step | Inputs |
| --- | --- |
| 1. Destination | Destination |
| 2. Departure | Departure city (needed for intercity transport options) |
| 3. Dates | Travel start date and duration, or start and end dates |
| 4. Travelers | Number of travelers (a positive whole number) |
| 5. Budget | Total trip budget (a positive number), currency, and the cost categories the budget includes |
| 6. Interests | One or more activities, attractions or travel interests |
| 7. Travel style | Relaxed or fast-paced |
| 8. Transport | Supported transportation preferences |
| 9. Accommodation | Supported accommodation preferences |
| 10. Special requirements | Optional notes such as accessibility or dietary needs |
| 11. Review | Summary of all choices, with links back to each step |

Departure city and special requirements are optional additions to the core inputs. The same form, pre-filled with the saved values, is used to edit a trip and regenerate its itinerary (US-08).

### Pages

| ID | Page | Purpose | Next |
| --- | --- | --- | --- |
| P-01 | Landing | Entry point with links to register or log in. | P-02 |
| P-02 | Register and login | Account creation and sign-in. Errors never reveal sensitive information. | P-03 |
| P-03 | My Trips | Lists the user's saved trips and itineraries. Open, edit and delete (with confirmation) are available. | P-04, P-06 |
| P-04 | Trip form | Collects the inputs above, validates each step, keeps earlier answers and shows field-level errors. Ends with the review screen. | P-05 |
| P-05 | Generation status | Shows a loading indicator, and offers retry or a way back to the form after a failure. | P-06 |
| P-06 | Itinerary dashboard | Day-wise schedule, activities, hotels, transport comparison, interactive map, travel times, cost breakdown, daily budget, alerts and data labels. Entry point for customization, regeneration, PDF export and deletion. | P-04, P-07 |
| P-07 | Customize itinerary | Add, remove, reorder or replace activities. Validation, route recalculation and budget updates run after each change. | P-06 |
| P-08 | Administrator console | Account management, flagged itineraries and feedback, and reference data. Limited to administrators. | Console, or login if unauthorized |

### Main flow

1. The user registers or logs in.
2. The user creates a trip with the trip form and confirms the review screen.
3. The frontend and backend validate the inputs. Invalid fields return the user to the relevant step.
4. The trip is saved with all its details.
5. The user requests an itinerary. The backend gathers destination, place and (where available) transport and hotel data.
6. The AI model proposes a structured day-wise itinerary.
7. The backend validates the proposal against the output schema and domain rules DR-01 to DR-09. Invalid or incomplete responses are retried a bounded number of times, then reported as a failure. They are never saved as successful.
8. Recommended places are verified against real-world location data. A place that cannot be found is replaced with a verified fallback or flagged as unverified.
9. The backend optimizes the order of activities, calculates distances and travel times, estimates costs and compares the total with the budget.
10. The dashboard shows the itinerary, map, transport comparison, costs, budget status and data labels.
11. The user customizes the itinerary. After every change the backend revalidates the schedule, recalculates routes and updates costs (FR-40).
12. If the estimate exceeds the budget or the alert threshold, the user sees the overrun and lower-cost alternatives.
13. The user can edit the trip preferences and regenerate the itinerary. Routes and costs are recalculated for the new itinerary.
14. The user saves, reopens or deletes itineraries from My Trips, and exports the latest saved itinerary as a PDF.
15. Separately, administrators manage accounts, review feedback and flagged itineraries, and maintain reference data.

## 4. Requirements

The requirements below are final. Section 13 maps them onto the five sprints.

### 4.1 Functional requirements

| ID | Requirement | Sprint |
| --- | --- | --- |
| FR-01 | The system shall allow users to register for an account. | 1 |
| FR-02 | The system shall allow registered users to log in securely. | 1 |
| FR-03 | The system shall allow users to create a new trip. | 1 |
| FR-04 | The system shall allow users to select a destination for their trip. | 1 |
| FR-05 | The system shall allow users to specify the travel start date and duration. | 1 |
| FR-06 | The system shall allow users to specify the number of travelers. | 1 |
| FR-07 | The system shall allow users to enter a total trip budget. | 1 |
| FR-08 | The system shall allow users to select their travel interests. | 1 |
| FR-09 | The system shall allow users to select a travel style, such as fast-paced or relaxed. | 1 |
| FR-10 | The system shall allow users to save generated itineraries. | 2 |
| FR-11 | The system shall allow users to view their saved itineraries. | 2 |
| FR-12 | The system shall allow users to edit trip details. | 1 |
| FR-13 | The system shall allow users to delete saved itineraries. | 2 |
| FR-14 | The system shall generate an itinerary using the user's trip details and preferences. | 2 |
| FR-15 | The system shall organize the generated itinerary day-wise according to the trip duration. | 2 |
| FR-16 | The system shall recommend activities and attractions based on the destination and the user's interests. | 2 |
| FR-17 | The system shall estimate the total cost of the planned trip. | 2 |
| FR-18 | The system shall validate AI-generated itineraries against the system's defined itinerary rules. | 2 |
| FR-19 | The system shall validate AI-generated output against a predefined structured data format. | 2 |
| FR-20 | The system shall provide alternative verified recommendations when a suggested place cannot be found or verified. | 2 |
| FR-21 | The system shall display itinerary activities on an interactive map. | 3 |
| FR-22 | The system shall calculate the distance between consecutive itinerary stops. | 3 |
| FR-23 | The system shall estimate travel time between consecutive itinerary stops. | 3 |
| FR-24 | The system shall verify recommended places against real-world location data. | 2, 3 |
| FR-25 | The system shall optimize activity routes to reduce unnecessary travel and backtracking. | 3 |
| FR-26 | The system shall recalculate routes when itinerary activities are added, removed, or reordered. | 3, 4 |
| FR-27 | The system shall recommend suitable transportation options for travel between activities. | 3 |
| FR-28 | The system shall compare available transportation options based on supported criteria, such as estimated travel time and cost. | 3 |
| FR-29 | The system shall track estimated trip spending against the user's specified budget. | 4 |
| FR-30 | The system shall notify users when estimated spending exceeds the budget or a defined budget threshold is reached. | 4 |
| FR-31 | The system shall display a category-wise breakdown of estimated trip expenses. | 4 |
| FR-32 | The system shall allow users to add activities to an itinerary manually. | 4 |
| FR-33 | The system shall allow users to remove activities from an itinerary manually. | 4 |
| FR-34 | The system shall allow users to reorder activities within an itinerary. | 4 |
| FR-35 | The system shall validate activity durations and scheduling feasibility. | 4 |
| FR-36 | The system shall detect and prevent overlapping scheduled activities. | 4 |
| FR-37 | The system shall validate planned activities against available opening-hours information. | 4 |
| FR-38 | The system shall check whether the estimated trip cost satisfies the user's budget constraint. | 4 |
| FR-39 | The system shall allow users to export their itineraries as PDF files. | 4, 5 |
| FR-40 | The system shall preserve itinerary consistency by integrating activity scheduling, budget validation, and route recalculation after itinerary modifications. | 4 |

### 4.2 Non-functional requirements

| ID | Requirement |
| --- | --- |
| NFR-01 | The system shall load standard application pages within 3 seconds under normal operating conditions. |
| NFR-02 | The system shall return saved itinerary details within 2 seconds under normal operating conditions. |
| NFR-03 | The system shall aim to generate a complete AI itinerary within 30 seconds under normal operating conditions, excluding exceptional third-party service delays. |
| NFR-04 | The system shall recalculate an itinerary's routes within 5 seconds after a user modification for a typical trip. |
| NFR-05 | The system shall protect user credentials using secure password hashing and shall not store passwords in plaintext. |
| NFR-06 | The system shall restrict access to private trip data to authorized users. |
| NFR-07 | The system shall validate and sanitize user inputs to reduce the risk of injection and other input-based attacks. |
| NFR-08 | The system shall use encrypted connections when transmitting sensitive user data. |
| NFR-09 | The system shall protect API keys and other secrets from exposure in client-side code and public repositories. |
| NFR-10 | The system shall handle AI-service and external API failures gracefully without crashing the application. |
| NFR-11 | The system shall display an appropriate error message when itinerary generation fails. |
| NFR-12 | The system shall preserve saved itinerary data when an external service becomes temporarily unavailable. |
| NFR-13 | The system shall avoid saving incomplete or invalid itinerary data as a successfully generated itinerary. |
| NFR-14 | The system shall provide a clear and consistent interface for creating, viewing, and editing trips. |
| NFR-15 | The system shall display itinerary activities in a readable day-wise format. |
| NFR-16 | The system shall provide clear feedback when an itinerary is generated, saved, edited, exported, or when an operation fails. |
| NFR-17 | The system shall present budget information, travel distances, and estimated travel times in understandable formats. |
| NFR-18 | The system shall allow users to complete the main trip-planning workflow without requiring technical knowledge of AI systems. |
| NFR-19 | The system shall validate AI-generated itinerary data before presenting it as a finalized itinerary. |
| NFR-20 | The system shall use real-world location data to verify recommended places and their geographic coordinates. |
| NFR-21 | The system shall calculate trip budgets, distances, and travel-time estimates consistently using the available input data. |
| NFR-22 | The system shall clearly identify estimated costs and travel times as estimates rather than guaranteed values. |
| NFR-23 | The system shall use available opening-hours information without treating missing or unavailable data as confirmed opening hours. |
| NFR-24 | The system shall use a modular architecture that separates user management, itinerary generation, route processing, and budget management. |
| NFR-25 | The system shall allow individual components to be updated without requiring unnecessary changes to unrelated components. |
| NFR-26 | The system shall maintain clear and consistent naming conventions and documentation for its code and APIs. |
| NFR-27 | The system shall support adding more destinations, activities, and transportation options without requiring a complete system redesign. |
| NFR-28 | The system shall function on commonly used modern web browsers, including Chrome, Firefox, Edge, and Safari. |
| NFR-29 | The user interface shall adapt to desktop, tablet, and mobile screen sizes. |
| NFR-30 | The system shall provide PDF exports that can be opened using standard PDF readers. |
| NFR-31 | The system shall maintain consistency between saved itinerary details and the activities displayed to the user. |
| NFR-32 | The system shall validate trip dates, traveler counts, budget values, and activity schedules before processing them. |
| NFR-33 | The system shall ensure that itinerary modifications trigger the required updates to routes, schedules, and budget estimates. |
| NFR-34 | The system shall prevent unauthorized users from modifying or deleting another user's private itineraries. |

### 4.3 User stories

<details>
<summary>Traveler (US-01 to US-14)</summary>

**US-01 — Register and Log In.** As a traveler, I want to register and log in to my account so that I can securely access and manage my saved trips.

- A new user can register using a valid email address and password.
- A registered user can log in with valid credentials.
- Invalid credentials produce a clear error message without revealing sensitive information.
- Users can access only their own private itineraries.

**US-02 — Create a Trip.** As a traveler, I want to create a trip by entering its destination, dates, and number of travelers so that the system can prepare a suitable travel plan.

- The user must provide a destination, travel dates or duration, and traveler count.
- The system rejects invalid date ranges.
- The traveler count must be a positive whole number.
- The system saves the submitted trip details when the trip is created successfully.

**US-03 — Set Budget, Interests, and Travel Style.** As a traveler, I want to specify my budget, interests, and travel style so that the generated itinerary reflects my preferences.

- The budget must be a positive numeric value.
- The user can select multiple interests.
- The user can choose a supported travel style, such as relaxed or fast-paced.
- The selected preferences are saved with the trip and used during itinerary generation.

**US-04 — Set Transportation and Accommodation Preferences.** As a traveler, I want to specify my transportation and accommodation preferences so that the recommendations align with my travel needs.

- The user can select from the transportation and accommodation preferences supported by the application.
- The selected preferences are associated with the trip.
- Recommendations use those preferences whenever relevant information is available.

**US-05 — Generate a Day-Wise Itinerary.** As a traveler, I want the system to generate a day-wise itinerary using my trip details and preferences so that I can plan my trip without arranging every activity manually.

- The generated itinerary covers the requested trip duration.
- Activities are organized by day and presented in chronological order.
- The system displays a loading indicator while generating the itinerary.
- If generation fails, the system displays an error and allows the user to retry.
- The generated itinerary is checked against the required output structure before being accepted.

**US-06 — View Activity and Travel Recommendations.** As a traveler, I want to view recommended attractions, activities, accommodation options, and transportation options so that I can choose suitable options for my trip.

- Each available recommendation displays its name and a short description.
- Approximate costs are displayed when cost information is available.
- Transportation options can be compared using estimated cost and travel time when data is available.
- Missing information is clearly identified instead of being presented as confirmed information.

**US-07 — View Estimated Trip Cost.** As a traveler, I want to view the estimated total and daily costs of my itinerary so that I can determine whether the trip fits my budget.

- The system displays the estimated total trip cost and estimated daily cost.
- The system provides a category-wise breakdown covering accommodation, transportation, activities, and food where estimates are available.
- The system compares the estimated total cost with the user's budget.
- If the estimated cost exceeds the budget, the system identifies the overrun and suggests a lower-cost alternative where possible.

**US-08 — Modify Preferences and Regenerate an Itinerary.** As a traveler, I want to modify my trip preferences and regenerate my itinerary so that I can obtain a plan that better meets my needs.

- The system allows the user to reopen the trip form with previously entered values populated.
- The user can modify supported trip details and preferences.
- The system generates an updated itinerary using the revised inputs.
- The updated itinerary's estimated costs, schedule, and routes are recalculated where applicable.

**US-09 — Replace an Activity with an Alternative.** As a traveler, I want to replace an activity with an alternative so that I can customize my itinerary without regenerating the entire trip.

- The user can request an alternative for an eligible activity.
- The alternative is checked against the user's interests and available schedule.
- The system updates the affected day's itinerary and estimated cost.
- The system recalculates the affected route when routing information is available.

**US-10 — View the Itinerary on an Interactive Map.** As a traveler, I want to view my itinerary activities on an interactive map so that I can understand the locations of activities and the travel required between them.

- Activities with verified coordinates are displayed as map markers.
- The system displays the route between consecutive stops when routing data is available.
- Estimated distance and travel time are displayed between consecutive stops.
- The system communicates unavailable location or routing information clearly.

**US-11 — Save, View, Edit, and Delete Itineraries.** As a traveler, I want to save, view, edit, and delete my itineraries so that I can manage my trips from my account.

- The system displays saved itineraries in the user's trip list.
- The user can reopen a saved itinerary.
- Changes made to an itinerary persist after saving.
- The system requests confirmation before deleting an itinerary.
- Users cannot modify or delete another user's private itineraries.

**US-12 — Export an Itinerary as PDF.** As a traveler, I want to export my itinerary as a PDF so that I can keep or share a readable copy of my travel plan.

- The user can export a saved or generated itinerary as a PDF.
- The PDF contains the day-wise itinerary and estimated cost summary.
- The exported content reflects the latest saved itinerary.
- The generated PDF can be opened using a standard PDF reader.

**US-13 — Validate an Itinerary.** As a traveler, I want the system to validate places, opening hours, activity durations, schedule conflicts, and budget constraints so that I receive a practical itinerary.

- Recommended places are checked against available real-world location data.
- Opening hours are checked when reliable information is available.
- Activity durations and schedule overlaps are validated.
- Estimated trip costs are checked against the user's budget.
- Invalid or unverifiable items are flagged or replaced where possible.
- Missing external information is not treated as verified.

**US-14 — Optimize Activity Routes.** As a traveler, I want activities to be grouped geographically and ordered efficiently so that I can reduce unnecessary travel and backtracking.

- The system uses available location and routing information to organize activities efficiently.
- Nearby activities are grouped together where practical.
- The system attempts to reduce unnecessary travel compared with the original activity order.
- The system recalculates the affected route after itinerary modifications.

</details>

<details>
<summary>Administrator (US-15 to US-17)</summary>

**US-15 — Manage User Accounts.** As an administrator, I want to view, suspend, or remove user accounts so that I can manage access to the platform.

- Only authorized administrators can access account-management functions.
- Administrators can perform the supported account-management actions.
- Administrative actions are logged.

**US-16 — Monitor AI Output Quality.** As an administrator, I want to review feedback and flagged itineraries so that I can identify problems with generated recommendations.

- The system displays submitted feedback and flagged itineraries to authorized administrators.
- Each entry includes enough context to identify the affected recommendation.
- Results can be filtered by rating or issue type.

**US-17 — Manage Reference Data.** As an administrator, I want to manage destination, accommodation, and transportation reference data so that future recommendations can use updated information.

- Authorized administrators can add, edit, or deactivate reference entries if this management feature is implemented.
- Changes are reflected in subsequent recommendations.
- The system records the data source or update time when available.

</details>

<details>
<summary>Development team (US-18 to US-20)</summary>

**US-18 — Configure Integrations and Handle Errors.** As a developer, I want API credentials, rate limits, logging, and error handling to be configurable so that external integrations remain maintainable and failures can be diagnosed.

- API credentials and secrets are stored outside the source code.
- Sensitive information is not exposed in application logs or user-facing error messages.
- API failures are logged with sufficient diagnostic information.
- Users receive a clear message when a required external service is unavailable.

**US-19 — Ground and Evaluate AI Output.** As a developer, I want to evaluate AI-generated itineraries and optionally use destination grounding so that the team can measure output quality and reduce unsupported recommendations.

- If destination grounding is implemented, it uses a defined source of destination information.
- If evaluation is implemented, it reports documented quality measures.
- Evaluation results are not treated as proof that every recommendation is correct.

**US-20 — Support Modular LLM Integration.** As a developer, I want LLM calls to use a common interface so that the model provider can be changed with minimal changes to the application.

- Provider calls use a defined interface.
- Provider-specific configuration is separated from itinerary-generation logic.
- Changing the provider does not require rewriting unrelated application components.

</details>

<details>
<summary>External data providers (US-21 to US-23)</summary>

**US-21 — Supply Accommodation Data.** As an accommodation data provider, I want available property information to be accessible to the planner so that travelers can receive relevant accommodation recommendations.

- Available accommodation data includes name, location, price range, and amenities when supplied.
- Updated information is reflected in subsequent recommendations after the data source refreshes.
- The system does not claim live availability unless the data source supports it.

**US-22 — Supply Transportation Data.** As a transportation data provider, I want available route, duration, and fare information to be accessible to the planner so that travelers can compare transportation options.

- Available transportation information includes mode, route, duration, and approximate cost.
- The system displays the available options in transportation comparisons.
- Missing or outdated information is not presented as confirmed live data.

**US-23 — Support Reliable Authenticated API Access.** As a developer integrating external LLM, map, or other APIs, I want API requests to be authenticated and handled within service limits so that integrations operate reliably.

- API requests use valid credentials.
- Requests comply with documented rate limits.
- Responses are parsed and validated before use.
- Timeouts and quota errors trigger an appropriate bounded retry or fallback when supported.
- External service failures do not crash the application.

</details>

### 4.4 Domain rules

Domain rules are enforced in backend code and covered by tests. A prompt to the AI model is not enough on its own. They implement the requirements above and are referenced from the flow and the failure-handling table.

| ID | Rule | Related requirements | Enforcement |
| --- | --- | --- | --- |
| DR-01 | Respect opening hours | FR-37, NFR-23, US-13 | Check opening hours from the source where reliable. Mark unknown hours explicitly and never treat them as confirmed. |
| DR-02 | Recommend activities relevant to the selected interests | FR-16 | Check each activity against the selected interests. |
| DR-03 | Account for the user's budget | FR-17, FR-29, FR-38 | Calculate the estimated cost and run the budget decision. |
| DR-04 | Avoid overlapping activities | FR-36 | Compare activity start and end intervals and reject conflicts. |
| DR-05 | Respect trip dates and duration | FR-15, FR-35, NFR-32 | Keep the schedule inside the user's travel dates and the itinerary length equal to the trip duration. |
| DR-06 | Account for travel time between locations | FR-23, FR-35 | Use route and time estimates and reject impossible transitions. |
| DR-07 | Aggregate costs by the categories the user selected | FR-31, US-07 | Include only selected categories in the total. |
| DR-08 | Unverified data is not shown as confirmed | FR-24, NFR-20, NFR-23, US-13 | Places, availability and schedules need a Verified label to be shown as confirmed. |
| DR-09 | Revalidate after a date change | FR-12, US-08 | Date-dependent schedule and cost data is rechecked before the itinerary is shown as current. |

## 5. Failure handling

| ID | Situation | Behavior |
| --- | --- | --- |
| AF-01 | Invalid or incomplete input | Show field errors, keep valid entries and return to the right step. The AI model is not called until required input is valid. |
| AF-02 | Unrealistic budget | Explain that the data does not support a suitable plan within the budget. Offer lower-cost alternatives or a budget change. The limit is never exceeded silently. |
| AF-03 | Malformed or invalid AI output | Validate structure and domain rules, retry a bounded number of times, then show an error with a retry option. Nothing incomplete or invalid is saved as a successful itinerary. |
| AF-04 | AI service or external API unavailable, timed out or over quota | Retry a bounded number of times with backoff, then fall back to cached data only where appropriate (showing its age) or report the limitation. The application keeps running and saved data is untouched. |
| AF-05 | Hotel or transport unavailable | Mark an option unavailable only when the provider confirms it. If it cannot be checked, label it unverified. |
| AF-06 | Recommended place cannot be found or verified | Replace it with a verified fallback recommendation that matches the user's interests. If none exists, keep it flagged as unverified on the map and in the itinerary. |
| AF-07 | Dates changed mid-plan | Invalidate date-dependent results, revalidate the itinerary, transport and accommodation, and recalculate costs and routes. |
| AF-08 | Edit causes a schedule conflict or does not fit the dates | Reject or flag the edit, explain the conflict and keep the last valid itinerary. |
| AF-09 | Budget exceeded or threshold reached after an edit | Recalculate, show the new overrun or alert and lower-cost alternatives. |
| AF-10 | Routing data unavailable | Show the stop without a route, state clearly that routing is unavailable, and mark any distance or time as estimated. |
| AF-11 | PDF export fails | Keep the itinerary intact, report the failure and allow a retry. |
| AF-12 | Unauthorized access to a trip, itinerary or the admin console | Deny access without revealing trip or administrative data. |
| AF-13 | No relevant hotel or transport results | Say that no suitable verified options were found. Offer estimates only when clearly labeled. |
| AF-14 | Delete a trip or itinerary | Ask for confirmation before deleting. Report database errors honestly. |

A provider timeout does not mean an option is unavailable. A timetable produced by the AI model does not prove that a train, flight or attraction runs at that time.

## 6. Budget and validation rules

### Cost aggregation

```text
estimated_total =
    included_transportation      # intercity and local
  + included_accommodation
  + included_food
  + included_activities
  + other_included_costs

planned_daily_budget = total_budget / number_of_days
```

Only categories the user selected are included. Each cost item records its amount (if known), currency, category, source or status, and whether it is included. Amounts in different currencies are not added without a reliable conversion source. A missing price is never treated as zero. All costs and travel times are shown as estimates (NFR-22).

### Budget status

```text
if total > budget:
    status = "over_budget"          # show the overrun and lower-cost alternatives
elif total >= budget * BUDGET_ALERT_THRESHOLD:
    status = "threshold_reached"    # alert the user (default threshold: 80%)
elif every included category has a known or estimated price:
    status = "within_budget"
else:
    status = "provisional"          # some prices are missing or unverified
    list the missing categories
```

A day whose estimated cost exceeds the planned daily budget raises a daily cost alert. The stored budget is never changed automatically. The user changes it explicitly through the trip form.

### Itinerary validation

An itinerary, generated or edited, is accepted only if:

- it matches the output schema;
- the number of days matches the trip duration and every activity falls inside the travel dates;
- recommended places are verified against real-world location data, or are clearly flagged as unverified;
- no activities overlap;
- activity durations are realistic, and the daily load suits the chosen travel style (relaxed or fast-paced);
- activities fall within opening hours and allow for travel time, where reliable data exists (missing hours are never treated as open);
- cost amounts, currencies and statuses are valid;
- source and freshness metadata is kept for source-backed facts.

Impossible schedules are rejected or flagged. After every accepted modification the backend runs, in order: schedule validation, route recalculation, cost recalculation and the budget check.

### Route optimization

For each day the backend groups activities by geographic proximity, then orders them to reduce total travel time and backtracking, starting from the day's anchor (for example the accommodation). It uses the route matrix from Google Routes API and a nearest-neighbor ordering improved with 2-opt. If routing data is unavailable it falls back to straight-line distance and labels the result Estimated. Leg results are cached per origin, destination and mode to meet the recalculation target of 5 seconds (NFR-04). Optimization is re-run after regeneration and after the user adds, removes or reorders activities.

## 7. Architecture and technology stack

The system is a modular monolith: a React single-page frontend talking to a FastAPI backend over a versioned REST API, with PostgreSQL for storage. The AI model is a proposal generator. External data and backend domain rules decide what can be presented as a practical itinerary.

The backend is split into separate modules for user management, itinerary generation, route processing and budget management (NFR-24). Each external provider sits behind an adapter, so none is tied to a specific vendor and new destinations, activities or transport sources can be added without a redesign (NFR-25, NFR-27). The AI model is called through a common LLM interface so the provider can be replaced with minimal changes (US-20).

### Frontend

| Technology | Purpose |
| --- | --- |
| JavaScript (ES6+) | Language. JavaScript is a project requirement. |
| React | UI components for the trip form, itinerary cards and dashboard. |
| Vite | Development server and production build. |
| React Router | Routing between landing, auth, My Trips, trip form, dashboard and admin pages. |
| Axios | HTTP client, centralized in `services/apiClient.js`. |
| React Hook Form | Form state and validation for the trip form. |
| CSS Modules | Styling without a large UI framework. Layouts adapt to desktop, tablet and mobile. |
| Google Maps JavaScript API | Interactive map with markers and routes, loaded with a separate, referrer-restricted browser key. |
| dnd-kit | Drag-and-drop reordering of activities. |

Places data is displayed on a Google map, as Google Maps Platform terms expect.

### Backend

| Technology | Purpose |
| --- | --- |
| Python 3.12+ | Language. |
| FastAPI | HTTP API with automatic OpenAPI documentation. |
| Pydantic | Request, response and AI-output schemas. |
| PostgreSQL | Users, trips, itineraries, costs, routes and ownership. |
| SQLAlchemy 2.x | ORM and database access, with the `psycopg` (v3) driver. |
| Alembic | Schema migrations. |
| HTTPX | Outbound calls to Google Places, Google Routes and Amadeus, with timeouts and bounded retries. |
| Google Gen AI SDK (`google-genai`) | Gemini client, wrapped behind the common LLM interface. |
| Argon2 | Password hashing. |
| JWT | Stateless access tokens for authenticated requests. |
| ReportLab | PDF generation. |
| Pydantic Settings and python-dotenv | Configuration from environment variables and a local `.env` file. |
| slowapi | Rate limiting on the backend's own endpoints (hardened in Sprint 5). |
| Pytest with the FastAPI test client | Unit and integration tests. |

### Database

PostgreSQL 15 or later is the only data store, accessed through SQLAlchemy 2.x with Alembic managing the schema.

- Models use the SQLAlchemy 2.x declarative style in `app/models/`. A session is created per request through a FastAPI dependency in `app/db/session.py`.
- Every schema change is an Alembic migration committed under `backend/alembic/versions/`. Tables are never created with `create_all` outside tests.
- Constraints are declared in the database as well as in Pydantic, for example `traveler_count > 0`, `budget_amount > 0` and `end_date >= start_date`. Money uses `NUMERIC`, never floating point.
- Foreign keys enforce ownership. Deleting a trip removes its itineraries and dependent rows. Queries for private data always filter by the authenticated user ID.
- Flexible AI-generated detail (for example activity descriptions and source metadata) can be stored as JSONB. Ownership, dates, budget, costs, statuses and ordering stay in ordinary columns so they can be queried reliably.
- All queries go through SQLAlchemy with bound parameters, which prevents SQL injection.
- The itinerary and its cost items are written in a single transaction. A failed or invalid generation writes nothing as a successful itinerary (NFR-13).

### External integrations

Credentials are supplied through environment variables listed in `.env.example`, and each integration is enabled in the sprint that needs it. Until an adapter is implemented and configured, its features report "not integrated" and never fill the gap with invented data.

| Provider | Credentials | Used for | Sprint |
| --- | --- | --- | --- |
| Google Gemini API | `GEMINI_API_KEY` | Generating and revising itineraries, and proposing alternatives for replacement. | 2 |
| Google Maps Platform: Places API | `GOOGLE_MAPS_API_KEY` | Verifying recommended places and coordinates, opening hours, and finding verified fallback places. | 2 |
| Google Maps Platform: Routes API | `GOOGLE_MAPS_API_KEY` | Distances, travel times, route geometry and local transit or driving options. | 3 |
| Google Maps Platform: Maps JavaScript API | `VITE_GOOGLE_MAPS_BROWSER_KEY` | Displaying the interactive map in the browser. This key is public by design. | 3 |
| Amadeus Self-Service APIs | `AMADEUS_CLIENT_ID`, `AMADEUS_CLIENT_SECRET`, `AMADEUS_BASE_URL` | Flight and hotel search for intercity transport and accommodation options. | 3 |
| Train, bus and cab providers | Provider-specific | Live schedules, fares and availability. No provider is selected yet. | 3 |

Notes:

- Gemini and Google Maps server keys, and the Amadeus secret, stay in the backend. The browser calls only FastAPI endpoints, apart from loading the map with the restricted browser key.
- Amadeus covers flights and hotels only. Local travel options (walking, driving, transit) come from Google Routes API where coverage exists. Cab cost uses a configurable distance-based estimate and is labeled Estimated. Intercity train and bus options are shown only from a reference entry or a selected provider and are otherwise reported as "no data" or "not integrated".
- An AI model does not know current travel inventory, so source data is retrieved first and passed to the model with its provenance and freshness. The model's output is validated and verified before it is shown.
- Retry and timeout behavior is configurable (`EXTERNAL_HTTP_TIMEOUT_SECONDS`, `EXTERNAL_MAX_RETRIES`). Requests respect each provider's documented rate limits, responses are parsed and validated before use, and quota errors trigger a bounded retry or fallback (US-23).

### AI integration

- `ai/base.py` defines the `LLMClient` interface. `ai/gemini_client.py` is the first implementation. Provider-specific configuration stays out of the generation logic (US-20).
- The model is asked for structured JSON that matches a Pydantic schema. The response is parsed and validated against the schema and domain rules before use (FR-19, NFR-19).
- User free text is length-limited, sanitized and passed to the model as data rather than as instructions. Account details such as email addresses are never sent to the model.
- Destination grounding and quality evaluation (US-19) are optional. If implemented, they use a defined source of destination information and report documented quality measures, which are not treated as proof that every recommendation is correct.

## 8. Data model

| Table | Contents |
| --- | --- |
| `users` | Accounts: email, password hash, role (`traveler` or `administrator`) and active flag. |
| `trips` | Owner, destination, departure city, start date, duration, traveler count, budget amount and currency, included cost categories, travel style, special requirements, status. |
| `trip_preferences` | Interests, transportation preferences and accommodation preferences for a trip. |
| `itineraries` | Generated itineraries of a trip: version, generation status (only complete, validated itineraries are stored as successful), estimated totals, budget status, timestamps. |
| `itinerary_days` | Days within an itinerary: date, day number, daily estimate. |
| `itinerary_items` | Activities within a day: place reference, position, start and end time, duration, estimated cost, verification and data status. |
| `places` | Verified place data: provider place ID, name, coordinates, opening hours, source and retrieval time. |
| `route_legs` | Distance, estimated travel time and mode between consecutive stops, with data status. |
| `route_cache` | Cached routing results keyed by origin, destination and mode. |
| `cost_items` | Amount, currency, category (accommodation, transportation, activities, food, other), source or status, and inclusion state. |
| `accommodation_options` | Hotel options attached to an itinerary, with price range, amenities, data status and external link. |
| `transport_options` | Transport options attached to an itinerary: mode, route, duration, estimated cost, data status and external link. |
| `itinerary_feedback` | User ratings and flags for generated itineraries or recommendations (US-16). |
| `admin_audit_log` | Administrative actions with actor, action, target and time (US-15). |
| `reference_data` | Administrator-managed destination, accommodation and transportation entries, with source and update time (US-17). |

`itinerary_feedback`, `admin_audit_log` and `reference_data` are created only when the administrator features are built. Migrations for all tables are managed with Alembic.

## 9. API

All endpoints are versioned under `/api/v1`. Authenticated endpoints require a valid access token, and trip and itinerary endpoints additionally check that the resource belongs to the caller. A resource owned by someone else is reported as not found.

| Method | Endpoint | Purpose | Access |
| --- | --- | --- | --- |
| GET | `/health` | Health check | Public |
| POST | `/auth/register` | Register | Public |
| POST | `/auth/login` | Log in | Public |
| GET | `/auth/me` | Current user | Authenticated |
| POST | `/trips` | Create a trip | Authenticated |
| GET | `/trips` | List the user's trips | Authenticated |
| GET | `/trips/{trip_id}` | Read a trip | Owner |
| PATCH | `/trips/{trip_id}` | Edit trip details and preferences | Owner |
| DELETE | `/trips/{trip_id}` | Delete a trip | Owner |
| POST | `/trips/{trip_id}/itineraries` | Generate (or regenerate) an itinerary | Owner |
| GET | `/trips/{trip_id}/itineraries` | List a trip's itineraries | Owner |
| GET | `/itineraries/{itinerary_id}` | Read an itinerary with days, activities, routes and costs | Owner |
| DELETE | `/itineraries/{itinerary_id}` | Delete an itinerary | Owner |
| GET | `/itineraries/{itinerary_id}/budget` | Estimated total, daily costs, category breakdown, status and alerts | Owner |
| GET | `/itineraries/{itinerary_id}/routes` | Distances, travel times and route geometry | Owner |
| POST | `/itineraries/{itinerary_id}/optimize` | Optimize activity order and recalculate routes | Owner |
| GET | `/itineraries/{itinerary_id}/transport` | Transport options and comparison | Owner |
| GET | `/itineraries/{itinerary_id}/accommodation` | Accommodation options | Owner |
| POST | `/itineraries/{itinerary_id}/items` | Add an activity manually | Owner |
| DELETE | `/itineraries/{itinerary_id}/items/{item_id}` | Remove an activity | Owner |
| PUT | `/itineraries/{itinerary_id}/days/{day_id}/order` | Reorder activities within a day | Owner |
| GET | `/itineraries/{itinerary_id}/items/{item_id}/alternatives` | Suggest alternatives for an activity | Owner |
| POST | `/itineraries/{itinerary_id}/items/{item_id}/replace` | Replace an activity with an alternative | Owner |
| POST | `/itineraries/{itinerary_id}/validate` | Run schedule, opening-hours and budget validation | Owner |
| GET | `/itineraries/{itinerary_id}/export/pdf` | Download the latest saved itinerary as PDF | Owner |
| POST | `/itineraries/{itinerary_id}/feedback` | Rate or flag an itinerary | Owner |
| | `/admin/users`, `/admin/feedback`, `/admin/reference-data` | Account management, feedback review and reference data | Administrator |

Every endpoint that modifies an itinerary (add, remove, reorder, replace, regenerate) runs validation, route recalculation and budget recalculation before responding, and returns the updated itinerary. Request and response bodies are defined as Pydantic schemas. Provider secrets and raw database objects are not exposed.

## 10. Authentication and privacy

- Users register with an email address and password and log in to receive a short-lived JWT access token, sent in the `Authorization` header.
- Passwords are hashed with Argon2 and never stored in plain text. Login errors do not reveal whether the email or the password was wrong.
- Ownership is checked in the backend on every trip and itinerary read, update, delete, export and feedback request. A trip ID sent by the client is never trusted on its own.
- Admin endpoints require the administrator role, checked in the backend. Administrative actions are written to an audit log.
- All user input is validated by Pydantic schemas and sanitized. Database access uses bound parameters.
- Traffic uses HTTPS in any deployment, and CORS allows only the configured frontend origin.
- Provider API keys stay on the server. Variables with the `VITE_` prefix are visible in the browser and must never hold secrets. The only such key is the Maps JavaScript key, which must be restricted by HTTP referrer and by API.
- Backend endpoints are rate limited, and outbound provider calls respect provider limits.
- Logs exclude passwords, tokens, API keys, authorization headers and unnecessary trip data. API failures are logged with enough detail to diagnose them, and user-facing errors never expose internals.
- `.env` files are never committed. A key that is committed by mistake is revoked and rotated, not just deleted.

## 11. Repository layout

Some paths are created when the sprint that needs them begins.

```text
ai-travel-planner/
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml                 # local PostgreSQL
├── docs/
│   ├── requirements/
│   ├── api/api-contract.md
│   └── decisions/architecture-decisions.md
├── frontend/
│   ├── package.json
│   ├── index.html
│   ├── vite.config.js
│   ├── .env.example
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── routes/                    # AppRoutes, ProtectedRoute
│       ├── pages/                     # Landing, Login, Signup, MyTrips, TripForm, ReviewTrip,
│       │                              # GenerationStatus, ItineraryDashboard, EditItinerary,
│       │                              # admin/
│       ├── components/                # layout, trip-form, itinerary, map, budget, common
│       ├── hooks/
│       ├── context/
│       ├── services/                  # apiClient, authService, tripService, itineraryService
│       ├── schemas/
│       ├── utils/
│       └── styles/
├── backend/
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── .env.example
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/
│   ├── scripts/
│   │   └── seed_reference_data.py
│   ├── app/
│   │   ├── main.py
│   │   ├── core/                      # config, security, logging, exceptions, rate limiting
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       └── endpoints/         # health, auth, trips, itineraries, export, admin
│   │   ├── schemas/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── services/                  # auth, trip, itinerary, verification, routing,
│   │   │                              # transport, budget, validation, export, admin
│   │   ├── ai/                        # base (LLMClient interface), gemini_client, prompts,
│   │   │                              # generation, alternatives, output_validator
│   │   ├── integrations/              # base, places, routes, amadeus, ground_transport,
│   │   │                              # provider_registry
│   │   ├── domain/                    # rules, schedule_validator, cost_calculator,
│   │   │                              # route_optimizer
│   │   └── db/                        # session, base
│   └── tests/
│       ├── conftest.py
│       ├── unit/
│       ├── integration/
│       └── fixtures/                  # recorded provider and AI responses
└── scripts/
    ├── dev-backend.sh
    └── dev-frontend.sh
```

| Directory | Responsibility |
| --- | --- |
| `api/` | HTTP routing and request handling. |
| `services/` | Application use cases, separated by concern: user management, itinerary generation, route processing and budget management. |
| `domain/` | Budget, schedule and route-optimization rules. |
| `integrations/` | Wrappers around external data providers. |
| `ai/` | LLM interface, provider client, prompts and output validation. |
| `models/`, `repositories/`, `db/` | SQLAlchemy models, data access and session handling. |

## 12. Testing

Run the backend tests with `pytest` from the `backend` directory. Tests use recorded or mocked responses for Gemini, Google Maps Platform and Amadeus, so they need no real keys and consume no quota. The sprint plan in section 13 lists the testing focus of each sprint.

### Unit tests

- Input validation: dates, traveler counts, budget values and email format.
- Password hashing and token handling.
- Budget aggregation, daily budget, threshold alerts, unknown prices and currencies.
- Overlapping-activity detection, duration and travel-time validation.
- Opening-hours validation, including missing hours.
- Distance and travel-time calculation and route optimization (the optimized order is not worse than the original).
- AI output schema validation, including missing fields and malformed JSON.
- Place verification and fallback selection.

### Integration tests

- Registration, login and invalid credentials.
- Trip create, edit, delete and persistence.
- A user cannot read, modify or delete another user's trip or itinerary.
- A non-admin cannot call admin endpoints.
- Itinerary generation for different destinations, durations, budgets, interests and travel styles.
- Invalid or incomplete AI output is retried or rejected and nothing is saved as successful.
- A provider outage or quota error never produces invented data, and saved itineraries remain available.
- Add, remove, reorder and replace trigger revalidation, route recalculation and budget updates.
- Regeneration after a preference change recalculates routes and costs.
- A PDF failure leaves the itinerary unchanged, and a generated PDF contains the itinerary and cost summary.

### End-to-end scenario

1. A user registers and logs in.
2. The user creates a trip with a valid destination, dates, travelers, budget, interests and travel style.
3. The system generates a valid itinerary or reports a controlled failure with a retry option.
4. The dashboard shows verified and unverified places, the map, optimized routes, travel times, transport comparison and costs with data-status labels.
5. The user customizes the itinerary and sees routes, schedule checks and budget alerts update.
6. The user saves the itinerary, edits the trip preferences and regenerates it.
7. The user exports a PDF and opens it in a standard reader.
8. The user deletes the itinerary after confirming.

## 13. Scope and sprint plan

The project is delivered in five sprints. Each sprint lists its goal, main points, testing and deliverable. The requirement IDs show the main requirements each sprint satisfies. Non-functional requirements apply to every sprint and are checked again in Sprint 5.

### Sprint 1: User authentication and trip management

Builds the foundation of the application, allowing users to securely access the system and manage their trips.

**Goal:** Implement user authentication and trip management, with all essential trip details stored correctly.

**Main points:**

- User registration and login.
- Create a trip by entering destination, travel dates or duration, and number of travelers.
- Set trip budget, interests and preferred travel style (fast-paced or relaxed).
- Save, view, edit and delete trips and trip details.
- Store passwords using secure hashing, and validate and sanitize all user inputs.
- Restrict access to private trip data to the owner.
- Set up the database and connect it to the frontend and backend.

**Implementation notes:** React and Vite shell, landing page and trip form; FastAPI skeleton; PostgreSQL models and the first Alembic migrations through SQLAlchemy; Argon2 and JWT authentication. The trip form also stores the transportation and accommodation preferences (US-04) so later sprints can use them.

**Requirements:** FR-01 to FR-09, FR-12; US-01 to US-04; NFR-05 to NFR-07, NFR-14, NFR-32, NFR-34.

**Testing:** Registration and login, input validation, trip creation, editing and deletion, data persistence, and access permissions to ensure users can access only their own trips.

**Deliverable:** A working application where users can register, log in, create trips and manage their saved trip details.

### Sprint 2: AI-powered itinerary generation

Uses AI to generate personalized, day-wise travel itineraries based on the user's trip details and preferences.

**Goal:** Generate structured, personalized itineraries that satisfy the user's travel preferences and provide useful activity recommendations.

**Main points:**

- Integrate the AI model for itinerary generation.
- Generate day-wise itineraries based on destination, dates, budget, interests, number of travelers and travel style.
- Recommend activities and attractions for each day.
- Generate an initial estimated trip cost.
- Validate the structure and completeness of AI-generated responses.
- Handle invalid or incomplete AI responses.
- Verify recommended places against real-world location data and provide verified fallback recommendations when a suggested place cannot be found.
- Allow users to update their preferences and regenerate an itinerary.
- Save, view and delete generated itineraries.
- Handle AI-service and external API failures gracefully, show clear error messages with a retry option, and never save incomplete or invalid itineraries as successful.

**Implementation notes:** `LLMClient` interface with the Gemini implementation and a structured output schema; Google Places verification; itinerary and cost tables; generation status page with retry; initial accommodation and transport cost estimates labeled Estimated.

**Requirements:** FR-10, FR-11, FR-13 to FR-20, FR-24; US-05, US-08, US-11 (save, view, delete), US-13 (places, durations, overlaps and budget checks), US-18 to US-20, US-23; NFR-03, NFR-10 to NFR-13, NFR-15, NFR-16, NFR-19, NFR-20.

**Testing:** Test itinerary generation for different destinations, durations, budgets, interests and travel styles. Check structured output, missing fields, invalid AI responses, fallback recommendations, and whether generated itineraries match the user's inputs.

**Deliverable:** A working AI itinerary generator that produces structured, personalized, day-wise travel plans.

### Sprint 3: Maps and route optimization

Connects itinerary activities with real-world locations and helps users understand how to travel between them.

**Goal:** Display itinerary activities on a map and generate practical routes with transportation recommendations.

**Main points:**

- Integrate map functionality to visualize itinerary locations.
- Calculate distances and estimated travel times between activities.
- Optimize the order of activities to reduce unnecessary travel.
- Recalculate routes after itinerary regeneration.
- Recommend suitable transportation options.
- Compare transportation options based on relevant factors such as estimated cost and travel time.
- Display unavailable or unverified locations clearly on the map and in the itinerary.

**Implementation notes:** Google Maps JavaScript API on the frontend; Google Routes API for distances, times and geometry; the route optimizer from section 6; Amadeus flight and hotel adapters and the transport and accommodation views (US-06, US-21, US-22), with each result labeled by data status.

**Requirements:** FR-21 to FR-28; US-06, US-10, US-14, US-21, US-22; NFR-17, NFR-21, NFR-22.

**Testing:** Check that places appear at the correct map locations, verify distance and travel-time calculations, test route optimization, validate transportation comparisons, and confirm that unavailable locations are handled properly.

**Deliverable:** An interactive itinerary map with verified places, optimized routes, travel-time estimates and transportation recommendations.

### Sprint 4: Budget management and itinerary customization

Gives users control over their itinerary while helping them stay within their planned budget and travel schedule.

**Goal:** Enable users to customize their travel plans while validating budget limits, activity timings and scheduling constraints.

**Main points:**

- Display estimated trip costs and activity-category budget breakdowns.
- Track the planned daily budget and provide cost alerts.
- Allow users to add, remove and reorder activities manually.
- Allow users to replace an activity with an alternative.
- Automatically recalculate routes after itinerary modifications.
- Validate whether the itinerary stays within the budget.
- Check activity durations and opening hours.
- Detect overlapping activities and scheduling conflicts.
- Validate that activities fit within the available travel dates and schedule.
- Implement PDF export for generated and customized itineraries.

**Implementation notes:** Budget service and dashboard panels; customization endpoints and the customize page with dnd-kit; schedule validator; the modification pipeline (validate, recalculate routes, recalculate costs, check budget) shared by every edit; ReportLab export.

**Requirements:** FR-26, FR-29 to FR-40; US-07, US-09, US-12, US-13; NFR-04, NFR-30, NFR-31, NFR-33.

**Testing:** Test manual itinerary modifications, route recalculation after changes, daily budget alerts, category-wise cost breakdowns, budget-limit violations, opening-hours checks, activity durations and overlapping activities.

**Deliverable:** A customizable itinerary with budget tracking, cost alerts, schedule validation, automatic route updates and PDF export.

### Sprint 5: Finalization and export

Makes the complete application stable, reliable and ready for demonstration and evaluation.

**Goal:** Deliver a fully integrated, tested and deployable AI Travel Planner with PDF export and complete end-to-end functionality.

**Main points:**

- Integrate authentication, trip management, AI generation, maps, route optimization, budget management and customization.
- Fix bugs and improve the user interface.
- Review and harden API error handling, rate limits and retries across all integrations.
- Audit that secrets and API keys are not exposed in client code, logs or the repository.
- Perform final performance and security checks.
- Complete the project report, presentation and demo preparation.
- Deploy the frontend, backend and database if deployment is required for evaluation.

**Implementation notes:** Rate limiting with slowapi; timeout and retry review for Gemini, Google Maps Platform and Amadeus; secret audit of the repository, build output and logs; HTTPS in deployment; browser and responsive checks (NFR-28, NFR-29); performance checks against NFR-01 to NFR-04.

**Requirements:** All of the above, with emphasis on FR-39, US-18, US-23 and NFR-01 to NFR-04, NFR-08, NFR-09, NFR-28, NFR-29.

**Testing:** Perform full regression testing and end-to-end journeys from registration and trip creation through itinerary generation, map visualization, route optimization, budget validation, manual customization, saving and PDF export. Check API failures, invalid AI responses, authentication, permissions and the complete user workflow.

**Deliverable:** A fully integrated and tested AI Travel Planner with PDF export, complete core functionality, project documentation and a presentation-ready demonstration.

### Administrator features

The administrator stories (US-15 to US-17) are not listed in any sprint deliverable. They are built after the sprint items above if time allows, in this order: account management (US-15), flagged itineraries and feedback (US-16), reference data (US-17). Until then the `administrator` role exists in the data model and admin endpoints return access denied to non-administrators.
