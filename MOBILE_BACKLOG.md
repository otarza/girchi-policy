# Girchi Digital Policy — Mobile App Backlog

> Priority: P0 = must have, P1 = should have, P2 = nice to have
> Status: `[ ]` = todo, `[x]` = done, `[-]` = skipped
> Estimate: S = small (1–2h), M = medium (3–5h), L = large (6–10h), XL = extra large (10+h)

> **Last updated:** 2026-02-11
> **Current state:** Prototype complete (16 screens, mock data, no backend). Ready for production build-out.
> **Backend dependency:** Backend Phase 2 in progress. Phases 3–6 not started.

---

## Overall Strategy

**Approach:** Evolve existing prototype into production app. The prototype has correct navigation structure, theme tokens, Georgian strings, and component shapes. Production adds: API layer, real auth, state management, error handling, offline support, remaining ~31 screens, and testing.

**Mobile/Backend synchronization:** Mobile phases are aligned with backend phases. Each mobile phase assumes the corresponding backend APIs exist. Where backend APIs are not yet built, mobile development uses mock data with a feature flag, then switches to real API when backend catches up.

**Screen inventory:** MOBILE_SPEC.md defines ~47 screens. Prototype has 16. Production adds ~31 more across phases.

---

## Phase 0: Production Infrastructure (Week 1)

**Goal:** Replace prototype scaffolding with production-grade architecture. No new screens — upgrade the 16 existing ones.

**Backend dependency:** None (infrastructure only).

### Sprint 0.1 — Architecture Foundation

- [ ] **MP-001** [P0] [L] API client and service layer
  - Create `src/services/api.ts` — Axios instance with baseURL, interceptors
  - Request interceptor: attach JWT from SecureStore
  - Response interceptor: handle 401 → attempt token refresh → retry, handle network errors
  - `src/services/auth.ts` — login, register, refreshToken, logout
  - `src/services/territories.ts`, `communities.ts`, `governance.ts`, `sos.ts`, `gamification.ts`
  - Each service file exports typed functions matching MOBILE_SPEC.md §13 API mapping
  - **AC:** All API calls go through typed service functions. Auth interceptor works.

- [ ] **MP-002** [P0] [M] State management setup
  - Install and configure `@tanstack/react-query` (v5)
  - Create `src/providers/QueryProvider.tsx` wrapping the app
  - Configure default staleTime (5 min), gcTime (30 min), retry (2)
  - Create `src/hooks/` directory for query hooks
  - **AC:** React Query devtools visible in dev. Queries cache and invalidate correctly.

- [ ] **MP-003** [P0] [M] Auth state with SecureStore
  - Replace `AppContext` boolean auth with real token management
  - `expo-secure-store` for JWT storage (access + refresh tokens)
  - `src/context/AuthContext.tsx` — `login()`, `logout()`, `isAuthenticated` (derived from token existence), token refresh on app resume
  - Persist onboarding state in `AsyncStorage`
  - **AC:** Tokens survive app restart. Expired tokens trigger re-login. Logout clears storage.

- [ ] **MP-004** [P0] [M] Environment configuration
  - `expo-constants` for env vars (API_URL, etc.)
  - `app.config.ts` (dynamic config) with dev/staging/prod profiles
  - `src/config.ts` exporting resolved `API_URL`, `GIRCHI_COM_URL`, etc.
  - **AC:** `npx expo start` uses dev config. Build uses prod config.

- [ ] **MP-005** [P0] [S] Mock data toggle
  - `src/services/mock/` directory mirroring real services with mock responses
  - `USE_MOCK_API` flag in config (default: true until backend is ready)
  - Service factory: `getService('auth')` returns mock or real based on flag
  - **AC:** App works identically with mock=true and mock=false (when backend is up).

### Sprint 0.2 — Component Hardening

- [ ] **MP-006** [P0] [M] Loading and error states for all components
  - Skeleton loader component: `src/components/ui/Skeleton.tsx` (shimmer animation)
  - Error boundary: `src/components/ui/ErrorBoundary.tsx`
  - Inline error banner: `src/components/ui/ErrorBanner.tsx` (retry button)
  - Empty state component: `src/components/ui/EmptyState.tsx` (icon, title, subtitle, CTA)
  - **AC:** Every list/detail screen has skeleton, error, and empty states.

