export interface Region {
  id: string;
  name: string;
}

export interface District {
  id: string;
  name: string;
  regionId: string;
}

export interface Precinct {
  id: string;
  name: string;
  districtId: string;
  memberCount: number;
  groupCount: number;
}

export const mockRegions: Region[] = [
  { id: 'r1', name: 'თბილისი' },
  { id: 'r2', name: 'იმერეთი' },
  { id: 'r3', name: 'აჭარა' },
];

export const mockDistricts: District[] = [
  { id: 'd1', name: 'საბურთალოს ოლქი', regionId: 'r1' },
  { id: 'd2', name: 'ვაკის ოლქი', regionId: 'r1' },
  { id: 'd3', name: 'ისანი-სამგორის ოლქი', regionId: 'r1' },
  { id: 'd4', name: 'ქუთაისის ოლქი', regionId: 'r2' },
  { id: 'd5', name: 'ზესტაფონის ოლქი', regionId: 'r2' },
  { id: 'd6', name: 'ბათუმის ოლქი', regionId: 'r3' },
  { id: 'd7', name: 'ქობულეთის ოლქი', regionId: 'r3' },
];

export const mockPrecincts: Precinct[] = [
  { id: 'p1', name: 'საბურთალო #12', districtId: 'd1', memberCount: 43, groupCount: 5 },
  { id: 'p2', name: 'საბურთალო #15', districtId: 'd1', memberCount: 28, groupCount: 3 },
  { id: 'p3', name: 'ვაკე #3', districtId: 'd2', memberCount: 35, groupCount: 4 },
  { id: 'p4', name: 'ვაკე #7', districtId: 'd2', memberCount: 12, groupCount: 1 },
  { id: 'p5', name: 'ისანი #5', districtId: 'd3', memberCount: 20, groupCount: 2 },
  { id: 'p6', name: 'ქუთაისი #1', districtId: 'd4', memberCount: 55, groupCount: 6 },
  { id: 'p7', name: 'ქუთაისი #4', districtId: 'd4', memberCount: 18, groupCount: 2 },
  { id: 'p8', name: 'ზესტაფონი #2', districtId: 'd5', memberCount: 8, groupCount: 1 },
  { id: 'p9', name: 'ბათუმი #1', districtId: 'd6', memberCount: 40, groupCount: 4 },
  { id: 'p10', name: 'ქობულეთი #1', districtId: 'd7', memberCount: 15, groupCount: 2 },
];
