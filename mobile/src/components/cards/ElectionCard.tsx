import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Card } from '@/src/components/ui/Card';
import { ElectionPhaseBadge } from '@/src/components/ui/Badge';
import { colors, typography, spacing } from '@/src/theme';
import type { Election } from '@/src/mock';

interface ElectionCardProps {
  election: Election;
  onPress: () => void;
}

export function ElectionCard({ election, onPress }: ElectionCardProps) {
  return (
    <Card onPress={onPress} style={styles.card}>
      <View style={styles.header}>
        <ElectionPhaseBadge phase={election.phase} />
        {election.phase === 'voting' && (
          <Text style={styles.countdown}>{election.daysLeft} დღე დარჩა</Text>
        )}
      </View>
      <Text style={styles.type}>{election.typeLabel}</Text>
      <Text style={styles.group}>{election.groupName}</Text>
      <View style={styles.footer}>
        <Ionicons name="people" size={14} color={colors.textSecondary} />
        <Text style={styles.candidateCount}>{election.candidates.length} კანდიდატი</Text>
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginBottom: spacing.sm,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  countdown: {
    ...typography.caption,
    color: colors.accent,
    fontWeight: '600',
  },
  type: {
    ...typography.h3,
    color: colors.textPrimary,
  },
  group: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    marginTop: 2,
  },
  footer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    marginTop: spacing.sm,
  },
  candidateCount: {
    ...typography.caption,
    color: colors.textSecondary,
  },
});
