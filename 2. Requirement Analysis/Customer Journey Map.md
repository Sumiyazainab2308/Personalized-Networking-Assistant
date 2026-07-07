# Customer Journey Map
## Personalized Networking Assistant

**Project:** Personalized Networking Assistant  
**Team Lead:** Shaik Sumiya Zainab  
**Version:** 1.0  
**Date:** July 2026  

---

## 1. Overview

The Customer Journey Map describes the end-to-end experience of a user interacting with the Personalized Networking Assistant — from the moment they hear about a networking event to reviewing their past conversations. It identifies key touchpoints, user actions, system responses, emotions, and opportunities for improvement at each stage.

---

## 2. User Persona

| Attribute | Details |
|---|---|
| **Name** | Sumiya (Professional Networker) |
| **Role** | Software Engineer / Graduate Student |
| **Goal** | Make meaningful connections at professional events |
| **Pain Point** | Struggles to start conversations at unfamiliar events |
| **Tech Comfort** | High — comfortable with web applications |
| **Device** | Laptop (Windows/Mac), occasionally mobile |

---

## 3. Journey Stages

### Stage 1: Awareness — "I have an upcoming event"

| Element | Details |
|---|---|
| **Touchpoint** | Hears about the app through a colleague or SmartBridge |
| **User Action** | Opens browser → navigates to `http://localhost:8501` |
| **System Response** | Streamlit app loads with dark-themed dashboard |
| **Emotion** | 😐 Curious but slightly anxious about networking |
| **Opportunity** | Show a compelling hero message explaining what the app does |

---

### Stage 2: Input — "I describe my event"

| Element | Details |
|---|---|
| **Touchpoint** | Main page input section |
| **User Action** | Types event description: *"AI for Sustainable Cities — a summit on smart urban infrastructure"* |
| **User Action** | Types interests: *"climate change, urban planning, machine learning"* |
| **User Action** | Optionally adds bio: *"Software engineer passionate about smart cities"* |
| **System Response** | Input validated (minimum 10 characters); ready for generation |
| **Emotion** | 🤔 Engaged — filling in relevant details |
| **Opportunity** | Provide placeholder examples to guide users who don't know what to write |

---

### Stage 3: Generation — "The AI creates starters for me"

| Element | Details |
|---|---|
| **Touchpoint** | "Generate Starters" button + spinner |
| **User Action** | Clicks **[Generate Conversation Starters]** |
| **System Response** | POST `/api/v1/generate-conversation` called |
| **System Process** | BART extracts themes → GPT-2 generates starters → auto-saved to history |
| **Output** | 3–5 conversation starters displayed as styled cards |
| **Wait Time** | ~5–10 seconds (model inference on CPU) |
| **Emotion** | 😮 Impressed — AI produced relevant, natural suggestions |
| **Opportunity** | Show a loading indicator with fun message: *"The AI is crafting your starters..."* |

**Example Generated Starters:**
1. *"What's your take on using machine learning for real-time traffic optimization in cities?"*
2. *"Have you seen any promising pilots that balance sustainability goals with infrastructure costs?"*
3. *"I'd love to hear what brought you specifically to the AI and urban planning intersection."*

---

### Stage 4: Review & Feedback — "I rate the suggestions"

| Element | Details |
|---|---|
| **Touchpoint** | Starter cards with 👍 / 👎 buttons |
| **User Action** | Reads each starter → clicks 👍 on useful ones, 👎 on irrelevant ones |
| **User Action** | Submits 4-star overall rating |
| **System Response** | Feedback logged to `data/feedback.json` with timestamp |
| **Emotion** | 😊 Empowered — feels in control of what's useful |
| **Opportunity** | Show a "thank you" toast message after feedback submission |

---

### Stage 5: Fact-Check — "I verify a topic before the event"

