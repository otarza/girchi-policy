import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { SOSButton } from '@/src/components/ui/SOSButton';
import { SegmentedControl } from '@/src/components/ui/SegmentedControl';
import { SOSCard } from '@/src/components/cards/SOSCard';
import { mockSOSReports } from '@/src/mock';
import { colors, typography, spacing } from '@/src/theme';

export default function SOSScreen() {
  const router = useRouter();
  const [segment, setSegment] = React.useState(0);

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Text style={styles.title}>SOS</Text>

      <View style={styles.buttonSection}>
        <SOSButton onPress={() => router.push('/(tabs)/sos/report-form')} />
        <Text style={styles.buttonLabel}>დააჭირეთ საგანგებო შეტყობინებისთვის</Text>
      </View>

      <View style={styles.segmentWrap}>
        <SegmentedControl
          segments={['ჩემი', 'მინიჭებული']}
          selectedIndex={segment}
          onSelect={setSegment}
        />
      </View>

      <ScrollView contentContainerStyle={styles.list} showsVerticalScrollIndicator={false}>
        <Text style={styles.sectionTitle}>ჩემი შეტყობინებები</Text>
        {mockSOSReports.map(report => (
          <SOSCard key={report.id} report={report} />
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
  title: {
    ...typography.h1,
    color: colors.textPrimary,
    paddingHorizontal: spacing.md,
    paddingTop: spacing.sm,
  },
  buttonSection: {
    alignItems: 'center',
    paddingVertical: spacing.lg,
    gap: spacing.md,
  },
  buttonLabel: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  segmentWrap: {
    paddingHorizontal: spacing.md,
    marginBottom: spacing.sm,
  },
  list: {
    padding: spacing.md,
    paddingTop: spacing.sm,
    gap: spacing.sm,
    paddingBottom: spacing.xl,
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.textPrimary,
  },
});
