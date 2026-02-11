import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Card } from '@/src/components/ui/Card';
import { RoleBadge, StatusBadge } from '@/src/components/ui/Badge';
import { ProgressCard } from '@/src/components/cards/ProgressCard';
import { PendingActionCard } from '@/src/components/cards/PendingActionCard';
import { useApp } from '@/src/context/AppContext';
import { gamificationData, mockElections, mockGroups } from '@/src/mock';
import { colors, typography, spacing } from '@/src/theme';

export default function HomeScreen() {
  const { user } = useApp();
  const router = useRouter();
  const activeElection = mockElections.find(e => e.phase === 'voting');
  const myGroup = mockGroups.find(g => g.id === user.groupId);

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView contentContainerStyle={styles.scroll} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.headerRow}>
          <Text style={styles.headerTitle}>მთავარი</Text>
          <Ionicons name="notifications-outline" size={24} color={colors.textPrimary} />
        </View>

        {/* Greeting */}
        <Card style={styles.greeting}>
          <Text style={styles.greetingText}>გამარჯობა, {user.firstName}!</Text>
          <View style={styles.badges}>
            <RoleBadge role={user.role} />
            <StatusBadge status={user.status} />
          </View>
        </Card>

        {/* Progress */}
        <ProgressCard
          data={gamificationData}
          onPress={() => router.push('/(tabs)/profile/progress')}
        />

        {/* Active Election Banner */}
        {activeElection && (
          <Card
            onPress={() => router.push(`/(tabs)/governance/election/${activeElection.id}`)}
            style={styles.electionBanner}
          >
            <View style={styles.electionRow}>
              <View style={styles.electionInfo}>
                <Text style={styles.electionLabel}>მიმდინარე არჩევნები</Text>
                <Text style={styles.electionType}>{activeElection.typeLabel}</Text>
                <Text style={styles.electionGroup}>{activeElection.groupName}</Text>
                <Text style={styles.countdown}>
                  ხმის მიცემა სრულდება {activeElection.daysLeft} დღეში
                </Text>
              </View>
              <Ionicons name="checkbox-outline" size={36} color={colors.primary} />
            </View>
          </Card>
        )}

        {/* My Group */}
        {myGroup && (
          <Card onPress={() => router.push(`/(tabs)/community/${myGroup.id}`)}>
            <View style={styles.groupRow}>
              <View>
                <Text style={styles.sectionLabel}>ჩემი ათეული</Text>
                <Text style={styles.groupName}>{myGroup.name}</Text>
                <Text style={styles.groupMeta}>
                  {myGroup.memberCount}/{myGroup.maxMembers} წევრი
                </Text>
              </View>
              <Ionicons name="chevron-forward" size={20} color={colors.textSecondary} />
            </View>
          </Card>
        )}

        {/* Pending Actions */}
        <Text style={styles.sectionHeader}>მომლოდინე მოქმედებები</Text>
        <Card>
          <PendingActionCard
            icon="shield"
            iconColor={colors.danger}
            title="SOS: სამეზობლო კონფლიქტი"
            subtitle="1 საათის წინ"
          />
          <PendingActionCard
            icon="hand-right"
            iconColor={colors.info}
            title="ენდორსმენტის მოთხოვნა"
            subtitle="დავით მამულაშვილი"
          />
          <PendingActionCard
            icon="document-text"
            iconColor={colors.accent}
            title="ხელმოუწერელი ინიციატივა"
            subtitle="საბურთალოს პარკის განახლება"
          />
        </Card>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  scroll: {
    padding: spacing.md,
    gap: spacing.md,
    paddingBottom: spacing.xl,
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerTitle: {
    ...typography.h1,
    color: colors.textPrimary,
  },
  greeting: {
    gap: spacing.sm,
  },
  greetingText: {
    ...typography.h2,
    color: colors.textPrimary,
  },
  badges: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  electionBanner: {
    borderLeftWidth: 3,
    borderLeftColor: colors.primary,
  },
  electionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  electionInfo: {
    flex: 1,
    gap: 2,
  },
  electionLabel: {
    ...typography.caption,
    color: colors.primary,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  electionType: {
    ...typography.h3,
    color: colors.textPrimary,
  },
  electionGroup: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  countdown: {
    ...typography.caption,
    color: colors.accent,
    fontWeight: '600',
    marginTop: spacing.xs,
  },
  groupRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  sectionLabel: {
    ...typography.caption,
    color: colors.textSecondary,
    fontWeight: '600',
    marginBottom: 2,
  },
  groupName: {
    ...typography.h3,
    color: colors.textPrimary,
  },
  groupMeta: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
  },
  sectionHeader: {
    ...typography.h3,
    color: colors.textPrimary,
    marginTop: spacing.sm,
  },
});
