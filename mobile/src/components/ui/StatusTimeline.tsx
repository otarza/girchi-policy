import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, spacing } from '@/src/theme';

interface TimelineStep {
  label: string;
  completed: boolean;
  active: boolean;
}

interface StatusTimelineProps {
  steps: TimelineStep[];
}

export function StatusTimeline({ steps }: StatusTimelineProps) {
  return (
    <View style={styles.container}>
      {steps.map((step, i) => (
        <View key={i} style={styles.row}>
          <View style={styles.indicator}>
            <View
              style={[
                styles.dot,
                step.completed && styles.dotCompleted,
                step.active && styles.dotActive,
              ]}
            >
              {step.completed && <Ionicons name="checkmark" size={12} color={colors.white} />}
            </View>
            {i < steps.length - 1 && (
              <View style={[styles.line, step.completed && styles.lineCompleted]} />
            )}
          </View>
          <Text
            style={[
              styles.label,
              step.completed && styles.labelCompleted,
              step.active && styles.labelActive,
            ]}
          >
            {step.label}
          </Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    paddingLeft: spacing.xs,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  indicator: {
    alignItems: 'center',
    width: 24,
    marginRight: spacing.sm,
  },
  dot: {
    width: 20,
    height: 20,
    borderRadius: 10,
    borderWidth: 2,
    borderColor: colors.divider,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
  },
  dotCompleted: {
    backgroundColor: colors.primaryLight,
    borderColor: colors.primaryLight,
  },
  dotActive: {
    borderColor: colors.primary,
    borderWidth: 3,
  },
  line: {
    width: 2,
    height: 28,
    backgroundColor: colors.divider,
  },
  lineCompleted: {
    backgroundColor: colors.primaryLight,
  },
  label: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    paddingTop: 1,
    paddingBottom: spacing.md,
  },
  labelCompleted: {
    color: colors.textPrimary,
  },
  labelActive: {
    color: colors.primary,
    fontWeight: '600',
  },
});
