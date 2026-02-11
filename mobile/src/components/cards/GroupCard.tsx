import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { Card } from '@/src/components/ui/Card';
import { ProgressBar } from '@/src/components/ui/ProgressBar';
import { colors, typography, spacing } from '@/src/theme';
import type { Group } from '@/src/mock';

interface GroupCardProps {
  group: Group;
  onPress: () => void;
}

export function GroupCard({ group, onPress }: GroupCardProps) {
  const isFull = group.memberCount >= group.maxMembers;

  return (
    <Card
      onPress={onPress}
      style={[styles.card, group.isOpen && !isFull ? styles.openBorder : undefined]}
    >
      <View style={styles.header}>
        <Text style={styles.name} numberOfLines={1}>{group.name}</Text>
        {isFull && (
          <View style={styles.fullBadge}>
            <Text style={styles.fullText}>სრულია</Text>
          </View>
        )}
      </View>
      <ProgressBar current={group.memberCount} total={group.maxMembers} />
      {group.atistaviName && (
        <View style={styles.atistavi}>
          <Ionicons name="ribbon" size={14} color={colors.accent} />
          <Text style={styles.atistaviText}>{group.atistaviName}</Text>
        </View>
      )}
    </Card>
  );
}

const styles = StyleSheet.create({
  card: {
    marginBottom: spacing.sm,
  },
  openBorder: {
    borderLeftWidth: 3,
    borderLeftColor: colors.primaryLight,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.sm,
  },
  name: {
    ...typography.h3,
    color: colors.textPrimary,
    flex: 1,
  },
  fullBadge: {
    backgroundColor: '#FFEBEE',
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: 9999,
  },
  fullText: {
    ...typography.caption,
    color: colors.danger,
    fontWeight: '600',
  },
  atistavi: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    marginTop: spacing.sm,
  },
  atistaviText: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
});