- [ ] **MP-007** [P1] [M] Form infrastructure
  - Install `react-hook-form` + `zod`
  - Create reusable `FormField` wrapper: label, error display, required indicator
  - `src/lib/validations.ts` — Zod schemas: phone, personalId, password, OTP
  - Georgian error messages from MOBILE_SPEC.md §10.2
  - **AC:** All forms validate client-side with Georgian error messages.

- [ ] **MP-008** [P1] [S] Toast notification system
  - `src/components/ui/Toast.tsx` — auto-dismiss, icon + text, bottom-positioned
  - `useToast()` hook with `show(message, type)` API
  - Types: success (green), error (red), info (blue), warning (amber)
  - **AC:** Toast appears above tab bar, auto-dismisses in 3 seconds.

- [ ] **MP-009** [P1] [S] Accessibility pass on existing components
  - `accessibilityLabel` on all interactive elements
  - Minimum touch targets 44x44pt
  - Respect system font scaling (test at 2x)
  - SOS button accessible via VoiceOver/TalkBack
  - **AC:** App navigable via VoiceOver. No unlabeled interactive elements.

- [ ] **MP-010** [P2] [S] Bottom sheet component
  - `src/components/ui/BottomSheet.tsx` — drag handle, drag-to-dismiss, snap points
  - Replace modals where spec calls for bottom sheet (moral filter, create group, filters)
  - Use `@gorhom/bottom-sheet` or simple Animated implementation
  - **AC:** Bottom sheets animate correctly, dismissible by drag or backdrop tap.

---

## Phase 1: Auth & Onboarding — Production (Weeks 2–3)

**Goal:** Real registration, OTP verification, GeD check, territory assignment. Connect to backend Phase 1+2 APIs.

**Backend dependency:** Backend Phase 1 (complete) + Phase 2 (GP-020 through GP-023).

### Sprint 1.1 — Registration & Login

- [ ] **MP-011** [P0] [M] Registration flow with real API
  - Wire `phone.tsx` → `POST /auth/register/` (phone + personal ID + password)
  - Wire `otp.tsx` → `POST /verification/sms/send-otp/` then `POST /verification/sms/verify-otp/`
  - Handle rate limiting (display "ძალიან ბევრი მოთხოვნა" with countdown)
  - Handle duplicate phone ("ეს ნომერი უკვე რეგისტრირებულია")
  - **AC:** Real user created in backend. OTP sent via SMS. 6-digit verification works.

- [ ] **MP-012** [P0] [M] Personal Details screen (new)
  - `app/(auth)/personal-details.tsx`
  - Fields: სახელი, გვარი, პირადი ნომერი (11 digits), პაროლი, პაროლის გამეორება
  - Password strength indicator
  - Zod validation with Georgian messages
  - **AC:** Screen matches MOBILE_SPEC.md §3.1 Screen 4.

- [ ] **MP-013** [P0] [M] Login screen (new)
  - `app/(auth)/login.tsx`
  - Phone + password login → `POST /auth/token/`
  - "პაროლი დაგავიწყდათ?" link (placeholder for future)
  - Store JWT pair in SecureStore
  - **AC:** Existing users can log in. Tokens stored. App navigates to appropriate screen.

- [ ] **MP-014** [P0] [S] Device fingerprinting
  - Collect device info on registration: model, OS, screen size, unique ID
  - `POST /verification/device/fingerprint/` after registration
  - **AC:** Device data sent to backend. Flagged duplicates handled gracefully.

- [ ] **MP-015** [P1] [S] Registration Complete screen (new)
  - `app/(auth)/registration-complete.tsx`
  - Checkmark animation, "ანგარიში შეიქმნა!" message
  - "გაგრძელება" → navigate to onboarding
  - **AC:** Screen matches MOBILE_SPEC.md §3.1 Screen 5.

### Sprint 1.2 — Onboarding with Real APIs

- [ ] **MP-016** [P0] [L] GeD verification with girchi.com
  - Wire `ged-check.tsx` "დიახ" → WebView/browser redirect to girchi.com
  - Capture JWT callback → `POST /verification/ged/verify/`
  - Display verification result (success: GeD balance, failure: retry/skip)
  - Loading state: "girchi.com-თან დაკავშირება..."
  - **AC:** Real GeD verification flow works. User promoted to 'geder' role on success.

