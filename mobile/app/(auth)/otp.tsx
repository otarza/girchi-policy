import React, { useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { OTPInput } from '@/src/components/ui/OTPInput';
import { useApp } from '@/src/context/AppContext';
import { colors, typography, spacing } from '@/src/theme';

export default function OTPScreen() {
  const router = useRouter();
  const { setAuthenticated } = useApp();
  const [verifying, setVerifying] = useState(false);

  const handleComplete = (_code: string) => {
    setVerifying(true);
    setTimeout(() => {
      setAuthenticated(true);
      router.replace('/(onboarding)/ged-check');
    }, 1000);
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <Text style={styles.header}>შეიყვანეთ კოდი</Text>
        <Text style={styles.subtitle}>კოდი გაგზავნილია +995 5XX XX XX XX-ზე</Text>

        <View style={styles.otpWrap}>
          {verifying ? (
            <View style={styles.spinner}>
              <ActivityIndicator size="large" color={colors.primary} />
              <Text style={styles.verifyingText}>მიმდინარეობს ვერიფიკაცია...</Text>
            </View>
          ) : (
            <OTPInput onComplete={handleComplete} />
          )}
        </View>

        <Text style={styles.resend}>ხელახლა გაგზავნა 01:30-ში</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.surface,
  },
  content: {
    flex: 1,
    padding: spacing.xl,
  },
  header: {
    ...typography.h1,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.body,
    color: colors.textSecondary,
    marginBottom: spacing.xxl,
  },
  otpWrap: {
    marginTop: spacing.lg,
  },
  spinner: {
    alignItems: 'center',
    gap: spacing.md,
    paddingVertical: spacing.xl,
  },
  verifyingText: {
    ...typography.body,
    color: colors.textSecondary,
  },
  resend: {
    ...typography.bodySmall,
    color: colors.textSecondary,
    textAlign: 'center',
    marginTop: spacing.xl,
  },
});
