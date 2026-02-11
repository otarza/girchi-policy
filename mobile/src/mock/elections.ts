export type ElectionPhase = 'nomination' | 'voting' | 'completed';

export interface Candidate {
  id: string;
  name: string;
  statement: string;
  isActive: boolean;
  voteCount?: number;
}

export interface Election {
  id: string;
  type: 'atistavi';
  typeLabel: string;
  groupName: string;
  phase: ElectionPhase;
  candidates: Candidate[];
  votingStartDate: string;
  votingEndDate: string;
  resultsDate: string;
  daysLeft: number;
}

export const mockElections: Election[] = [
  {
    id: 'e1',
    type: 'atistavi',
    typeLabel: 'ათისთავის არჩევნები',
    groupName: 'ათეული #3 — საბურთალო',
    phase: 'voting',
    votingStartDate: '2026-02-10',
    votingEndDate: '2026-02-14',
    resultsDate: '2026-02-15',
    daysLeft: 2,
    candidates: [
      {
        id: 'c1',
        name: 'ბექა ლომიძე',
        statement: 'მინდა ჩვენი ათეული გავხადო აქტიური და ეფექტური. მაქვს გამოცდილება საზოგადოებრივ საქმიანობაში და მზად ვარ პასუხისმგებლობისთვის.',
        isActive: true,
      },
      {
        id: 'c2',
        name: 'სოფო გელაშვილი',
        statement: 'მჯერა, რომ თანამშრომლობით შეგვიძლია ბევრის მიღწევა. ჩემი მიზანია უბნის პრობლემების ეფექტურად მოგვარება.',
        isActive: true,
      },
    ],
  },
  {
    id: 'e2',
    type: 'atistavi',
    typeLabel: 'ათისთავის არჩევნები',
    groupName: 'ათეული #1 — საბურთალო',
    phase: 'completed',
    votingStartDate: '2026-01-20',
    votingEndDate: '2026-01-24',
    resultsDate: '2026-01-25',
    daysLeft: 0,
    candidates: [
      {
        id: 'c3',
        name: 'გიორგი ბერიძე',
        statement: 'აქტიური მონაწილეობა და გამჭვირვალე მმართველობა — ჩემი პრიორიტეტია.',
        isActive: true,
        voteCount: 5,
      },
      {
        id: 'c4',
        name: 'ნინო კვარაცხელია',
        statement: 'მზად ვარ ვიმუშაო ჩვენი ათეულის განვითარებისთვის.',
        isActive: true,
        voteCount: 3,
      },
    ],
  },
];