- [ ] **MP-017** [P0] [M] Territory selection with real data
  - Wire `territory.tsx` → `GET /territories/regions/`, `.../districts/`, `.../precincts/`
  - Add search/filter to region and district lists
  - On confirm → `PATCH /auth/me/` with `precinct_id`
  - **AC:** Territories load from backend. User assigned to precinct.

- [ ] **MP-018** [P1] [M] Location-based precinct selection (new)
  - `app/(onboarding)/territory-map.tsx`
  - Request GPS permission → `GET /territories/precincts/nearby/?lat=&lng=`
  - Map view with user dot + precinct pins (using `react-native-maps` or simple list)
  - Bottom sheet with nearby precincts sorted by distance
  - **AC:** Nearby precincts shown. User can select from map or list.

- [ ] **MP-019** [P0] [S] Onboarding submission
  - Wire `complete.tsx` → `POST /auth/me/onboarding/`
  - Send: join_reason, member_status, constitution_accepted, precinct_id, is_diaspora
  - **AC:** Onboarding data persisted. User marked as onboarded in backend.

- [ ] **MP-020** [P1] [M] Join Reason screen (new)
  - `app/(onboarding)/join-reason.tsx`
  - Multi-line text input, 10 char minimum, 500 char max with counter
  - **AC:** Screen matches MOBILE_SPEC.md §3.3 Screen 1.

- [ ] **MP-021** [P1] [M] Constitution Acceptance screen (new)
  - `app/(onboarding)/constitution.tsx`
  - Scrollable text, scroll-to-bottom detection, checkbox + confirm button
  - **AC:** Screen matches MOBILE_SPEC.md §3.3 Screen 3.

- [ ] **MP-022** [P1] [S] Diaspora Declaration screen (new)
  - `app/(onboarding)/diaspora.tsx`
  - Toggle: "დიახ, საზღვარგარეთ ვცხოვრობ"
  - Skip precinct assignment if diaspora
  - **AC:** Screen matches MOBILE_SPEC.md §3.4 Screen 3.

---

## Phase 2: Community & Endorsement (Weeks 4–6)

**Goal:** Groups, endorsement system, member management — the social core.

**Backend dependency:** Backend Phase 3 (GP-025 through GP-032).

### Sprint 2.1 — Groups

- [ ] **MP-023** [P0] [M] Groups list with real API
  - Wire community `index.tsx` groups segment → `GET /communities/groups/?precinct_id=`
  - `useQuery` hook with precinct-scoped key
  - Pull-to-refresh, skeleton loading, empty state
  - **AC:** Real groups load. Filter chips work. Empty state shown for new precincts.

- [ ] **MP-024** [P0] [M] Group detail with real API
  - Wire `[groupId].tsx` → `GET /communities/groups/{id}/`
  - Real member list with roles and join dates
  - Join button → `POST /communities/groups/{id}/join/` with confirmation modal
  - Leave button → `POST /communities/groups/{id}/leave/` with confirmation modal
  - **AC:** Join/leave works. Member list refreshes. Full group shows "სრულია" badge.

- [ ] **MP-025** [P0] [M] Create Group bottom sheet (new)
  - Triggered by FAB on groups list (GeDer only)
  - Group name input (optional, defaults to "ათეული #N")
  - Precinct auto-filled
  - `POST /communities/groups/`
  - **AC:** GeDer creates group. Non-GeDers don't see FAB. Screen matches §3.6.

- [ ] **MP-026** [P1] [S] Join Confirmation modal
  - "გსურთ გაწევრიანება?" with group name
  - Endorsement check: if supporter without endorsement, show link to Find GeDer
  - **AC:** Matches §3.5 Screen 3. Permission errors show actionable guidance.

### Sprint 2.2 — Endorsement

- [ ] **MP-027** [P0] [M] Endorsement Hub with real API
  - Wire community endorsement segment → `GET /communities/endorsements/` + `.../quota/`
  - Quota card with progress bar
  - Endorsement list with active/revoked status
  - Swipe-to-reveal "გაუქმება" (revoke) → `DELETE /communities/endorsements/{id}/`
  - Suspended banner when `is_suspended=true`
  - **AC:** Real endorsement data loads. Quota displays. Revocation works.

