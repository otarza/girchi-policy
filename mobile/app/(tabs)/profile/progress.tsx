import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useRouter, Stack } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Card } from '@/src/components/ui/Card';
import { ProgressRing } from '@/src/components/ui/ProgressRing';
import { TierBadge } from '@/src/components/ui/Badge';
import { gamificationData, tiers } from '@/src/mock';
import { colors, typography, spacing, borderRadius } from '@/src/theme';

export default function ProgressScreen() {
  const router = useRouter();
  const data = gamificationData;
  const progress = data.currentMembers / data.nextTierThreshold;

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Stack.Screen options={{ headerShown: false }} />

      <View style={styles.header}>
        <Ionicons name="arrow-back" size={24} color={colors.textPrimary} onPress={() => router.back()} />
        <Text style={styles.headerTitle}>პროგრესი</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {/* Hero Card */}
        <Card style={styles.heroCard}>
          <Text style={styles.precinctName}>{data.precinctName}</Text>
          <View style={styles.heroCenter}>
            <ProgressRing
              progress={progress}
              size={120}
              strokeWidth={10}
              label={`${data.currentMembers}`}
            />
          </View>
          <TierBadge tier={data.currentTier} />
          <Text style={styles.membersLabel}>{data.currentMembers}/{data.nextTierThreshold} წევრი</Text>
          <Text style={styles.motivational}>{data.motivationalMessage}</Text>

          {/* Stats Row */}
          <View style={styles.statsRow}>
            <View style={styles.stat}>
              <Text style={styles.statValue}>{data.totalGeders}</Text>
              <Text style={styles.statLabel}>GeDer</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statValue}>{data.totalSupporters}</Text>
              <Text style={styles.statLabel}>მხარდამჭერი</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statValue}>{data.totalGroups}</Text>
              <Text style={styles.statLabel}>ათეული</Text>
            </View>
          </View>
        </Card>

        {/* Tier Timeline */}
        <Text style={styles.sectionTitle}>დონეები და შესაძლებლობები</Text>
        {tiers.map((tier, i) => (
          <Card
            key={tier.key}
            style={[styles.tierCard, !tier.unlocked ? styles.tierLocked : undefined]}
          >
            <View style={styles.tierHeader}>
              <View style={styles.tierLabelRow}>
                {tier.unlocked ? (
                  <Ionicons name="checkmark-circle" size={20} color={colors.primaryLight} />
                ) : (
                  <Ionicons name="lock-closed" size={20} color={colors.unverifiedGray} />
                )}
                <Text style={[styles.tierLabel, !tier.unlocked && styles.tierLabelLocked]}>
                  {tier.label}
                </Text>
              </View>
              <Text style={styles.tierThreshold}>{tier.threshold}+</Text>
            </View>
            <View style={styles.capabilities}>
              {tier.capabilities.map((cap, j) => (
                <View key={j} style={styles.capRow}>
                  <Ionicons
                    name={tier.unlocked ? 'checkmark' : 'remove'}
                    size={14}
                    color={tier.unlocked ? colors.primaryLight : colors.unverifiedGray}
                  />
                  <Text style={[styles.capText, !tier.unlocked && styles.capTextLocked]}>
                    {cap}
                  </Text>
                </View>
              ))}
            </View>
            {!tier.unlocked && (
              <Text style={styles.neededText}>
                {tier.threshold - data.currentMembers} წევრი აკლია
              </Text>
            )}
          </Card>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  headerTitle: {
    ...typography.h2,
    color: colors.textPrimary,
  },
  content: {
    padding: spacing.md,
    gap: spacing.md,
    paddingBottom: spacing.xl,
  },
  heroCard: {
    alignItems: 'center',
    gap: spacing.sm,
    backgroundColor: colors.primarySurface,
  },
  precinctName: {
    ...typography.h3,
    color: colors.textPrimary,
  },
  heroCenter: {
    paddingVertical: spacing.md,
  },
  membersLabel: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: '600',
  },
  motivational: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    marginTop: spacing.sm,
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.divider,
  },
  stat: {
    alignItems: 'center',
  },
  statValue: {
    ...typography.h2,
    color: colors.textPrimary,
  },
  statLabel: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.textPrimary,
    marginTop: spacing.sm,
  },
  tierCard: {
    gap: spacing.sm,
  },
  tierLocked: {
    opacity: 0.6,
  },
  tierHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  tierLabelRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  tierLabel: {
    ...typography.h3,
    color: colors.textPrimary,
  },
  tierLabelLocked: {
    color: colors.textSecondary,
  },
  tierThreshold: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    fontWeight: '600',
  },
  capabilities: {
    gap: spacing.xs,
  },
  capRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  capText: {
    ...typography.bodySmall,
    color: colors.textPrimary,
  },
  capTextLocked: {
    color: colors.textSecondary,
  },
  neededText: {
    ...typography.caption,
    color: colors.accent,
    fontWeight: '600',
  },
});
