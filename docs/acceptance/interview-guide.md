# Stakeholder interview guide, round 1 (IMP-114)

- Card: IMP-114 · Stakeholder interviews round 1 and recorded findings (US-151)
- Guide and findings: Krrish · Interviews: Junaid · Review: Junaid and the supervisor
- Results: [interviews-round1.md](interviews-round1.md)
- Sources: the card's step 1 cites "blueprint §4 and Appendix D". That blueprint is not in this repository, so this guide is built from the specification instead:
  - the product objective and main journey (§1.1, §1.6);
  - the scope and out-of-scope lists (§1.2, §1.3);
  - the functional requirement register (§2.2).

## 1. Purpose of round 1

Round 1 checks the requirement register (§2) against what people who plan trips actually need, before the build starts. It asks:

- whether the MVP journey matches how people plan a trip: describe a trip, get a day-wise, costed plan, check it and edit it;
- which requirements matter most to them, and which they would not miss;
- where what they expect **conflicts** with a requirement in §2. Each conflict becomes one change-request issue citing the FR IDs (US-151 AC2).

Round 1 does not test a screen. It is a conversation about how people plan trips today and what they would expect from the product.

## 2. Consent note (read aloud before the first question)

> Thank you for taking part. This is a short conversation, about 20 to 30 minutes, about how you plan trips. It is for a student project building a trip-planning web app.
>
> - Taking part is voluntary. You can skip any question or stop at any time, without giving a reason.
> - We take notes, but we do not write down your name, contact details or anything else that identifies you. Your notes get an interview number only.
> - We do not record audio or video unless you say yes to that now. If you say no, we only take written notes.
> - The anonymised notes are stored in the project repository, where the team and our supervisor can read them.
>
> Do you agree to take part? And do you agree to an audio recording, yes or no?

Write down only "consent given: yes/no" and "recording: yes/no" in the session log. If consent is not given, end the interview and record nothing else.

## 3. Stakeholder roles to cover

The specification has no separate stakeholder section, so these roles come from the people it describes in §1.1 and §2. The interviewer records the role of each interview, never the person.

| Role | Why it matters | Where the specification describes it |
| --- | --- | --- |
| Traveller planning their own trip | The signed-in traveller who describes a trip and receives a day-wise, costed, editable plan | §1.1; FR-007, FR-009, FR-059 |
| Traveller planning for a group with children | Trips have adults and children; places carry child suitability; prices may be per person or per group | FR-007, FR-008, FR-019, FR-071 |
| Traveller who needs step-free access | Step-free is a preference and a place fact, and unknown is never shown as "no" | FR-009, FR-019 |
| Budget-focused traveller | Budget, cost breakdown, alerts near and over budget | FR-071, FR-073, FR-074 |
| Course supervisor | Reviews the round 1 findings with Junaid (the card's test) and takes part in scope decisions | Card IMP-114 tests; IMP-499 week 4 cut decision; Appendix B.3 (OD-07, OD-11) |

## 4. Questions

Ask the questions in order, one at a time, without suggesting an answer. Follow-ups are "Can you tell me more?" or "Can you give an example from a trip you planned?". Each question cites the FR IDs whose assumptions it probes. The interviewer does not read the FR IDs aloud.

### Accounts and trips

1. The last time you planned a trip, what did you need to decide before you could start planning the days? (FR-007, FR-009)
2. What would make you want to stop halfway through planning and come back later, and what would you expect to find when you return? (FR-013, FR-014)
3. When something about the trip changes after you have a plan, such as the dates or who is coming, what do you expect to happen to that plan? (FR-011)

### Places

4. How do you choose which places to visit at a destination, and what do you need to know about a place before you add it? (FR-016, FR-017, FR-018)
5. When a fact about a place, such as its price or opening hours, is uncertain or unknown, how would you like that to be shown to you? (FR-018, FR-076)
6. Which needs of the people in your group decide whether a place is suitable, for example for children or for step-free access? (FR-019)

### Generation

7. If a tool proposed a day-by-day plan for you, what would make you trust it, and what would make you distrust it? (FR-031, FR-033, FR-035)
8. How full do you like a day to be, and how do you plan meals into it? (FR-029, FR-083)
9. If the planning service were briefly unavailable, what would you expect to see instead? (FR-036, FR-037)

### Validation

10. What problems have you run into with a day plan in practice, such as a place being closed, too little time to get between places, or too much in one day? How would you want to be told about them? (FR-050, FR-051, FR-052, FR-053, FR-056)

### Editing

11. After you get a plan, which changes would you expect to make yourself, and which would you expect the tool to handle for you? (FR-060, FR-061, FR-062, FR-063, FR-065, FR-066, FR-067)

### Costs and routes

12. How do you estimate what a trip will cost, and how detailed do you need that estimate to be? (FR-071, FR-072, FR-073)
13. What would you want to happen when a plan comes close to or goes over your budget? (FR-074, FR-075)
14. How do you work out travel times between places, and how do you use a map while planning? (FR-078, FR-079, FR-080)

### Output and accessibility

15. When the plan is ready, what would you want to take away from it, and on which device would you use it during the trip? (FR-094, FR-114, FR-115)

## 5. Out of scope: record as wishes, not conflicts

These are not offered in the eight-week release (§1.3, IMD-46):

- in-app booking of flights and hotels;
- payments;
- live prices, live opening hours and live availability.

The product never books or takes payment, and every price and hour is curated or estimated and labelled.

If an interviewee asks for one of these, record it in the notes as **"out-of-scope wish (§1.3, IMD-46)"**. It is **not** a conflict with §2 and gets no change-request issue. The same applies to the other §1.3 items (T1, R2, PP, Stage 2), for example receipts and expenses, reviews, or a conversational assistant. Record them as out-of-scope wishes with the §1.3 item where you can name it.

## 6. How to take anonymised notes

- **Identify interviews by number only:** 1 to 5, in the order held. Never write a name, initials, an e-mail address, a phone number, a workplace, a school, a social media handle or a photo.
- **Record the role, not the person:** use one role from section 3, plus at most a general description such as "plans family trips once a year". Never use details that could identify someone, such as an exact age, an employer or a home town.
- **Write what was said, briefly, in your own words.** Quote only short phrases that carry no identifying detail. Do not add your own interpretation to the notes; findings come later, in the findings summary.
- **Separate observations from wishes:** mark each point as a need, a problem from past trips, or an out-of-scope wish (section 5).
- **Note the question number** each point answers, so the findings can be mapped to FR IDs.
- **Recordings:** if recording was allowed, keep the file outside the repository, use it only to complete the notes, and delete it once the notes are written. Never commit a recording or a transcript.
- **Check before committing:** read the notes once for anything that identifies a person, and remove it.
