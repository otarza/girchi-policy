import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Button } from '@/src/components/ui/Button';
import { colors, typography, spacing, borderRadius } from '@/src/theme';

type StatusChoice = 'passive' | 'active' | null;

export default function StatusSelectionScreen() {
  const router = useRouter();
  const [selected, setSelected] = useState<StatusChoice>(null);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View>
          <Text style={styles.header}>აირჩიეთ თქვენი ჩართულობის დონე</Text>
          <Text style={styles.subtitle}>ეს არჩევანი განსაზღვრავს თქვენს უფლებებს სისტემაში</Text>
        </View>

        <View style={styles.cards}>
          <TouchableOpacity
            style={[styles.card, selected === 'passive' && styles.cardSelected]}
            onPress={() => setSelected('passive')}
            activeOpacity={0.7}
          >
            {selected === 'passive' && (
              <Ionicons name="checkmark-circle" size={24} color={colors.primary} style={styles.check} />
            )}
            <Ionicons name="eye-outline" size={32} color={selected === 'passive' ? colors.primary : colors.textSecondary} />
            <Text style={[styles.cardTitle, selected === 'passive' && styles.cardTitleSelected]}>
              პასიური წევრი
            </Text>
            <Text style={styles.cardDesc}>მზად ვარ, მივიღო მონაწილეობა არჩევნებში</Text>
            <Text style={styles.cardFootnote}>შეგიძლიათ ხმის მიცემა, პეტიციების ხელმოწერა</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.card, styles.cardBold, selected === 'active' && styles.cardSelected]}
            onPress={() => setSelected('active')}
            activeOpacity={0.7}
          >
            {selected === 'active' && (
              <Ionicons name="checkmark-circle" size={24} color={colors.primary} style={styles.check} />
            )}
            <Ionicons name="megaphone-outline" size={32} color={selected === 'active' ? colors.primary : colors.accent} />
            <Text style={[styles.cardTitle, selected === 'active' && styles.cardTitleSelected]}>
              აქტიური წევრი
            </Text>
            <Text style={styles.cardDesc}>მზად ვარ, საჯაროდ გამოვხატო ჩემი პოზიცია</Text>
            <Text style={styles.cardFootnote}>მხოლოდ აქტიური წევრი შეიძლება აირჩეს ათისთავად</Text>
          </TouchableOpacity>
        </View>

        <Button
          title="შემდეგი"
          onPress={() => router.push('/(onboarding)/territory')}
          disabled={!selected}
        />
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
    justifyContent: 'space-between',
  },
  header: {
    ...typography.h2,
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.body,
    color: colors.textSecondary,
  },
  cards: {
    gap: spacing.md,
  },
  card: {
    borderWidth: 2,
    borderColor: colors.divider,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    gap: spacing.xs,
    position: 'relative',
  },
  cardBold: {
    borderColor: colors.accent + '40',
    backgroundColor: colors.accent + '06',
  },
  cardSelected: {
    borderColor: colors.primary,
    backgroundColor: colors.primarySurface,
  },
  check: {
    position: 'absolute',
    top: spacing.md,
    right: spacing.md,
  },
  cardTitle: {
    ...typography.h3,
    color: colors.textPrimary,
    marginTop: spacing.xs,
  },
  cardTitleSelected: {
    color: colors.primary,
  },
  cardDesc: {
    ...typography.body,
    color: colors.textSecondary,
  },
  cardFootnote: {
    ...typography.caption,
    color: colors.textSecondary,
    fontStyle: 'italic',
  },
});
