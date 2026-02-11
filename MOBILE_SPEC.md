# Girchi Digital Policy — Mobile App Design Specification

**Version:** 1.0
**Date:** February 2026
**Primary Language:** Georgian (ka-GE)
**Secondary Language:** English (en-US)

---

## Table of Contents

1. [User Personas](#1-user-personas)
2. [Information Architecture](#2-information-architecture)
3. [User Flows](#3-user-flows)
4. [Screen-by-Screen Wireframe Descriptions](#4-screen-by-screen-wireframe-descriptions)
5. [Design System](#5-design-system)
6. [Navigation Architecture](#6-navigation-architecture)
7. [Notification Strategy](#7-notification-strategy)
8. [Offline & Performance Strategy](#8-offline--performance-strategy)
9. [Onboarding & Empty States](#9-onboarding--empty-states)
10. [Error Handling UX](#10-error-handling-ux)
11. [Localization](#11-localization)
12. [Security UX](#12-security-ux)
13. [API Endpoint Mapping](#13-api-endpoint-mapping)

---

## 1. User Personas

### Persona 1: Giorgi, 28, Tbilisi — The Civic Activist

- **Role:** GeDer, Active Member
- **Tech comfort:** High — uses smartphone daily, familiar with digital platforms
- **GeD status:** Verified GeD holder
- **Goals:** Lead his neighborhood group, run for Atistavi, endorse friends, grow his precinct's member count
- **App usage:** Daily — checks election status, manages endorsements, responds to SOS reports
- **Motivations:** Political influence, community building, visibility within the party
- **Pain points:** Bureaucratic complexity, unclear hierarchy navigation, concern about fake accounts diluting votes
- **Key flows:** Create group, endorse supporters, run as candidate, vote, view hierarchy

### Persona 2: Nino, 42, Kutaisi — The Cautious Supporter

- **Role:** Endorsed Supporter, Passive Member
- **Tech comfort:** Medium — uses messaging apps and social media, less comfortable with complex apps
- **GeD status:** Does not own a GeD; heard about Girchi from a coworker who is a GeDer
- **Goals:** Vote in elections, sign petitions, participate without public exposure
- **App usage:** Weekly — votes when elections are active, checks initiatives
- **Motivations:** Having a political voice without full public exposure
- **Pain points:** Finding a GeDer willing to endorse her, understanding the system, navigating governance hierarchy
- **Key flows:** Find a GeDer, get endorsed, join a group, vote, sign initiatives

### Persona 3: Dato, 35, Berlin — The Diaspora Observer

- **Role:** GeDer (diaspora), Active Member
- **Tech comfort:** High — tech professional living abroad
- **GeD status:** Verified GeD holder, marked as diaspora
- **Goals:** Stay connected to Georgian politics, participate in parliamentary elections, follow national initiatives
- **App usage:** A few times per month — checks news, votes in parliamentary elections
- **Motivations:** Maintaining connection to homeland, contributing from abroad
- **Pain points:** Excluded from local governance decisions, time zone differences for live elections, limited features compared to local members
- **Key flows:** Registration with diaspora flag, parliamentary voting, browsing initiatives, viewing hierarchy

### Persona 4: Tamar, 52, Batumi — The Local Leader

- **Role:** GeDer, Active Member, elected Atistavi
- **Tech comfort:** Medium — learns through doing, comfortable with basic smartphone operations
- **GeD status:** Verified GeD holder, holds Atistavi position
- **Goals:** Solve real community problems, grow her precinct to the next tier, manage her group effectively
- **App usage:** Multiple times daily — manages SOS reports, verifies new members, handles endorsements
- **Motivations:** Community impact, unlocking new capabilities for her territory, keeping group members engaged
- **Pain points:** Managing multiple SOS reports simultaneously, keeping track of endorsement fraud risks, motivating passive members to participate
- **Key flows:** Verify SOS reports, escalate issues, endorse supporters, manage group, view gamification progress

---

## 2. Information Architecture

### 2.1 Full Sitemap

```
Root
├── Splash / Loading
│
├── Auth Stack (unauthenticated)
│   ├── Welcome Screen
│   ├── Registration
│   │   ├── Phone Input
│   │   ├── OTP Verification
│   │   ├── Personal Details (name, personal ID, password)
│   │   └── Registration Complete
│   └── Login
│       └── Phone + Password Input
│
├── Onboarding Stack (authenticated, not onboarded)
│   ├── GeD Check Prompt
│   │   ├── GeD Verification Flow (girchi.com JWT)
│   │   └── Skip (proceed as unverified)
│   ├── Join Reason
│   ├── Status Selection (Passive / Active)
│   ├── Constitution Acceptance
│   ├── Territory Assignment
│   │   ├── Map-based Precinct Selection
│   │   ├── Nearby Precincts List
│   │   └── Manual Region > District > Precinct Drill-down
│   ├── Diaspora Declaration (conditional)
│   └── Onboarding Complete
│
├── Main App (authenticated + onboarded)
│   │
│   ├── Tab 1: მთავარი (Home)
│   │   ├── Dashboard
│   │   │   ├── Progress Card (gamification)
│   │   │   ├── Active Elections Banner
│   │   │   ├── Recent SOS Reports (if leader)
│   │   │   ├── My Group Summary
│   │   │   └── Pending Actions Feed
│   │   └── Notification Center
│   │
│   ├── Tab 2: თემი (Community)
│   │   ├── My Group Detail
│   │   │   ├── Member List
│   │   │   └── Group Elections
│   │   ├── Browse Groups (in precinct)
│   │   │   ├── Join Group
│   │   │   └── Create Group (GeDer only)
│   │   ├── Endorsement Hub
│   │   │   ├── My Endorsements (given/received)
│   │   │   ├── Endorse a Supporter (GeDer)
│   │   │   ├── Find a GeDer (Supporter)
│   │   │   └── Endorsement Quota Status
│   │   └── Nearby GeDers Map
│   │
│   ├── Tab 3: მმართველობა (Governance)
│   │   ├── Elections
│   │   │   ├── Active Elections List
│   │   │   ├── Election Detail
│   │   │   │   ├── Candidates List
│   │   │   │   ├── Vote Screen
│   │   │   │   ├── Results Screen
│   │   │   │   └── Nominate Self
│   │   │   └── Past Elections Archive
│   │   ├── Hierarchy View
│   │   │   └── Interactive Tree (district level)
│   │   ├── Initiatives
│   │   │   ├── Browse Initiatives
│   │   │   ├── Initiative Detail
│   │   │   │   ├── Sign / Withdraw
│   │   │   │   └── Response (if threshold met)
│   │   │   └── Create Initiative
│   │   └── My Positions (if leader)
│   │
│   ├── Tab 4: SOS
│   │   ├── SOS Landing
│   │   │   └── SOS Button (prominent)
│   │   ├── Create Report
│   │   │   ├── Moral Filter
│   │   │   ├── Report Details
│   │   │   └── Submission Confirmation
│   │   ├── My Reports
│   │   │   └── Report Detail + Status Timeline
│   │   └── Assigned Reports (leader view)
│   │       ├── Verify / Reject
│   │       ├── Escalate
│   │       └── Resolve
│   │
│   ├── Tab 5: პროფილი (Profile)
│   │   ├── Profile Overview
│   │   ├── Edit Profile
│   │   ├── Gamification / Progress
│   │   │   ├── Territory Progress
│   │   │   ├── Unlocked Capabilities
│   │   │   └── Tier Milestones
│   │   ├── My Arbitration Cases
│   │   │   ├── Filed Cases
│   │   │   ├── Cases Against Me
│   │   │   └── File New Case
│   │   ├── Notification Center
│   │   ├── Settings
│   │   │   ├── Language (KA / EN)
│   │   │   ├── Biometric Lock
│   │   │   ├── Push Notification Preferences
│   │   │   ├── Device Management
│   │   │   └── About / Terms
│   │   └── Logout
│   │
│   └── Modals / Overlays
│       ├── Vote Confirmation Modal
│       ├── Endorsement Confirmation Modal
│       ├── Constitution Full Text Modal
│       ├── SOS Moral Filter Bottom Sheet
│       └── Session Expired Alert
```

### 2.2 Bottom Tab Bar

| Position | Icon | Label (KA) | Label (EN) | Badge Source |
|----------|------|-----------|-----------|-------------|
| 1 | House | მთავარი | Home | Pending actions count |
| 2 | People | თემი | Community | New endorsement requests |
| 3 | Scales | მმართველობა | Governance | Active elections not yet voted |
| 4 | Shield | SOS | SOS | Assigned unhandled reports (leaders) |
| 5 | Person | პროფილი | Profile | Unread notifications |

### 2.3 Screen Count Summary

| Category | Count | Screens |
|----------|-------|---------|
| Auth | 5 | Welcome, Phone Input, OTP, Personal Details, Registration Complete |
| Onboarding | 7 | GeD Check, GeD Verification, Join Reason, Status Selection, Constitution, Territory Assignment, Diaspora Declaration |
| Home | 2 | Dashboard, Notification Center |
| Community | 8 | Groups List, Group Detail, Create Group, Endorsement Hub, Endorse Supporter, Find GeDer, Nearby GeDers Map, Endorsement Detail |
| Governance | 9 | Elections List, Election Detail, Vote, Nominate, Results, Hierarchy Tree, Initiatives List, Initiative Detail, Create Initiative |
| SOS | 5 | SOS Landing, Moral Filter, Report Form, Report Detail, Assigned Reports |
| Profile | 7 | Profile Overview, Edit Profile, Gamification, Capabilities, Arbitration List, Case Detail, File Case |
| Settings | 4 | Settings Main, Language, Security, Notification Preferences |
| **Total** | **~47** | |

---

## 3. User Flows

### 3.1 Registration & Phone Verification

```
[Welcome] → [Phone Input] → [OTP Verification] → [Personal Details] → [Registration Complete]
```

**Screen 1: Welcome**
- Girchi logo centered
- Tagline: "თავისუფალი საზოგადოების პროტოტიპი" (Prototype of a free society)
- Two buttons:
  - "რეგისტრაცია" (Register) — primary
  - "შესვლა" (Log In) — secondary
- Language toggle (KA/EN) in top-right corner

**Screen 2: Phone Input**
- Header: "ტელეფონის ნომერი" (Phone Number)
- Country code pre-filled: +995 (Georgian flag icon)
- Phone number input field — numeric keyboard
- "გაგრძელება" (Continue) button — disabled until 9 digits entered
- Privacy policy link at bottom: "კონფიდენციალურობის პოლიტიკა"

**Screen 3: OTP Verification**
- Header: "შეიყვანეთ კოდი" (Enter the code)
- Subtext: "კოდი გაგზავნილია +995 XXX XX XX XX-ზე" (Code sent to +995...)
- 6 separate digit input boxes — auto-advance on entry, paste support
- Countdown timer: "ხელახლა გაგზავნა XX:XX-ში" (Resend in XX:XX)
- Resend link — disabled during countdown, enabled after, max 5/hour
- Auto-submits on 6th digit entry
- Error state: "არასწორი კოდი. დარჩენილია X მცდელობა" (Wrong code. X attempts remaining)

**Screen 4: Personal Details**
- Header: "პირადი მონაცემები" (Personal Details)
- Fields:
  - "სახელი" (First Name) — text input
  - "გვარი" (Last Name) — text input
  - "პირადი ნომერი" (Personal ID Number) — numeric, 11 digits, hint: "11-ნიშნა"
  - "პაროლი" (Password) — secure input with show/hide toggle
  - "პაროლის გამეორება" (Confirm Password) — secure input
- Password strength indicator below password field
- "ანგარიშის შექმნა" (Create Account) button

**Screen 5: Registration Complete**
- Checkmark animation (green circle, white check drawn)
- "ანგარიში შეიქმნა!" (Account Created!)
- "გთხოვთ, გაიარეთ ადაპტაციის პროცესი" (Please complete the onboarding process)
- "გაგრძელება" (Continue) button → navigates to onboarding stack

### 3.2 GeD Verification

```
[GeD Check Prompt] → [GeD Login WebView] → [GeD Verification Result]
```

**Screen 1: GeD Check Prompt**
- Illustration: stylized GeD badge/card
- Header: "ხართ თუ არა GeDer?" (Are you a GeDer?)
- Explanatory text: "GeD (Girchi e-Democracy) არის გირჩის ციფრული საიდენტიფიკაციო სისტემა. GeDer-ები სისტემის ბირთვია — მათ აქვთ ხმის მიცემის, ენდორსმენტის და ლიდერობის სრული უფლება." (GeD is Girchi's digital identification system. GeDers are the system core — they have full rights to vote, endorse, and lead.)
- Two buttons:
  - "დიახ, მაქვს GeD" (Yes, I have GeD) — primary
  - "არა, გამოტოვება" (No, skip) — text button

**Screen 2: GeD Login**
- WebView or external browser redirect to girchi.com
- Loading indicator: "girchi.com-თან დაკავშირება..." (Connecting to girchi.com...)
- User authenticates on girchi.com
- JWT token captured via callback/redirect
- Loading spinner: "მიმდინარეობს ვერიფიკაცია..." (Verification in progress...)

**Screen 3: GeD Verification Result**
- **Success state:**
  - Green checkmark icon
  - "თქვენ ხართ ვერიფიცირებული GeDer!" (You are a verified GeDer!)
  - GeD balance displayed: "თქვენი GeD ბალანსი: XXX"
  - "გაგრძელება" (Continue) button
- **Failure state:**
  - Red X icon
  - "ვერიფიკაცია ვერ მოხერხდა" (Verification failed)
  - "გთხოვთ, ცადეთ ხელახლა ან გამოტოვეთ" (Please try again or skip)
  - "ხელახლა ცდა" (Try Again) button + "გამოტოვება" (Skip) text button

### 3.3 Onboarding — Join Reason, Status Selection, Constitution

```
[Join Reason] → [Status Selection] → [Constitution Acceptance]
```

**Screen 1: Join Reason**
- Header: "რატომ უერთდებით ჩვენს საზოგადოებას?" (Why are you joining our community?)
- Subtext: "გთხოვთ, მოკლედ აღწეროთ" (Please describe briefly)
- Large multi-line text input (minimum 3 lines visible)
- Character counter: "0/500"
- "შემდეგი" (Next) button — disabled until at least 10 characters entered

**Screen 2: Status Selection**
- Header: "აირჩიეთ თქვენი ჩართულობის დონე" (Choose your engagement level)
- Subtext: "ეს არჩევანი განსაზღვრავს თქვენს უფლებებს სისტემაში" (This choice determines your rights in the system)
- Two large tappable cards:

  **Card A — Passive:**
  - Icon: Eye symbol
  - Title: "პასიური წევრი" (Passive Member)
  - Description: "მზად ვარ, მივიღო მონაწილეობა არჩევნებში" (I'm ready to participate in elections)
  - Footnote: "შეგიძლიათ ხმის მიცემა, პეტიციების ხელმოწერა" (You can vote, sign petitions)
  - Subdued color styling

  **Card B — Active:**
  - Icon: Megaphone symbol
  - Title: "აქტიური წევრი" (Active Member)
  - Description: "მზად ვარ, საჯაროდ გამოვხატო ჩემი პოზიცია" (I'm ready to publicly express my position)
  - Footnote: "მხოლოდ აქტიური წევრი შეიძლება აირჩეს ათისთავად" (Only active members can be elected as Atistavi)
  - Bold/highlighted color styling

- Selected card: border highlight + checkmark
- "შემდეგი" (Next) button — disabled until selection made

**Screen 3: Constitution Acceptance**
- Header: "გირჩის კონსტიტუცია" (Girchi Constitution)
- Scrollable full text of the constitution in a contained view
- Scroll progress indicator on right edge
- After scrolling to bottom, checkbox appears:
  - "ვეთანხმები კონსტიტუციას" (I agree to the constitution) — checkbox
- "დასრულება" (Complete) button — disabled until checkbox is checked
- Acceptance timestamp recorded

### 3.4 Territory Assignment & Precinct Discovery

```
[Territory Assignment] → [Map/Manual Selection] → [Diaspora Check] → [Confirmation]
```

**Screen 1: Territory Assignment**
- Header: "სად ცხოვრობთ?" (Where do you live?)
- Subtext: "თქვენი ტერიტორია განსაზღვრავს საარჩევნო უბანს და საზოგადოებას" (Your territory determines your precinct and community)
- "ჩემი ადგილმდებარეობის გამოყენება" (Use My Location) button — primary, requests GPS permission
- "ხელით არჩევა" (Select Manually) — secondary text button
- Small map preview of Georgia below buttons

**Screen 2A: Map View (if location used)**
- Full-screen map centered on user's GPS location
- User location shown as blue dot
- Nearby precincts as green pins with name labels
- Bottom sheet (half-screen, draggable) listing nearby precincts sorted by distance:
  - Each row: precinct name (KA), district name, distance ("~2.3 კმ"), member count, group count
  - Tap a row to select → pin highlights on map
- "არჩევა" (Select) button in bottom sheet when a precinct is tapped

**Screen 2B: Manual Selection (drill-down)**
- Step 1: Region list
  - Header: "აირჩიეთ რეგიონი" (Select Region)
  - Searchable list of all regions
- Step 2: District list (filtered by selected region)
  - Header: "აირჩიეთ ოლქი" (Select District)
  - Breadcrumb: "რეგიონი > ..."
  - Searchable list
- Step 3: Precinct list (filtered by selected district)
  - Header: "აირჩიეთ უბანი" (Select Precinct)
  - Breadcrumb: "რეგიონი > ოლქი > ..."
  - Each precinct shows member count and group count

**Screen 3: Diaspora Declaration (conditional)**
- Shown only if user explicitly triggers or if no precinct assignment is applicable
- "ცხოვრობთ თუ არა საზღვარგარეთ?" (Do you live abroad?)
- Explanatory text: "დიასპორის წევრები არ მონაწილეობენ ადგილობრივ მმართველობაში, მაგრამ მონაწილეობენ საპარლამენტო არჩევნებში" (Diaspora members don't participate in local governance but participate in parliamentary elections)
- Toggle: "დიახ, საზღვარგარეთ ვცხოვრობ" (Yes, I live abroad)
- If toggled on: precinct assignment skipped, diaspora badge applied

**Screen 4: Confirmation**
- Mini-map showing selected precinct location
- Summary card:
  - "რეგიონი:" (Region:) — value
  - "ოლქი:" (District:) — value
  - "უბანი:" (Precinct:) — value
- "დადასტურება" (Confirm) button
- "შეცვლა" (Change) text button
- On confirm → navigate to main app with brief success animation

### 3.5 Joining a Group of 10

```
[Groups List] → [Group Detail] → [Join Confirmation]
```

**Screen 1: Groups List (Community Tab)**
- Header: "ათეულები ჩემს უბანში" (Groups in my precinct)
- Precinct name shown as subtitle
- Filter chips (horizontal scroll): "ყველა" (All), "თავისუფალი" (Open), "ჩემი" (My Group)
- Scrollable card list, each card showing:
  - Group name (left)
  - Member progress bar with count "7/10" (right)
  - Atistavi name if elected (subtitle, with crown icon)
  - "სრულია" (Full) badge in red if at capacity
- Cards for open groups have a subtle green left border

**Screen 2: Group Detail**
- Header: group name with back button
- Info row: precinct name, creation date, member count
- Atistavi section (highlighted with background):
  - Crown icon + "ათისთავი:" (Atistavi:) + name
  - Or "ათისთავი ჯერ არ არჩეულა" (Atistavi not yet elected) if vacant
- Member list:
  - Each row: avatar (initials-based), full name, role badge (green "GeDer" / blue "მხარდამჭერი"), join date
- Bottom action:
  - If not a member and group not full: "გაწევრიანება" (Join) button — primary
  - If supporter without endorsement: "საჭიროა თავდები გაწევრიანებისთვის" (Endorsement required to join) — with link to Find a GeDer
  - If already a member: "გასვლა" (Leave) — danger text button

**Screen 3: Join Confirmation (Modal)**
- "გსურთ გაწევრიანება?" (Do you want to join?)
- Group name displayed
- "თქვენ ხდებით [Group Name]-ის წევრი" (You are becoming a member of [Group Name])
- "დადასტურება" (Confirm) — primary button
- "გაუქმება" (Cancel) — text button
- On success: brief confetti animation, navigate to My Group view

### 3.6 Creating a Group of 10

```
[Create Group Sheet] → [Group Created]
```

**Screen 1: Create Group (Bottom Sheet from Groups List)**
- Triggered by FAB "+" button (visible only to GeDers)
- Header: "ახალი ათეულის შექმნა" (Create New Group of 10)
- Group name input (optional): "სახელი (არასავალდებულო)" — placeholder: "ათეული #N"
- Precinct auto-filled (read-only): user's precinct
- "შექმნა" (Create) button

**Screen 2: Group Created (Full Screen)**
- Success checkmark animation
- "ათეული შეიქმნა!" (Group Created!)
- "თქვენ ხართ პირველი წევრი" (You are the first member)
- Share card: deep link to group for inviting others
- "გაზიარება" (Share) button — opens system share sheet
- "ათეულის ნახვა" (View Group) button → navigates to Group Detail

### 3.7 Finding a GeDer for Endorsement (Supporter Flow)

```
[Endorsement Needed Prompt] → [Nearby GeDers] → [Request Sent]
```

**Screen 1: Endorsement Needed Prompt**
- Shown when an unverified user tries to join a group or access restricted features
- Illustration: handshake icon
- Header: "საჭიროა თავდები" (Endorsement Required)
- Text: "თემში გასაწევრიანებლად საჭიროა GeDer-ი, რომელიც დაადასტურებს თქვენს ვინაობას და გახდება თქვენი თავდები." (To join the community, you need a GeDer who will verify your identity and become your guarantor.)
- "ჯედერის პოვნა" (Find a GeDer) button — primary
- "მოგვიანებით" (Later) — text button

**Screen 2: Nearby GeDers**
- Header: "ჯედერები ჩემს უბანში" (GeDers in My Precinct)
- Toggle: map view / list view
- **Map view:** Pins for each available GeDer in precinct
- **List view:** Cards for each GeDer:
  - Name
  - Available slots: "X თავისუფალი ადგილი X-დან" (X available slots out of X)
  - Group membership (if any)
  - "მოთხოვნის გაგზავნა" (Send Request) button per card
- Empty state: "ამ უბანში ხელმისაწვდომი ჯედერი ვერ მოიძებნა" (No available GeDers found in this precinct)

**Screen 3: Request Sent**
- Checkmark animation
- "მოთხოვნა გაგზავნილია!" (Request Sent!)
- "დაელოდეთ ჯედერის თანხმობას — შეტყობინებას მიიღებთ" (Wait for GeDer's approval — you'll receive a notification)
- "კარგი" (OK) button → returns to previous screen

### 3.8 Endorsing a Supporter (GeDer Flow)

```
[Endorsement Hub] → [Select Supporter] → [Responsibility Warning] → [Endorsement Complete]
```

**Screen 1: Endorsement Hub (Community Tab > Endorsement segment)**
- Quota card at top:
  - Visual progress bar: "4/10 გამოყენებული" (4/10 used)
  - "6 თავისუფალი ადგილი" (6 available slots)
- If suspended: red warning banner: "ენდორსმენტის უფლება შეჩერებულია — [reason]" (Endorsement right suspended)
- "ახალი ენდორსმენტი" (New Endorsement) button — disabled if quota full or suspended
- Section: "ჩემი ენდორსმენტები" (My Endorsements)
  - List of endorsed supporters with status (active / revoked), date
  - Swipe-to-reveal on each: "გაუქმება" (Revoke)

**Screen 2: Select Supporter**
- Header: "ახალი ენდორსმენტი" (New Endorsement)
- Search input: "მოძებნეთ სახელით ან ტელეფონით" (Search by name or phone)
- Or: "მომლოდინე მოთხოვნები" (Pending Requests) section — list of supporters who requested endorsement
- Each result card: name, registration date, "არჩევა" (Select) button

**Screen 3: Endorsement Confirmation (Modal)**
- Warning icon (triangle with exclamation)
- Header: "ყურადღება!" (Attention!)
- Text: "თქვენ ხდებით [Name]-ის თავდები. თუ ეს ადამიანი აღმოჩნდება ფეიკი ან მავნე, თქვენ დაკარგავთ ენდორსმენტის უფლებას და დაჯარიმდებით." (You are becoming [Name]'s guarantor. If this person turns out to be fake or harmful, you will lose endorsement rights and be penalized.)
- Checkbox: "ვიღებ პასუხისმგებლობას" (I accept responsibility) — must be checked
- "დადასტურება" (Confirm) — primary, disabled until checkbox checked
- "გაუქმება" (Cancel) — text button

**Screen 4: Endorsement Complete**
- Green checkmark animation
- "ენდორსმენტი შესრულებულია!" (Endorsement Completed!)
- "[Name] ახლა არის თავდებით დადასტურებული მხარდამჭერი" ([Name] is now an endorsed supporter)
- Updated quota: "5/10 გამოყენებული" (5/10 used)
- "კარგი" (OK) button

### 3.9 Voting in Atistavi Election

```
[Election Banner on Home] → [Election Detail] → [Vote Confirmation] → [Vote Cast]
```

**Screen 1: Election Banner (Home Dashboard)**
- Prominent card with election icon:
  - "მიმდინარე არჩევნები" (Active Election)
  - Election type: "ათისთავის არჩევნები" (Atistavi Election)
  - Group name
  - Countdown: "ხმის მიცემა სრულდება 2 დღეში" (Voting ends in 2 days)
  - "ხმის მიცემა" (Vote) button

**Screen 2: Election Detail**
- Header: election type badge + position name
- Phase timeline (horizontal 3-dot stepper):
  - "ნომინაცია" (Nomination) — with start/end dates
  - "კენჭისყრა" (Voting) — highlighted as active, with dates
  - "შედეგები" (Results) — with date
- Candidate cards (vertical list):
  - Each card: name, avatar (initials), "აქტიური წევრი" (Active Member) badge
  - Statement text (truncated with "ვრცლად" / Read more)
  - "ხმის მიცემა" (Vote) button — green, per candidate
- If user already voted: all vote buttons replaced with "თქვენ უკვე მისცემით ხმა" (You already voted) indicator; voted candidate highlighted with checkmark

**Screen 3: Vote Confirmation (Modal)**
- Ballot box icon
- "ნამდვილად გსურთ ხმის მიცემა?" (Are you sure you want to vote?)
- Candidate name displayed prominently
- Warning text: "ხმის მიცემა საბოლოოა და შეცვლა შეუძლებელია" (Your vote is final and cannot be changed)
- "ხმის მიცემა" (Cast Vote) — primary button
- "გაუქმება" (Cancel) — text button

**Screen 4: Vote Cast**
- Checkmark animation + subtle haptic feedback
- "ხმა მიცემულია!" (Vote Cast!)
- "მადლობა მონაწილეობისთვის" (Thank you for participating)
- "შედეგების ნახვა" (View Results) button — navigates back to Election Detail with voted state

### 3.10 Running as Candidate

```
[Election Detail (Nomination Phase)] → [Candidacy Registration] → [Candidacy Confirmed]
```

**Screen 1: Election Detail (Nomination Phase)**
- Same as Election Detail but during nomination phase
- Bottom action: "კანდიდატად წარდგომა" (Run as Candidate) — primary button
  - Visible only to Active Members in the relevant group
  - Hidden for Passive Members with tooltip: "მხოლოდ აქტიურ წევრებს შეუძლიათ კანდიდატად წარდგომა" (Only active members can run as candidates)

**Screen 2: Candidacy Registration**
- Header: "კანდიდატად წარდგომა" (Run as Candidate)
- Position info (read-only): election type, group name
- "თქვენი განცხადება" (Your Statement) — multi-line text input
  - Placeholder: "რატომ უნდა აგირჩიონ?" (Why should they elect you?)
  - Character counter: "0/500"
- Preview card showing how the statement will appear to voters
- "წარდგომა" (Submit) — primary button

**Screen 3: Candidacy Confirmed**
- Checkmark animation
- "თქვენ წარდგენილი ხართ კანდიდატად!" (You are registered as a candidate!)
- "კენჭისყრა დაიწყება: [date]" (Voting starts: [date])
- Share card: "გააზიარეთ თქვენი კანდიდატურა" (Share your candidacy)
- "კარგი" (OK) button → returns to Election Detail

### 3.11 SOS Crisis Report Submission

```
[SOS Tab] → [Moral Filter] → [Report Details] → [Report Submitted]
```

**Screen 1: SOS Tab Landing**
- Large SOS button: 80px diameter, red (#C62828), white shield icon, subtle pulsing animation (scale 1.0 → 1.02, 2-second loop)
- Below SOS button: section "ჩემი შეტყობინებები" (My Reports)
  - List of past reports with status badges (color-coded)
  - Each card: title, status, escalation level icon, time ago
- If user is a leader: segmented control "ჩემი" (Mine) | "მინიჭებული" (Assigned)

**Screen 2: Moral Filter (Bottom Sheet)**
- Slides up from bottom
- Header: "გთხოვთ, უპასუხეთ კითხვას" (Please answer the question)
- Question text: "ხართ თუ არა პატიოსანი, მშრომელი ადამიანი, რომელიც გახდა უსამართლობის მსხვერპლი?" (Are you an honest, hardworking person who has become a victim of injustice?)
- Multi-line text input for answer
- "გაგრძელება" (Continue) button — disabled until answer provided
- Purpose: creates psychological friction to prevent frivolous reports

**Screen 3: Report Details**
- Header: "SOS შეტყობინება" (SOS Report)
- "სათაური" (Title) — text input
- "აღწერა" (Description) — multi-line text input
- "ადგილმდებარეობა" (Location) — auto-filled from GPS, editable, with map pin preview
- Future: "ფოტო/დოკუმენტი" (Photo/Document) — attachment area (placeholder for future implementation)
- "გაგზავნა" (Submit) — red primary button

**Screen 4: Report Submitted**
- Shield checkmark animation
- "შეტყობინება გაგზავნილია!" (Report Submitted!)
- "თქვენი ათისთავი მიიღებს შეტყობინებას და განიხილავს" (Your Atistavi will receive the report and review it)
- Status timeline preview: მომლოდინე (Pending) → დადასტურებული (Verified) → ესკალირებული (Escalated) → მოგვარებული (Resolved)
- "შეტყობინების ნახვა" (View Report) button → navigates to Report Detail

### 3.12 SOS Escalation (Leader View)

```
[Assigned Reports List] → [Report Detail (Leader)] → [Action Confirmation]
```

**Screen 1: Assigned Reports List**
- Header: "მინიჭებული შეტყობინებები" (Assigned Reports)
- Cards sorted by urgency (oldest first):
  - Title, reporter name, time since submission
  - Escalation level badge (10 / 50 / 100 / 1000)
  - Status badge
- Red highlight for reports pending > 12 hours
- "გადაუხედავი: X" (Unhandled: X) counter at top

**Screen 2: Report Detail (Leader View)**
- Full report content: title, description
- Moral filter answer (collapsible section): "მორალური ფილტრის პასუხი" (Moral Filter Answer)
- Reporter info card: name, role badge, group, precinct
- Status timeline (vertical stepper):
  - Each step: level (10/50/100/1000/9999), handler name, action taken, timestamp
  - Current position highlighted
- Action buttons at bottom (sticky):
  - "დადასტურება" (Verify) — green button
  - "ესკალაცია" (Escalate) — orange button
  - "უარყოფა" (Reject) — gray outline button

**Screen 3A: Verify Confirmation (Modal)**
- "ადასტურებთ ამ შეტყობინების სინამდვილეს?" (Do you confirm this report is legitimate?)
- "დადასტურება" (Confirm) / "გაუქმება" (Cancel)

**Screen 3B: Escalate Confirmation (Modal)**
- "ესკალაცია შემდეგ დონეზე" (Escalate to next level)
- Current level → Next level shown with arrow (e.g., "10 → 50")
- "შენიშვნა" (Note) — text input for escalation reason
- "ესკალაცია" (Escalate) / "გაუქმება" (Cancel)

**Screen 3C: Reject Confirmation (Modal)**
- "ნამდვილად გსურთ შეტყობინების უარყოფა?" (Are you sure you want to reject this report?)
- "მიზეზი" (Reason) — text input (required)
- "უარყოფა" (Reject) / "გაუქმება" (Cancel)

### 3.13 Creating an Initiative/Petition

```
[Initiatives List] → [Create Initiative] → [Initiative Created]
```

**Screen 1: Initiatives List (Governance Tab > Initiatives segment)**
- Header: "ინიციატივები" (Initiatives)
- Filter chips: "ყველა" (All), "ღია" (Open), "მხარდაჭერილი" (Threshold Met), "ჩემი" (Mine)
- Card list:
  - Each card: title, author name, signature progress bar "23/25", status badge, scope badge ("უბანი" / "ოლქი")
- FAB "+" button: "ახალი ინიციატივა" (New Initiative)

**Screen 2: Create Initiative**
- Header: "ახალი ინიციატივა" (New Initiative)
- "სათაური" (Title) — text input
- "აღწერა" (Description) — multi-line text input
- "მოქმედების არეალი" (Scope) — segmented control: "უბანი" (Precinct) | "ოლქი" (District)
- Territory auto-filled based on scope (read-only)
- "ხელმოწერების ზღვარი" (Signature Threshold) — numeric input, default 10
  - Helper text: "რამდენი ხელმოწერაა საჭირო?" (How many signatures are needed?)
- "შექმნა" (Create) — primary button

**Screen 3: Initiative Created**
- Lightbulb checkmark animation
- "ინიციატივა შეიქმნა!" (Initiative Created!)
- "გააზიარეთ თანამოაზრეებთან" (Share with like-minded people)
- Share card with deep link
- "გაზიარება" (Share) button → system share sheet
- "ინიციატივის ნახვა" (View Initiative) button

### 3.14 Signing an Initiative

```
[Initiative Detail] → [Sign Confirmation]
```

**Screen 1: Initiative Detail**
- Header with back button
- Author info: avatar (initials), name, date
- Scope badge: "უბანი: [Name]" or "ოლქი: [Name]"
- Title (large text)
- Description (full scrollable text)
- Signature progress card:
  - Progress bar: "23/25 ხელმოწერა" (23/25 signatures)
  - Percentage label
- Action button:
  - If not signed: "ხელმოწერა" (Sign) — primary green button
  - If already signed: "ხელმოწერის გაუქმება" (Withdraw Signature) — outline button
- Signers section: "ხელმომწერები (23)" (Signers (23)) — expandable list showing first 5
- Response section (if threshold met):
  - "პასუხი წარმომადგენლისგან:" (Response from representative:)
  - Representative name, response text, timestamp

**Screen 2: Sign Confirmation (Modal)**
- "გსურთ ხელმოწერა?" (Do you want to sign?)
- Initiative title shown
- "ხელმოწერა" (Sign) / "გაუქმება" (Cancel)
- On success: toast "ხელმოწერა დამატებულია" (Signature added), progress bar updates

### 3.15 Filing an Arbitration Case

```
[Arbitration List] → [Case Type Selection] → [Case Details] → [Case Filed]
```

**Screen 1: Arbitration List (Profile > Arbitration)**
- Segmented control: "აღძრული" (Filed by Me) | "ჩემს წინააღმდეგ" (Against Me)
- Card list:
  - Each card: case type badge, title, status badge, respondent/complainant name, date
- "ახალი საქმე" (New Case) button

**Screen 2: Case Type Selection**
- Header: "აირჩიეთ საქმის ტიპი" (Select Case Type)
- Four tappable cards:
  - "წევრთა დავა" (Member Dispute) — two people icon
  - "ენდორსმენტის გაყალბება" (Endorsement Fraud) — warning shield icon
  - "საარჩევნო გასაჩივრება" (Election Challenge) — ballot icon
  - "სხვა" (Other) — dots icon
- Each card has a short description underneath

**Screen 3: Case Details**
- Header: "საქმის აღძვრა" (File Case)
- Case type badge (read-only, from previous step)
- "მოპასუხე" (Respondent) — search input: "მოძებნეთ სახელით ან ტელეფონით" (Search by name or phone)
- "სათაური" (Title) — text input
- "აღწერა" (Description) — multi-line text input
- "მტკიცებულებები" (Evidence) — text entries (expandable list with "+" to add)
- If endorsement fraud: "დაკავშირებული ენდორსმენტი" (Related Endorsement) — dropdown selector
- "გაგზავნა" (Submit) — primary button

**Screen 4: Case Filed**
- Scales of justice animation
- "საქმე აღიძრა!" (Case Filed!)
- "თქვენი წარმომადგენელი განიხილავს საქმეს" (Your representative will review the case)
- Case status: "წარდგენილი" (Submitted)
- "კარგი" (OK) button → returns to Arbitration List

### 3.16 Viewing Gamification Progress

```
[Profile > Progress] → [Capabilities Detail]
```

**Screen 1: Territory Progress**
- Header: "პროგრესი" (Progress)
- Hero card:
  - Precinct name
  - Large circular progress indicator (animated on load)
  - Current tier badge with icon: "ათეული" (Ten) / "ორმოცდაათეული" (Fifty) / etc.
  - Members count: "43/50" with label
  - Motivational message: "თქვენს უბანს 7 წევრი აკლია ორმოცდაათეულის შესაქმნელად" (Your precinct needs 7 more members to form a fifty)
- Stats row:
  - Total GeDers count
  - Total Supporters count
  - Total Groups count
- "შესაძლებლობები" (Capabilities) button → navigates to detail

**Screen 2: Unlocked Capabilities**
- Header: "დონეები და შესაძლებლობები" (Tiers and Capabilities)
- Vertical tier timeline:
  - **Tier 10 — "ათეული" (Ten):** full color if unlocked
    - ხმის მიცემა (Voting)
    - SOS შეტყობინება (SOS Reporting)
    - ადგილობრივი არბიტრაჟი (Local Arbitration)
  - **Tier 50 — "ორმოცდაათეული" (Fifty):** full color or grayed
    - გაძლიერებული ხილვადობა (Increased Visibility)
    - არბიტრაჟი — ბაზისური (Arbitration — Basic)
    - ტელევიზიის დრო (TV Time)
  - **Tier 100 — "ასეული" (Hundred):** grayed if locked
    - ტელევიზიის დრო — გაძლიერებული (TV Time — Enhanced)
    - არბიტრაჟი — გაძლიერებული (Arbitration — Advanced)
    - ბიუჯეტის უფლება (Budget Authority)
  - **Tier 1000 — "ათასეული" (Thousand):** grayed if locked
    - სრული ბიუჯეტი (Full Budget)
    - საბჭოს წევრობა (Council Membership)
    - რეგიონალური მედია (Regional Media)
- Locked tiers show lock icon and "X წევრი აკლია" (X members needed) message

---

## 4. Screen-by-Screen Wireframe Descriptions

### 4.1 Home / Dashboard

**Purpose:** Central hub showing personalized summary and pending actions.

**Layout (top to bottom):**
1. **Status bar + Header:** "მთავარი" (Home) left-aligned, notification bell icon top-right with unread badge count
2. **User greeting card:** "გამარჯობა, [სახელი]" (Hello, [Name]), role badge (GeDer/Supporter), status badge (Active/Passive)
3. **Progress card:** Circular progress ring (animated), tier label, "X/Y წევრი" (X/Y members), motivational message. Tappable → navigates to Gamification.
4. **Active elections banner (conditional):** Shown only when active elections exist. Horizontal card: election type, countdown timer, "ხმის მიცემა" (Vote) CTA button. Hidden if no active elections.
5. **My Group card:** Group name, member count, Atistavi name. Tappable → navigates to Group Detail. Shows "იპოვეთ ათეული" (Find a Group) if user has no group.
6. **Pending actions list:** Vertically stacked action items with icons:
   - SOS reports requiring attention (leader only)
   - Pending endorsement requests
   - Unsigned initiatives in precinct
   - Upcoming election nominations
7. **Recent activity feed:** Last 5 events: new member joined, election completed, initiative threshold met, etc.

**States:**
- *Loading:* Skeleton cards with shimmer animation for all sections
- *Empty (new user, no group):* Greeting + prominent "იპოვეთ ათეული" (Find a Group) CTA, simplified dashboard
- *Error:* Inline error banner with retry, cached data shown if available
- *Populated:* Full dashboard as described

**Interactions:**
- Pull-to-refresh (entire screen)
- Tap any card → navigates to respective detail
- Notification bell → Notification Center

### 4.2 Community Tab

**Purpose:** Browse groups, manage endorsements, find GeDers.

**Layout:**
- Segmented control at top: "ათეულები" (Groups) | "ენდორსმენტი" (Endorsement)
- Content area switches based on selected segment

**Groups segment:** See Flow 3.5 Screen 1 for full description.

**Endorsement segment:** See Flow 3.8 Screen 1 for full description.

**States:**
- *Loading:* 3 skeleton cards in list
- *Empty groups:* Illustration + "ამ უბანში ჯერ არ არის ათეული" (No groups yet) + CTA to create (GeDer) or "ჯერ ათეულები არ შექმნილა" (No groups created yet) for non-GeDers
- *Empty endorsements (GeDer):* "ჯერ არავინ დადასტურებულა" (No one endorsed yet) + CTA
- *Empty endorsements (Supporter):* Status card showing endorsement status

### 4.3 Governance Tab

**Purpose:** Elections, initiatives, and hierarchy visualization.

**Layout:**
- Segmented control at top: "არჩევნები" (Elections) | "ინიციატივები" (Initiatives) | "იერარქია" (Hierarchy)

**Elections segment:**
- Sub-filter chips: "მიმდინარე" (Active), "დასრულებული" (Completed)
- Card list of elections (see Flow 3.9 Screen 2 for Election Detail)

**Initiatives segment:** See Flow 3.13 Screen 1 for full description.

**Hierarchy segment:**
- Interactive tree visualization of governance hierarchy for user's district
- Nodes represent positions (Atistavi → 50-leader → 100-leader → 1000-leader → Council)
- Each node shows: position name, holder name (or "ვაკანტური" / Vacant), member count
- Tap a node → shows position detail with holder profile
- Pinch to zoom, pan to scroll
- Legend at bottom explaining tier icons

**States:**
- *No elections:* "ამჟამად არ მიმდინარეობს არჩევნები" (No elections currently) + subtitle
- *No initiatives:* See Flow 3.13 empty state
- *Hierarchy empty:* "თქვენს ოლქში ჯერ არ არის ჩამოყალიბებული იერარქია" (No hierarchy formed in your district yet) — shows empty tree structure

### 4.4 SOS Tab

See Flow 3.11 and 3.12 for complete description.

**Additional notes:**
- SOS button should be visible and tappable within 1 second of tab switch (no loading gate)
- Report list should load below the button without blocking it
- Leader view shows both personal reports and assigned reports via segmented control

### 4.5 Profile Tab

**Purpose:** User profile, settings, secondary features.

**Layout (top to bottom):**
1. **Profile header card:**
   - Avatar circle (initials-based, colored by role: green=GeDer, blue=Supporter, gray=Unverified)
   - Full name (large text)
   - Role badge: "GeDer" (green) / "მხარდამჭერი" (Supporter, blue) / "დაუდასტურებელი" (Unverified, gray)
   - Status badge: "აქტიური" (Active, green outline) / "პასიური" (Passive, gray outline)
   - Phone (masked): "+995 *** ** 56"
   - Precinct name
   - GeD balance (if GeDer): "GeD ბალანსი: XXX"

2. **Menu items (list with icons and chevrons):**
   - "პროფილის რედაქტირება" (Edit Profile) — person-edit icon
   - "პროგრესი" (Progress) — chart icon, with current tier badge
   - "არბიტრაჟი" (Arbitration) — scales icon, with active case count badge
   - "შეტყობინებები" (Notifications) — bell icon, with unread count badge
   - "პარამეტრები" (Settings) — gear icon
   - Divider
   - "გასვლა" (Log Out) — red text, door icon, no chevron

### 4.6 Settings Screen

**Layout (grouped list):**

**Section: "ზოგადი" (General)**
- Language toggle: "ქართული" ↔ "English"

**Section: "უსაფრთხოება" (Security)**
- Biometric lock toggle: "Face ID" / "Touch ID" / "თითის ანაბეჭდი" (Fingerprint)
- "აქტიური სესიები" (Active Sessions) — chevron right → device list
- "პაროლის შეცვლა" (Change Password) — chevron right

**Section: "შეტყობინებები" (Notifications)**
- Toggle rows:
  - "არჩევნების შეტყობინებები" (Election Notifications)
  - "SOS განახლებები" (SOS Updates)
  - "ინიციატივის განახლებები" (Initiative Updates)
  - "ენდორსმენტის მოთხოვნები" (Endorsement Requests)

**Section: "ინფორმაცია" (About)**
- "მომსახურების პირობები" (Terms of Service)
- "კონფიდენციალურობის პოლიტიკა" (Privacy Policy)
- App version: "ვერსია X.Y.Z"

---

## 5. Design System

### 5.1 Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| `primary` | #1B5E20 | Girchi brand green, headers, CTAs |
| `primary-light` | #43A047 | Active states, success indicators |
| `primary-surface` | #E8F5E9 | Card backgrounds, selection highlights |
| `secondary` | #263238 | Body text, navigation chrome |
| `accent` | #FF6F00 | Warnings, escalation badges, gamification progress |
| `danger` | #C62828 | SOS button, error states, destructive actions |
| `info` | #1565C0 | Supporter badges, informational elements |
| `surface` | #FFFFFF | Card backgrounds |
| `background` | #F5F5F5 | Screen backgrounds |
| `text-primary` | #212121 | Body text |
| `text-secondary` | #757575 | Captions, metadata, timestamps |
| `divider` | #E0E0E0 | List separators, card borders |

**Dark mode adjustments:**
- Background: #121212, Surface: #1E1E1E
- Primary brightens to #66BB6A for contrast
- Text-primary: #E0E0E0, Text-secondary: #9E9E9E
- Maintain badge and status colors with slight vibrancy increase

### 5.2 Typography

Georgian script (Mkhedruli) requires specific font selection. Georgian characters are taller and wider than Latin — use generous line heights (1.5x) and padding.

| Level | Font Family | Size | Weight | Line Height | Usage |
|-------|------------|------|--------|-------------|-------|
| H1 | BPG Nino Mtavruli | 28sp | Bold | 42sp | Screen titles |
| H2 | BPG Nino Mtavruli | 22sp | SemiBold | 33sp | Section headers |
| H3 | BPG Nino Mtavruli | 18sp | Medium | 27sp | Card titles |
| Body | BPG Nino Mkhedruli | 16sp | Regular | 24sp | Body text, descriptions |
| Body Small | BPG Nino Mkhedruli | 14sp | Regular | 21sp | Captions, secondary text |
| Caption | BPG Nino Mkhedruli | 12sp | Regular | 18sp | Timestamps, metadata |
| Button | BPG Nino Mkhedruli | 16sp | SemiBold | 24sp | Button labels |

**English fallback:** Inter (cross-platform) or SF Pro (iOS) / Roboto (Android).

### 5.3 Component Library

#### Cards

| Card Type | Content | Interaction |
|-----------|---------|-------------|
| `GroupCard` | Name, member progress bar (7/10), Atistavi name, Full badge | Tap → Group Detail |
| `ElectionCard` | Type badge, phase indicator, countdown, candidate count | Tap → Election Detail |
| `SOSCard` | Title, status badge (color-coded), escalation level, time ago | Tap → Report Detail |
| `InitiativeCard` | Title, signature progress bar, scope badge, status | Tap → Initiative Detail |
| `MemberCard` | Avatar (initials), name, role badge, join date | Tap → Member Profile |
| `ProgressCard` | Circular progress ring, tier label, motivational message | Tap → Gamification |
| `NotificationCard` | Type icon, title, body preview, time ago, unread dot | Tap → Deep link target |

#### Buttons

| Button Type | Style | Usage |
|-------------|-------|-------|
| `PrimaryButton` | Green (#1B5E20) filled, white text, 48dp height, 8dp radius | Main CTAs: Register, Vote, Submit |
| `SecondaryButton` | Green outlined border, green text, transparent fill | Secondary actions: Cancel, Skip |
| `DangerButton` | Red (#C62828) filled, white text | SOS submit, revoke endorsement |
| `TextButton` | No background, colored text only | Navigation links, tertiary actions |
| `SOSButton` | 80dp circle, red filled, white shield icon, pulse animation | SOS tab center button |
| `FAB` | 56dp circle, green filled, white "+" icon | Create group, create initiative |

#### Badges

| Badge Type | Variants | Size |
|------------|----------|------|
| `RoleBadge` | GeDer (green), მხარდამჭერი/Supporter (blue), დაუდასტურებელი/Unverified (gray) | 24dp pill |
| `StatusBadge` | აქტიური/Active (green outline), პასიური/Passive (gray outline) | 24dp pill |
| `TierBadge` | 10/ათეული (bronze), 50 (silver), 100 (gold), 1000 (platinum) | 28dp icon |
| `ElectionPhaseBadge` | ნომინაცია/Nomination (blue), კენჭისყრა/Voting (green), დასრულებული/Completed (gray) | 24dp pill |
| `SOSStatusBadge` | მომლოდინე/Pending (yellow), დადასტურებული/Verified (green), ესკალირებული/Escalated (orange), მოგვარებული/Resolved (blue), უარყოფილი/Rejected (gray) | 24dp pill |

#### Inputs

| Input Type | Details |
|------------|---------|
| `PhoneInput` | "+995" prefix (flag icon), numeric keyboard, 9-digit mask |
| `OTPInput` | 6 separate boxes, auto-advance on digit entry, paste from clipboard support |
| `TextArea` | Multi-line, character count, expandable, min 3 visible lines |
| `SearchInput` | Magnifying glass prefix icon, clear (X) button, 300ms debounce |
| `DropdownSelect` | Triggers bottom sheet picker (not inline dropdown — better for mobile) |

#### Navigation

| Component | Details |
|-----------|---------|
| `BottomTabBar` | 5 tabs, badge count support, haptic feedback on selection, safe area insets |
| `SegmentedControl` | 2-3 segments, pill-shaped, animated selection indicator |
| `FilterChips` | Horizontally scrollable row, single-select, active chip filled |
| `Breadcrumb` | Used in territory drill-down: "რეგიონი > ოლქი > უბანი" |

#### Feedback

| Component | Details |
|-----------|---------|
| `ConfirmationModal` | Centered card, blurred/dimmed background, title + body + 2 buttons |
| `BottomSheet` | Drag handle at top, rounded top corners, drag-to-dismiss |
| `Toast` | Appears bottom above tab bar, auto-dismiss 3 seconds, icon + text |
| `InlineBanner` | Full-width within screen, color-coded (red/amber/blue/green), icon + text + optional action |

### 5.4 Iconography

Base icon set: **Phosphor Icons** (open source, consistent weight, wide coverage).

Custom icons needed:
- GeD badge/logo (Girchi brand element)
- Georgian governance tier symbols (crown for Atistavi, graduated icons for 50/100/1000)
- SOS shield icon
- Constitution scroll
- Endorsement handshake
- Electoral ballot
- Girchi party logo (app icon and splash)

### 5.5 Motion & Animation

| Trigger | Animation | Duration | Easing |
|---------|-----------|----------|--------|
| Screen transition | Horizontal slide (push/pop) | 300ms | ease-out |
| Modal appearance | Fade in + scale 0.9→1.0 | 250ms | ease-out |
| Bottom sheet | Slide from bottom | 300ms | spring |
| Success state | Checkmark draw + confetti particles | 800ms | ease-out |
| SOS button idle | Subtle pulse (scale 1.0→1.02→1.0) | 2s | ease-in-out (loop) |
| Progress ring fill | Animated arc fill on load | 600ms | ease-out |
| Vote cast | Checkmark draw + haptic | 500ms | ease-out |
| List items appear | Staggered fade-in from bottom | 50ms delay per item | ease-out |
| Pull to refresh | Elastic overscroll | Spring physics | — |
| Tab switch | Cross-fade content | 200ms | ease-in-out |
| Skeleton shimmer | Left-to-right gradient sweep | 1.5s | linear (loop) |

All animations must respect system "Reduce Motion" / accessibility settings — when enabled, replace animations with instant state changes.

### 5.6 Accessibility

- **Touch targets:** Minimum 44x44pt (iOS) / 48x48dp (Android) for all interactive elements
- **Color contrast:** WCAG AA minimum — 4.5:1 for body text, 3:1 for large text and icons
- **Labels:** All icons paired with text labels. No icon-only buttons for critical actions.
- **Screen readers:** Meaningful `accessibilityLabel` on all interactive elements. Georgian TTS compatibility.
- **Font scaling:** Support Dynamic Type (iOS) / system font scale (Android) up to 2x without layout breaking
- **SOS button:** Accessible via VoiceOver / TalkBack, assistive touch, and keyboard navigation
- **Vote confirmation:** Double-confirmation pattern (modal + explicit button) prevents accidental votes
- **Color independence:** Never rely on color alone to convey information — always pair with icon/text/shape

---

## 6. Navigation Architecture

### 6.1 Tab Navigation Stacks

| Tab | Root Screen | Stack Depth Examples |
|-----|------------|---------------------|
| მთავარი (Home) | Dashboard | Dashboard → Notification Center |
| თემი (Community) | Groups/Endorsement | Groups List → Group Detail → Member Profile |
| | | Endorsement Hub → Nearby GeDers → GeDer Profile |
| მმართველობა (Governance) | Elections/Initiatives/Hierarchy | Elections List → Election Detail → Vote Screen |
| | | Initiatives List → Initiative Detail → Create Initiative |
| | | Hierarchy Tree (no further push) |
| SOS | SOS Landing | SOS Landing → Create Report → Report Detail |
| | | Assigned Reports → Report Detail (leader) |
| პროფილი (Profile) | Profile Overview | Edit Profile, Gamification → Capabilities, Arbitration → Case Detail → File Case, Settings → sub-screens |

### 6.2 Modal vs Push Navigation

**Modals (blocking, require decision):**
- Vote confirmation
- Endorsement confirmation (with responsibility checkbox)
- Endorsement revocation confirmation
- Leave group confirmation
- SOS report submission confirmation
- Session expired alert

**Push navigation (content drill-down):**
- All detail screens (group, election, initiative, report, case, member)
- Notification center
- Gamification detail
- Settings sub-screens

**Bottom sheets (quick action, partial screen):**
- Filter options
- Moral filter question (SOS)
- Create group form
- Status selection (onboarding)
- Endorsement request actions

### 6.3 Deep Linking

```
girchipolicy://home                          → Dashboard
girchipolicy://community/groups              → Groups List
girchipolicy://community/groups/{id}         → Group Detail
girchipolicy://community/endorsements        → Endorsement Hub
girchipolicy://governance/elections           → Elections List
girchipolicy://governance/elections/{id}      → Election Detail
girchipolicy://governance/initiatives         → Initiatives List
girchipolicy://governance/initiatives/{id}    → Initiative Detail
girchipolicy://governance/hierarchy           → Hierarchy View
girchipolicy://sos                           → SOS Tab
girchipolicy://sos/reports/{id}              → Report Detail
girchipolicy://profile                       → Profile
girchipolicy://profile/gamification          → Progress View
girchipolicy://profile/arbitration           → Arbitration Cases
girchipolicy://profile/arbitration/{id}      → Case Detail
girchipolicy://profile/settings              → Settings
girchipolicy://profile/notifications         → Notification Center
```

**Universal Links (HTTPS):** `https://policy.girchi.com/` with matching paths for web fallback.

---

## 7. Notification Strategy

### 7.1 Push Notification Types

| Type | Trigger | Title (KA) | Body Template (KA) | Deep Link |
|------|---------|-----------|-------------------|-----------|
| `election_started` | Election → voting phase | "კენჭისყრა დაიწყო" | "[Group] ათეულში მიმდინარეობს არჩევნები" | `/governance/elections/{id}` |
| `election_ending` | 24h before voting_end | "არჩევნები სრულდება" | "ხვალ სრულდება კენჭისყრა [Group]-ში" | `/governance/elections/{id}` |
| `election_result` | Election completed | "არჩევნების შედეგი" | "[Name] აირჩიეს ათისთავად" | `/governance/elections/{id}` |
| `endorsement_received` | Supporter endorsed | "ენდორსმენტი მიღებულია" | "[GeDer] გახდა თქვენი თავდები" | `/community/endorsements` |
| `endorsement_request` | Request received | "ენდორსმენტის მოთხოვნა" | "[Name] ითხოვს თავდებობას" | `/community/endorsements` |
| `endorsement_revoked` | Endorsement revoked | "ენდორსმენტი გაუქმდა" | "თქვენი თავდებობა გაუქმებულია" | `/profile` |
| `sos_assigned` | Report assigned to leader | "SOS შეტყობინება" | "ახალი SOS თქვენს ათეულში" | `/sos/reports/{id}` |
| `sos_verified` | Report verified | "SOS დადასტურებულია" | "თქვენი შეტყობინება დადასტურდა" | `/sos/reports/{id}` |
| `sos_escalated` | Report escalated | "SOS ესკალაცია" | "შეტყობინება გადაეცა [level]-ს" | `/sos/reports/{id}` |
| `sos_resolved` | Report resolved | "SOS მოგვარებულია" | "თქვენი შეტყობინება მოგვარდა" | `/sos/reports/{id}` |
| `initiative_threshold` | Threshold met | "ინიციატივამ მოიპოვა მხარდაჭერა" | "[Title] მიაღწია ხელმოწერების რაოდენობას" | `/governance/initiatives/{id}` |
| `initiative_response` | Representative responded | "პასუხი ინიციატივაზე" | "მიღებულია პასუხი [Title]-ზე" | `/governance/initiatives/{id}` |
| `arbitration_update` | Case status change | "არბიტრაჟის განახლება" | "თქვენი საქმის სტატუსი შეიცვალა" | `/profile/arbitration/{id}` |
| `tier_unlocked` | New tier reached | "ახალი დონე!" | "თქვენმა უბანმა მიაღწია [tier]-ს!" | `/profile/gamification` |
| `group_member_joined` | New member in group | "ახალი წევრი" | "[Name] შემოუერთდა [Group]-ს" | `/community/groups/{id}` |
| `group_member_left` | Member left group | "წევრმა დატოვა ჯგუფი" | "[Name]-მა დატოვა [Group]" | `/community/groups/{id}` |
| `position_elected` | User elected to position | "თქვენ აგირჩიეს!" | "თქვენ ხართ [Group]-ის ათისთავი" | `/governance/elections/{id}` |

### 7.2 In-App Notification Center

- Grouped by date: "დღეს" (Today), "გუშინ" (Yesterday), "ამ კვირაში" (This Week), "ძველი" (Older)
- Each notification: type icon (color-coded), title (bold if unread), body preview (1 line), timestamp
- Unread indicator: blue dot on left side
- Tap → navigates to deep link target + marks as read
- Header action: "ყველას წაკითხვა" (Mark All Read)
- Pull to refresh
- Paginated (cursor-based, 20 per page)

### 7.3 Badge Counts

| Location | Count Source |
|----------|-------------|
| Home tab | Pending actions: unhandled SOS (leader) + endorsement requests + unvoted active elections |
| Community tab | Pending endorsement requests |
| Governance tab | Active elections where user hasn't voted |
| SOS tab | Assigned unhandled reports (leaders only, 0 for non-leaders) |
| Profile tab | Unread notifications count |
| App icon (OS level) | Total unread notifications |

---

## 8. Offline & Performance Strategy

### 8.1 Local Caching

| Data | Cache Duration | Storage Method |
|------|---------------|----------------|
| User profile | Until explicit refresh | Local database (SQLite / equivalent) |
| Territory data (regions, districts, precincts) | 7 days | Local database |
| My group details + members | 5 minutes | In-memory + local database |
| Active elections list | 1 minute | In-memory |
| Gamification progress | 5 minutes | In-memory |
| Notification list | Until refresh | Local database |
| Constitution text | Indefinite (versioned) | Local database |
| JWT tokens | Per token expiry (access: 15min, refresh: 7 days) | Secure storage (Keychain / Keystore) |

### 8.2 Offline-Capable Screens

| Screen | Offline Behavior |
|--------|-----------------|
| Home Dashboard | Show cached data with "ოფლაინ" (Offline) banner and stale timestamp |
| Profile | Fully available from cache |
| My Group Detail | Cached member list with stale note |
| Constitution | Fully available |
| Territory selection (onboarding) | Cached territory tree |
| Notification Center | Cached notifications |
| Gamification progress | Cached progress data |

**Not available offline (require network):**
- Voting, endorsing, signing initiatives
- SOS submission
- Registration, login, OTP verification
- GeD verification
- Creating groups, initiatives, or cases

### 8.3 Sync Strategy

- **Optimistic UI** for non-critical actions: signing an initiative shows immediate UI update, syncs in background
- **Pessimistic UI** for critical actions: voting, endorsing — wait for server confirmation before updating UI
- **Background refresh:** On app resume from background (after 5+ minutes), refresh: user profile, notification count, active elections
- **Polling** (initial implementation): 30-second interval on election result screen, 60-second on SOS detail screen
- **WebSocket** (future): For real-time election results and SOS escalation updates

### 8.4 Loading States

Every list and detail screen has a matching skeleton loading state:
- **Cards:** Gray rounded rectangles matching card dimensions
- **Text lines:** Gray bars at 60% and 80% width
- **Avatars:** Gray circles
- **Progress bars:** Gray bar at 0%
- **Shimmer animation:** Left-to-right gradient sweep, 1.5s loop

**Blocking spinners** (centered loading indicator) only for: OTP verification, GeD verification, vote submission — actions where the user must wait for server response.

---

## 9. Onboarding & Empty States

### 9.1 First-Time User Experience

After registration, onboarding, and first entry to the main app:

**Coach marks (tooltip overlays):**
1. Points to progress card: "ეს არის თქვენი პროგრესი — აქ ხედავთ რამდენი წევრი სჭირდება თქვენს უბანს" (This is your progress — see how many members your precinct needs)
2. Points to Community tab: "იპოვეთ ან შექმენით ათეული" (Find or create a group)
3. Points to SOS tab: "SOS ღილაკი — გამოიყენეთ კრიზისის დროს" (SOS button — use during a crisis)

- Coach marks dismissible individually or all at once
- Shown once, stored in local preferences as "seen"
- Brief, non-blocking, semi-transparent overlay

**Contextual education moments:**
- First time opening Community tab: brief card explaining groups-of-10 concept
- First time viewing an election: card explaining Atistavi election process
- First time on SOS tab: card explaining moral filter and escalation chain
- All dismissible, stored as seen, never shown again

### 9.2 Empty State Designs

| Screen | Illustration | Title (KA) | Subtitle/CTA |
|--------|-------------|-----------|-------------|
| Groups List | Three people standing | "ამ უბანში ჯერ არ არის ათეული" | CTA: "შექმენით პირველი" (GeDer) / subtitle for non-GeDer |
| My Group | Puzzle piece | "თქვენ ჯერ არ ხართ არცერთ ათეულში" | CTA: "ათეულების ნახვა" (Browse Groups) |
| Elections List | Ballot box | "ამჟამად არ მიმდინარეობს არჩევნები" | "ყველა მომავალი არჩევნები აქ გამოჩნდება" |
| SOS Reports | Peace/dove symbol | "თქვენ ჯერ არ გაქვთ შეტყობინება" | (No CTA — this is a positive state) |
| Initiatives | Lightbulb | "ინიციატივები ჯერ არ არის" | CTA: "შექმენით ინიციატივა" |
| Arbitration Cases | Balanced scale | "საქმეები არ არის" | "აქ გამოჩნდება თქვენი არბიტრაჟის საქმეები" |
| Notifications | Bell | "შეტყობინებები არ არის" | "ახალი შეტყობინებები აქ გამოჩნდება" |
| Endorsements (GeDer) | Handshake | "ჯერ არავინ დადასტურებულა" | CTA: "ახალი ენდორსმენტი" |

---

## 10. Error Handling UX

### 10.1 Network Errors

**No connectivity (no cached data):**
- Full-screen state: cloud icon with X
- "ინტერნეტ კავშირი არ არის" (No Internet Connection)
- "ცადეთ ხელახლა" (Try Again) button
- Auto-retry when connectivity is restored

**No connectivity (cached data available):**
- Yellow inline banner at top: "ოფლაინ რეჟიმი — ნაჩვენებია ბოლო მონაცემები" (Offline mode — showing last data)
- Cached content shown below with stale timestamp
- Auto-refresh on reconnect

**Server error (5xx):**
- Inline error card: "დროებითი შეფერხება" (Temporary Issue)
- "სერვერი დროებით მიუწვდომელია. გთხოვთ, ცადოთ მოგვიანებით." (Server temporarily unavailable. Please try again later.)
- "ხელახლა ცდა" (Try Again) button

### 10.2 Validation Errors

- Inline field-level: red text below input, red border on field
- Scroll to first error on form submission
- All messages in Georgian:
  - Phone: "არასწორი ტელეფონის ნომერი" (Invalid phone number)
  - Personal ID: "პირადი ნომერი უნდა შეიცავდეს 11 ციფრს" (Personal ID must be 11 digits)
  - Password: "პაროლი უნდა შეიცავდეს მინიმუმ 8 სიმბოლოს" (Password must be at least 8 characters)
  - Duplicate: "ეს ნომერი უკვე რეგისტრირებულია" (This number is already registered)
  - Required field: "ეს ველი სავალდებულოა" (This field is required)

### 10.3 Session Expiry

- When access token refresh fails (refresh token expired):
  - Alert dialog: "სესია ამოიწურა" (Session Expired)
  - "გთხოვთ, თავიდან შეხვიდეთ" (Please log in again)
  - Single button: "შესვლა" (Log In)
  - Clears auth state, navigates to login
  - Preserves current deep link for post-login redirect

### 10.4 Rate Limiting

- OTP rate limit: "ძალიან ბევრი მოთხოვნა. ცადეთ [X] წუთში" (Too many requests. Try in [X] minutes) — with visible countdown
- General API: toast notification: "ძალიან ხშირი მოთხოვნა" (Too frequent requests) — brief, auto-dismiss

### 10.5 Permission Errors

Permission errors include actionable guidance, not dead-end messages:
- Non-GeDer creating group → bottom sheet: explanation of what GeD is + "გაიარეთ ვერიფიკაცია" (Get verified) CTA
- Unverified user voting → bottom sheet: endorsement path explanation + "ჯედერის პოვნა" (Find a GeDer) CTA
- Passive member running for office → bottom sheet: explain active status requirement + "პროფილის შეცვლა" (Edit Profile) CTA
- Diaspora user in local governance → info dialog: "დიასპორის წევრები არ მონაწილეობენ ადგილობრივ მმართველობაში" (Diaspora members don't participate in local governance)

---

## 11. Localization

### 11.1 Language Support

- **Primary:** Georgian (ka-GE)
- **Secondary:** English (en-US)
- **Default:** Follows device language (Georgian if device is Georgian, English otherwise)
- **Selection points:** Welcome screen (pre-registration) + Settings (post-registration)

### 11.2 Georgian-Specific Considerations

- Georgian script (Mkhedruli) is **left-to-right** — same layout direction as English. No RTL support needed.
- Georgian text is **~30-40% longer** than equivalent English. All layouts must use flexible containers, proper text truncation (ellipsis), and avoid fixed-width labels.
- Georgian **has no uppercase/lowercase** distinction. Do not rely on case for emphasis — use font weight and size instead.
- Georgian names: **[First Name] [Last Name]** pattern — same as Western convention.
- Personal ID ("პირადი ნომერი"): always **11 digits**, no letters.

### 11.3 Date/Time Formatting

| Context | Georgian (ka-GE) | English (en-US) |
|---------|-----------------|-----------------|
| Full date | 11 თებერვალი, 2026 | February 11, 2026 |
| Short date | 11.02.2026 | 02/11/2026 |
| Time | 14:30 | 2:30 PM |
| Relative | 2 საათის წინ | 2 hours ago |
| Countdown | 2 დღე, 4 საათი | 2 days, 4 hours |

All server dates are UTC. Display in user's local timezone.

### 11.4 String Management

- All user-facing strings in localization files (JSON / ARB format)
- No hardcoded text in code
- Placeholder support: "თქვენს უბანს {count} წევრი აკლია" (Your precinct needs {count} more members)
- ICU message format for pluralization (Georgian has complex plural rules)
- String keys follow dot notation: `community.groups.empty_title`, `sos.moral_filter.question`

---

## 12. Security UX

### 12.1 Biometric Authentication

- Optional — configured in Settings > Security
- Supported: Face ID (iOS), Touch ID (iOS), Fingerprint (Android), Face Unlock (Android)
- Behavior: biometric prompt on app open (cold start and resume after 5+ minutes in background)
- Fallback: app password (not device PIN)
- Implementation: biometric unlocks stored JWT refresh token from secure storage

### 12.2 Session Management

**Settings > Security > Active Sessions ("აქტიური სესიები"):**
- List of devices:
  - Device name (from platform/model)
  - Last active timestamp
  - Current device labeled: "ეს მოწყობილობა" (This Device)
  - "წაშლა" (Remove) button per other session
- "ყველა სესიის გაუქმება" (Revoke All Sessions) button — requires password confirmation

### 12.3 Sensitive Action Protections

**Double-confirmation required:**
- Casting a vote (modal confirmation)
- Endorsing a supporter (modal + responsibility checkbox)
- Revoking an endorsement (modal confirmation)
- Filing an arbitration case (modal confirmation)
- SOS submission (moral filter acts as friction gate)
- Changing password (current password required)
- Revoking all sessions (password required)

**Screenshot prevention:**
- Vote screens: prevent screenshots (FLAG_SECURE on Android, screenshot detection on iOS)
- App switcher: show blurred preview, not actual screen content

**Data privacy:**
- Personal ID displayed masked everywhere: "***********" except self-profile edit
- Phone number masked: "+995 *** ** 56"
- OTP clipboard auto-cleared after paste

---

## 13. API Endpoint Mapping

| Screen | Primary API Call | Secondary Calls |
|--------|-----------------|-----------------|
| Registration | `POST /auth/register/` | `POST /verification/device/fingerprint/` |
| OTP Verification | `POST /verification/sms/send-otp/` | `POST /verification/sms/verify-otp/` |
| Login | `POST /auth/token/` | |
| Token Refresh | `POST /auth/token/refresh/` | |
| GeD Verification | `POST /verification/ged/verify/` | `GET /verification/ged/status/` |
| Onboarding | `POST /auth/me/onboarding/` | |
| Dashboard | `GET /auth/me/` | `GET /gamification/progress/`, `GET /governance/elections/?status=voting` |
| Territory Selection | `GET /territories/regions/` | `GET /territories/regions/{id}/districts/`, `GET /territories/districts/{id}/precincts/` |
| Nearby Precincts | `GET /territories/precincts/nearby/?lat=&lng=` | |
| Groups List | `GET /communities/groups/?precinct_id=` | |
| Group Detail | `GET /communities/groups/{id}/` | |
| Join Group | `POST /communities/groups/{id}/join/` | |
| Leave Group | `POST /communities/groups/{id}/leave/` | |
| Create Group | `POST /communities/groups/` | |
| Endorsement Hub | `GET /communities/endorsements/` | `GET /communities/endorsements/quota/` |
| Endorse Supporter | `POST /communities/endorsements/` | |
| Revoke Endorsement | `DELETE /communities/endorsements/{id}/` | |
| Nearby GeDers | `GET /communities/nearby-geders/?precinct_id=` | |
| Elections List | `GET /governance/elections/` | |
| Election Detail | `GET /governance/elections/{id}/` | `GET /governance/elections/{id}/results/` |
| Vote | `POST /governance/elections/{id}/vote/` | |
| Nominate | `POST /governance/elections/{id}/nominate/` | |
| Create Election | `POST /governance/elections/` | |
| Positions List | `GET /governance/positions/` | |
| Hierarchy Tree | `GET /governance/hierarchy/?district_id=` | |
| Initiatives List | `GET /initiatives/` | |
| Initiative Detail | `GET /initiatives/{id}/` | |
| Sign Initiative | `POST /initiatives/{id}/sign/` | |
| Withdraw Signature | `DELETE /initiatives/{id}/sign/` | |
| Create Initiative | `POST /initiatives/` | |
| Respond to Initiative | `POST /initiatives/{id}/respond/` | |
| SOS Landing | `GET /sos/reports/` | |
| Create SOS Report | `POST /sos/reports/` | |
| SOS Report Detail | `GET /sos/reports/{id}/` | |
| Verify SOS Report | `POST /sos/reports/{id}/verify/` | |
| Escalate SOS Report | `POST /sos/reports/{id}/escalate/` | |
| Resolve SOS Report | `POST /sos/reports/{id}/resolve/` | |
| Reject SOS Report | `POST /sos/reports/{id}/reject/` | |
| Arbitration Cases | `GET /arbitration/cases/` | |
| File Case | `POST /arbitration/cases/` | |
| Case Decision | `POST /arbitration/cases/{id}/decide/` | |
| Case Appeal | `POST /arbitration/cases/{id}/appeal/` | |
| Gamification Progress | `GET /gamification/progress/` | `GET /gamification/capabilities/unlocked/` |
| Arbitration Case Detail | `GET /arbitration/cases/{id}/` | |
| Notification Center | `GET /notifications/` | |
| Profile | `GET /auth/me/` | |
| Edit Profile | `PATCH /auth/me/` | |
| Change Password | `PATCH /auth/me/password/` | |
| Active Sessions | `GET /auth/sessions/` | `DELETE /auth/sessions/{id}/` |

---

## Appendix A: Backend API Gaps

The following endpoints are required by this mobile specification but are **not yet defined** in `TECH_SPEC.md`. These should be added to the backend specification before mobile development reaches these features.

| Endpoint | Purpose | Priority |
|----------|---------|----------|
| `GET /notifications/` | Paginated notification list for in-app notification center | P1 — needed for all users |
| `PATCH /notifications/{id}/read/` | Mark notification as read | P1 |
| `POST /notifications/read-all/` | Mark all notifications as read | P2 |
| `POST /notifications/device-token/` | Register FCM/APNs push notification token | P1 — needed for push notifications |
| `GET /arbitration/cases/{id}/` | Arbitration case detail view | P0 — standard REST, likely implied |
| `GET /governance/elections/{id}/` | Election detail with candidates | P0 — standard REST, likely implied |
| `PATCH /auth/me/password/` | Change password | P1 |
| `GET /auth/sessions/` | List active device sessions | P2 |
| `DELETE /auth/sessions/{id}/` | Revoke a specific session | P2 |
| `POST /auth/sessions/revoke-all/` | Revoke all sessions except current | P2 |

**Note:** The endorsement request workflow (supporter requests endorsement from GeDer) is described in Flow 3.7 but has no explicit backend endpoint. This could be handled via push notifications + the existing `POST /communities/endorsements/` endpoint, or a dedicated request model could be added.
