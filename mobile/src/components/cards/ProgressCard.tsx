import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Card } from '@/src/components/ui/Card';
import { ProgressRing } from '@/src/components/ui/ProgressRing';
import { TierBadge } from '@/src/components/ui/Badge';
import { colors, typography, spacing } from '@/src/theme';
import type { GamificationData } from '@/src/mock';

interface ProgressCardProps {
  data: GamificationData;
  onPress?: () => void;
}

export function ProgressCard({ data, onPress }: ProgressCardProps) {
  const progress = data.currentMembers / data.nextTierThreshold;

  return (
    <Card onPress={onPress} style={styles.card}>
      <View style={styles.row}>
        <ProgressRing
          progress={progress}
          size={80}
          strokeWidth={6}
          label={`${data.currentMembers}`}
        />
        <View style={styles.info}>
          <TierBadge tier={data.currentTier} />
          <Text style={styles.members}>
            {data.currentMembers}/{data.nextTierThreshold} წევრი
          </Text>
          <Text style={styles.message} numberOfLines={2}>
            {data.motivationalMessage}
          </Text>
        </View>
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.primarySurface,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
  },
  info: {
    flex: 1,
    gap: spacing.xs,
  },
  members: {
    ...typography.bodySmall,
    color: colors.textPrimary,
    fontWeight: '600',
  },
  message: {
    ...typography.caption,
    color: colors.textSecondary,
  },
});
