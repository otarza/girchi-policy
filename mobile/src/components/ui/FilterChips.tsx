import React from 'react';
import { ScrollView, TouchableOpacity, Text, StyleSheet } from 'react-native';
import { colors, typography, borderRadius, spacing } from '@/src/theme';

interface FilterChipsProps {
  chips: string[];
  selectedIndex: number;
  onSelect: (index: number) => void;
}

export function FilterChips({ chips, selectedIndex, onSelect }: FilterChipsProps) {
  return (
    <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.container}>
      {chips.map((label, i) => (
        <TouchableOpacity
          key={i}
          style={[styles.chip, i === selectedIndex && styles.chipActive]}
          onPress={() => onSelect(i)}
          activeOpacity={0.7}
        >
          <Text style={[styles.label, i === selectedIndex && styles.labelActive]}>
            {label}
          </Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    gap: spacing.sm,
    paddingVertical: spacing.xs,
  },
  chip: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.xs + 2,
    borderRadius: borderRadius.full,
    borderWidth: 1,
    borderColor: colors.divider,
    backgroundColor: colors.surface,
  },
  chipActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  label: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  labelActive: {
    color: colors.white,
    fontWeight: '600',
  },
});
