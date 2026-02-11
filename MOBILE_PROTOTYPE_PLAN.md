# Girchi Digital Policy — Mobile Prototype Implementation Plan

**Purpose:** Clickable Expo prototype for stakeholder presentation. ~16 screens, mock data, Georgian text, working navigation.

---

## Project Structure

```
mobile/
  app/
    _layout.tsx              # Root: font loading, auth context, route switching
    index.tsx                # Redirect based on auth state
    (auth)/
      _layout.tsx
      welcome.tsx            # Logo, tagline, Register/Login
      phone.tsx              # +995 phone input
      otp.tsx                # 6-digit OTP (auto-verifies any input)
    (onboarding)/
      _layout.tsx
      ged-check.tsx          # "Are you a GeDer?" Yes/Skip
      status-selection.tsx   # Passive/Active cards
      territory.tsx          # Region > District > Precinct drill-down
      complete.tsx           # Success → enter main app
    (tabs)/
      _layout.tsx            # Tab bar: მთავარი, თემი, მმართველობა, SOS, პროფილი
      index.tsx              # Home Dashboard
      community/
        _layout.tsx
        index.tsx            # Groups list + Endorsement segment
        [groupId].tsx        # Group detail with members
        endorsements.tsx     # Quota card + endorsement list
      governance/
        _layout.tsx
        index.tsx            # Elections + Initiatives segments
        election/[id].tsx    # Election detail + vote modal
        initiatives.tsx      # Initiative cards with progress bars
      sos/
        _layout.tsx
        index.tsx            # Big red SOS button + reports list
        report-form.tsx      # Moral filter + report form
      profile/
        _layout.tsx
        index.tsx            # Profile card + menu
        progress.tsx         # Gamification tiers + progress ring
  src/
    context/
      AppContext.tsx          # Auth state: isAuthenticated, isOnboarded, user data
    theme/
      colors.ts
      typography.ts
      spacing.ts
      index.ts
    components/
      ui/
        Button.tsx
        Badge.tsx
        Card.tsx
        Avatar.tsx
        ProgressBar.tsx
        ProgressRing.tsx
        SegmentedControl.tsx
        FilterChips.tsx
        OTPInput.tsx
        PhoneInput.tsx
        ConfirmationModal.tsx
        SOSButton.tsx
        StatusTimeline.tsx
      cards/
        GroupCard.tsx
        ElectionCard.tsx
        InitiativeCard.tsx
        SOSCard.tsx
        ProgressCard.tsx
        MemberCard.tsx
        PendingActionCard.tsx
    mock/
      user.ts
      groups.ts
      elections.ts
      initiatives.ts
      sosReports.ts
      endorsements.ts
      territories.ts
      gamification.ts
      index.ts
```

---

## Mock Data Schemas

### user.ts
```ts
export const mockUser = {
  id: '1',
  firstName: 'გიორგი',
  lastName: 'ბერიძე',
  phone: '+995 598 12 34 56',
  phoneMasked: '+995 *** ** 56',
  personalId: '01234567890',
  role: 'geder' as const,        // 'geder' | 'supporter' | 'unverified'
  status: 'active' as const,     // 'active' | 'passive'
  gedBalance: 1250,
  precinctId: 'p1',
  precinctName: 'საბურთალო #12',
  districtName: 'საბურთალოს ოლქი',
  regionName: 'თბილისი',
  groupId: 'g1',
  isAtistavi: true,
  avatarColor: '#1B5E20',
};
```

### groups.ts
```ts
export interface Group {
  id: string;
  name: string;
  precinctName: string;
  memberCount: number;
  maxMembers: number;
  atistaviName: string | null;
  createdAt: string;
  members: Member[];
  isOpen: boolean;
}

// 3-4 mock groups with Georgian names
```

