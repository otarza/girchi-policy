export interface Endorsement {
  id: string;
  supporterName: string;
  status: 'active' | 'revoked';
  date: string;
}

export interface EndorsementQuota {
  used: number;
  total: number;
  available: number;
  isSuspended: boolean;
}

export const endorsementQuota: EndorsementQuota = {
  used: 4,
  total: 10,
  available: 6,
  isSuspended: false,
};

export const mockEndorsements: Endorsement[] = [
  { id: 'en1', supporterName: 'დავით მამულაშვილი', status: 'active', date: '2026-01-17' },
  { id: 'en2', supporterName: 'ლევან გოგიჩაიშვილი', status: 'active', date: '2026-01-20' },
  { id: 'en3', supporterName: 'ზურა ხარაბაძე', status: 'active', date: '2026-01-25' },
  { id: 'en4', supporterName: 'ნათია ფხაკაძე', status: 'revoked', date: '2026-01-12' },
];