- [ ] **MP-028** [P0] [M] New Endorsement flow (new)
  - `app/(tabs)/community/endorse.tsx`
  - Search by name or phone
  - Pending requests section
  - Responsibility warning modal with checkbox: "ვიღებ პასუხისმგებლობას"
  - `POST /communities/endorsements/`
  - Success: updated quota display
  - **AC:** Full endorsement flow works. Matches §3.8.

- [ ] **MP-029** [P1] [M] Find a GeDer screen (new)
  - `app/(tabs)/community/find-geder.tsx`
  - Endorsement needed prompt for unverified users
  - `GET /communities/nearby-geders/?precinct_id=`
  - GeDer cards with available slots
  - "მოთხოვნის გაგზავნა" button
  - **AC:** Matches §3.7. Supporters can find and request endorsement.

- [ ] **MP-030** [P2] [L] Nearby GeDers map view (new)
  - Map integration (`react-native-maps`) showing GeDer locations
  - Toggle between map/list view
  - **AC:** Map pins render. Tap pin shows GeDer info. Optional — list view is fallback.

---

## Phase 3: Governance & Elections (Weeks 7–10)

**Goal:** Full election lifecycle, initiatives, hierarchy visualization.

**Backend dependency:** Backend Phase 4 (GP-033 through GP-043).

### Sprint 3.1 — Elections

- [ ] **MP-031** [P0] [M] Elections list with real API
  - Wire governance `index.tsx` elections segment → `GET /governance/elections/`
  - Filter: active vs completed
  - Election cards with phase badges and countdowns
  - **AC:** Real elections load with correct phase indicators.

- [ ] **MP-032** [P0] [L] Election detail with real voting
  - Wire `election/[id].tsx` → `GET /governance/elections/{id}/`
  - Phase timeline (nomination → voting → results)
  - Candidate cards with statements
  - Vote: `POST /governance/elections/{id}/vote/` with confirmation modal
  - "ხმის მიცემა საბოლოოა" warning
  - Post-vote: disable vote buttons, show checkmark on voted candidate
  - Results view: vote counts after election completes
  - **AC:** Full voting flow works. Vote is final. Results display correctly.

- [ ] **MP-033** [P0] [M] Candidacy Registration screen (new)
  - `app/(tabs)/governance/election/nominate.tsx`
  - Statement text input (500 chars)
  - Preview card showing how statement appears to voters
  - `POST /governance/elections/{id}/nominate/`
  - Visible only to Active Members during nomination phase
  - **AC:** Matches §3.10. Active members can register as candidates.

- [ ] **MP-034** [P1] [M] Election Results screen (new)
  - `app/(tabs)/governance/election/results.tsx`
  - Vote tallies per candidate
  - Winner highlighted
  - 30-second polling for live results during completion
  - **AC:** Results update in near-real-time. Winner clearly indicated.

### Sprint 3.2 — Initiatives

- [ ] **MP-035** [P0] [M] Initiatives list with real API
  - Wire governance initiatives segment → `GET /initiatives/`
  - Filter chips: ყველა, ღია, მხარდაჭერილი, ჩემი
  - Initiative cards with signature progress
  - **AC:** Real initiatives load. Filters work correctly.

- [ ] **MP-036** [P0] [M] Initiative Detail screen (new)
  - `app/(tabs)/governance/initiative/[id].tsx`
  - Full description, signature progress card
  - Sign: `POST /initiatives/{id}/sign/` → progress bar updates
  - Withdraw: `DELETE /initiatives/{id}/sign/`
  - Signers list (expandable, first 5)
  - Response section when threshold met
  - **AC:** Matches §3.14. Sign/withdraw works. Progress updates optimistically.

- [ ] **MP-037** [P1] [M] Create Initiative screen (new)
  - `app/(tabs)/governance/initiative/create.tsx`
  - Title, description, scope (precinct/district), signature threshold
  - `POST /initiatives/`
  - Share card with deep link after creation
  - **AC:** Matches §3.13. Initiative created and visible in list.

### Sprint 3.3 — Hierarchy

