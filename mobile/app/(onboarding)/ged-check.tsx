import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Button } from '@/src/components/ui/Button';
import { colors, typography, spacing } from '@/src/theme';

export default function GedCheckScreen() {
  const router = useRouter();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.center}>
          <View style={styles.icon}>
            <Ionicons name="shield-checkmark" size={56} color={colors.primary} />
          </View>
          <Text style={styles.header}>ხართ თუ არა GeDer?</Text>
          <Text style={styles.description}>
            GeD (Girchi e-Democracy) არის გირჩის ციფრული საიდენტიფიკაციო სისტემა. GeDer-ები
            სისტემის ბირთვია — მათ აქვთ ხმის მიცემის, ენდორსმენტის და ლიდერობის სრული უფლება.
          </Text>
        </View>

        <View style={styles.actions}>
          <Button
            title="დიახ, მაქვს GeD"
            onPress={() => router.push('/(onboarding)/status-selection')}
          />
          <Button
            title="არა, გამოტოვება"
            variant="text"
            onPress={() => router.push('/(onboarding)/status-selection')}
          />
        </View>
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
    justifyContent: 'space-between',
    padding: spacing.xl,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  icon: {
    marginBottom: spacing.lg,
  },
  header: {
    ...typography.h1,
    color: colors.textPrimary,
    textAlign: 'center',
    marginBottom: spacing.md,
  },
  description: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 26,
  },
  actions: {
    gap: spacing.sm,
    paddingBottom: spacing.lg,
  },
});