### elections.ts
```ts
export interface Election {
  id: string;
  type: 'atistavi';
  groupName: string;
  phase: 'nomination' | 'voting' | 'completed';
  candidates: Candidate[];
  votingStartDate: string;
  votingEndDate: string;
  daysLeft: number;
}

export interface Candidate {
  id: string;
  name: string;
  statement: string;
  isActive: boolean;
  voteCount?: number;
}

// 2 mock elections: one active (voting), one completed
```

### initiatives.ts
```ts
export interface Initiative {
  id: string;
  title: string;
  description: string;
  authorName: string;
  scope: 'precinct' | 'district';
  scopeName: string;
  signatureCount: number;
  signatureThreshold: number;
  status: 'open' | 'threshold_met' | 'responded' | 'closed';
}

// 3 mock initiatives
```

### sosReports.ts
```ts
export interface SOSReport {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'verified' | 'escalated' | 'resolved' | 'rejected';
  escalationLevel: 10 | 50 | 100 | 1000;
  reporterName: string;
  createdAt: string;
  timeAgo: string;
}

// 3 mock reports with different statuses
```

### endorsements.ts
```ts
export interface Endorsement {
  id: string;
  supporterName: string;
  status: 'active' | 'revoked';
  date: string;
}

export const endorsementQuota = {
  used: 4,
  total: 10,
  available: 6,
  isSuspended: false,
};

// 4 mock endorsements
```

### territories.ts
```ts
export interface Region { id: string; name: string; }
export interface District { id: string; name: string; regionId: string; }
export interface Precinct { id: string; name: string; districtId: string; memberCount: number; groupCount: number; }

// 3 regions, 2-3 districts each, 2-3 precincts each
// Regions: თბილისი, იმერეთი, აჭარა
```

### gamification.ts
```ts
export const gamificationData = {
  precinctName: 'საბურთალო #12',
  currentTier: 'ten' as const,  // 'ten' | 'fifty' | 'hundred' | 'thousand'
  currentMembers: 43,
  nextTierThreshold: 50,
  totalGeders: 28,
  totalSupporters: 15,
  totalGroups: 5,
  motivationalMessage: 'თქვენს უბანს 7 წევრი აკლია ორმოცდაათეულის შესაქმნელად',
};

export const tiers = [
  { key: 'ten', label: 'ათეული', threshold: 10, capabilities: ['ხმის მიცემა', 'SOS შეტყობინება', 'ადგილობრივი არბიტრაჟი'], unlocked: true },
  { key: 'fifty', label: 'ორმოცდაათეული', threshold: 50, capabilities: ['გაძლიერებული ხილვადობა', 'არბიტრაჟი — ბაზისური', 'ტელევიზიის დრო'], unlocked: false },
  { key: 'hundred', label: 'ასეული', threshold: 100, capabilities: ['ტელევიზიის დრო — გაძლიერებული', 'არბიტრაჟი — გაძლიერებული', 'ბიუჯეტის უფლება'], unlocked: false },
  { key: 'thousand', label: 'ათასეული', threshold: 1000, capabilities: ['სრული ბიუჯეტი', 'საბჭოს წევრობა', 'რეგიონალური მედია'], unlocked: false },
];
```

---

## Design System Tokens

### Colors
```ts
primary: '#1B5E20'
primaryLight: '#43A047'
primarySurface: '#E8F5E9'
secondary: '#263238'
accent: '#FF6F00'
danger: '#C62828'
info: '#1565C0'
surface: '#FFFFFF'
background: '#F5F5F5'
textPrimary: '#212121'
textSecondary: '#757575'
divider: '#E0E0E0'
```

### Typography (system fonts — Georgian renders natively on both platforms)
```ts
h1: { fontSize: 28, fontWeight: '700', lineHeight: 42 }
h2: { fontSize: 22, fontWeight: '600', lineHeight: 33 }
h3: { fontSize: 18, fontWeight: '500', lineHeight: 27 }
body: { fontSize: 16, fontWeight: '400', lineHeight: 24 }
bodySmall: { fontSize: 14, fontWeight: '400', lineHeight: 21 }
caption: { fontSize: 12, fontWeight: '400', lineHeight: 18 }
button: { fontSize: 16, fontWeight: '600', lineHeight: 24 }
```

