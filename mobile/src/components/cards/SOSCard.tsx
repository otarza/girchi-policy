import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Card } from '@/src/components/ui/Card';
import { SOSStatusBadge } from '@/src/components/ui/Badge';
import { colors, typography, spacing } from '@/src/theme';
import type { SOSReport } from '@/src/mock';

interface SOSCardProps {
  report: SOSReport;
  onPress?: () => void;
}

export function SOSCard({ report, onPress }: SOSCardProps) {
  return (
    <Card onPress={onPress} style={styles.card}>
      <View style={styles.header}>
        <Text style={styles.title} numberOfLines={1}>{report.title}</Text>
        <SOSStatusBadge status={report.status} />
      </View>
      <View style={styles.footer}>
        <Text style={styles.level}>L{report.escalationLevel}</Text>
        <Text style={styles.time}>{report.timeAgo}</Text>
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
    gap: spacing.sm,
  },
  title: {
    ...typography.h3,
    color: colors.textPrimary,
    flex: 1,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: spacing.sm,
  },
  level: {
    ...typography.caption,
    color: colors.accent,
    fontWeight: '700',
  },
  time: {
    ...typography.caption,
    color: colors.textSecondary,
  },
});
