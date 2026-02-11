import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, typography, borderRadius, spacing } from '@/src/theme';
import type { UserRole, UserStatus, SOSStatus, ElectionPhase, TierKey } from '@/src/mock';

// --- Role Badge ---
const roleConfig: Record<UserRole, { label: string; bg: string; text: string }> = {
  geder: { label: 'GeDer', bg: colors.primarySurface, text: colors.primary },
  supporter: { label: 'მხარდამჭერი', bg: '#E3F2FD', text: colors.info },
  unverified: { label: 'დაუდასტურებელი', bg: '#F5F5F5', text: colors.unverifiedGray },
};

export function RoleBadge({ role }: { role: UserRole }) {
  const c = roleConfig[role];
  return (
    <View style={[styles.pill, { backgroundColor: c.bg }]}>
      <Text style={[styles.pillText, { color: c.text }]}>{c.label}</Text>
    </View>
  );
}

// --- Status Badge ---
const statusConfig: Record<UserStatus, { label: string; color: string }> = {
  active: { label: 'აქტიური', color: colors.primaryLight },
  passive: { label: 'პასიური', color: colors.unverifiedGray },
};

export function StatusBadge({ status }: { status: UserStatus }) {
  const c = statusConfig[status];
  return (
    <View style={[styles.pill, { borderWidth: 1, borderColor: c.color, backgroundColor: 'transparent' }]}>
      <Text style={[styles.pillText, { color: c.color }]}>{c.label}</Text>
    </View>
  );
}

// --- SOS Status Badge ---
const sosConfig: Record<SOSStatus, { label: string; bg: string; text: string }> = {
  pending: { label: 'მომლოდინე', bg: '#FFF8E1', text: '#F57F17' },
  verified: { label: 'დადასტურებული', bg: colors.primarySurface, text: colors.primaryLight },
  escalated: { label: 'ესკალირებული', bg: '#FFF3E0', text: colors.accent },
  resolved: { label: 'მოგვარებული', bg: '#E3F2FD', text: colors.info },
  rejected: { label: 'უარყოფილი', bg: '#F5F5F5', text: colors.unverifiedGray },
};

export function SOSStatusBadge({ status }: { status: SOSStatus }) {
  const c = sosConfig[status];
  return (
    <View style={[styles.pill, { backgroundColor: c.bg }]}>
      <Text style={[styles.pillText, { color: c.text }]}>{c.label}</Text>
    </View>
  );
}

// --- Election Phase Badge ---
const phaseConfig: Record<ElectionPhase, { label: string; bg: string; text: string }> = {
  nomination: { label: 'ნომინაცია', bg: '#E3F2FD', text: colors.info },
  voting: { label: 'კენჭისყრა', bg: colors.primarySurface, text: colors.primary },
  completed: { label: 'დასრულებული', bg: '#F5F5F5', text: colors.unverifiedGray },
};

export function ElectionPhaseBadge({ phase }: { phase: ElectionPhase }) {
  const c = phaseConfig[phase];
  return (
    <View style={[styles.pill, { backgroundColor: c.bg }]}>
      <Text style={[styles.pillText, { color: c.text }]}>{c.label}</Text>
    </View>
  );
}

// --- Tier Badge ---
const tierConfig: Record<TierKey, { label: string; color: string }> = {
  ten: { label: 'ათეული', color: colors.tierBronze },
  fifty: { label: 'ორმოცდაათეული', color: colors.tierSilver },
  hundred: { label: 'ასეული', color: colors.tierGold },
  thousand: { label: 'ათასეული', color: colors.tierPlatinum },
};

export function TierBadge({ tier }: { tier: TierKey }) {
  const c = tierConfig[tier];
  return (
    <View style={[styles.pill, { backgroundColor: c.color + '22', borderWidth: 1, borderColor: c.color }]}>
      <Text style={[styles.pillText, { color: c.color }]}>{c.label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  pill: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: borderRadius.full,
    alignSelf: 'flex-start',
  },
  pillText: {
    ...typography.caption,
    fontWeight: '600',
  },
});