- [ ] **MP-038** [P1] [L] Hierarchy Tree screen (new)
  - Add "იერარქია" segment to governance tab
  - `GET /governance/hierarchy/?district_id=`
  - Interactive tree: Atistavi → 50-leader → 100-leader → 1000-leader → Council
  - Nodes show: position, holder name or "ვაკანტური", member count
  - Tap node → detail overlay
  - Pinch to zoom, pan to scroll
  - **AC:** Matches §4.3 Hierarchy segment. Tree renders correctly for user's district.

---

## Phase 4: SOS System (Weeks 11–12)

**Goal:** Real SOS reporting, leader verification, escalation chain.

**Backend dependency:** Backend Phase 5 Sprint 5.1 (GP-044 through GP-047).

### Sprint 4.1 — SOS Creation & Viewing

- [ ] **MP-039** [P0] [M] SOS landing with real API
  - Wire SOS `index.tsx` → `GET /sos/reports/` (own + assigned)
  - Segmented control: ჩემი / მინიჭებული (leader view)
  - Report cards with status badges and escalation level
  - Pulsing SOS button always visible (not gated by loading)
  - **AC:** Real reports load. Leader sees assigned tab with unhandled count.

- [ ] **MP-040** [P0] [M] SOS report creation with real API
  - Wire `report-form.tsx` moral filter → form → `POST /sos/reports/`
  - Location auto-fill from GPS (editable)
  - Future: photo/document attachment (placeholder area)
  - Submission confirmation → status timeline preview
  - **AC:** Report created in backend. Auto-assigned to atistavi.

- [ ] **MP-041** [P0] [M] SOS Report Detail screen (new)
  - `app/(tabs)/sos/[id].tsx`
  - Full report content, moral filter answer (collapsible), reporter info
  - Vertical status timeline showing escalation history
  - 60-second polling for status updates
  - **AC:** Report detail loads. Timeline shows escalation chain.

### Sprint 4.2 — Leader Actions

- [ ] **MP-042** [P0] [M] SOS leader actions (new)
  - In report detail (leader view): Verify / Escalate / Reject buttons
  - Verify → `POST /sos/reports/{id}/verify/` with confirmation modal
  - Escalate → `POST /sos/reports/{id}/escalate/` with level arrow + note
  - Reject → `POST /sos/reports/{id}/reject/` with required reason
  - Resolve → `POST /sos/reports/{id}/resolve/`
  - **AC:** All four actions work. Status updates reflected in timeline.

- [ ] **MP-043** [P1] [M] Assigned Reports list (leader view)
  - Red highlight for reports pending > 12 hours
  - "გადაუხედავი: X" counter at top
  - Sorted by urgency (oldest first)
  - **AC:** Matches §3.12 Screen 1. Urgency clearly visible.

---

## Phase 5: Profile, Gamification & Secondary Features (Weeks 13–15)

**Goal:** Full profile management, gamification, arbitration, settings, notifications.

**Backend dependency:** Backend Phase 5 Sprint 5.3 + Phase 6.

### Sprint 5.1 — Profile & Settings

- [ ] **MP-044** [P0] [M] Profile with real API
  - Wire profile `index.tsx` → `GET /auth/me/`
  - Real user data: name, masked phone, precinct, GeD balance, role, status
  - **AC:** Profile displays real user data.

- [ ] **MP-045** [P1] [M] Edit Profile screen (new)
  - `app/(tabs)/profile/edit.tsx`
  - Editable fields: first name, last name, member_status
  - `PATCH /auth/me/`
  - **AC:** Profile updates persist. Matches §4.5 menu item.

- [ ] **MP-046** [P1] [M] Settings screen (new)
  - `app/(tabs)/profile/settings.tsx`
  - Language toggle (KA/EN)
  - Biometric lock toggle (expo-local-authentication)
  - Push notification toggles
  - About section: terms, privacy, app version
  - **AC:** Matches §4.6. Toggles persist in AsyncStorage.

- [ ] **MP-047** [P1] [M] Change Password screen (new)
  - `app/(tabs)/profile/change-password.tsx`
  - Current password + new password + confirm
  - `PATCH /auth/me/password/`
  - **AC:** Password change works. Requires current password.

