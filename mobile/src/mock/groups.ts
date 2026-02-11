export interface Member {
  id: string;
  firstName: string;
  lastName: string;
  role: 'geder' | 'supporter';
  joinDate: string;
}

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

export const mockGroups: Group[] = [
  {
    id: 'g1',
    name: 'ათეული #1 — საბურთალო',
    precinctName: 'საბურთალო #12',
    memberCount: 8,
    maxMembers: 10,
    atistaviName: 'გიორგი ბერიძე',
    createdAt: '2026-01-15',
    isOpen: true,
    members: [
      { id: 'm1', firstName: 'გიორგი', lastName: 'ბერიძე', role: 'geder', joinDate: '2026-01-15' },
      { id: 'm2', firstName: 'ნინო', lastName: 'კვარაცხელია', role: 'geder', joinDate: '2026-01-16' },
      { id: 'm3', firstName: 'დავით', lastName: 'მამულაშვილი', role: 'supporter', joinDate: '2026-01-17' },
      { id: 'm4', firstName: 'მარიამ', lastName: 'ჯანელიძე', role: 'geder', joinDate: '2026-01-18' },
      { id: 'm5', firstName: 'ლევან', lastName: 'გოგიჩაიშვილი', role: 'supporter', joinDate: '2026-01-20' },
      { id: 'm6', firstName: 'თამარ', lastName: 'წერეთელი', role: 'geder', joinDate: '2026-01-22' },
      { id: 'm7', firstName: 'ზურა', lastName: 'ხარაბაძე', role: 'supporter', joinDate: '2026-01-25' },
      { id: 'm8', firstName: 'ანა', lastName: 'მეტრეველი', role: 'geder', joinDate: '2026-02-01' },
    ],
  },
  {
    id: 'g2',
    name: 'ათეული #2 — საბურთალო',
    precinctName: 'საბურთალო #12',
    memberCount: 10,
    maxMembers: 10,
    atistaviName: 'ელენე ნოზაძე',
    createdAt: '2026-01-10',
    isOpen: false,
    members: [
      { id: 'm9', firstName: 'ელენე', lastName: 'ნოზაძე', role: 'geder', joinDate: '2026-01-10' },
      { id: 'm10', firstName: 'გია', lastName: 'ბაქრაძე', role: 'geder', joinDate: '2026-01-10' },
    ],
  },
  {
    id: 'g3',
    name: 'ათეული #3 — საბურთალო',
    precinctName: 'საბურთალო #12',
    memberCount: 5,
    maxMembers: 10,
    atistaviName: null,
    createdAt: '2026-02-01',
    isOpen: true,
    members: [
      { id: 'm11', firstName: 'ბექა', lastName: 'ლომიძე', role: 'geder', joinDate: '2026-02-01' },
      { id: 'm12', firstName: 'სოფო', lastName: 'გელაშვილი', role: 'supporter', joinDate: '2026-02-02' },
    ],
  },
  {
    id: 'g4',
    name: 'ათეული #4 — საბურთალო',
    precinctName: 'საბურთალო #12',
    memberCount: 3,
    maxMembers: 10,
    atistaviName: null,
    createdAt: '2026-02-05',
    isOpen: true,
    members: [
      { id: 'm13', firstName: 'ირაკლი', lastName: 'ჩხეიძე', role: 'geder', joinDate: '2026-02-05' },
    ],
  },
];
