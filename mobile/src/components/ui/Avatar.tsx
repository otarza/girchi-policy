import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, typography } from '@/src/theme';

interface AvatarProps {
  firstName: string;
  lastName: string;
  size?: number;
  role?: 'geder' | 'supporter' | 'unverified';
}

const roleColors = {
  geder: colors.primary,
  supporter: colors.info,
  unverified: colors.unverifiedGray,
};

export function Avatar({ firstName, lastName, size = 40, role = 'geder' }: AvatarProps) {
  const initials = `${firstName.charAt(0)}${lastName.charAt(0)}`;
  const bg = roleColors[role];

  return (
    <View style={[styles.container, { width: size, height: size, borderRadius: size / 2, backgroundColor: bg }]}>
      <Text style={[styles.initials, { fontSize: size * 0.38 }]}>{initials}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  initials: {
    color: colors.white,
    fontWeight: '600',
  },
});
