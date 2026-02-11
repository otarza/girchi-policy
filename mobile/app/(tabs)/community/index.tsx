import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { SegmentedControl } from '@/src/components/ui/SegmentedControl';
import { FilterChips } from '@/src/components/ui/FilterChips';
import { ProgressBar } from '@/src/components/ui/ProgressBar';
import { Card } from '@/src/components/ui/Card';
import { GroupCard } from '@/src/components/cards/GroupCard';
import { mockGroups, mockEndorsements, endorsementQuota } from '@/src/mock';
import { colors, typography, spacing } from '@/src/theme';

const groupFilters = ['ყველა', 'თავისუფალი', 'ჩემი'];

export default function CommunityScreen() {
  const router = useRouter();
  const [segment, setSegment] = useState(0);
  const [groupFilter, setGroupFilter] = useState(0);

  const filteredGroups = groupFilter === 1
    ? mockGroups.filter(g => g.isOpen && g.memberCount < g.maxMembers)
    : groupFilter === 2
    ? mockGroups.filter(g => g.id === 'g1')
    : mockGroups;

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Text style={styles.title}>თემი</Text>
      <View style={styles.segmentWrap}>
        <SegmentedControl
          segments={['ათეულები', 'ენდორსმენტი']}
          selectedIndex={segment}
          onSelect={setSegment}
        />
      </View>

      {segment === 0 ? (
        <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
          <FilterChips chips={groupFilters} selectedIndex={groupFilter} onSelect={setGroupFilter} />
          <Text style={styles.subtitle}>საბურთალო #12</Text>
          {filteredGroups.map(group => (
            <GroupCard
              key={group.id}
              group={group}
              onPress={() => router.push(`/(tabs)/community/${group.id}`)}
            />
          ))}
        </ScrollView>
      ) : (
        <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
          {/* Quota Card */}
          <Card style={styles.quotaCard}>
            <Text style={styles.quotaTitle}>ენდორსმენტის კვოტა</Text>
            <ProgressBar current={endorsementQuota.used} total={endorsementQuota.total} />
            <Text style={styles.quotaAvailable}>
              {endorsementQuota.available} თავისუფალი ადგილი
            </Text>
          </Card>

          {/* Endorsement List */}
          <Text style={styles.sectionTitle}>ჩემი ენდორსმენტები</Text>
          {mockEndorsements.map(e => (
            <Card key={e.id} style={styles.endorsementCard}>
              <View style={styles.endorsementRow}>
                <View>
                  <Text style={styles.endorsementName}>{e.supporterName}</Text>
                  <Text style={styles.endorsementDate}>{e.date}</Text>
                </View>
                <View style={[
                  styles.statusPill,
                  { backgroundColor: e.status === 'active' ? colors.primarySurface : '#FFF3E0' },
                ]}>
                  <Text style={[
                    styles.statusText,
                    { color: e.status === 'active' ? colors.primary : colors.accent },
                  ]}>
                    {e.status === 'active' ? 'აქტიური' : 'გაუქმებული'}
                  </Text>
                </View>
              </View>
            </Card>
          ))}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  title: {
    ...typography.h1,
    color: colors.textPrimary,
    paddingHorizontal: spacing.md,
    paddingTop: spacing.sm,
  },
  segmentWrap: {
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.md,
  },
  content: {
    padding: spacing.md,
    paddingTop: 0,
    gap: spacing.sm,
    paddingBottom: spacing.xl,
  },
  subtitle: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  quotaCard: {
    gap: spacing.sm,
  },
  quotaTitle: {
    ...typography.h3,
    color: colors.textPrimary,
  },
  quotaAvailable: {
    ...typography.bodySmall,
    color: colors.primaryLight,
    fontWeight: '600',
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.textPrimary,
    marginTop: spacing.sm,
  },
  endorsementCard: {
    marginBottom: 0,
  },
  endorsementRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  endorsementName: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: '500',
  },
  endorsementDate: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  statusPill: {
    paddingHorizontal: spacing.sm,
    paddingVertical: 2,
    borderRadius: 9999,
  },
  statusText: {
    ...typography.caption,
    fontWeight: '600',
  },
});