- [ ] **MP-048** [P2] [M] Active Sessions screen (new)
  - `app/(tabs)/profile/sessions.tsx`
  - Device list with "ეს მოწყობილობა" marker
  - Remove individual sessions, revoke all
  - `GET /auth/sessions/`, `DELETE /auth/sessions/{id}/`
  - **AC:** Matches §12.2. Sessions listed and revocable.

### Sprint 5.2 — Gamification

- [ ] **MP-049** [P0] [M] Gamification with real API
  - Wire `progress.tsx` → `GET /gamification/progress/` + `GET /gamification/capabilities/unlocked/`
  - Animated progress ring on load
  - Real tier data and member counts
  - **AC:** Gamification shows real precinct progress.

- [ ] **MP-050** [P1] [S] Tier unlock celebration
  - When a new tier is reached (detected via query comparison), show celebration modal
  - Confetti animation + tier badge + unlocked capabilities list
  - **AC:** Tier unlock feels rewarding. Only shown once per tier.

### Sprint 5.3 — Arbitration

- [ ] **MP-051** [P1] [M] Arbitration Cases list (new)
  - `app/(tabs)/profile/arbitration/index.tsx`
  - Segmented: "აღძრული" (Filed by Me) / "ჩემს წინააღმდეგ" (Against Me)
  - Case cards with type badge, status, date
  - **AC:** Matches §3.15 Screen 1.

- [ ] **MP-052** [P1] [L] File Arbitration Case flow (new)
  - `app/(tabs)/profile/arbitration/file-case.tsx`
  - Step 1: case type selection (4 cards)
  - Step 2: respondent search + title + description + evidence
  - `POST /arbitration/cases/`
  - **AC:** Matches §3.15 Screens 2-4. Case filed and visible in list.

- [ ] **MP-053** [P1] [M] Arbitration Case Detail (new)
  - `app/(tabs)/profile/arbitration/[id].tsx`
  - Full case info, status timeline, decision (if rendered)
  - Appeal button (if eligible)
  - **AC:** Case detail loads. Appeal triggers `POST /arbitration/cases/{id}/appeal/`.

### Sprint 5.4 — Notifications

- [ ] **MP-054** [P1] [M] Notification Center screen (new)
  - `app/(tabs)/profile/notifications.tsx` or accessible from home bell icon
  - Grouped by date: დღეს, გუშინ, ამ კვირაში, ძველი
  - Unread dot, tap → deep link, "ყველას წაკითხვა" header action
  - `GET /notifications/`, `PATCH /notifications/{id}/read/`
  - Paginated (cursor-based, 20 per page)
  - **AC:** Matches §7.2. Notifications load, mark-as-read works.

- [ ] **MP-055** [P1] [M] Push notification registration
  - `expo-notifications` for FCM/APNs token
  - `POST /notifications/device-token/` on login
  - Handle notification tap → navigate to deep link
  - **AC:** Push tokens registered. Tapping notification opens correct screen.

- [ ] **MP-056** [P2] [S] Badge counts on tab bar
  - Home: pending actions count
  - Community: endorsement requests
  - Governance: unvoted active elections
  - SOS: unhandled assigned reports (leaders)
  - Profile: unread notifications
  - Periodic refresh (60s) or on tab focus
  - **AC:** Badge counts match §7.3 spec.

---

## Phase 6: Offline, Performance & Polish (Weeks 16–18)

**Goal:** Offline support, performance optimization, i18n, testing, app store readiness.

**Backend dependency:** All backend phases complete.

### Sprint 6.1 — Offline & Caching

- [ ] **MP-057** [P1] [L] Offline data layer
  - SQLite via `expo-sqlite` for persistent cache
  - Cache: user profile (until refresh), territories (7 days), group details (5 min), notifications
  - Offline banner: "ოფლაინ რეჟიმი — ნაჩვენებია ბოლო მონაცემები"
  - Network state detection via `@react-native-community/netinfo`
  - **AC:** Matches §8. Cached screens work offline. Online screens show error state.

- [ ] **MP-058** [P1] [M] Optimistic UI for non-critical actions
  - Initiative signing: immediate UI update, sync in background
  - Group join: immediate member count update
  - Rollback on failure with toast error
  - **AC:** UI feels instant for non-critical actions.

