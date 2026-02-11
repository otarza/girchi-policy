import React, { useState } from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { useLocalSearchParams, useRouter, Stack } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Card } from '@/src/components/ui/Card';
import { Button } from '@/src/components/ui/Button';
import { ElectionPhaseBadge, StatusBadge } from '@/src/components/ui/Badge';
import { Avatar } from '@/src/components/ui/Avatar';
import { ConfirmationModal } from '@/src/components/ui/ConfirmationModal';
import { mockElections } from '@/src/mock';
import { colors, typography, spacing, borderRadius } from '@/src/theme';

export default function ElectionDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const router = useRouter();
  const election = mockElections.find(e => e.id === id) ?? mockElections[0];
  const [hasVoted, setHasVoted] = useState(false);
  const [voteCandidate, setVoteCandidate] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedCandidateName, setSelectedCandidateName] = useState('');

  const handleVotePress = (candidateId: string, name: string) => {
    setVoteCandidate(candidateId);
    setSelectedCandidateName(name);
    setShowModal(true);
  };

  const handleConfirmVote = () => {
    setHasVoted(true);
    setShowModal(false);
  };

  const phases = [
    { label: 'ნომინაცია', active: election.phase === 'nomination', completed: election.phase !== 'nomination' },
    { label: 'კენჭისყრა', active: election.phase === 'voting', completed: election.phase === 'completed' },
    { label: 'შედეგები', active: false, completed: election.phase === 'completed' },
  ];

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Stack.Screen options={{ headerShown: false }} />

      {/* Header */}
      <View style={styles.header}>
        <Ionicons name="arrow-back" size={24} color={colors.textPrimary} onPress={() => router.back()} />
        <ElectionPhaseBadge phase={election.phase} />
      </View>

      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <Text style={styles.title}>{election.typeLabel}</Text>
        <Text style={styles.groupName}>{election.groupName}</Text>

        {/* Phase Timeline */}
        <View style={styles.timeline}>
          {phases.map((p, i) => (
            <View key={i} style={styles.phaseItem}>
              <View style={[
                styles.phaseDot,
                p.completed && styles.phaseDotCompleted,
                p.active && styles.phaseDotActive,
              ]} />
              <Text style={[
                styles.phaseLabel,
                p.active && styles.phaseLabelActive,
                p.completed && styles.phaseLabelCompleted,
              ]}>{p.label}</Text>
              {i < phases.length - 1 && (
                <View style={[styles.phaseLine, p.completed && styles.phaseLineCompleted]} />
              )}
            </View>
          ))}
        </View>

        {/* Voted indicator */}
        {hasVoted && (
          <Card style={styles.votedCard}>
            <View style={styles.votedRow}>
              <Ionicons name="checkmark-circle" size={20} color={colors.primaryLight} />
              <Text style={styles.votedText}>თქვენ უკვე მისცემით ხმა</Text>
            </View>
          </Card>
        )}

        {/* Candidates */}
        <Text style={styles.sectionTitle}>კანდიდატები</Text>
        {election.candidates.map(candidate => (
          <Card key={candidate.id} style={[
            styles.candidateCard,
            hasVoted && voteCandidate === candidate.id ? styles.votedCandidateCard : undefined,
          ]}>
            <View style={styles.candidateHeader}>
              <Avatar
                firstName={candidate.name.split(' ')[0]}
                lastName={candidate.name.split(' ')[1] || ''}
                size={44}
              />
              <View style={styles.candidateInfo}>
                <Text style={styles.candidateName}>{candidate.name}</Text>
                <Text style={styles.candidateStatus}>აქტიური წევრი</Text>
              </View>
              {hasVoted && voteCandidate === candidate.id && (
                <Ionicons name="checkmark-circle" size={24} color={colors.primaryLight} />
              )}
            </View>
            <Text style={styles.statement}>{candidate.statement}</Text>
            {election.phase === 'completed' && candidate.voteCount != null && (
              <Text style={styles.voteCount}>{candidate.voteCount} ხმა</Text>
            )}
            {election.phase === 'voting' && !hasVoted && (
              <Button
                title="ხმის მიცემა"
                onPress={() => handleVotePress(candidate.id, candidate.name)}
                style={styles.voteBtn}
              />
            )}
          </Card>
        ))}
      </ScrollView>

      <ConfirmationModal
        visible={showModal}
        title="ნამდვილად გსურთ ხმის მიცემა?"
        message={`${selectedCandidateName}\n\nხმის მიცემა საბოლოოა და შეცვლა შეუძლებელია`}
        confirmLabel="ხმის მიცემა"
        cancelLabel="გაუქმება"
        onConfirm={handleConfirmVote}
        onCancel={() => setShowModal(false)}
      />
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
    justifyContent: 'space-between',
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
  },
  content: {
    padding: spacing.md,
    gap: spacing.md,
    paddingBottom: spacing.xl,
  },
  title: {
    ...typography.h1,
    color: colors.textPrimary,
  },
  groupName: {
    ...typography.body,
    color: colors.textSecondary,
    marginTop: -spacing.sm,
  },
  timeline: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.md,
  },
  phaseItem: {
    alignItems: 'center',
    flex: 1,
    position: 'relative',
  },
  phaseDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
    backgroundColor: colors.divider,
    marginBottom: spacing.xs,
  },
  phaseDotActive: {
    backgroundColor: colors.primary,
    width: 16,
    height: 16,
    borderRadius: 8,
  },
  phaseDotCompleted: {
    backgroundColor: colors.primaryLight,
  },
  phaseLabel: {
    ...typography.caption,
    color: colors.textSecondary,
  },
  phaseLabelActive: {
    color: colors.primary,
    fontWeight: '600',
  },
  phaseLabelCompleted: {
    color: colors.textPrimary,
  },
  phaseLine: {
    position: 'absolute',
    top: 5,
    left: '60%',
    right: '-40%',
    height: 2,
    backgroundColor: colors.divider,
  },
  phaseLineCompleted: {
    backgroundColor: colors.primaryLight,
  },
  votedCard: {
    backgroundColor: colors.primarySurface,
  },
  votedRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  votedText: {
    ...typography.body,
    color: colors.primary,
    fontWeight: '600',
  },
  sectionTitle: {
    ...typography.h3,
    color: colors.textPrimary,
  },
  candidateCard: {
    gap: spacing.sm,
  },
  votedCandidateCard: {
    borderWidth: 2,
    borderColor: colors.primaryLight,
  },
  candidateHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm,
  },
  candidateInfo: {
    flex: 1,
  },
  candidateName: {
    ...typography.h3,
    color: colors.textPrimary,
  },
  candidateStatus: {
    ...typography.caption,
    color: colors.primaryLight,
  },
  statement: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    lineHeight: 22,
  },
  voteCount: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    fontWeight: '600',
  },
  voteBtn: {
    marginTop: spacing.xs,
  },
});
