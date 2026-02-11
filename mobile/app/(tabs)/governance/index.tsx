import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { SegmentedControl } from '@/src/components/ui/SegmentedControl';
import { FilterChips } from '@/src/components/ui/FilterChips';
import { ElectionCard } from '@/src/components/cards/ElectionCard';
import { InitiativeCard } from '@/src/components/cards/InitiativeCard';
import { mockElections, mockInitiatives } from '@/src/mock';
import { colors, typography, spacing } from '@/src/theme';

const electionFilters = ['მიმდინარე', 'დასრულებული'];
const initiativeFilters = ['ყველა', 'ღია', 'მხარდაჭერილი'];

export default function GovernanceScreen() {
  const router = useRouter();
  const [segment, setSegment] = useState(0);
  const [electionFilter, setElectionFilter] = useState(0);
  const [initiativeFilter, setInitiativeFilter] = useState(0);

  const filteredElections = electionFilter === 0
    ? mockElections.filter(e => e.phase !== 'completed')
    : mockElections.filter(e => e.phase === 'completed');

  const filteredInitiatives = initiativeFilter === 1
    ? mockInitiatives.filter(i => i.status === 'open')
    : initiativeFilter === 2
    ? mockInitiatives.filter(i => i.status === 'threshold_met' || i.status === 'responded')
    : mockInitiatives;

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Text style={styles.title}>მმართველობა</Text>
      <View style={styles.segmentWrap}>
        <SegmentedControl
          segments={['არჩევნები', 'ინიციატივები']}
          selectedIndex={segment}
          onSelect={setSegment}
        />
      </View>

      {segment === 0 ? (
        <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
          <FilterChips chips={electionFilters} selectedIndex={electionFilter} onSelect={setElectionFilter} />
          {filteredElections.length === 0 ? (
            <Text style={styles.empty}>ამჟამად არ მიმდინარეობს არჩევნები</Text>
          ) : (
            filteredElections.map(e => (
              <ElectionCard
                key={e.id}
                election={e}
                onPress={() => router.push(`/(tabs)/governance/election/${e.id}`)}
              />
            ))
          )}
        </ScrollView>
      ) : (
        <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
          <FilterChips chips={initiativeFilters} selectedIndex={initiativeFilter} onSelect={setInitiativeFilter} />
          {filteredInitiatives.map(i => (
            <InitiativeCard key={i.id} initiative={i} />
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
  empty: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.xxl,
  },
});
