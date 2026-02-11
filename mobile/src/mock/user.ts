export type UserRole = 'geder' | 'supporter' | 'unverified';
export type UserStatus = 'active' | 'passive';

export interface User {
  id: string;
  firstName: string;
  lastName: string;
  phone: string;
  phoneMasked: string;
  personalId: string;
  role: UserRole;
  status: UserStatus;
  gedBalance: number;
  precinctId: string;
  precinctName: string;
  districtName: string;
  regionName: string;
  groupId: string | null;
  isAtistavi: boolean;
}

export const mockUser: User = {
  id: '1',
  firstName: 'გიორგი',
  lastName: 'ბერიძე',
  phone: '+995 598 12 34 56',
  phoneMasked: '+995 *** ** 56',
  personalId: '01234567890',
  role: 'geder',
  status: 'active',
  gedBalance: 1250,
  precinctId: 'p1',
  precinctName: 'საბურთალო #12',
  districtName: 'საბურთალოს ოლქი',
  regionName: 'თბილისი',
  groupId: 'g1',
  isAtistavi: true,
};
