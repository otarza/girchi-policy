export type InitiativeStatus = 'open' | 'threshold_met' | 'responded' | 'closed';

export interface Initiative {
  id: string;
  title: string;
  description: string;
  authorName: string;
  scope: 'precinct' | 'district';
  scopeName: string;
  signatureCount: number;
  signatureThreshold: number;
  status: InitiativeStatus;
}

export const mockInitiatives: Initiative[] = [
  {
    id: 'i1',
    title: 'საბურთალოს პარკის განახლება',
    description: 'მოვითხოვოთ საბურთალოს ცენტრალური პარკის განახლება, ახალი სათამაშო მოედნისა და სავარჯიშო ზონის მოწყობა.',
    authorName: 'ნინო კვარაცხელია',
    scope: 'precinct',
    scopeName: 'საბურთალო #12',
    signatureCount: 23,
    signatureThreshold: 25,
    status: 'open',
  },
  {
    id: 'i2',
    title: 'საზოგადოებრივი ტრანსპორტის გაუმჯობესება',
    description: 'ინიციატივა საბურთალოს ოლქში ავტობუსების სიხშირის გაზრდისა და ახალი მარშრუტების დამატების შესახებ.',
    authorName: 'დავით მამულაშვილი',
    scope: 'district',
    scopeName: 'საბურთალოს ოლქი',
    signatureCount: 45,
    signatureThreshold: 40,
    status: 'threshold_met',
  },
  {
    id: 'i3',
    title: 'უბნის უსაფრთხოების გაძლიერება',
    description: 'განათების გაუმჯობესება და დამატებითი კამერების დამონტაჟება საბურთალოს ქუჩებში.',
    authorName: 'გიორგი ბერიძე',
    scope: 'precinct',
    scopeName: 'საბურთალო #12',
    signatureCount: 8,
    signatureThreshold: 15,
    status: 'open',
  },
];