- [ ] **MP-059** [P1] [M] Background refresh
  - On app resume (after 5+ min in background): refresh profile, notification count, active elections
  - Background fetch via `expo-background-fetch` (if feasible)
  - **AC:** Data refreshes automatically when returning to app.

### Sprint 6.2 — i18n & Localization

- [ ] **MP-060** [P1] [L] i18n framework
  - Install `i18next` + `react-i18next` + `expo-localization`
  - Extract all hardcoded Georgian strings to `src/i18n/ka.json` and `src/i18n/en.json`
  - ICU message format for pluralization (Georgian plural rules)
  - Date/time formatting per §11.3
  - Language toggle: follow device default, override in settings
  - **AC:** App fully functional in both KA and EN. Language switch is instant.

### Sprint 6.3 — Security UX

- [ ] **MP-061** [P1] [M] Biometric authentication
  - `expo-local-authentication` for Face ID / Touch ID / Fingerprint
  - Prompt on app open (cold start and resume after 5+ min)
  - Optional — configured in Settings
  - Fallback: app password prompt
  - **AC:** Matches §12.1. Biometric unlock protects stored JWT.

- [ ] **MP-062** [P2] [S] Screenshot prevention on sensitive screens
  - Vote screens: `FLAG_SECURE` (Android) / screenshot detection (iOS)
  - App switcher: blurred preview
  - **AC:** Matches §12.3. Vote screen cannot be screenshotted on Android.

- [ ] **MP-063** [P1] [S] Session expiry handling
  - When refresh token fails → alert: "სესია ამოიწურა"
  - Clear auth state, navigate to login
  - Preserve current deep link for post-login redirect
  - **AC:** Matches §10.3. Smooth re-login experience.

### Sprint 6.4 — Testing & Quality

- [ ] **MP-064** [P0] [XL] Unit and integration tests
  - Jest + React Native Testing Library
  - Test all hooks (query hooks, auth hooks)
  - Test all form validations
  - Test navigation flows (auth → onboarding → tabs)
  - Test critical interactions: vote, endorse, SOS submit
  - Target: 70% coverage on `src/` directory
  - **AC:** `npm test` passes. Coverage report generated. Critical flows tested.

- [ ] **MP-065** [P1] [L] E2E tests
  - Detox or Maestro for E2E testing
  - Core flows: registration → onboarding → dashboard → vote → SOS
  - Run on CI (if set up)
  - **AC:** E2E suite runs and passes for 5 core flows.

- [ ] **MP-066** [P1] [M] Performance audit
  - Profile startup time (target: < 2s to interactive)
  - Audit list performance (FlatList optimizations, memo)
  - Image optimization (if images added)
  - Bundle size analysis
  - **AC:** No jank in lists. Startup under 2s. Bundle size reasonable.

### Sprint 6.5 — App Store Preparation

- [ ] **MP-067** [P0] [M] App icons and splash screen
  - Girchi party logo as app icon (all required sizes)
  - Splash screen with logo and tagline
  - `expo-splash-screen` configuration
  - **AC:** Professional app icon and splash on both platforms.

- [ ] **MP-068** [P0] [M] EAS Build configuration
  - `eas.json` with development, preview, production profiles
  - iOS: provisioning profile and certificates
  - Android: signing keystore
  - OTA updates via `expo-updates`
  - **AC:** `eas build` produces installable builds for both platforms.

- [ ] **MP-069** [P1] [M] App store metadata
  - Screenshots (6.7" iPhone, 6.5" iPhone, Android phone)
  - Georgian + English app descriptions
  - Privacy policy URL
  - Content rating questionnaire
  - **AC:** Ready to submit to App Store and Google Play.

---

## Cross-Cutting Concerns (Ongoing)

- [ ] **MP-100** [P1] [M] Deep linking
  - Configure `girchipolicy://` scheme and `https://policy.girchi.com/` universal links
  - All routes from §6.3 mapped to app screens
  - Handle deep links when app is closed, backgrounded, or foregrounded
  - **AC:** Tapping a deep link opens correct screen in all app states.

- [ ] **MP-101** [P1] [S] Analytics integration
  - `expo-analytics` or custom events
  - Track: screen views, button taps, funnel completion (registration, onboarding, first vote)
  - **AC:** Core events tracked. Funnel visibility in dashboard.

