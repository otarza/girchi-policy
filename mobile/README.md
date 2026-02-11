# Girchi Digital Policy — Mobile App

Expo prototype for the Girchi decentralized political governance platform. Georgian-language clickable demo with 16 screens, mock data, and working navigation.

## Stack

- Expo SDK 54 + TypeScript
- Expo Router v4 (file-based navigation)
- react-native-svg, react-native-reanimated
- @expo/vector-icons (Ionicons)

## Quick Start

```bash
cd mobile
npm install
npx expo start
```

Scan the QR code with **Expo Go** (iOS/Android).

## Screens

### Auth
Welcome → Phone (+995 input) → OTP (any 6 digits verifies)

### Onboarding
GeD Check → Status Selection (Passive/Active) → Territory (Region > District > Precinct) → Complete

### Main App (5 tabs)

| Tab | Screens |
|-----|---------|
| მთავარი (Home) | Dashboard with progress card, election banner, group summary, pending actions |
| თემი (Community) | Groups list + filter chips, Group detail with members, Endorsement hub with quota |
| მმართველობა (Governance) | Elections list, Election detail with vote modal, Initiatives with signature progress |
| SOS | Pulsing SOS button, Report form with moral filter, Submission success with status timeline |
| პროფილი (Profile) | Profile card with badges, Menu, Gamification progress with tier timeline |

## Project Structure

```
mobile/
  app/                    # Expo Router screens
    (auth)/               # Welcome, Phone, OTP
    (onboarding)/         # GeD Check, Status, Territory, Complete
    (tabs)/               # 5-tab main app
      community/          # Groups list, Group detail
      governance/         # Elections, Election detail, Initiatives
      sos/                # SOS landing, Report form
      profile/            # Profile, Gamification progress
  src/
    theme/                # Design tokens (colors, typography, spacing)
    components/
      ui/                 # 13 reusable components
      cards/              # 7 domain card components
    mock/                 # Georgian mock data (users, groups, elections, etc.)
    context/              # AppContext (auth state)
```

## Notes

- **Prototype only** — no backend connection, all data is hardcoded mock
- **Georgian text** — all UI strings in Georgian (ქართული), renders via system fonts
- **Auth flow** — `AppContext` toggles `isAuthenticated`/`isOnboarded` booleans
- **OTP** — any 6 digits triggers a 1-second spinner then advances

See `MOBILE_SPEC.md` for the full 47-screen design specification and `MOBILE_BACKLOG.md` for the production roadmap.
