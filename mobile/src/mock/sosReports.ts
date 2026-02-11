export type SOSStatus = 'pending' | 'verified' | 'escalated' | 'resolved' | 'rejected';

export interface SOSReport {
  id: string;
  title: string;
  description: string;
  status: SOSStatus;
  escalationLevel: 10 | 50 | 100 | 1000;
  reporterName: string;
  createdAt: string;
  timeAgo: string;
}

export const mockSOSReports: SOSReport[] = [
  {
    id: 's1',
    title: 'წყლის მილის გაფუჭება',
    description: 'ჩვენს კორპუსში უკვე 2 დღეა წყალი არ მოდის. მეზობლებს ვერ ვუკავშირდებით კომუნალურ სამსახურს.',
    status: 'verified',
    escalationLevel: 10,
    reporterName: 'ლევან გოგიჩაიშვილი',
    createdAt: '2026-02-09',
    timeAgo: '2 დღის წინ',
  },
  {
    id: 's2',
    title: 'ქუჩის განათების პრობლემა',
    description: 'პეკინის ქუჩაზე 3 ფანარი არ მუშაობს. საღამოს ძალიან ბნელა და საშიშია ფეხით მოსიარულეებისთვის.',
    status: 'escalated',
    escalationLevel: 50,
    reporterName: 'ანა მეტრეველი',
    createdAt: '2026-02-07',
    timeAgo: '4 დღის წინ',
  },
  {
    id: 's3',
    title: 'სამეზობლო კონფლიქტი',
    description: 'მეზობელი ხმაურს აწყობს ღამის 12-ის შემდეგ. უკვე რამდენჯერმე ვცადე საუბარი, მაგრამ უშედეგოდ.',
    status: 'pending',
    escalationLevel: 10,
    reporterName: 'მარიამ ჯანელიძე',
    createdAt: '2026-02-11',
    timeAgo: '1 საათის წინ',
  },
];
