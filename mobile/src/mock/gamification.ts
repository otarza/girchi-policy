export type TierKey = 'ten' | 'fifty' | 'hundred' | 'thousand';

export interface Tier {
  key: TierKey;
  label: string;
  threshold: number;
  capabilities: string[];
  unlocked: boolean;
}

export interface GamificationData {
  precinctName: string;
  currentTier: TierKey;
  currentMembers: number;
  nextTierThreshold: number;
  totalGeders: number;
  totalSupporters: number;
  totalGroups: number;
  motivationalMessage: string;
}

export const gamificationData: GamificationData = {
  precinctName: 'საბურთალო #12',
  currentTier: 'ten',
  currentMembers: 43,
  nextTierThreshold: 50,
  totalGeders: 28,
  totalSupporters: 15,
  totalGroups: 5,
  motivationalMessage: 'თქვენს უბანს 7 წევრი აკლია ორმოცდაათეულის შესაქმნელად',
};

export const tiers: Tier[] = [
  {
    key: 'ten',
    label: 'ათეული',
    threshold: 10,
    capabilities: ['ხმის მიცემა', 'SOS შეტყობინება', 'ადგილობრივი არბიტრაჟი'],
    unlocked: true,
  },
  {
    key: 'fifty',
    label: 'ორმოცდაათეული',
    threshold: 50,
    capabilities: ['გაძლიერებული ხილვადობა', 'არბიტრაჟი — ბაზისური', 'ტელევიზიის დრო'],
    unlocked: false,
  },
  {
    key: 'hundred',
    label: 'ასეული',
    threshold: 100,
    capabilities: ['ტელევიზიის დრო — გაძლიერებული', 'არბიტრაჟი — გაძლიერებული', 'ბიუჯეტის უფლება'],
    unlocked: false,
  },
  {
    key: 'thousand',
    label: 'ათასეული',
    threshold: 1000,
    capabilities: ['სრული ბიუჯეტი', 'საბჭოს წევრობა', 'რეგიონალური მედია'],
    unlocked: false,
  },
];