### Spacing
```ts
xs: 4, sm: 8, md: 16, lg: 24, xl: 32, xxl: 48
borderRadius: { sm: 4, md: 8, lg: 16, full: 9999 }
```

---

## Component Specs

### Button (4 variants)
- **Primary:** bg=primary, text=white, height=48, borderRadius=8
- **Secondary:** bg=transparent, border=primary, text=primary
- **Danger:** bg=danger, text=white
- **Text:** no bg, colored text only

### Badge (5 types)
- **Role:** GeDer(green), მხარდამჭერი(blue), დაუდასტურებელი(gray) — pill shape
- **Status:** აქტიური(green outline), პასიური(gray outline)
- **Tier:** 10(bronze), 50(silver), 100(gold), 1000(platinum)
- **SOSStatus:** pending(yellow), verified(green), escalated(orange), resolved(blue), rejected(gray)
- **ElectionPhase:** nomination(blue), voting(green), completed(gray)

### ProgressRing
- SVG circle, radius=40, strokeWidth=8
- strokeDasharray = circumference
- strokeDashoffset = circumference * (1 - progress)
- Animated on mount

### SOSButton
- 80px diameter circle, bg=danger, white shield icon
- Animated.loop: scale 1.0 → 1.02 over 2 seconds

### OTPInput
- 6 separate TextInput boxes, auto-advance, paste support
- Any 6 digits → 1 second fake spinner → advance

### PhoneInput
- +995 prefix (non-editable), 9-digit numeric input

---

## Screen Descriptions (16 screens)

### Auth Stack (3 screens)
1. **Welcome:** Girchi logo, tagline "თავისუფალი საზოგადოების პროტოტიპი", Register + Login buttons
2. **Phone:** +995 input, Continue button (enabled at 9 digits)
3. **OTP:** 6 digit boxes, fake countdown, auto-verify any input

### Onboarding Stack (4 screens)
4. **GeD Check:** "ხართ თუ არა GeDer?" with Yes/Skip buttons
5. **Status Selection:** Passive/Active cards with descriptions
6. **Territory:** Region > District > Precinct drill-down lists
7. **Complete:** Success checkmark, "გაგრძელება" button

### Main App (9 screens across 5 tabs)
8. **Home Dashboard:** Greeting, progress card, election banner, group summary, pending actions
9. **Community - Groups:** SegmentedControl (ათეულები/ენდორსმენტი), group cards, filter chips
10. **Community - Group Detail:** Members list, Atistavi section, member cards
11. **Community - Endorsements:** Quota progress, endorsement list
12. **Governance - Elections:** Election cards, filter chips (active/completed)
13. **Governance - Election Detail:** Phase timeline, candidate cards, vote button → ConfirmationModal
14. **Governance - Initiatives:** Initiative cards with signature progress
15. **SOS Landing:** Pulsing SOS button + reports list
16. **SOS Report Form:** Moral filter question + title/description fields
17. **Profile Overview:** Avatar, name, badges, menu items (Progress, Settings, Logout)
18. **Profile - Gamification:** Progress ring, tier timeline, capabilities

---

## Key Implementation Notes

- **No backend:** All data from mock files, state managed with React Context + useState
- **Auth flow:** AppContext with `isAuthenticated` + `isOnboarded` booleans, root index.tsx redirects accordingly
- **OTP:** Any 6 digits → 1s spinner → sets isAuthenticated=true
- **Onboarding complete:** Sets isOnboarded=true → redirects to tabs
- **Vote modal:** React Native Modal, "Cast Vote" sets hasVoted=true locally
- **SOS pulse:** Animated.loop with scale interpolation
- **Progress ring:** SVG with animated strokeDashoffset
- **Fonts:** System fonts (Georgian Mkhedruli renders correctly on both iOS/Android)
- **Navigation:** Expo Router v4 file-based routing with (auth), (onboarding), (tabs) groups
