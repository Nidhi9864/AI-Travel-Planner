[FINAL_README_updated.md](https://github.com/user-attachments/files/33434406/FINAL_README_updated.md)
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
11. The user customizes the itinerary. After every change the backend revalidates the schedule, recalculates routes and updates costs (FR-20).
12. If the estimate exceeds the budget or the alert threshold, the user sees the overrun and lower-cost alternatives.
13. The user can edit the trip preferences and regenerate the itinerary. Routes and costs are recalculated for the new itinerary.
14. The user saves, reopens or deletes itineraries from My Trips, and exports the latest saved itinerary as a PDF.
15. Separately, administrators manage accounts, review feedback and flagged itineraries, and maintain reference data.

## 4. Requirements

The requirements below are final. Section 13 maps them onto the five sprints.

### 4.1 Functional requirements

> Merged requirements are noted in parentheses to show which original items were consolidated.

#### Authentication

| ID | Requirement | Sprint |
| --- | --- | --- |
| FR-01 | The system shall allow users to register for an account with a unique email address and a validated password. | 1 |
| FR-02 | The system shall allow registered users to log in with their email and password; error messages shall not reveal which credential was incorrect. | 1 |

#### Trip management

| ID | Requirement | Sprint |
| --- | --- | --- |
| FR-03 | The system shall allow users to create a trip by providing: destination, optional departure city, travel start date, duration in days, number of travelers (≥ 1), total budget with currency and selected cost categories, interests (at least one), travel style (relaxed or fast-paced), transport preferences, accommodation preferences, and optional special requirements. *(consolidates former FR-03 to FR-09)* | 1 |
| FR-04 | The system shall allow users to view, edit and delete their saved trips, and shall restrict access so that a user can only manage their own trips. *(consolidates former FR-12 and trip-level parts of FR-11/FR-13)* | 1 |

#### Itinerary generation

| ID | Requirement | Sprint |
| --- | --- | --- |
| FR-05 | The system shall generate a complete, day-wise itinerary using an AI model based on the user's trip details and preferences. *(consolidates former FR-14 and FR-15)* | 2 |
| FR-06 | The system shall recommend activities and attractions for each day that are relevant to the destination and match at least one of the user's stated interests. | 2 |
| FR-07 | The system shall validate AI-generated output against both a predefined JSON schema and the system's domain rules before accepting it; if validation fails the system shall retry with the failure reasons as feedback and reject the output if it cannot be corrected within the retry limit. *(consolidates former FR-18 and FR-19)* | 2 |
| FR-08 | The system shall verify every recommended place against real-world location data; if a place cannot be verified the system shall substitute a verified fallback that matches the user's interests; places that cannot be replaced shall be flagged as unverified. *(consolidates former FR-24 and FR-20)* | 2 |

#### Itinerary persistence

| ID | Requirement | Sprint |
| --- | --- | --- |
| FR-09 | The system shall allow users to save, view and delete generated itineraries; only itineraries that passed full validation shall be saved as successful. *(consolidates former FR-10, FR-11 and FR-13)* | 2 |
| FR-10 | The system shall allow users to edit their trip preferences and regenerate a new itinerary version; previously saved itineraries shall remain available. | 2 |

#### Map and routes

| ID | Requirement | Sprint |
| --- | --- | --- |
| FR-11 | The system shall display itinerary activities as markers on an interactive map, draw the optimized daily route between them, and clearly indicate any location that is unverified or unavailable. | 3 |
| FR-12 | The system shall calculate the distance and estimated travel time between consecutive itinerary stops for each supported transport mode, and cache results to avoid redundant calls. *(consolidates former FR-22 and FR-23)* | 3 |
| FR-13 | The system shall optimize the order of daily activities to minimize total travel time and backtracking, and shall recalculate the optimized route and travel-time estimates after any activity is added, removed or reordered. *(consolidates former FR-25 and FR-26)* | 3 |

#### Transport and accommodation

| ID | Requirement | Sprint |
| --- | --- | --- |
| FR-14 | The system shall present available transportation options (flights, trains, buses and estimated cab fares) and compare them by estimated cost and travel time; each option shall be labeled with its data status. *(consolidates former FR-27 and FR-28)* | 3 |
| FR-15 | The system shall display available accommodation options for the destination with estimated costs and booking links where available. | 3 |

#### Budget

| ID | Requirement | Sprint |
| --- | --- | --- |
| FR-16 | The system shall calculate and display the estimated total trip cost, a planned daily budget, and a breakdown by selected cost categories (accommodation, transport, activities, food). *(consolidates former FR-17, FR-29 and FR-31)* | 2, 4 |
| FR-17 | The system shall alert the user when estimated spending reaches 80 % of the budget and when it exceeds the budget in full; a missing price shall never be counted as zero and shall instead mark the total as provisional. *(consolidates former FR-30 and FR-38)* | 4 |

#### Itinerary customization

| ID | Requirement | Sprint |
| --- | --- | --- |
| FR-18 | The system shall allow users to manually add, remove and reorder activities within an itinerary, and to replace any activity with an AI-suggested or manually selected alternative. *(consolidates former FR-32, FR-33 and FR-34)* | 4 |
| FR-19 | The system shall validate the itinerary schedule after every modification: activity durations must be positive; no two activities may overlap; each activity must be reachable from the previous one given the travel time; activities must fall within available opening hours where data exists (missing hours are never assumed to be open); all activities must fit within the trip's travel dates. *(consolidates former FR-35, FR-36 and FR-37)* | 4 |
| FR-20 | The system shall apply schedule revalidation, route recalculation and budget recalculation as a single atomic operation after every itinerary modification, and shall preserve the last valid itinerary state if the modification produces a conflict. *(refines former FR-40)* | 4 |

#### Export

| ID | Requirement | Sprint |
| --- | --- | --- |
| FR-21 | The system shall allow users to export their itinerary as a PDF file containing the day-wise schedule and cost summary; a PDF generation failure shall leave the saved itinerary unchanged. | 4, 5 |

### 4.2 Non-functional requirements

> Merged requirements are noted in parentheses.

#### Performance

| ID | Requirement |
| --- | --- |
| NFR-01 | Standard application pages shall load within 3 seconds under normal operating conditions. |
| NFR-02 | Saved itinerary reads shall return a response within 2 seconds under normal operating conditions. |
| NFR-03 | AI itinerary generation shall complete within 30 seconds under normal conditions, excluding unrecoverable third-party delays. |
| NFR-04 | Route recalculation shall complete within 5 seconds after any user modification for a typical trip, aided by route caching. |

#### Security

| ID | Requirement |
| --- | --- |
| NFR-05 | Passwords shall be hashed with Argon2 and never stored, logged or transmitted in plain text. |
| NFR-06 | Access to trip and itinerary data shall be restricted to the authenticated owner; a request for another user's resource shall return not-found rather than forbidden, to avoid leaking the existence of private data. *(consolidates former NFR-06 and NFR-34)* |
| NFR-07 | All user inputs shall be validated by schema (Pydantic on the backend, Zod on the frontend) and all database queries shall use bound parameters; free-text inputs shall be length-limited and sanitized before use in AI prompts. *(consolidates former NFR-07 and NFR-32)* |
| NFR-08 | All data transmission shall use HTTPS; the CORS policy shall restrict cross-origin requests to the configured frontend origin only. |
| NFR-09 | API keys and secrets shall be stored exclusively in server-side environment variables; the only value permitted in client-side code is the Google Maps browser key, restricted by HTTP referrer and API type. |

#### Resilience

| ID | Requirement |
| --- | --- |
| NFR-10 | When an AI service or external API fails, the system shall retry a bounded number of times with exponential backoff, fall back to cached or estimated data where appropriate, and keep the application and all saved data intact throughout. *(consolidates former NFR-10, NFR-12 and NFR-13)* |
| NFR-11 | When generation or an external operation fails, the system shall display a clear, non-technical error message with a retry option; it shall never save an incomplete or invalid result as a successful itinerary. *(consolidates former NFR-11 and NFR-13)* |

#### Usability

| ID | Requirement |
| --- | --- |
| NFR-12 | The interface shall provide a clear and consistent layout for all pages, display itinerary activities in a readable day-wise format, and present budget totals, distances and travel times in human-readable units. *(consolidates former NFR-14, NFR-15 and NFR-17)* |
| NFR-13 | The system shall provide immediate, contextual feedback for every significant user action (generation, save, edit, export, failure) and shall allow users to complete the full trip-planning workflow without requiring knowledge of AI systems. *(consolidates former NFR-16 and NFR-18)* |

#### Data quality

| ID | Requirement |
| --- | --- |
| NFR-14 | Every cost estimate, travel time and place availability status shall be labeled with its data provenance (Verified, Cached, Estimated, Unverified or Unavailable); estimates shall never be presented as guaranteed values, and missing data shall never be assumed to be zero or open. *(consolidates former NFR-21, NFR-22 and NFR-23)* |

#### Maintainability and extensibility

| ID | Requirement |
| --- | --- |
| NFR-15 | The backend shall use a modular, layered architecture (API, services, domain, repositories, integrations) that separates user management, itinerary generation, route processing and budget management; each external provider shall be accessed through an adapter interface so providers, destinations and activity types can be added or replaced without redesigning unrelated components. *(consolidates former NFR-24, NFR-25 and NFR-27)* |
| NFR-16 | The codebase shall maintain clear, consistent naming conventions and inline documentation; APIs shall be described in a versioned contract document. *(refines former NFR-26)* |

#### Data integrity

| ID | Requirement |
| --- | --- |
| NFR-17 | The itinerary and all its dependent records (days, items, cost items, route legs) shall be written and updated in a single database transaction; every modification shall trigger schedule revalidation, route recalculation and budget update before the response is returned, and the last valid itinerary state shall always be preserved on rejection. *(consolidates former NFR-31 and NFR-33)* |

#### Compatibility

| ID | Requirement |
| --- | --- |
| NFR-18 | The application shall function on modern versions of Chrome, Firefox, Edge and Safari; the user interface shall adapt to desktop, tablet and mobile screen sizes; exported PDFs shall open in standard PDF readers. *(consolidates former NFR-28, NFR-29 and NFR-30)* |

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
| DR-01 | Respect opening hours | FR-19, NFR-14, US-13 | Check opening hours from the source where reliable. Mark unknown hours explicitly and never treat them as confirmed. |
| DR-02 | Recommend activities relevant to the selected interests | FR-06 | Check each activity against the selected interests. |
| DR-03 | Account for the user's budget | FR-16, FR-17 | Calculate the estimated cost and run the budget decision. |
| DR-04 | Avoid overlapping activities | FR-19 | Compare activity start and end intervals and reject conflicts. |
| DR-05 | Respect trip dates and duration | FR-05, FR-19, NFR-07 | Keep the schedule inside the user's travel dates and the itinerary length equal to the trip duration. |
| DR-06 | Account for travel time between locations | FR-12, FR-19 | Use route and time estimates and reject impossible transitions. |
| DR-07 | Aggregate costs by the categories the user selected | FR-16, US-07 | Include only selected categories in the total. |
| DR-08 | Unverified data is not shown as confirmed | FR-08, NFR-14, US-13 | Places, availability and schedules need a Verified label to be shown as confirmed. |
| DR-09 | Revalidate after a date change | FR-04, FR-10, US-08 | Date-dependent schedule and cost data is rechecked before the itinerary is shown as current. |

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

Only categories the user selected are included. Each cost item records its amount (if known), currency, category, source or status, and whether it is included. Amounts in different currencies are not added without a reliable conversion source. A missing price is never treated as zero. All costs and travel times are shown as estimates (NFR-14).

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

The backend is split into separate modules for user management, itinerary generation, route processing and budget management. Each external provider sits behind an adapter, so none is tied to a specific vendor and new destinations, activities or transport sources can be added without a redesign (NFR-15). The AI model is called through a common LLM interface so the provider can be replaced with minimal changes (US-20).

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
├── .env.example                               # Root environment variables template
├── .gitignore                                 # Git ignore patterns
├── docker-compose.yml                         # PostgreSQL 15 local database service definition
├── PROJECT_FILES_README.md                    # File-by-file functionality reference manual
├── README.md                                  # Primary project overview and specification
├── docs/                                      # Engineering and architecture documentation
│   ├── api/
│   │   └── api-contract.md                    # Formal OpenAPI/REST endpoint contract definitions
│   ├── decisions/
│   │   └── architecture-decisions.md          # Architecture Decision Records (ADRs)
│   └── requirements/
│       └── requirements.md                    # Supplementary requirements and validation matrices
├── scripts/                                   # Root developer convenience execution scripts
│   ├── dev-backend.sh                         # Script to launch FastAPI with Uvicorn hot-reload
│   └── dev-frontend.sh                        # Script to launch Vite development server
├── frontend/                                  # React 18 + Vite SPA Single-Page Application
│   ├── .env.example                           # Frontend environment configuration template
│   ├── index.html                             # HTML entry point and application container
│   ├── package.json                           # NPM dependencies and build scripts
│   ├── vite.config.js                         # Vite build configuration and proxy setup
│   └── src/
│       ├── App.jsx                            # Root component configuring providers & routes
│       ├── main.jsx                           # React DOM rendering entrypoint
│       ├── components/                        # Reusable modular UI components
│       │   ├── budget/                        # Budget tracking panels, alerts, breakdowns
│       │   ├── common/                        # Status badges, toasts, modal dialogs, buttons
│       │   ├── itinerary/                     # Day-by-day activity cards, timeline renderers
│       │   ├── layout/                        # Navigation header, footer, app container shells
│       │   ├── map/                           # Google Maps JavaScript interactive map view
│       │   └── trip-form/                     # Multi-step wizard inputs and preference selectors
│       ├── context/
│       │   └── AuthContext.jsx                # Global authentication state & session provider
│       ├── hooks/                             # Custom React hooks (useAuth, useItinerary, etc.)
│       ├── pages/                             # Route-level page views
│       │   ├── EditItinerary.jsx              # Drag-and-drop customization workspace
│       │   ├── GenerationStatus.jsx           # AI generation polling and retry interface
│       │   ├── ItineraryDashboard.jsx         # Primary trip dashboard (Map + Schedule + Budget)
│       │   ├── Landing.jsx                    # Marketing landing page & sign-in links
│       │   ├── Login.jsx                      # User login form with credentials validation
│       │   ├── MyTrips.jsx                    # Saved trip collection & version list
│       │   ├── ReviewTrip.jsx                 # Pre-generation summary and confirmation
│       │   ├── Signup.jsx                     # Account registration form
│       │   ├── TripForm.jsx                   # Multi-step trip preference creator
│       │   └── admin/
│       │       └── AdminConsole.jsx           # Administrative management console
│       ├── routes/                            # Client-side route declarations
│       │   ├── AppRoutes.jsx                  # Main route mapping table
│       │   └── ProtectedRoute.jsx             # Authentication guard wrapper
│       ├── schemas/                           # Zod frontend form validation schemas
│       ├── services/                          # API client service layer
│       │   ├── apiClient.js                   # Axios client instance with auth interceptors
│       │   ├── authService.js                 # Authentication API calls (login, register, me)
│       │   ├── itineraryService.js            # Itinerary generation, read, mutate, export APIs
│       │   └── tripService.js                 # Trip CRUD and preference API operations
│       ├── styles/
│       │   └── global.css                     # Global design tokens and reset styles
│       └── utils/                             # Date, currency, and unit formatters
└── backend/                                   # FastAPI Python Backend Application
    ├── .env.example                           # Backend secrets and environment variable template
    ├── alembic.ini                            # Alembic database migration tool configuration
    ├── pyproject.toml                         # Poetry/Pip dependencies and project metadata
    ├── alembic/                               # Database migration management
    │   ├── env.py                             # Alembic runtime environment and model metadata
    │   └── versions/                          # Linear SQL migration revision scripts
    ├── scripts/                               # Data seeding and operational scripts
    │   └── seed_reference_data.py             # Pre-populates sample destinations and categories
    ├── tests/                                 # Automated test suite
    │   ├── conftest.py                        # Pytest fixtures, test DB, and client setup
    │   ├── fixtures/                          # Recorded external provider mock responses
    │   │   ├── amadeus_responses.json         # Mock flight and hotel responses
    │   │   ├── gemini_responses.json          # Mock valid and malformed Gemini AI responses
    │   │   ├── places_responses.json          # Mock Google Places search results
    │   │   └── routes_responses.json          # Mock Google Routes matrices and distances
    │   ├── integration/                       # Multi-component integration test suite
    │   │   ├── test_auth.py                   # User registration, login, token lifecycle
    │   │   ├── test_customization.py          # Atomic add/remove/reorder/replace pipeline
    │   │   ├── test_export.py                 # PDF generation and error isolation tests
    │   │   ├── test_itineraries.py            # AI generation, persistence, ownership
    │   │   └── test_trips.py                  # Trip CRUD, validation, unauthorized access
    │   └── unit/                              # Pure function and business domain tests
    │       ├── test_cost_calculator.py        # Budget aggregation, daily limits, threshold alerts
    │       ├── test_output_validator.py       # Pydantic schema validation & hallucination checks
    │       ├── test_route_optimizer.py        # 2-opt heuristic traversal and distance metrics
    │       ├── test_schedule_validator.py     # Overlap detection, duration, opening-hours logic
    │       ├── test_security.py               # Argon2 password hashing and JWT encoding
    │       ├── test_validation.py             # Input boundary conditions and sanitization
    │       └── test_verification.py           # Place verification and interest fallback selection
    └── app/                                   # Core application package
        ├── main.py                            # FastAPI entry point, CORS, lifespan, middleware
        ├── ai/                                # AI Subsystem & LLM Integration
        │   ├── alternatives.py                # Activity replacement candidate generator
        │   ├── base.py                        # Abstract LLMClient interface and exception types
        │   ├── gemini_client.py               # Google GenAI Gemini implementation with retries
        │   ├── generation.py                  # Multi-step generation workflow orchestrator
        │   ├── output_validator.py            # Structured JSON parsing and domain constraint check
        │   └── prompts.py                     # System prompts, grounded context builders
        ├── api/                               # HTTP Presentation Layer
        │   ├── deps.py                        # Dependency injection (get_db, get_current_user)
        │   └── v1/                            # API Version 1
        │       ├── router.py                  # Main v1 router aggregating all endpoints
        │       └── endpoints/                 # REST Resource Endpoints
        │           ├── admin.py               # Platform administration and system metrics
        │           ├── auth.py                # Authentication (register, login, session)
        │           ├── export.py              # Itinerary PDF export endpoint
        │           ├── health.py              # Liveness and readiness health checks
        │           ├── itineraries.py         # Generation, retrieval, customization endpoints
        │           └── trips.py               # Trip resource CRUD endpoints
        ├── core/                              # Cross-Cutting Infrastructure
        │   ├── config.py                      # Pydantic Settings reading environment variables
        │   ├── exceptions.py                  # Custom domain and HTTP exception handlers
        │   ├── logging.py                     # Structured JSON logging with credential redaction
        │   ├── rate_limit.py                  # Slowapi request throttling and rate limiting
        │   └── security.py                    # Argon2 hashing, JWT creation and verification
        ├── db/                                # Persistence & Session Management
        │   ├── base.py                        # SQLAlchemy declarative base class
        │   └── session.py                     # Engine instantiation, connection pool, sessionmaker
        ├── domain/                            # Pure Business Logic & Domain Engine
        │   ├── cost_calculator.py             # Spending aggregation, daily splits, threshold checks
        │   ├── route_optimizer.py             # 2-opt TSP heuristic route optimizer
        │   ├── rules.py                       # System domain rules DR-01 through DR-09
        │   └── schedule_validator.py          # Temporal overlap, travel time & opening hour validator
        ├── integrations/                      # External Provider Adapters
        │   ├── amadeus.py                     # Amadeus Self-Service API (flights, hotels)
        │   ├── base.py                        # Base provider interface with bounded retries
        │   ├── ground_transport.py            # Rail and bus transit fare and timetable adapter
        │   ├── places.py                      # Google Places API (POI search, coordinates, hours)
        │   ├── provider_registry.py           # Dynamic runtime registry for external adapters
        │   └── routes.py                      # Google Routes API (distance, time, polylines)
        ├── models/                            # SQLAlchemy ORM Database Entities
        │   ├── itinerary.py                   # Itinerary, ItineraryDay, ItineraryItem, CostItem
        │   ├── trip.py                        # Trip and TripPreferences models with CHECK constraints
        │   └── user.py                        # User account model (email, hash, role, timestamps)
        ├── repositories/                      # Data Access Layer
        │   ├── itinerary_repository.py        # Itinerary persistence and eager-loading queries
        │   ├── trip_repository.py             # Trip CRUD queries filtered by authenticated user
        │   └── user_repository.py             # User retrieval and registration queries
        ├── schemas/                           # Pydantic Data Contracts & Validation Schemas
        │   ├── auth.py                        # Login, Registration, Token schemas
        │   ├── itinerary.py                   # Itinerary structure, items, modifications, export
        │   └── trip.py                        # Trip creation, update, and preference schemas
        └── services/                          # Application Service Layer (Use Cases)
            ├── admin.py                       # Admin auditing and feedback moderation services
            ├── auth.py                        # Authentication, registration & credential verification
            ├── budget.py                      # Budget status calculation and alerts
            ├── export.py                      # ReportLab PDF document compilation service
            ├── itinerary_service.py           # End-to-end itinerary generation orchestration
            ├── routing.py                     # Transit routing matrix and caching operations
            ├── transport.py                   # Multi-modal transport comparison service
            ├── trip.py                        # Trip management business logic
            ├── validation.py                  # Itinerary schedule and constraint validation
            └── verification.py                # Place verification and fallback selection service
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

This section governs the planning and sprint distribution for the **entire AI Travel Planner project**. It integrates all software engineering tracks (**Frontend & UI/UX**, **Backend & Data Persistence**, **DevOps, Infrastructure & Deployment**, and **Quality Assurance & Verification**) across five sequential sprints.

### 13.1 Engineering tracks

The project is executed across four engineering tracks:

| Engineering track | Primary focus | Key technologies and modules |
| :--- | :--- | :--- |
| **Backend & Data Persistence (Sprints 1–4)** | Core framework, data models, session pooling, Alembic migrations, AI pipeline orchestration, external provider adapters, geo-spatial optimization, financial calculations and PDF generation. | FastAPI, PostgreSQL 15, SQLAlchemy 2.0, Alembic, Gemini LLM (`google-genai`), Google Places/Routes, ReportLab, pytest. |
| **DevOps, Infrastructure & Deployment** | Local containerization, multi-stage production Docker images, cloud hosting provisioning, automated GitHub Actions CI/CD pipelines, production database setup, SSL/TLS reverse proxy, secret leak auditing and live smoke testing. Production deployment is delivered in Sprint 5. | Docker, Docker Compose, Nginx, GitHub Actions, Linux, Cloud Run / ECS / Render, Let's Encrypt SSL, Slowapi / Redis. |
| **Frontend & UI/UX Engineering** | Single-page application, responsive layout grid, design tokens, interactive trip forms, multi-day itinerary timelines, Google Maps visualization, drag-and-drop customization, financial dashboard and PDF streaming. | React 18, Vite, Tailwind CSS, `@react-google-maps/api`, `@dnd-kit/core`, Axios, Lucide React, Context API. |
| **Quality Assurance & Verification** | Test automation, unit and integration suites, offline provider mock datasets, end-to-end user journeys, performance SLA benchmarking, accessibility auditing (WCAG AA) and security vulnerability scanning. | Pytest, Vitest / React Testing Library, mock JSON fixtures, Postman, TruffleHog / Git-Secrets, Lighthouse. |

---

### 13.2 Sprint-by-sprint distribution

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                      PHASE 1: FEATURE ENGINEERING (SPRINTS 1 TO 4)                     │
├────────────────────────────┬─────────────────────────────┬─────────────────────────────┤
│   FRONTEND & UI/UX TRACK   │   BACKEND & DATABASE TRACK  │   DEVOPS & QA TRACK         │
│   • React 18 + Vite SPA    │   • AI pipeline & core      │   • Dev Docker Containers   │
│   • Tailwind CSS Design    │   • Auth, DB & cost engine  │   • Offline Test Fixtures   │
│   • Maps JS & Route Canvas │   • Trip domain & geo-opt   │   • CI Test Automation      │
│   • DnD-Kit Customization  │                             │   • SLA Benchmarks (<5s)    │
└────────────────────────────┴──────────────┬──────────────┴─────────────────────────────┘
                                            │ Feature Freeze & Release Handoff
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│             PHASE 2: PRODUCTION DEPLOYMENT & RELEASE OPERATIONS (SPRINT 5)             │
├────────────────────────────────────────────────────────────────────────────────────────┤
│   • Production Multi-Stage Docker Containerization (`Dockerfile.prod`)                 │
│   • Cloud Infrastructure & Managed PostgreSQL 15 Database Provisioning                 │
│   • Automated GitHub Actions CI/CD Deployment Pipeline (`.github/workflows/deploy.yml`)│
│   • Production Secret Store Configuration & Automated Secret Leak Audit                │
│   • Automated Production Database Migration Hook (`alembic upgrade head`)              │
│   • Nginx Reverse Proxy with SSL/TLS Termination (HTTPS) & Production CORS             │
│   • Production Rate Limiting (Slowapi/Redis), Health Probes & Log Monitoring           │
│   • Automated Post-Deployment Live Smoke Testing & Disaster Recovery Runbook           │
│                                                                                        │
│   [All tracks: post-deployment verification & live feature sign-off]                   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### Sprint 1: Project foundation, user authentication and trip management

*Builds the core foundation across frontend and backend, enabling travelers to register, authenticate securely, and manage trips with database-enforced constraints.*

- **Target requirements:** FR-01, FR-02, FR-03, FR-04; US-01, US-02, US-03, US-04; NFR-05, NFR-06, NFR-07, NFR-08, NFR-09, NFR-12.

#### 1. Frontend & UI/UX track
- **Application shell and layout:** Initialize React 18 + Vite project shell, establish Tailwind CSS typography and design tokens, and build responsive `Navbar.jsx` with dynamic authentication state and `Footer.jsx`.
- **Authentication pages:** Implement `Login.jsx` and `Signup.jsx` pages with client-side field validation (email syntax, password complexity, confirm-password matching) and user-friendly error banners.
- **Client auth state:** Build `AuthContext.jsx` and `useAuth.js` managing JWT storage in secure cookies/memory, token expiration timers, and protected client routes (`ProtectedRoute.jsx`).
- **Trip creation wizard:** Implement `TripForm.jsx` multi-step form:
  - Destination input with real-time text autocomplete.
  - Date range selector enforcing `end_date >= start_date`.
  - Traveler counter enforcing positive integers (`travelers > 0`).
  - Budget slider with currency selector enforcing positive values.
  - Interest selector chips (cultural, culinary, adventure, nature, relaxation).
  - Travel style toggle (`fast-paced` vs `relaxed`).
- **Trip management dashboard:** Build `MyTrips.jsx` displaying trip cards, edit modal, delete confirmation modal, and empty state illustrations.
- **API client:** Author `services/api.js` and `services/auth.js` with Axios interceptors attaching JWT Bearer headers and handling automatic 401 unauthenticated redirects.

#### 2. Backend & database track
- **Core application architecture and health:**
  - Implement `app/main.py` with FastAPI initialization, lifespan management, OpenAPI metadata, and CORS middleware configured for development origins.
  - Build `app/core/config.py` using `pydantic-settings` to load and validate backend environment variables (`DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`).
  - Create `app/core/exceptions.py` defining domain exceptions (`EntityNotFoundException`, `UnauthorizedException`, `ValidationException`) and global HTTP exception handlers producing unified RFC-7807 error envelopes.
  - Implement `app/core/logging.py` featuring structured JSON formatting and regex redaction for passwords, API keys, and JWT bearer tokens (NFR-09).
  - Implement `app/api/v1/endpoints/health.py` (`GET /health` liveness and readiness probes).
- **Security, authentication and DB session layer:**
  - Implement `app/models/user.py` with SQLAlchemy 2.0 mapped columns: `id`, `email` (unique index), `hashed_password`, `role`, `is_active`, and timestamps.
  - Implement `app/core/security.py` featuring password hashing using Argon2id (`argon2-cffi`) and JWT access token creation/decoding (`python-jose`).
  - Implement `app/db/session.py` and `app/db/base.py` configuring SQLAlchemy connection pooling (`pool_size=10`, `max_overflow=20`, `pool_pre_ping=True`).
  - Create `app/schemas/auth.py` and `app/services/auth.py` with registration and credential verification logic.
  - Implement `app/api/v1/endpoints/auth.py` (`POST /register`, `POST /login`, `GET /me`) and `app/api/deps.py` with the reusable `get_current_user` dependency.
- **Trip domain, migrations and test harness:**
  - Implement `app/models/trip.py` with `Trip` and `TripPreferences` tables, foreign keys to `users.id`, and database-level `CheckConstraint` enforcing `traveler_count > 0`, `budget_amount > 0`, and `end_date >= start_date`.
  - Initialize `alembic.ini` and `alembic/env.py`; generate the baseline migration script creating `users`, `trips`, and `trip_preferences` tables.
  - Build `app/schemas/trip.py` (`TripCreate`, `TripUpdate`, `TripResponse`) enforcing strict field validations.
  - Implement `app/repositories/trip_repository.py` and `app/services/trip.py` ensuring all queries automatically scope by `user_id` to strictly isolate private trips.
  - Implement `app/api/v1/endpoints/trips.py` (`POST /trips`, `GET /trips`, `GET /trips/{id}`, `PATCH /trips/{id}`, `DELETE /trips/{id}`).

#### 3. DevOps, infrastructure & deployment track
- **Local container runtime:** Author `docker-compose.yml` provisioning local PostgreSQL 15 with persistent named volumes (`pgdata`), health check probes, and network isolation.
- **Environment specification:** Author `.env.example` templates for both frontend and backend.
- **Pre-deployment architecture planning:** Research target cloud platform hosting specs, containerization layer caching strategies, and database connection limits for Phase 2.

#### 4. Quality assurance & verification track
- **Frontend tests:** Unit tests for form validation rules, token storage, and route guard redirects.
- **Backend tests:** Implement `tests/conftest.py` with test database fixtures, isolated transaction rollback per test, and `TestClient` injection; author `tests/integration/test_auth.py` and `tests/integration/test_trips.py` verifying registration, duplicate email rejection, login failure anonymity (NFR-02), and cross-user data isolation (HTTP 404 on foreign trip access).

- **Deliverable:** Fully functional end-to-end application where users register, log in with JWT, and create, view, edit, and delete trips with database-enforced constraints.

---

### Sprint 2: AI itinerary generation, location verification and fallback engine

*Implements the AI generation pipeline using Gemini via google-genai, structured JSON validation, real-world Google Places verification, fallback substitution, and rich multi-day timeline visualization.*

- **Target requirements:** FR-05, FR-06, FR-07, FR-08, FR-09, FR-10, FR-16; US-05, US-08, US-11, US-13, US-18, US-19, US-20, US-23; NFR-03, NFR-10, NFR-11, NFR-12, NFR-13, NFR-14.

#### 1. Frontend & UI/UX track
- **Generation progress screen:** Build `GenerationStatus.jsx` featuring animated progress steps (Prompting AI, Validating Structure, Verifying Real Places, Building Timeline), background polling with timeout handling, and clear error banners with a one-click retry button.
- **Multi-day itinerary dashboard:** Build `ItineraryDashboard.jsx` featuring tabbed day navigation, expandable timeline view, activity time slots, duration chips, and category tags.
- **Data provenance badges:** Implement `StatusBadge.jsx` displaying clear provenance indicators (`Verified`, `Cached`, `Estimated`, `Unverified`, `Unavailable`) complying with DR-08 and NFR-14.
- **Fallback notification UI:** Build callout banners alerting users when an interest-matched alternative is substituted for an unverified POI (FR-08, AF-06).
- **Preliminary cost summary:** Render initial estimated trip cost panel displaying provisional cost breakdown by category (DR-07).
- **Service integration:** Implement `services/itineraries.js` handling generation triggers, itinerary retrieval, and deletion.

#### 2. Backend & database track
- **AI pipeline, generation loop and output validation:**
  - Implement `app/ai/base.py` defining the abstract `LLMClient` protocol and unified AI exceptions (`LLMTimeoutException`, `LLMQuotaException`, `LLMMalformedException`).
  - Build `app/ai/gemini_client.py` wrapping the `google-genai` SDK with server-side API key resolution, temperature configuration, and request timeouts.
  - Author `app/ai/prompts.py` constructing structured generation prompts enforcing day-wise JSON schemas, incorporating trip constraints, sanitizing user inputs, and injecting ground truth facts.
  - Implement `app/ai/generation.py` coordinating the AI request lifecycle with bounded retries (up to 3 attempts) feeding validation errors back to the model.
  - Implement `app/ai/output_validator.py` parsing raw model output, validating JSON types, checking day-count alignment with trip duration (DR-05), detecting temporal overlaps, and implement `app/services/itinerary_service.py`.
- **Itinerary persistence, models and initial cost aggregator:**
  - Implement `app/models/itinerary.py` defining `Itinerary`, `ItineraryDay`, `ItineraryItem`, and `CostItem` entities with foreign keys and cascade deletes.
  - Build `app/repositories/itinerary_repository.py` with optimized queries utilizing `selectinload` for eager-loading days, activities, and cost records.
  - Implement atomic transactional database persistence in `app/services/itinerary_service.py` ensuring complete itineraries are written atomically or rolled back completely on failure.
  - Implement preliminary cost calculator in `app/domain/cost_calculator.py` aggregating estimated costs across categories with provisional status flags (DR-07).
  - Create Alembic migration for itinerary tables and implement `app/api/v1/endpoints/itineraries.py` (`GET /trips/{id}/itineraries`, `GET /itineraries/{id}`, `DELETE /itineraries/{id}`).
- **Place verification, fallbacks, provider registry and schemas:**
  - Implement `app/integrations/base.py` and `app/integrations/provider_registry.py` with extensible adapter registry and shared HTTP client with timeout management.
  - Author `app/integrations/places.py` interfacing with the Google Places API (Find Place from Text, Place Details) to retrieve real-world coordinates, place IDs, address data, and operating hours.
  - Implement `app/services/verification.py` verifying every AI-suggested POI against Google Places and querying alternative nearby places matching user interests when unverified (FR-08, AF-06).
  - Author `app/schemas/itinerary.py` defining strict JSON input/output schemas and tagging places with data provenance labels (`Verified`, `Cached`, `Estimated`, `Unverified`, `Unavailable`).
  - Author offline recorded mock datasets in `tests/fixtures/gemini_responses.json` and `tests/fixtures/places_responses.json`.

#### 3. DevOps, infrastructure & deployment track
- **CI secret isolation:** Configure CI environment variables and key management preventing API key exposure in automated builds.
- **Provider mock framework:** Validate that offline test suites run 100% disconnected from external network access using recorded mock JSON fixtures.
- **Pre-deployment image architecture:** Plan multi-stage Docker build specifications and base image evaluation (`python:3.11-slim`).

#### 4. Quality assurance & verification track
- **Frontend tests:** Component tests for generation polling, retry error handling, and timeline item rendering.
- **Backend tests:** Author `tests/unit/test_output_validator.py` and `tests/integration/test_itineraries.py` simulating external API outages, rate-limit 429s, and malformed JSON to verify that unvalidated data is never saved as successful (NFR-11, NFR-13).

- **Deliverable:** Working AI itinerary generation pipeline producing structured, validated, multi-day travel plans with real-world location verification and fallback recommendations, displayed in an interactive dashboard.

---

### Sprint 3: Interactive maps, route calculation, 2-opt optimization and transport services

*Connects itinerary activities with real-world geographic routing via Google Routes API, implements a 2-opt route optimization algorithm, caches routes, and provides multi-modal transport comparison.*

- **Target requirements:** FR-11, FR-12, FR-13, FR-14, FR-15; US-06, US-10, US-14, US-21, US-22; NFR-04, NFR-14.

#### 1. Frontend & UI/UX track
- **Google Maps integration:** Embed Google Maps JavaScript API via `@react-google-maps/api` in `MapView.jsx` with responsive centering and day-specific marker filtering.
- **Interactive map markers:** Render numbered markers matching itinerary sequence with category icons and interactive `PlaceInfoWindow.jsx` displaying place details, address, photo, and operating hours.
- **Route polyline visualization:** Render color-coded route polylines between consecutive stops on the map, with transit duration and distance badges displayed along legs.
- **Route optimization UI:** Implement "Optimize Route" action button with animated reordering feedback and before/after travel time reduction metrics.
- **Multi-modal transport drawer:** Build `TransportDrawer.jsx` displaying flights, trains, intercity buses, and local cabs sorted by cost and travel time, complete with external booking link-outs.
- **Accommodation options view:** Build `AccommodationList.jsx` presenting hotels filtered by destination and budget tier with data provenance labels.

#### 2. Backend & database track
- **Transport integrations, multi-modal comparison and Haversine fallback:**
  - Implement `app/integrations/amadeus.py` connecting to Amadeus for Developers API with client credential OAuth2 token rotation, supporting flight offers search and hotel list lookups.
  - Implement `app/integrations/ground_transport.py` providing structured timetable and fare estimates for intercity rail and bus connections.
  - Implement `app/services/transport.py` calculating and comparing transportation choices (flights, trains, buses, local transit, and distance-based cab estimates) sorted by cost and travel time.
  - Build endpoints in `app/api/v1/endpoints/itineraries.py` (`GET /itineraries/{id}/transport`, `GET /accommodation`) returning options tagged with data provenance and provider booking links.
  - Implement Haversine straight-line distance math in `app/domain/route_optimizer.py` as a graceful fallback when external routing APIs time out (AF-10).
- **Google Routes API, routing service and route cache layer:**
  - Implement `app/integrations/routes.py` invoking the Google Routes API (Compute Route Matrix and Route Geometry) supporting driving, walking, and transit travel modes.
  - Implement `app/services/routing.py` taking consecutive itinerary stops, computing point-to-point distances (meters) and durations (seconds), and formatting human-readable metrics.
  - Define `RouteLeg` models and `route_cache` table in `app/models/itinerary.py` storing origin/destination coordinates, polyline geometry, mode, distance, duration, and TTL expiration.
  - Implement route caching repository layer and `GET /itineraries/{id}/routes` delivering daily route polylines, segment distances, and estimated travel times.
  - Create Alembic revision for `route_legs` and `route_cache`, and author `tests/integration/test_routing.py`.
- **2-opt route optimization and geo-spatial performance:**
  - Implement `app/domain/route_optimizer.py` utilizing nearest-neighbor heuristic initialization improved by 2-opt local search to eliminate route backtracking.
  - Build clustering logic in `app/domain/route_optimizer.py` anchoring daily activity sequences to accommodation locations or primary morning arrival points.
  - Build `POST /itineraries/{id}/optimize` in `app/services/itinerary_service.py` to reorder itinerary items in the database and return before-and-after travel time metrics.
  - Implement logic in `route_optimizer.py` excluding unverified or missing-coordinate places from routing calculations while preserving their scheduled slots (AF-10).
  - Author `tests/fixtures/routes_responses.json` and `tests/unit/test_route_optimizer.py` verifying route optimization benchmarks execute under 5 seconds (NFR-04).

#### 3. DevOps, infrastructure & deployment track
- **Staging database setup:** Provision staging PostgreSQL database with geo-query indexing.
- **Automated performance benchmarking:** Author automated benchmark runner testing route recalculation latency across 3-day, 7-day, and 14-day itineraries under concurrent loads.
- **CI benchmark gate:** Integrate performance benchmark verification into GitHub Actions pull request checks.

#### 4. Quality assurance & verification track
- **Frontend tests:** Visual tests for map rendering, marker pin mapping, and route polyline display.
- **Backend tests:** Unit tests in `test_route_optimizer.py` demonstrating that the optimized route order never exceeds initial travel time, and handles degenerate cases (0, 1, or 2 stops); integration tests in `test_routing.py` and `test_transport.py` testing route calculations across varied coordinates.

- **Deliverable:** Interactive itinerary map with verified places, route polylines, 2-opt route optimization reducing travel time, and multi-modal transport comparison with booking link-outs.

---

### Sprint 4: Budget engine, schedule validation, customization and PDF export

*Delivers the financial calculation engine with budget thresholds and alerts, schedule validation for conflict detection, an atomic customization pipeline, AI-powered alternative activity replacement, and ReportLab PDF export.*

- **Target requirements:** FR-16, FR-17, FR-18, FR-19, FR-20, FR-21; US-07, US-09, US-12, US-13; NFR-04, NFR-17, NFR-18.

#### 1. Frontend & UI/UX track
- **Financial dashboard:** Build `BudgetSummaryCard.jsx` and `CategoryCostBar.jsx` displaying total estimated costs, planned trip budget, category-wise spending distribution, and daily spending averages.
- **Real-time budget alerts:** Implement visual alert banners: 80% threshold warning banner and 100% budget overrun alert banner with recommendations for lower-cost alternatives (DR-03, AF-09).
- **Drag-and-drop itinerary customization:** Implement full interactive editing in `EditItinerary.jsx` using `@dnd-kit/core`:
  - Drag-and-drop activity reordering within a day.
  - Moving activities between different days.
  - Adding manual activities with name, time, and estimated cost.
  - Removing activities with automatic gap-filling.
- **AI alternative replacement modal:** Build `AlternativesModal.jsx` allowing travelers to browse and swap an activity with an interest-matched alternative (US-09).
- **Schedule conflict warnings:** Display inline diagnostic badges highlighting overlapping activity times (DR-04), transit feasibility violations (DR-06), and closed operating hours conflicts (DR-01).
- **PDF export interface:** Implement PDF export button with animated download state, streaming binary PDF from backend and launching it in browser or external reader.

#### 2. Backend & database track
- **Schedule feasibility, opening hours and AI alternatives:**
  - Implement `app/domain/schedule_validator.py` enforcing temporal rules: positive activity durations, zero temporal overlaps between scheduled items (DR-04), and transit feasibility between stops (DR-06).
  - Enhance `schedule_validator.py` with opening-hours checking against verified POI operating hours (DR-01); explicitly ensure missing hours are never assumed open (NFR-14).
  - Implement `app/ai/alternatives.py` generating substitute activity recommendations based on remaining time windows, budget headroom, and user interests (US-09).
  - Implement `app/services/validation.py` and `POST /itineraries/{id}/validate` returning structured conflict diagnostics (`ScheduleConflictError`) with actionable resolution suggestions.
  - Implement concurrency locking guards during validation and author `tests/unit/test_schedule_validator.py`.
- **Financial engine, budget tracking and PDF document generation:**
  - Complete `app/domain/cost_calculator.py` supporting category aggregation, planned daily budget division, multi-currency verification, and provisional flags for unpriced items.
  - Implement `app/services/budget.py` and `GET /itineraries/{id}/budget` returning spending totals, 80% threshold warnings, 100% budget overrun alerts, and lower-cost alternatives (DR-03, AF-09).
  - Implement `app/services/export.py` using ReportLab compiling the latest saved itinerary into a clean, formatted PDF document containing day-by-day schedules, route notes, and cost breakdowns.
  - Implement `app/api/v1/endpoints/export.py` (`GET /itineraries/{id}/export/pdf`) streaming the generated PDF binary with proper MIME headers (`application/pdf`) and filename disposition.
  - Author `tests/unit/test_cost_calculator.py` and `tests/integration/test_export.py` (verifying failure isolation where PDF error leaves data intact, AF-11).
- **Customization pipeline, atomic transactions and database auditing:**
  - Implement item-level CRUD in `app/api/v1/endpoints/itineraries.py`: `POST /items` (add), `DELETE /items/{id}` (remove), and `PUT /days/{id}/order` (reorder).
  - Implement `POST /itineraries/{id}/items/{item_id}/replace` swapping an existing itinerary item with a verified alternative while preserving day continuity.
  - Build the atomic mutation pipeline in `app/services/itinerary_service.py` that executes re-validation, route recalculation, cost re-aggregation, and budget checks within a single database transaction.
  - Implement rollback mechanics in the modification pipeline ensuring that any edit triggering a schedule or route conflict rejects cleanly and preserves the last valid itinerary state (FR-20, AF-08, NFR-17).
  - Create Alembic revision for activity sorting indices and modification audit fields, and author `tests/integration/test_customization.py` verifying recalculation under 5 seconds (NFR-04).

#### 3. DevOps, infrastructure & deployment track
- **Container build optimization:** Configure ReportLab C-dependencies (FreeType fonts, libpng) in container build manifests.
- **Database concurrency tuning:** Audit database transaction isolation and row locking to ensure atomic customizations under concurrent requests.
- **Production build manifests:** Author final `Dockerfile.prod` and cloud environment provisioning scripts for Sprint 5 deployment.

#### 4. Quality assurance & verification track
- **Frontend tests:** End-to-end user interaction tests testing drag-and-drop reordering, alternative replacement, and PDF blob download.
- **Backend tests:** Comprehensive test suite in `test_cost_calculator.py`, `test_schedule_validator.py`, `test_customization.py`, and `test_export.py` verifying atomic rollback on schedule conflicts, budget threshold mathematics, and PDF generation failure isolation (AF-11).

- **Deliverable:** Customizable itinerary with budget tracking, cost alerts, schedule validation, automatic route updates, atomic rollback on error, and ReportLab PDF export.

---

### Sprint 5: System integration, security hardening, production deployment and release operations

*Unifies all subsystems, hardens frontend and backend security, executes production multi-stage containerization, provisions cloud infrastructure, configures automated CI/CD deployment, hardens SSL/TLS and CORS, and performs live smoke tests.*

- **Target requirements:** All functional requirements (FR-01 through FR-21); NFR-01, NFR-02, NFR-03, NFR-04, NFR-05, NFR-06, NFR-07, NFR-08, NFR-09, NFR-10, NFR-11, NFR-15, NFR-16, NFR-17, NFR-18.

#### 1. Frontend & UI/UX track
- **Production build optimization:** Execute bundle analysis, configure route code splitting via `React.lazy`, enable tree-shaking, and optimize static assets to guarantee page load times under 2 seconds (NFR-01).
- **Responsive layout hardening:** Audit and polish responsive design across mobile phones (375px+), tablets, and desktop displays (NFR-18).
- **Cross-browser verification:** Test and verify flawless execution across modern Chrome, Firefox, Safari, and Edge browsers.
- **Accessibility (a11y) audit:** Ensure full WCAG AA compliance: semantic heading hierarchy, ARIA labels on map controls and drag handles, keyboard navigation, and focus traps on modals.
- **Error boundaries:** Implement global React `ErrorBoundary.jsx` and network-failure recovery screens.

#### 2. Backend & database track
- **Integration resiliency hardening:** Audit and tune exponential backoff, retry caps, and timeout thresholds across all external integrations (Gemini, Google Places, Google Routes, Amadeus) to guarantee graceful failure behavior (NFR-10, AF-04).
- **AI latency optimization:** Parallelize independent backend tasks (running Google Places lookups concurrently) to consistently achieve complete generation under the 30-second target (NFR-03).
- **Security and sanitization audit:** Audit Pydantic models, SQL queries, and input length limits across all endpoints to ensure zero XSS or SQL injection vectors (NFR-07).
- **API contract publication:** Generate and publish complete OpenAPI 3.0 specification (`docs/api/api-contract.md`) and verify zero stack trace leakage on error responses (NFR-11).
- **Live cloud verification and sign-off:** Perform post-deployment smoke testing on the deployed cloud URL, covering the live Gemini AI generation loop, live JWT authentication and PDF export, and live Google Maps API and trip customization.

#### 3. DevOps, infrastructure & deployment track
- **Production Docker multi-stage containerization:**
  - Build production-ready `Dockerfile.prod` utilizing a two-stage build: build stage for compilers and wheels; lean runtime stage using `python:3.11-slim`, non-root user `appuser` (UID 10001), pre-compiled bytecode (`PYTHONDONTWRITEBYTECODE=1`), and production Uvicorn worker settings.
  - Author `docker-compose.prod.yml` orchestrating the FastAPI backend, PostgreSQL 15 container with encrypted persistent volumes, internal isolated bridge network, and Nginx reverse proxy.
- **Cloud hosting and infrastructure provisioning:**
  - Deploy and provision backend and frontend containers to the production cloud hosting environment (Render, Railway, AWS ECS/EC2, or GCP Cloud Run).
  - Provision managed PostgreSQL 15 database instance with connection pooling limits, automated daily snapshots, encrypted storage volumes, and private VPC firewall restrictions.
- **Automated CI/CD deployment pipeline:**
  - Author `.github/workflows/deploy.yml` configuring automated continuous deployment: runs linter and pytest suite, builds Docker image, performs security vulnerability scan, and pushes release to the production cloud host upon pull request merge to `main`.
- **Production secret management and security audit:**
  - Configure production secrets within cloud secret manager (`DATABASE_URL`, `SECRET_KEY`, `GEMINI_API_KEY`, `GOOGLE_MAPS_API_KEY`, `AMADEUS_API_KEY`).
  - Execute automated secret scanning (`git-secrets`, `trufflehog`) across Git commit history, configuration files, and build logs to verify zero exposed credentials (NFR-09).
  - Verify that production logging cleanly redacts passwords, tokens, and keys in production log streams.
- **Production database migration execution and reference seeding:**
  - Configure automated pre-deployment migration execution hook (`alembic upgrade head`) ensuring schema updates apply before incoming traffic starts serving.
  - Execute automated seed script (`scripts/seed_reference_data.py`) in production to populate reference destinations and categories.
- **Nginx reverse proxy, SSL/TLS termination and production hardening:**
  - Author `nginx/nginx.conf` acting as reverse proxy for the Uvicorn application server.
  - Configure SSL/TLS certificates (Let's Encrypt / Cloud SSL) enforcing strict HTTPS encryption across all API routes (NFR-08) with automatic HTTP-to-HTTPS 301 redirection.
  - Enforce modern security headers (`Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Content-Security-Policy`).
  - Restrict production CORS headers strictly to the production frontend domain.
  - Configure production rate limiting using `slowapi` backed by Redis or shared memory.
- **Health probes, centralized logging and system monitoring:**
  - Connect cloud container liveness and readiness monitors to `GET /health`.
  - Configure structured JSON log aggregation and real-time error tracking (e.g. Sentry or CloudWatch/Stackdriver) to capture unhandled exceptions without leaking stack traces to clients (NFR-11).
  - Set up uptime monitoring alerts to notify the team in case of service degradation or API quota exhaustion.
- **Automated smoke testing and rollback runbook:**
  - Execute automated post-deployment smoke test suite against the live cloud domain testing health, user registration/login, trip creation, AI generation, and PDF export.
  - Document `docs/deployment/runbook.md` specifying step-by-step procedures for zero-downtime deployment, blue/green cutover, database backup restoration, and emergency rollback to previous stable Docker tags.

#### 4. Quality assurance & verification track
- **Full end-to-end regression suite:** Execute and report complete automated test suite (unit, integration, failure-injection, and end-to-end journeys from registration through trip creation, AI generation, map visualization, route optimization, budget validation, manual customization, saving, and PDF export).
- **Performance benchmark audit:** Benchmark system against all performance SLAs: page load < 2s (NFR-01), saved itinerary read < 2s (NFR-02), AI generation < 30s (NFR-03), and route recalculation < 5s (NFR-04).
- **Security and integrity sign-off:** Execute final security audit confirming zero secret leaks, 100% test pass rate, and full compliance with all NFRs.

- **Deliverable:** Fully integrated, tested, hardened, and containerized AI Travel Planner deployed to the production cloud environment with HTTPS, automated CI/CD, complete documentation, and passing smoke tests.

---

### 13.3 Project-wide workload matrix

| Sprint | Frontend & UI/UX | Backend & database | DevOps & deployment | QA & verification |
| :---: | :--- | :--- | :--- | :--- |
| **Sprint 1** | React/Vite shell, Tailwind tokens, Auth pages (`Login`, `Signup`), `TripForm` wizard, `MyTrips` list. | Core shell, config, exceptions, logging, health; user model, Argon2, JWT, DB session pool; trip model, CHECK rules, trip CRUD, Alembic base. | Local Docker Compose, PostgreSQL 15 container, env templates, cloud research. | Form validation tests, auth integration tests (`test_auth.py`), trip isolation tests (`test_trips.py`). |
| **Sprint 2** | Generation status page with polling, multi-day itinerary timeline, provenance badges, fallback callout. | Gemini SDK client, prompt builder, AI loop, JSON validator; itinerary models, eager joins, atomic persist, cost calc; Places adapter, verification service, fallbacks, schemas. | CI secret isolation, offline mock JSON fixtures (`gemini_responses.json`), container specs. | Output validator unit tests, API outage and 429 rate-limit injection tests (`test_itineraries.py`). |
| **Sprint 3** | Google Maps embed, sequence marker pins, route polylines, transport drawer, accommodation list. | Amadeus adapter, ground transit, transport API, Haversine; Routes API adapter, routing service, route cache table; 2-opt route optimizer, cluster logic, optimization API. | Staging database setup, automated performance benchmark scripts for route optimization. | Visual map regression tests, 2-opt route solver unit tests, route calculation tests (`test_routing.py`). |
| **Sprint 4** | Financial dashboard, budget alert banners (80%/100%), dnd-kit drag-and-drop customization, PDF trigger. | Schedule validator, opening hours check, AI alternatives; cost calculator, budget service, ReportLab PDF engine; customization CRUD, alternative replace, atomic pipeline. | ReportLab C-dependencies in container, DB concurrency locking, production build manifests. | DnD interaction tests, budget threshold boundary tests, PDF failure isolation tests (`test_export.py`). |
| **Sprint 5** | Production bundle optimization (<2s load), responsive hardening, WCAG AA a11y audit, ErrorBoundary. | Resiliency tuning, AI parallelization, security audit, API contract publication, live cloud endpoint verification. | Multi-stage Docker, cloud hosting, CI/CD pipeline, production DB, SSL/TLS, Nginx, secrets audit, live smoke tests. | Full E2E regression suite, performance SLA audit (<2s reads, <30s generation, <5s routes), security sign-off. |

### Administrator features

The administrator stories (US-15 to US-17) are not listed in any sprint deliverable. They are built after the sprint items above if time allows, in this order: account management (US-15), flagged itineraries and feedback (US-16), reference data (US-17). Until then the `administrator` role exists in the data model and admin endpoints return access denied to non-administrators.