- [ ] **MP-102** [P2] [S] Crash reporting
  - Sentry (`@sentry/react-native`) or Expo's built-in error reporting
  - Source maps uploaded on build
  - **AC:** Crashes captured with stack traces. Alerts configured.

- [ ] **MP-103** [P2] [S] Dark mode support
  - Extend theme with dark mode tokens from §5.1
  - `useColorScheme()` detection
  - Toggle in settings (system / light / dark)
  - **AC:** Dark mode matches spec color adjustments. No contrast issues.

---

## Progress Summary

| Phase | Tasks | P0 | P1 | P2 | Screens Added |
|-------|-------|----|----|----|---------------|
| Phase 0: Infrastructure | 10 | 5 | 4 | 1 | 0 (upgrade existing 16) |
| Phase 1: Auth & Onboarding | 12 | 7 | 5 | 0 | +5 (login, personal details, registration complete, join reason, constitution, diaspora) |
| Phase 2: Community | 8 | 4 | 3 | 1 | +4 (create group, endorse, find GeDer, nearby map) |
| Phase 3: Governance | 8 | 4 | 4 | 0 | +5 (nominate, results, initiative detail, create initiative, hierarchy) |
| Phase 4: SOS | 5 | 3 | 2 | 0 | +2 (report detail, assigned reports) |
| Phase 5: Profile & Secondary | 13 | 2 | 9 | 2 | +9 (edit profile, settings, password, sessions, arbitration x3, notifications, push) |
| Phase 6: Polish | 13 | 3 | 7 | 3 | 0 (infrastructure) |
| Cross-Cutting | 4 | 0 | 2 | 2 | 0 |
| **Total** | **73** | **28** | **36** | **9** | **~25 new screens** |

**Prototype screens:** 16 (reused and upgraded)
**New screens:** ~25
**Total production screens:** ~41 (of ~47 in spec — 6 deferred: Nearby Map, Hierarchy detail, Case Detail sub-views, Device management detail)

---

## Dependency Graph

```
MP-001 (API client) ← everything with real API
MP-002 (React Query) ← all query hooks
MP-003 (Auth/SecureStore) ← MP-011 (registration), MP-013 (login)
MP-005 (Mock toggle) ← allows parallel mobile/backend development

MP-011,012,013 (Auth screens) ← MP-016 (GeD), MP-017 (Territory)
MP-016,017,019 (Onboarding) ← MP-023 (Groups — needs precinct)

MP-023,024 (Groups) ← MP-025 (Create group), MP-026 (Join confirmation)
MP-027 (Endorsement hub) ← MP-028 (New endorsement), MP-029 (Find GeDer)

MP-031,032 (Elections) ← MP-033 (Candidacy), MP-034 (Results)
MP-035 (Initiatives list) ← MP-036 (Detail), MP-037 (Create)

MP-039,040 (SOS) ← MP-041 (Detail), MP-042 (Leader actions)

MP-044 (Profile) ← MP-045 (Edit), MP-046 (Settings)
MP-049 (Gamification) ← MP-050 (Tier celebration)
MP-054 (Notifications) ← MP-055 (Push), MP-056 (Badge counts)

MP-060 (i18n) — can run in parallel with any phase
MP-064 (Tests) — ongoing, but formal pass in Phase 6
```

---

## Mobile ↔ Backend Alignment

| Mobile Phase | Backend Dependency | Backend Status |
|---|---|---|
| Phase 0 | None | N/A |
| Phase 1 | Backend Phase 1 + 2 | Phase 1 complete, Phase 2 in progress |
| Phase 2 | Backend Phase 3 | Not started |
| Phase 3 | Backend Phase 4 | Not started |
| Phase 4 | Backend Phase 5.1 | Not started |
| Phase 5 | Backend Phase 5.3 + 6 | Not started |
| Phase 6 | All | Not started |

**Key insight:** Mobile Phase 0 and Phase 1 Sprint 1.1 can start immediately (backend Phase 1 APIs exist). Phase 1 Sprint 1.2 needs GP-020/021 (territory endpoints). Use mock toggle (MP-005) to unblock mobile work when backend lags.
