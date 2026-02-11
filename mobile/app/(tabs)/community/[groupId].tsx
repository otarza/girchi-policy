import React from 'react';
import { View, Text, StyleSheet, ScrollView, FlatList } from 'react-native';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Card } from '@/src/components/ui/Card';
import { ProgressBar } from '@/src/components/ui/ProgressBar';
import { MemberCard } from '@/src/components/cards/MemberCard';
import { mockGroups } from '@/src/mock';
import { colors, typography, spacing } from '@/src/theme';

export default function GroupDetailScreen() {
  const { groupId } = useLocalSearchParams<{ groupId: string }>();
  const router = useRouter();
  const group = mockGroups.find(g => g.id === groupId) ?? mockGroups[0];

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Stack.Screen options={{ headerShown: false }} />

      {/* Header */}
      <View style={styles.header}>
        <Ionicons name="arrow-back" size={24} color={colors.textPrimary} onPress={() => router.back()} />
        <Text style={styles.headerTitle} numberOfLines={1}>{group.name}</Text>
      </View>

      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {/* Info */}
        <Card>
          <Text style={styles.infoLabel}>{group.precinctName}</Text>
          <Text style={styles.infoDate}>შექმნილია: {group.createdAt}</Text>
          <View style={styles.progressRow}>
            <ProgressBar current={group.memberCount} total={group.maxMembers} />
          </View>
        </Card>

        {/* Atistavi */}
        <Card style={group.atistaviName ? styles.atistaviCard : undefined}>
          <View style={styles.atistaviRow}>
            <Ionicons name="ribbon" size={20} color={colors.accent} />
            <Text style={styles.atistaviLabel}>ათისთავი:</Text>
            <Text style={styles.atistaviName}>
              {group.atistaviName ?? 'ჯერ არ არჩეულა'}
            </Text>
          </View>
        </Card>

        {/* Members */}
        <Text style={styles.sectionTitle}>წევრები ({group.members.length})</Text>
        {group.members.map(member => (
          <MemberCard key={member.id} member={member} />
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
    flex: 1,
  },
  content: {
    padding: spacing.md,
    gap: spacing.md,
    paddingBottom: spacing.xl,
  },
  infoLabel: {
    ...typography.bodySmall,
    color: colors.textSecondary,
  },
  infoDate: {
    ...typography.caption,
    color: colors.textSecondary,
    marginTop: 2,
    marginBottom: spacing.sm,
  },
  progressRow: {
    marginTop: spacing.xs,
  },
  atistaviCard: {
    backgroundColor: colors.primarySurface,
  },
  atistaviRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  atistaviLabel: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    fontWeight: '600',
  },
  atistaviName: {
    ...typography.body,
    color: colors.textPrimary,
    fontWeight: '600',
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.textPrimary,
  },
});