| Element | Details |
|---|---|
| **Touchpoint** | Fact-Check tab in the main app |
| **User Action** | Types: *"blockchain in healthcare"* → clicks **[Fact Check]** |
| **System Response** | GET `/api/v1/fact-check?query=blockchain+in+healthcare` |
| **System Process** | Wikipedia REST API queried → extract returned |
| **Output** | Green card with Wikipedia summary and link |
| **Emotion** | 😌 Confident — walks into the event with verified context |
| **Opportunity** | Allow bookmarking or downloading fact-check results |

---

### Stage 6: History Review — "I revisit past conversations"

| Element | Details |
|---|---|
| **Touchpoint** | History tab / History page in sidebar |
| **User Action** | Navigates to History → sees last 5 sessions |
| **User Action** | Optionally searches by keyword (*"blockchain"*) |
| **System Response** | GET `/api/v1/history` → paginated results displayed |
| **Output** | Expandable cards: event, themes, starters, date, rating |
| **Emotion** | 🧠 Reflective — learning from previous strategies |
| **Opportunity** | Add "Export History as PDF" button for offline use |

---

### Stage 7: Continuous Improvement — "I track what worked"

| Element | Details |
|---|---|
| **Touchpoint** | Feedback History section / Dashboard |
| **User Action** | Reviews the Feedback History View (last 10 rated starters) |
| **User Action** | Visits Analytics Dashboard to see top themes and average ratings |
| **System Response** | Aggregate stats displayed: total sessions, avg rating, top theme |
| **Emotion** | 📈 Motivated — sees improvement in networking strategy over time |
| **Opportunity** | Add AI-driven recommendation: "Based on your feedback, try these themes..." |

---

## 4. Journey Map Visual Summary

```
STAGE        1          2          3          4          5          6          7
           Aware     Input    Generate   Feedback  Fact-Check  History   Improve
             │          │          │          │          │          │          │
USER      Opens      Types      Clicks     Rates     Verifies  Reviews   Reflects
ACTION    App →      Event →    Button →   Stars →   Topic →   Past →    Learns
             │          │          │          │          │          │          │
SYSTEM    Load       Validate   BART +     Save to   Wikipedia  Read      Dashboard
ACTION    UI →       Input →    GPT-2 →    JSON →    API →     JSON →    Stats
             │          │          │          │          │          │          │
EMOTION   Curious    Engaged   Impressed  Empowered Confident Reflective Motivated
            😐         🤔         😮         😊         😌         🧠         📈
             │          │          │          │          │          │          │
PAIN      Slow       No         Long       No         Limited   Hard to   No
POINTS    load       hints      wait       undo       results   search    filter
```

---

## 5. Key Pain Points & Solutions

| Pain Point | Stage | Solution Implemented |
|---|---|---|
| Long model load time | Generation | Lazy loading singleton — model loaded once, cached |
| No internet? Can't fact-check | Fact-Check | Graceful error handling with user-friendly fallback message |
| Forgot what worked previously | History | History persisted to JSON; search supported |
| Blank/bad starters from GPT-2 | Generation | Post-processing: strips blanks, bullet markers, truncated text |
| Hard to navigate multiple features | All | Tabs (Generate / Fact-Check / History) in Streamlit UI |

---

## 6. Moments That Matter (Peak Moments)

1. **"WOW" Moment** — When the AI generates a starter that feels genuinely personalized (Stage 3)
2. **Trust Moment** — When Wikipedia confirms a fact the user was unsure about (Stage 5)
3. **Reflection Moment** — When the user sees their past session history and realizes their improvement (Stage 6–7)

---

## 7. Future Journey Enhancements

| Enhancement | Target Stage | Benefit |
|---|---|---|
| User authentication | Stage 1 | Multi-user support; personalized history |
| Voice input for event description | Stage 2 | Hands-free accessibility |
| AI-ranked starters (by past feedback) | Stage 3 | Smarter personalization |
| Real-time collaborative session | Stage 3 | Team networking prep |
| Export starters as PDF / note card | Stage 4 | Offline use at events |
| Push notifications before events | Stage 1 | Timely reminders |
