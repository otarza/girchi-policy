import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { Button } from '@/src/components/ui/Button';
import { useApp } from '@/src/context/AppContext';
import { colors, typography, spacing } from '@/src/theme';

export default function CompleteScreen() {
  const router = useRouter();
  const { setOnboarded } = useApp();

  const handleContinue = () => {
    setOnboarded(true);
    router.replace('/(tabs)');
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.center}>
          <View style={styles.checkCircle}>
            <Ionicons name="checkmark" size={48} color={colors.white} />
          </View>
          <Text style={styles.title}>მოგესალმებით!</Text>
          <Text style={styles.subtitle}>
            თქვენი ადაპტაცია დასრულებულია. კეთილი იყოს თქვენი მობრძანება გირჩის ციფრულ პოლიტიკის პლატფორმაზე.
          </Text>
        </View>

        <View style={styles.bottom}>
          <Button title="გაგრძელება" onPress={handleContinue} />
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
  checkCircle: {
    width: 88,
    height: 88,
    borderRadius: 44,
    backgroundColor: colors.primaryLight,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: spacing.lg,
  },
  title: {
    ...typography.h1,
    color: colors.primary,
    marginBottom: spacing.sm,
  },
  subtitle: {
    ...typography.body,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 26,
  },
  bottom: {
    paddingBottom: spacing.lg,
  },
});
