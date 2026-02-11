import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Card } from '@/src/components/ui/Card';
import { ProgressBar } from '@/src/components/ui/ProgressBar';
import { colors, typography, spacing } from '@/src/theme';
import type { Initiative } from '@/src/mock';

interface InitiativeCardProps {
  initiative: Initiative;
  onPress?: () => void;
}

export function InitiativeCard({ initiative, onPress }: InitiativeCardProps) {
  const isThresholdMet = initiative.status === 'threshold_met' || initiative.status === 'responded';

  return (
    <Card onPress={onPress} style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.title} numberOfLines={2}>{initiative.title}</Text>
        <View style={[styles.scopeBadge]}>
          <Text style={styles.scopeText}>
            {initiative.scope === 'precinct' ? 'უბანი' : 'ოლქი'}
          </Text>
        </View>
      </View>
      <Text style={styles.author}>{initiative.authorName}</Text>
      <View style={styles.progress}>
        <ProgressBar
          current={initiative.signatureCount}
          total={initiative.signatureThreshold}
          color={isThresholdMet ? colors.primaryLight : colors.accent}
        />
      </View>
      <Text style={styles.signatures}>
        {initiative.signatureCount}/{initiative.signatureThreshold} ხელმოწერა
      </Text>
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
    alignItems: 'flex-start',
    gap: spacing.sm,
  },
  title: {
    ...typography.h3,
    color: colors.textPrimary,
    flex: 1,
  },
  scopeBadge: {
    backgroundColor: colors.primarySurface,
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: 9999,
  },
  scopeText: {
    ...typography.caption,
    color: colors.primary,
    fontWeight: '600',
  },
  author: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
  progress: {
    marginTop: spacing.sm,
  },
  signatures: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: spacing.xs,
  },
});
