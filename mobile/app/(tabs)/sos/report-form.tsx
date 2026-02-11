import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, ScrollView, KeyboardAvoidingView, Platform } from 'react-native';
import { useRouter, Stack } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Button } from '@/src/components/ui/Button';
import { Card } from '@/src/components/ui/Card';
import { StatusTimeline } from '@/src/components/ui/StatusTimeline';
import { colors, typography, spacing, borderRadius } from '@/src/theme';

type Step = 'moral-filter' | 'form' | 'submitted';

export default function ReportFormScreen() {
  const router = useRouter();
  const [step, setStep] = useState<Step>('moral-filter');
  const [moralAnswer, setMoralAnswer] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  if (step === 'submitted') {
    return (
      <SafeAreaView style={styles.container} edges={['top']}>
        <Stack.Screen options={{ headerShown: false }} />
        <View style={styles.successCenter}>
          <View style={styles.successIcon}>
            <Ionicons name="shield-checkmark" size={48} color={colors.white} />
          </View>
          <Text style={styles.successTitle}>შეტყობინება გაგზავნილია!</Text>
          <Text style={styles.successSubtitle}>
            თქვენი ათისთავი მიიღებს შეტყობინებას და განიხილავს
          </Text>

          <StatusTimeline
            steps={[
              { label: 'მომლოდინე', completed: false, active: true },
              { label: 'დადასტურებული', completed: false, active: false },
              { label: 'ესკალირებული', completed: false, active: false },
              { label: 'მოგვარებული', completed: false, active: false },
            ]}
          />

          <Button title="მთავარზე დაბრუნება" onPress={() => router.back()} style={styles.successBtn} />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <Stack.Screen options={{ headerShown: false }} />

      {/* Header */}
      <View style={styles.header}>
        <Ionicons name="arrow-back" size={24} color={colors.textPrimary} onPress={() => router.back()} />
        <Text style={styles.headerTitle}>
          {step === 'moral-filter' ? 'მორალური ფილტრი' : 'SOS შეტყობინება'}
        </Text>
      </View>

      <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <ScrollView contentContainerStyle={styles.content}>
          {step === 'moral-filter' ? (
            <>
              <Card>
                <Text style={styles.filterQuestion}>
                  ხართ თუ არა პატიოსანი, მშრომელი ადამიანი, რომელიც გახდა უსამართლობის მსხვერპლი?
                </Text>
              </Card>
              <Text style={styles.inputLabel}>თქვენი პასუხი</Text>
              <TextInput
                style={styles.textArea}
                multiline
                numberOfLines={4}
                value={moralAnswer}
                onChangeText={setMoralAnswer}
                placeholder="აღწერეთ თქვენი სიტუაცია..."
                placeholderTextColor={colors.textSecondary}
                textAlignVertical="top"
              />
              <Button
                title="გაგრძელება"
                onPress={() => setStep('form')}
                disabled={moralAnswer.length < 10}
              />
            </>
          ) : (
            <>
              <Text style={styles.inputLabel}>სათაური</Text>
              <TextInput
                style={styles.input}
                value={title}
                onChangeText={setTitle}
                placeholder="შეტყობინების სათაური"
                placeholderTextColor={colors.textSecondary}
              />

              <Text style={styles.inputLabel}>აღწერა</Text>
              <TextInput
                style={styles.textArea}
                multiline
                numberOfLines={5}
                value={description}
                onChangeText={setDescription}
                placeholder="აღწერეთ პრობლემა დეტალურად..."
                placeholderTextColor={colors.textSecondary}
                textAlignVertical="top"
              />

              <Button
                title="გაგზავნა"
                variant="danger"
                onPress={() => setStep('submitted')}
                disabled={!title || description.length < 10}
              />
            </>
          )}
        </ScrollView>
      </KeyboardAvoidingView>
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
  filterQuestion: {
    ...typography.body,
    color: colors.textPrimary,
    lineHeight: 26,
  },
  inputLabel: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    fontWeight: '600',
  },
  input: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    ...typography.body,
    color: colors.textPrimary,
  },
  textArea: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.divider,
    borderRadius: borderRadius.md,
    padding: spacing.md,
    ...typography.body,
    color: colors.textPrimary,
    minHeight: 120,
  },
  // Success state
  successCenter: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: spacing.xl,
    gap: spacing.md,
  },
  successIcon: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.primaryLight,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.sm,
  },
  successTitle: {
    ...typography.h1,
    color: colors.primary,
  },
  successSubtitle: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.md,
  },
  successBtn: {
    width: '100%',
    marginTop: spacing.lg,
  },
});
